from __future__ import annotations

from datetime import datetime, timezone
from fastapi import APIRouter, Header, HTTPException, WebSocket, WebSocketDisconnect

from .cloud_device_registry import DeviceSession
from .cloud_task_channel import DeviceTaskResultEnvelope
from .gateway_auth import parse_bearer_principal
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
        "list_devices", "get_device_status", "run_device_task",
    ]}
@router.websocket("/device/ws/{device_id}")
async def device_ws(websocket: WebSocket, device_id: str):
    token = websocket.query_params.get("token", "")
    principal = parse_bearer_principal(f"Bearer {token}" if token else "")
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
