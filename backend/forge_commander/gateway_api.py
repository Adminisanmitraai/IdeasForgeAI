from __future__ import annotations

from datetime import datetime, timezone
import hmac
import os
import time
from hashlib import sha256
from fastapi import APIRouter, Header, HTTPException, WebSocket, WebSocketDisconnect

from .cloud_device_registry import DeviceSession
from .cloud_task_channel import DeviceTaskResultEnvelope
from .gateway_auth import parse_bearer_principal
from .device_auth import issue_device_token, parse_device_token
from .gateway_session_manager import GatewaySessionManager, LiveGatewaySession

FORGE_COMMANDER_GATEWAY_API_VERSION = "forge-commander.gateway-api.v1"

router = APIRouter(prefix="/forge-commander", tags=["forge-commander"])
session_manager = GatewaySessionManager()

@router.get("/health")
def gateway_health():
    return {"ok": True, "service": "forge-commander-gateway"}

@router.get("/mcp/tools")
def list_mcp_tools(authorization: str | None = Header(default=None)):
    principal = parse_bearer_principal(authorization or "")
    if principal is None:
        raise HTTPException(status_code=401, detail="unauthorized")
    return {"owner_subject": principal.owner_subject, "tools": [
        "list_devices", "get_device_status",
        "device_identity", "device_resources", "device_runtime", "device_hardware",
        "device_storage", "device_processes", "device_network", "device_software",
        "device_dev_environment", "file_list", "file_read_text", "terminal_read",
        "run_device_task", "write_file_text", "delete_file", "run_terminal_profile",
    ]}
@router.post("/device/enroll")
def enroll_device(payload: dict, x_forge_enrollment_secret: str | None = Header(default=None)):
    configured_hash = os.getenv("FORGE_COMMANDER_ENROLLMENT_BOOTSTRAP_SHA256", "")
    allowed_hashes = (configured_hash,) if configured_hash else ()
    presented = (x_forge_enrollment_secret or "").strip()
    presented_hash = sha256(presented.encode("utf-8")).hexdigest() if presented else ""

    print(
        "FC_AUTH_R1C_R2",
        "env_present=", bool(configured_hash),
        "env_len=", len(configured_hash),
        "env_suffix=", configured_hash[-6:] if configured_hash else "EMPTY",
        "presented_len=", len(presented),
        "presented_hash_suffix=", presented_hash[-6:] if presented_hash else "EMPTY",
        flush=True,
    )
    if not presented_hash or not any(hmac.compare_digest(presented_hash, candidate) for candidate in allowed_hashes):
        raise HTTPException(status_code=401, detail="invalid_enrollment_secret")
    owner = str(payload.get("owner_subject", "")).strip()
    device_id = str(payload.get("device_id", "")).strip()
    if not owner or not device_id:
        raise HTTPException(status_code=400, detail="owner_subject_and_device_id_required")
    signing_key = os.getenv("FORGE_COMMANDER_GATEWAY_SIGNING_KEY", "")
    if not signing_key:
        raise HTTPException(status_code=503, detail="gateway_signing_unavailable")
    expires_at = int(time.time()) + 90 * 24 * 60 * 60
    token = issue_device_token(owner, device_id, signing_key=signing_key, expires_at=expires_at)
    return {"enrolled": True, "owner_subject": owner, "device_id": device_id,
            "device_token": token, "expires_at": expires_at}

@router.websocket("/device/ws/{device_id}")
async def device_ws(websocket: WebSocket, device_id: str):
    authorization = websocket.headers.get("authorization", "")
    token = authorization[7:].strip() if authorization.startswith("Bearer ") else ""
    principal = parse_device_token(token, expected_device_id=device_id)
    if principal is None:
        await websocket.close(code=4401)
        return
    session_id = websocket.query_params.get("session_id", "").strip()
    instance_id = websocket.query_params.get("instance_id", "").strip()
    if not session_id or not instance_id:
        await websocket.close(code=4400)
        return
    await websocket.accept()
    now = datetime.now(timezone.utc).isoformat()
    session = DeviceSession(
        session_id=session_id, device_id=device_id,
        owner_subject=principal.owner_subject, instance_id=instance_id,
        connected_at=now, heartbeat_at=now,
    )
    try:
        session_manager.attach(LiveGatewaySession(session, websocket, now))
        while True:
            message = await websocket.receive_json()
            if message.get("type") == "heartbeat":
                heartbeat_at = message.get("at", datetime.now(timezone.utc).isoformat())
                session_manager.heartbeat(device_id, session_id, heartbeat_at)
                await websocket.send_json({"type": "heartbeat_ack", "at": heartbeat_at})
            elif message.get("type") == "result":
                session_manager.accept_result(DeviceTaskResultEnvelope(
                    task_id=str(message.get("task_id", "")), device_id=device_id,
                    session_id=session_id, succeeded=bool(message.get("succeeded")),
                    reason=str(message.get("reason", "device_result")), output=message.get("output"),
                ))
    except WebSocketDisconnect:
        session_manager.detach(device_id, session_id)

__all__ = [
    "FORGE_COMMANDER_GATEWAY_API_VERSION", "router", "session_manager",
]
