from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Literal

FORGE_COMMANDER_UNIVERSAL_DEVICE_VERSION = "forge-commander.universal-device.v1"

DevicePlatform = Literal["windows", "android", "ios", "macos", "linux"]
DevicePresence = Literal["online", "offline", "busy", "approval_required"]
Capability = Literal[
    "terminal", "files", "git", "desktop_vision", "gui_control",
    "notifications", "device_info", "app_actions", "voice",
]

@dataclass(frozen=True, slots=True)
class EnrolledDevice:
    device_id: str
    owner_subject: str
    display_name: str
    platform: DevicePlatform
    capabilities: tuple[Capability, ...]
    presence: DevicePresence = "offline"
    last_seen_at: str | None = None

@dataclass(frozen=True, slots=True)
class DeviceRouteRequest:
    owner_subject: str
    required_capability: Capability
    preferred_device_id: str | None = None

@dataclass(frozen=True, slots=True)
class DeviceRouteDecision:
    routed: bool
    device_id: str | None
    reason: str
    route_id: str


def _route_id(subject: str, capability: str, device_id: str | None) -> str:
    raw = f"{subject}\n{capability}\n{device_id or ''}"
    return "fc-route-" + sha256(raw.encode("utf-8")).hexdigest()[:20]


def route_device(request: DeviceRouteRequest,
                 devices: tuple[EnrolledDevice, ...]) -> DeviceRouteDecision:
    owned = tuple(d for d in devices if d.owner_subject == request.owner_subject)
    if request.preferred_device_id:
        owned = tuple(d for d in owned if d.device_id == request.preferred_device_id)
    capable = tuple(
        d for d in owned
        if request.required_capability in d.capabilities and d.presence == "online"
    )
    if not capable:
        return DeviceRouteDecision(
            False, None, "no_online_capable_device",
            _route_id(request.owner_subject, request.required_capability, None),
        )
    selected = capable[0]
    return DeviceRouteDecision(
        True, selected.device_id, "device_routed",
        _route_id(request.owner_subject, request.required_capability, selected.device_id),
    )

__all__ = [
    "FORGE_COMMANDER_UNIVERSAL_DEVICE_VERSION", "DevicePlatform",
    "DevicePresence", "Capability", "EnrolledDevice", "DeviceRouteRequest",
    "DeviceRouteDecision", "route_device",
]
