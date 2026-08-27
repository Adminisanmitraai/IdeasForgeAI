from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from hashlib import sha256

from .universal_device_contract import EnrolledDevice

FORGE_COMMANDER_CLOUD_REGISTRY_VERSION = "forge-commander.cloud-registry.v1"

@dataclass(frozen=True, slots=True)
class DeviceSession:
    session_id: str
    device_id: str
    owner_subject: str
    instance_id: str
    connected_at: str
    heartbeat_at: str
    transport: str = "wss"

@dataclass(frozen=True, slots=True)
class SessionDecision:
    accepted: bool
    session: DeviceSession | None
    reason: str

def _parse(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _session_id(device_id: str, instance_id: str, connected_at: str) -> str:
    digest = sha256(
        f"{device_id}\n{instance_id}\n{connected_at}".encode("utf-8")
    ).hexdigest()[:20]
    return f"fc-session-{digest}"


def open_device_session(device: EnrolledDevice, *, instance_id: str,
                        connected_at: str, existing: DeviceSession | None = None,
                        stale_after_seconds: int = 90) -> SessionDecision:
    if not instance_id.strip():
        return SessionDecision(False, None, "instance_id_required")
    if existing and existing.device_id != device.device_id:
        return SessionDecision(False, None, "session_device_mismatch")
    if existing:
        age = (_parse(connected_at) - _parse(existing.heartbeat_at)).total_seconds()
        if existing.instance_id != instance_id and age <= max(1, stale_after_seconds):
            return SessionDecision(False, None, "fresh_session_already_active")
    session = DeviceSession(
        session_id=_session_id(device.device_id, instance_id, connected_at),
        device_id=device.device_id, owner_subject=device.owner_subject,
        instance_id=instance_id.strip(), connected_at=connected_at,
        heartbeat_at=connected_at,
    )
    return SessionDecision(True, session, "session_opened")


def refresh_device_session(session: DeviceSession, *, heartbeat_at: str) -> DeviceSession:
    return replace(session, heartbeat_at=heartbeat_at)


def session_online(session: DeviceSession, *, now: str,
                   offline_after_seconds: int = 120) -> bool:
    age = (_parse(now) - _parse(session.heartbeat_at)).total_seconds()
    return age <= max(1, offline_after_seconds)

__all__ = [
    "FORGE_COMMANDER_CLOUD_REGISTRY_VERSION", "DeviceSession",
    "SessionDecision", "open_device_session", "refresh_device_session",
    "session_online",
]


def project_registry_devices(devices: tuple[EnrolledDevice, ...],
                             sessions: tuple[DeviceSession, ...], *, now: str,
                             offline_after_seconds: int = 120) -> tuple[EnrolledDevice, ...]:
    by_device = {s.device_id: s for s in sessions}
    projected: list[EnrolledDevice] = []
    for device in devices:
        session = by_device.get(device.device_id)
        online = bool(session and session.owner_subject == device.owner_subject and
                      session_online(session, now=now, offline_after_seconds=offline_after_seconds))
        projected.append(replace(
            device,
            presence="online" if online else "offline",
            last_seen_at=session.heartbeat_at if session else device.last_seen_at,
        ))
    return tuple(projected)
