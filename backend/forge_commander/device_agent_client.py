from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Awaitable, Callable

import websockets

FORGE_COMMANDER_DEVICE_AGENT_CLIENT_VERSION = "forge-commander.device-agent-client.v1"

TaskHandler = Callable[[dict], Awaitable[dict]]

@dataclass(frozen=True, slots=True)
class AgentConnectionConfig:
    gateway_ws_url: str
    device_id: str
    session_id: str
    instance_id: str
    bearer_token: str
    heartbeat_seconds: float = 15.0

def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _connect_url(config: AgentConnectionConfig) -> str:
    from urllib.parse import urlencode
    query = urlencode({
        "token": config.bearer_token,
        "session_id": config.session_id,
        "instance_id": config.instance_id,
    })
    return f"{config.gateway_ws_url.rstrip('/')}/{config.device_id}?{query}"


async def _heartbeat_loop(ws, seconds: float) -> None:
    while True:
        await asyncio.sleep(max(1.0, seconds))
        await ws.send(json.dumps({"type": "heartbeat", "at": _utc_now()}))


async def run_agent_once(config: AgentConnectionConfig, handler: TaskHandler) -> dict:
    url = _connect_url(config)
    async with websockets.connect(url, open_timeout=10, close_timeout=5) as ws:
        heartbeat = asyncio.create_task(_heartbeat_loop(ws, config.heartbeat_seconds))
        try:
            while True:
                message = json.loads(await ws.recv())
                if message.get("type") != "task":
                    continue
                result = await handler(message)
                payload = {
                    "type": "result",
                    "task_id": message["task_id"],
                    "device_id": config.device_id,
                    "session_id": config.session_id,
                    "succeeded": bool(result.get("succeeded")),
                    "reason": str(result.get("reason", "completed")),
                    "output": result.get("output"),
                }
                await ws.send(json.dumps(payload))
                return payload
        finally:
            heartbeat.cancel()


__all__ = [
    "FORGE_COMMANDER_DEVICE_AGENT_CLIENT_VERSION", "AgentConnectionConfig",
    "TaskHandler", "run_agent_once",
]
