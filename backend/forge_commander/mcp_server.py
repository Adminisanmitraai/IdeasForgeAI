from __future__ import annotations

import asyncio
import os
from typing import Any

from mcp.server.fastmcp import Context, FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import ToolAnnotations

from .cloud_task_channel import build_task_envelope
from .gateway_auth import parse_bearer_principal
from .gateway_session_manager import GatewaySessionManager

FORGE_COMMANDER_MCP_SERVER_VERSION = "forge-commander.mcp-server.v1"


def _owner_from_context(ctx: Context) -> str:
    req = ctx.request_context.request if ctx.request_context else None
    authorization = req.headers.get("authorization", "") if req is not None else ""
    principal = parse_bearer_principal(authorization)
    if principal is None:
        raise PermissionError("unauthorized")
    return principal.owner_subject

def build_mcp_server(manager: GatewaySessionManager) -> FastMCP:
    test_mode = os.getenv("FORGE_COMMANDER_MCP_TEST_MODE", "").lower() in {"1", "true", "yes"}
    security = TransportSecuritySettings(
        enable_dns_rebinding_protection=not test_mode,
    )
    mcp = FastMCP(
        "ForgeCommander", instructions="Governed access to enrolled Forge devices.",
        stateless_http=True, json_response=True, transport_security=security,
    )

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

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True, idempotentHint=False))
    async def run_device_task(device_id: str, instruction: str,
                              required_capability: str = "gui_control",
                              approval_required: bool = True,
                              ctx: Context | None = None) -> dict[str, Any]:
        if ctx is None:
            raise PermissionError("missing request context")
        owner = _owner_from_context(ctx)
        live = manager.get(device_id)
        if live is None or live.session.owner_subject != owner:
            return {"succeeded": False, "reason": "device_not_online"}
        envelope = build_task_envelope(
            live.session, instruction=instruction,
            required_capability=required_capability,
            approval_required=approval_required,
        )
        await manager.dispatch(envelope)
        result = await manager.wait_result(envelope.task_id, timeout_seconds=20.0)
        if result is None:
            return {"succeeded": False, "reason": "device_result_timeout", "task_id": envelope.task_id}
        return {"succeeded": result.succeeded, "reason": result.reason,
                "output": result.output, "task_id": result.task_id}

    return mcp

__all__ = ["FORGE_COMMANDER_MCP_SERVER_VERSION", "build_mcp_server"]
