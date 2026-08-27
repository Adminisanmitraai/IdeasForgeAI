from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Literal

FORGE_COMMANDER_DEVICE_WS_VERSION = "forge-commander.device-ws.v1"
MessageType = Literal["hello", "heartbeat", "task", "result", "error"]

@dataclass(frozen=True, slots=True)
class DeviceWsMessage:
    message_id: str
    message_type: MessageType
    device_id: str
    session_id: str
    payload: str = ""


def build_message(message_type: MessageType, *, device_id: str,
                  session_id: str, payload: str = "") -> DeviceWsMessage:
    if not device_id.strip() or not session_id.strip():
        raise ValueError("device_id and session_id are required")
    raw = f"{message_type}\n{device_id}\n{session_id}\n{payload}"
    digest = sha256(raw.encode("utf-8")).hexdigest()[:24]
    return DeviceWsMessage(f"fc-ws-{digest}", message_type,
                           device_id.strip(), session_id.strip(), payload)
