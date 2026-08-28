from __future__ import annotations

import asyncio
import html
import json
import os
from typing import Any

from mcp.server.fastmcp import Context, FastMCP
from mcp.server.auth.middleware.auth_context import get_access_token
from mcp.server.auth.settings import AuthSettings, ClientRegistrationOptions
from pydantic import AnyHttpUrl
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import ToolAnnotations

from .cloud_task_channel import build_task_envelope
from .oauth_provider import ForgeCommanderOAuthProvider
from .gateway_session_manager import GatewaySessionManager

FORGE_COMMANDER_MCP_SERVER_VERSION = "forge-commander.mcp-server.v1"

_CAPABILITY_ALIASES = {
    "write_file_text": "file.write_text",
    "delete_file": "file.delete",
    "run_terminal_profile": "terminal.execute_profile",
    "file_read_text": "file.read_text",
    "file_list": "file.list",
    "terminal_read": "terminal.query",
}


def _canonical_capability(value: str) -> str:
    normalized = value.strip()
    return _CAPABILITY_ALIASES.get(normalized, normalized)


def _csv_env(name: str) -> list[str]:
    return [item.strip() for item in os.getenv(name, "").split(",") if item.strip()]


def _host_allowlist() -> list[str]:
    hosts: list[str] = []
    for host in _csv_env("FORGE_COMMANDER_MCP_ALLOWED_HOSTS"):
        if host not in hosts:
            hosts.append(host)
        if ":" not in host and f"{host}:*" not in hosts:
            hosts.append(f"{host}:*")
    return hosts


def _oauth_access():
    token = get_access_token()
    if token is None or not token.subject:
        raise PermissionError("unauthorized")
    return token

def _owner_from_context(ctx: Context) -> str:
    return str(_oauth_access().subject)

def build_mcp_server(manager: GatewaySessionManager) -> FastMCP:
    test_mode = os.getenv("FORGE_COMMANDER_MCP_TEST_MODE", "").lower() in {"1", "true", "yes"}
    security = TransportSecuritySettings(
        enable_dns_rebinding_protection=not test_mode,
        allowed_hosts=_host_allowlist(),
        allowed_origins=_csv_env("FORGE_COMMANDER_MCP_ALLOWED_ORIGINS"),
    )
    issuer = os.getenv("FORGE_COMMANDER_OAUTH_ISSUER", "https://commander.ideasforgeai.com/forge-commander").rstrip("/")
    resource = os.getenv("FORGE_COMMANDER_OAUTH_RESOURCE", issuer + "/mcp")
    provider = ForgeCommanderOAuthProvider(issuer)
    auth = AuthSettings(
        issuer_url=AnyHttpUrl(issuer), resource_server_url=AnyHttpUrl(resource),
        client_registration_options=ClientRegistrationOptions(
            enabled=True, valid_scopes=["forge.devices.read", "forge.devices.control"],
            default_scopes=["forge.devices.read", "forge.devices.control"],
        ), required_scopes=["forge.devices.read"],
    )
    mcp = FastMCP(
        "ForgeCommander", instructions="Governed access to enrolled Forge devices.",
        auth_server_provider=provider, auth=auth,
        stateless_http=True, json_response=True, transport_security=security,
    )

    @mcp.custom_route("/oauth/approve", methods=["GET", "POST"])
    async def oauth_approve(request: Request):
        if request.method == "GET":
            pending = request.query_params.get("request", "")
            safe_pending = html.escape(pending, quote=True)
            return HTMLResponse(f"""<!doctype html><html><head><title>ForgeCommander Authorization</title>
<meta name='viewport' content='width=device-width,initial-scale=1'>
<style>body{{font-family:system-ui;background:#0b0d12;color:#f7f7f7;display:grid;place-items:center;min-height:100vh}}
main{{width:min(460px,90vw);padding:28px;border:1px solid #343946;border-radius:18px;background:#151923}}
input,button{{width:100%;box-sizing:border-box;padding:12px;margin-top:12px;border-radius:10px}}button{{font-weight:700}}</style></head>
<body><main><h2>Authorize ForgeCommander</h2><p>Allow ChatGPT to access your enrolled Forge devices.</p>
<form method='post'><input type='hidden' name='request' value='{safe_pending}'>
<input type='password' name='owner_secret' placeholder='One-time owner approval secret' required autocomplete='one-time-code'>
<button type='submit'>Authorize ChatGPT</button></form></main></body></html>""", headers={"Cache-Control":"no-store"})
        form = await request.form()
        redirect = provider.approve_request(str(form.get("request", "")), str(form.get("owner_secret", "")))
        if redirect is None:
            return HTMLResponse("Authorization denied", status_code=401, headers={"Cache-Control":"no-store"})
        return RedirectResponse(redirect, status_code=302, headers={"Cache-Control":"no-store"})

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True))
    def list_devices(ctx: Context) -> dict[str, Any]:
        owner = _owner_from_context(ctx)
        devices = [
            {"device_id": live.session.device_id, "session_id": live.session.session_id,
             "online": True, "last_heartbeat_at": live.last_heartbeat_at}
            for live in manager.live_sessions(owner_subject=owner)
        ]
        return {"devices": devices}

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True))
    def get_device_status(device_id: str, ctx: Context) -> dict[str, Any]:
        owner = _owner_from_context(ctx)
        live = manager.get(device_id)
        if live is None or live.session.owner_subject != owner:
            return {"device_id": device_id, "online": False}
        return {"device_id": device_id, "online": True, "session_id": live.session.session_id,
                "last_heartbeat_at": live.last_heartbeat_at}

    async def _run_read_only_probe(device_id: str, capability: str, ctx: Context, request: dict[str, Any] | None = None) -> dict[str, Any]:
        owner = _owner_from_context(ctx)
        live = manager.get(device_id)
        if live is None or live.session.owner_subject != owner:
            return {"succeeded": False, "reason": "device_not_online"}
        instruction = json.dumps(request, separators=(",", ":")) if request is not None else f"Read-only ForgeCommander probe: {capability}"
        envelope = build_task_envelope(
            live.session,
            instruction=instruction,
            required_capability=capability,
            approval_required=False,
            request=request,
        )
        await manager.dispatch(envelope)
        result = await manager.wait_result(envelope.task_id, timeout_seconds=20.0)
        if result is None:
            return {"succeeded": False, "reason": "device_result_timeout", "task_id": envelope.task_id}
        return {"succeeded": result.succeeded, "reason": result.reason,
                "output": result.output, "task_id": result.task_id}

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True))
    async def device_identity(device_id: str, ctx: Context) -> dict[str, Any]:
        """Read basic device identity such as hostname, OS, and architecture."""
        return await _run_read_only_probe(device_id, "device.identity", ctx)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True))
    async def device_resources(device_id: str, ctx: Context) -> dict[str, Any]:
        """Read CPU, memory, and disk resource information from the device."""
        return await _run_read_only_probe(device_id, "device.resources", ctx)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True))
    async def device_runtime(device_id: str, ctx: Context) -> dict[str, Any]:
        """Read ForgeCommander runtime information from the device."""
        return await _run_read_only_probe(device_id, "device.runtime", ctx)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True))
    async def device_hardware(device_id: str, ctx: Context) -> dict[str, Any]:
        """Read CPU architecture and graphics hardware summary."""
        return await _run_read_only_probe(device_id, "device.hardware", ctx)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True))
    async def device_storage(device_id: str, ctx: Context) -> dict[str, Any]:
        """Read mounted storage volumes and free capacity."""
        return await _run_read_only_probe(device_id, "device.storage", ctx)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True))
    async def device_processes(device_id: str, ctx: Context) -> dict[str, Any]:
        """Read a bounded process summary without command-line arguments."""
        return await _run_read_only_probe(device_id, "device.processes", ctx)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True))
    async def device_network(device_id: str, ctx: Context) -> dict[str, Any]:
        """Read local hostname and bounded interface address information."""
        return await _run_read_only_probe(device_id, "device.network", ctx)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True))
    async def device_software(device_id: str, ctx: Context) -> dict[str, Any]:
        """Read a bounded installed-software inventory."""
        return await _run_read_only_probe(device_id, "device.software", ctx)

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True))
    async def device_dev_environment(device_id: str, ctx: Context) -> dict[str, Any]:
        """Read availability of common development tools."""
        return await _run_read_only_probe(device_id, "device.dev_environment", ctx)


    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True))
    async def file_list(device_id: str, path: str, ctx: Context) -> dict[str, Any]:
        """List up to 100 entries in an allowed local directory; no file content is read."""
        return await _run_read_only_probe(device_id, "file.list", ctx, {"path": path})

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True))
    async def file_read_text(device_id: str, path: str, ctx: Context) -> dict[str, Any]:
        """Read an allowlisted text file up to 64 KB; sensitive credential paths are blocked."""
        return await _run_read_only_probe(device_id, "file.read_text", ctx, {"path": path})

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True))
    async def terminal_read(device_id: str, profile: str, cwd: str, ctx: Context) -> dict[str, Any]:
        """Run a fixed read-only diagnostic profile such as git_status or python_version; arbitrary commands are not accepted."""
        return await _run_read_only_probe(device_id, "terminal.query", ctx, {"profile": profile, "cwd": cwd})

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True, idempotentHint=False))
    async def run_device_task(device_id: str, instruction: str,
                              required_capability: str = "gui_control",
                              approval_required: bool = True,
                              approval_granted: bool = False,
                              ctx: Context | None = None) -> dict[str, Any]:
        if ctx is None:
            raise PermissionError("missing request context")
        capability = _canonical_capability(required_capability)
        if capability in {"file.write_text", "file.delete", "terminal.execute_profile"}:
            try:
                request = json.loads(instruction)
            except (TypeError, json.JSONDecodeError):
                return {"succeeded": False, "reason": "structured_request_required"}
            if not isinstance(request, dict):
                return {"succeeded": False, "reason": "structured_request_required"}
            return await _dispatch_approved(
                device_id, capability, request, approval_granted, ctx,
            )
        access = _oauth_access()
        if "forge.devices.control" not in access.scopes:
            return {"succeeded": False, "reason": "oauth_control_scope_required"}
        owner = str(access.subject)
        live = manager.get(device_id)
        if live is None or live.session.owner_subject != owner:
            return {"succeeded": False, "reason": "device_not_online"}
        envelope = build_task_envelope(
            live.session, instruction=instruction,
            required_capability=capability,
            approval_required=approval_required,
            approval_granted=approval_granted,
        )
        await manager.dispatch(envelope)
        result = await manager.wait_result(envelope.task_id, timeout_seconds=20.0)
        if result is None:
            return {"succeeded": False, "reason": "device_result_timeout", "task_id": envelope.task_id}
        return {"succeeded": result.succeeded, "reason": result.reason,
                "output": result.output, "task_id": result.task_id}

    async def _dispatch_approved(device_id: str, capability: str,
                                 request: dict[str, Any],
                                 approval_granted: bool,
                                 ctx: Context) -> dict[str, Any]:
        access = _oauth_access()
        if "forge.devices.control" not in access.scopes:
            return {"succeeded": False, "reason": "oauth_control_scope_required"}
        owner = str(access.subject)
        live = manager.get(device_id)
        if live is None or live.session.owner_subject != owner:
            return {"succeeded": False, "reason": "device_not_online"}
        envelope = build_task_envelope(
            live.session, instruction=json.dumps(request, separators=(",", ":")),
            required_capability=capability, approval_required=True,
            request=request, approval_granted=approval_granted,
        )
        await manager.dispatch(envelope)
        result = await manager.wait_result(envelope.task_id, timeout_seconds=120.0)
        if result is None:
            return {"succeeded": False, "reason": "device_result_timeout",
                    "task_id": envelope.task_id}
        return {"succeeded": result.succeeded, "reason": result.reason,
                "output": result.output, "task_id": result.task_id}

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False, destructiveHint=True, idempotentHint=False,
    ))
    async def write_file_text(device_id: str, path: str, content: str,
                              approval_granted: bool = False,
                              ctx: Context | None = None) -> dict[str, Any]:
        """Write bounded text in an approved root after explicit approval."""
        if ctx is None:
            raise PermissionError("missing request context")
        return await _dispatch_approved(
            device_id, "file.write_text", {"path": path, "content": content},
            approval_granted, ctx,
        )

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False, destructiveHint=True, idempotentHint=False,
    ))
    async def delete_file(device_id: str, path: str,
                          approval_granted: bool = False,
                          ctx: Context | None = None) -> dict[str, Any]:
        """Delete one allowlisted file after explicit approval; directories and sensitive paths are blocked."""
        if ctx is None:
            raise PermissionError("missing request context")
        return await _dispatch_approved(
            device_id, "file.delete", {"path": path}, approval_granted, ctx,
        )

    @mcp.tool(annotations=ToolAnnotations(
        readOnlyHint=False, destructiveHint=True, idempotentHint=False,
    ))
    async def run_terminal_profile(device_id: str, profile: str, cwd: str,
                                   approval_granted: bool = False,
                                   ctx: Context | None = None) -> dict[str, Any]:
        """Run an approval-gated profile: forge_commander_tests, python_compile, or git_diff_check."""
        if ctx is None:
            raise PermissionError("missing request context")
        return await _dispatch_approved(
            device_id, "terminal.execute_profile", {"profile": profile, "cwd": cwd},
            approval_granted, ctx,
        )

    return mcp

__all__ = ["FORGE_COMMANDER_MCP_SERVER_VERSION", "build_mcp_server"]
