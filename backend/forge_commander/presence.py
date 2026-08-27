from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone

from .contracts import ForgeCommanderDevice

FORGE_COMMANDER_PRESENCE_VERSION = "forge-commander.presence.v1"


def _parse(value: str) -> datetime:
    text = value.strip().replace("Z", "+00:00")
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def register_device(
    device: ForgeCommanderDevice, *, connected_at: str
) -> ForgeCommanderDevice:
    return replace(
        device,
        state="online",
        connected_at=connected_at,
        last_heartbeat_at=connected_at,
    )


def heartbeat(
    device: ForgeCommanderDevice, *, at: str,
    state: str | None = None,
) -> ForgeCommanderDevice:
    next_state = device.state if state is None else state
    if next_state not in {"online", "working", "approval_required"}:
        raise ValueError("heartbeat state must represent a connected device")
    return replace(
        device,
        state=next_state,
        last_heartbeat_at=at,
    )


def resolve_presence(
    device: ForgeCommanderDevice, *, now: str,
    offline_after_seconds: int = 90,
) -> ForgeCommanderDevice:
    if device.last_heartbeat_at is None:
        return replace(device, state="offline")
    age = (_parse(now) - _parse(device.last_heartbeat_at)).total_seconds()
    if age > max(1, int(offline_after_seconds)):
        return replace(device, state="offline")
    return device


__all__ = [
    "FORGE_COMMANDER_PRESENCE_VERSION",
    "register_device",
    "heartbeat",
    "resolve_presence",
]
