from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .cloud_device_registry import DeviceSession
from .cloud_task_channel import DeviceTaskEnvelope, DeviceTaskResultEnvelope

FORGE_COMMANDER_GATEWAY_SESSION_MANAGER_VERSION = "forge-commander.gateway-session-manager.v1"

@dataclass
class LiveGatewaySession:
    session: DeviceSession
    transport: Any
    last_heartbeat_at: str

class GatewaySessionManager:
    def __init__(self) -> None:
        self._sessions: dict[str, LiveGatewaySession] = {}
        self._pending_results: dict[str, DeviceTaskResultEnvelope] = {}
    def attach(self, live: LiveGatewaySession) -> None:
        existing = self._sessions.get(live.session.device_id)
        if existing and existing.session.session_id != live.session.session_id:
            raise ValueError("device already has a live gateway session")
        self._sessions[live.session.device_id] = live

    def detach(self, device_id: str, session_id: str) -> None:
        existing = self._sessions.get(device_id)
        if existing and existing.session.session_id == session_id:
            self._sessions.pop(device_id, None)

    def heartbeat(self, device_id: str, session_id: str, at: str) -> None:
        live = self._sessions.get(device_id)
        if not live or live.session.session_id != session_id:
            raise ValueError("gateway session not found")
        live.last_heartbeat_at = at

    def get(self, device_id: str) -> LiveGatewaySession | None:
        return self._sessions.get(device_id)
    async def dispatch(self, envelope: DeviceTaskEnvelope) -> None:
        live = self._sessions.get(envelope.device_id)
        if not live or live.session.session_id != envelope.session_id:
            raise ValueError("target device session is not connected")
        await live.transport.send_json({
            "type": "task",
            "task_id": envelope.task_id,
            "device_id": envelope.device_id,
            "session_id": envelope.session_id,
            "instruction": envelope.instruction,
            "required_capability": envelope.required_capability,
            "approval_required": envelope.approval_required,
            "request": envelope.request,
        })

    def accept_result(self, result: DeviceTaskResultEnvelope) -> None:
        live = self._sessions.get(result.device_id)
        if not live or live.session.session_id != result.session_id:
            raise ValueError("result session does not match live gateway session")
        self._pending_results[result.task_id] = result

    def pop_result(self, task_id: str) -> DeviceTaskResultEnvelope | None:
        return self._pending_results.pop(task_id, None)

__all__ = [
    "FORGE_COMMANDER_GATEWAY_SESSION_MANAGER_VERSION",
    "LiveGatewaySession", "GatewaySessionManager",
]


# FC-6U.4 async MCP helpers
def _live_sessions(self: GatewaySessionManager, *, owner_subject: str | None = None):
    values = tuple(self._sessions.values())
    if owner_subject is None:
        return values
    return tuple(v for v in values if v.session.owner_subject == owner_subject)

async def _wait_result(self: GatewaySessionManager, task_id: str,
                       *, timeout_seconds: float = 20.0,
                       poll_seconds: float = 0.05):
    import asyncio
    deadline = asyncio.get_running_loop().time() + max(0.1, timeout_seconds)
    while asyncio.get_running_loop().time() < deadline:
        result = self.pop_result(task_id)
        if result is not None:
            return result
        await asyncio.sleep(poll_seconds)
    return None

GatewaySessionManager.live_sessions = _live_sessions
GatewaySessionManager.wait_result = _wait_result
