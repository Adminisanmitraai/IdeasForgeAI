from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from rtx_node_enrollment_preflight import stable_windows_device_id


DEFAULT_HTTP_BASE = "https://ideasforgeai-api.onrender.com/forge-commander"
DEFAULT_WS_URL = "wss://ideasforgeai-api.onrender.com/forge-commander/device/ws"


class PairingRecoveryError(RuntimeError):
    pass


def _request_json(
    url: str,
    *,
    method: str,
    body: dict[str, Any] | None = None,
    bearer_token: str | None = None,
    timeout_seconds: int = 15,
) -> dict[str, Any]:
    payload = None if body is None else json.dumps(body).encode("utf-8")
    headers = {"Accept": "application/json", "User-Agent": "ForgeATL-RTX-Pairing/2D-R1A-R1"}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    if bearer_token:
        headers["Authorization"] = f"Bearer {bearer_token}"
    request = urllib.request.Request(url, data=payload, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            data = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raise PairingRecoveryError(f"gateway_http_{exc.code}") from exc
    except urllib.error.URLError as exc:
        raise PairingRecoveryError("gateway_unreachable") from exc
    try:
        parsed = json.loads(data)
    except json.JSONDecodeError as exc:
        raise PairingRecoveryError("gateway_invalid_json") from exc
    if not isinstance(parsed, dict):
        raise PairingRecoveryError("gateway_invalid_shape")
    return parsed


def _load_dpapi_token(path: Path) -> str:
    if not path.exists():
        raise PairingRecoveryError("device_token_missing")
    script = (
        "$e=Get-Content -Raw -LiteralPath '" + str(path).replace("'", "''") + "';"
        "$s=ConvertTo-SecureString $e;"
        "$b=[Runtime.InteropServices.Marshal]::SecureStringToBSTR($s);"
        "try{[Runtime.InteropServices.Marshal]::PtrToStringBSTR($b)}finally{"
        "[Runtime.InteropServices.Marshal]::ZeroFreeBSTR($b)}"
    )
    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-Command", script],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=10,
        check=False,
        shell=False,
    )
    token = result.stdout.strip()
    if result.returncode != 0 or not token:
        raise PairingRecoveryError("device_token_decrypt_failed")
    return token


def _save_dpapi_token(token: str, path: Path) -> None:
    if not token.strip():
        raise PairingRecoveryError("paired_token_empty")
    path.parent.mkdir(parents=True, exist_ok=True)
    script = (
        "$p=[Console]::In.ReadToEnd();"
        "$s=ConvertTo-SecureString $p -AsPlainText -Force;"
        "$e=ConvertFrom-SecureString $s;"
        "[IO.File]::WriteAllText($args[0],$e,[Text.Encoding]::UTF8)"
    )
    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-Command", script, str(path)],
        input=token,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=10,
        check=False,
        shell=False,
    )
    if result.returncode != 0:
        raise PairingRecoveryError("paired_token_encrypt_failed")


def request_pairing_ticket(
    *,
    existing_token_file: Path,
    http_base: str = DEFAULT_HTTP_BASE,
) -> dict[str, Any]:
    token = _load_dpapi_token(existing_token_file)
    response = _request_json(
        f"{http_base.rstrip('/')}/device/pairing-ticket",
        method="POST",
        bearer_token=token,
    )
    code = str(response.get("pairing_code") or "").strip()
    if not code:
        raise PairingRecoveryError("pairing_ticket_missing_code")
    return {
        "pairing_code": code,
        "expires_at": response.get("expires_at"),
        "ttl_seconds": response.get("ttl_seconds"),
    }


def write_pairing_ticket_file(ticket: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(str(ticket["pairing_code"]), encoding="utf-8")


def consume_pairing_ticket(
    *,
    pairing_code: str,
    current_device_id: str | None,
    state_dir: Path,
    project_root: Path,
    http_base: str = DEFAULT_HTTP_BASE,
    ws_url: str = DEFAULT_WS_URL,
) -> dict[str, Any]:
    derived_device_id = stable_windows_device_id()
    if current_device_id and current_device_id.strip() == derived_device_id:
        raise PairingRecoveryError("derived_device_id_matches_existing")
    response = _request_json(
        f"{http_base.rstrip('/')}/device/pair",
        method="POST",
        body={"pairing_code": pairing_code.strip(), "device_id": derived_device_id},
    )
    if response.get("enrolled") is not True:
        raise PairingRecoveryError("pairing_not_enrolled")
    returned_device_id = str(response.get("device_id") or "").strip()
    if returned_device_id != derived_device_id:
        raise PairingRecoveryError("paired_device_id_mismatch")
    token = str(response.get("device_token") or "").strip()
    owner = str(response.get("owner_subject") or "").strip()
    if not token or not owner:
        raise PairingRecoveryError("pairing_response_incomplete")

    token_path = state_dir / "device-token.dpapi"
    _save_dpapi_token(token, token_path)

    config = {
        "device_id": derived_device_id,
        "owner_subject": owner,
        "gateway_ws_url": ws_url,
        "credential_file": str(token_path),
        "project_root": str(project_root),
        "paired_via": "forgeatl-2d-r1a-r1",
    }
    (state_dir / "agent-config.json").write_text(
        json.dumps(config, indent=2), encoding="utf-8"
    )

    launcher = (
        "import asyncio\n"
        "from backend.forge_commander.production_agent_runtime import "
        "ProductionAgentConfig, run_persistent_agent\n\n"
        f"config = ProductionAgentConfig(\n"
        f"    gateway_ws_url={ws_url!r},\n"
        f"    device_id={derived_device_id!r},\n"
        f"    owner_subject={owner!r},\n"
        f"    credential_file={str(token_path)!r},\n"
        "    heartbeat_seconds=15.0,\n"
        "    reconnect_min_seconds=2.0,\n"
        "    reconnect_max_seconds=60.0,\n"
        ")\n\n"
        "asyncio.run(run_persistent_agent(config))\n"
    )
    launcher_path = state_dir / "agent-launcher.py"
    launcher_path.write_text(launcher, encoding="utf-8")

    return {
        "device_id": derived_device_id,
        "owner_subject": owner,
        "state_dir": str(state_dir),
        "launcher_path": str(launcher_path),
        "project_root": str(project_root),
        "token_persisted_dpapi": True,
        "token_exposed": False,
        "session_started": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    ticket = sub.add_parser("issue-ticket")
    ticket.add_argument("--token-file", required=True)
    ticket.add_argument("--output-file", required=True)

    pair = sub.add_parser("pair-rtx")
    pair.add_argument("--pairing-code-file", required=True)
    pair.add_argument("--state-dir", required=True)
    pair.add_argument("--project-root", required=True)
    pair.add_argument("--existing-device-id")

    args = parser.parse_args()

    if args.command == "issue-ticket":
        result = request_pairing_ticket(existing_token_file=Path(args.token_file))
        write_pairing_ticket_file(result, Path(args.output_file))
        print(json.dumps({
            "ticket_written": True,
            "output_file": args.output_file,
            "ttl_seconds": result.get("ttl_seconds"),
            "pairing_code_exposed": False,
        }, indent=2))
        return 0

    code = Path(args.pairing_code_file).read_text(encoding="utf-8").strip()
    result = consume_pairing_ticket(
        pairing_code=code,
        current_device_id=args.existing_device_id,
        state_dir=Path(args.state_dir),
        project_root=Path(args.project_root),
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
