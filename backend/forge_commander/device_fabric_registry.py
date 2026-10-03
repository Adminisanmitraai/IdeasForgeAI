from __future__ import annotations

from dataclasses import dataclass, field, replace
import re
from typing import Any, Iterable

FORGE_DEVICE_FABRIC_REGISTRY_VERSION = "forge-device-fabric.registry.v1"

_DEVICE_CLASSES = frozenset({"phone", "tablet", "laptop", "workstation", "server", "unknown"})
_EXECUTION_MODES = frozenset({"read_only", "approval_required", "task_authorized"})
_CAPABILITY_STATES = frozenset({"available", "degraded", "unavailable"})
_CAPABILITY_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{1,127}$")


def _required(value: str, field_name: str) -> str:
    normalized = str(value or "").strip()
    if not normalized:
        raise ValueError(f"{field_name}_required")
    return normalized


def _normalized_tags(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(sorted({_required(value, "role_tag").lower() for value in values}))


@dataclass(frozen=True, slots=True)
class CapabilityDescriptor:
    capability_id: str
    execution_mode: str
    state: str = "available"
    source: str = "device_announcement"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        capability_id = _required(self.capability_id, "capability_id").lower()
        execution_mode = _required(self.execution_mode, "execution_mode").lower()
        state = _required(self.state, "capability_state").lower()
        source = _required(self.source, "capability_source")
        if not _CAPABILITY_ID_RE.fullmatch(capability_id):
            raise ValueError("capability_id_invalid")
        if execution_mode not in _EXECUTION_MODES:
            raise ValueError("execution_mode_invalid")
        if state not in _CAPABILITY_STATES:
            raise ValueError("capability_state_invalid")
        object.__setattr__(self, "capability_id", capability_id)
        object.__setattr__(self, "execution_mode", execution_mode)
        object.__setattr__(self, "state", state)
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "metadata", dict(self.metadata or {}))

    def as_dict(self) -> dict[str, Any]:
        return {
            "capability_id": self.capability_id,
            "execution_mode": self.execution_mode,
            "state": self.state,
            "source": self.source,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class DeviceIdentity:
    device_id: str
    owner_subject: str
    device_class: str = "unknown"
    display_name: str = ""
    platform: str = "unknown"
    architecture: str = "unknown"
    role_tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        device_id = _required(self.device_id, "device_id")
        owner_subject = _required(self.owner_subject, "owner_subject")
        device_class = _required(self.device_class, "device_class").lower()
        if device_class not in _DEVICE_CLASSES:
            raise ValueError("device_class_invalid")
        object.__setattr__(self, "device_id", device_id)
        object.__setattr__(self, "owner_subject", owner_subject)
        object.__setattr__(self, "device_class", device_class)
        object.__setattr__(self, "display_name", str(self.display_name or device_id).strip())
        object.__setattr__(self, "platform", str(self.platform or "unknown").strip().lower())
        object.__setattr__(self, "architecture", str(self.architecture or "unknown").strip().lower())
        object.__setattr__(self, "role_tags", _normalized_tags(self.role_tags))

    def as_dict(self) -> dict[str, Any]:
        return {
            "device_id": self.device_id,
            "owner_subject": self.owner_subject,
            "device_class": self.device_class,
            "display_name": self.display_name,
            "platform": self.platform,
            "architecture": self.architecture,
            "role_tags": list(self.role_tags),
        }


@dataclass(frozen=True, slots=True)
class DevicePresence:
    online: bool = False
    session_id: str | None = None
    last_heartbeat_at: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "online": self.online,
            "session_id": self.session_id,
            "last_heartbeat_at": self.last_heartbeat_at,
        }


@dataclass(frozen=True, slots=True)
class DeviceFabricRecord:
    identity: DeviceIdentity
    presence: DevicePresence = DevicePresence()
    capabilities: tuple[CapabilityDescriptor, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "identity": self.identity.as_dict(),
            "presence": self.presence.as_dict(),
            "capabilities": [item.as_dict() for item in self.capabilities],
        }


class DeviceFabricRegistry:
    """Owner-scoped device identity, presence, and explicit capability registry.

    Device class and role tags are descriptive only. Routing is based on explicit
    capability announcements; the registry never infers executable capability
    from a device name, class, GPU model, or role tag.
    """

    def __init__(self) -> None:
        self._records: dict[tuple[str, str], DeviceFabricRecord] = {}
        self._owner_by_device_id: dict[str, str] = {}

    def upsert_identity(self, identity: DeviceIdentity) -> DeviceFabricRecord:
        bound_owner = self._owner_by_device_id.get(identity.device_id)
        if bound_owner is not None and bound_owner != identity.owner_subject:
            raise PermissionError("device_owner_binding_mismatch")
        self._owner_by_device_id[identity.device_id] = identity.owner_subject
        key = (identity.owner_subject, identity.device_id)
        current = self._records.get(key)
        record = DeviceFabricRecord(identity=identity) if current is None else replace(current, identity=identity)
        self._records[key] = record
        return record

    def attach_session(
        self,
        owner_subject: str,
        device_id: str,
        session_id: str,
        *,
        heartbeat_at: str,
    ) -> DeviceFabricRecord:
        key = self._key(owner_subject, device_id)
        current = self._require_record(key)
        presence = DevicePresence(
            online=True,
            session_id=_required(session_id, "session_id"),
            last_heartbeat_at=_required(heartbeat_at, "heartbeat_at"),
        )
        updated = replace(current, presence=presence)
        self._records[key] = updated
        return updated

    def detach_session(self, owner_subject: str, device_id: str, session_id: str) -> DeviceFabricRecord:
        key = self._key(owner_subject, device_id)
        current = self._require_record(key)
        if current.presence.session_id != str(session_id or "").strip():
            return current
        updated = replace(current, presence=DevicePresence())
        self._records[key] = updated
        return updated

    def heartbeat(
        self,
        owner_subject: str,
        device_id: str,
        session_id: str,
        *,
        heartbeat_at: str,
    ) -> DeviceFabricRecord:
        key = self._key(owner_subject, device_id)
        current = self._require_record(key)
        if not current.presence.online or current.presence.session_id != str(session_id or "").strip():
            raise ValueError("device_session_not_current")
        updated = replace(
            current,
            presence=replace(
                current.presence,
                last_heartbeat_at=_required(heartbeat_at, "heartbeat_at"),
            ),
        )
        self._records[key] = updated
        return updated

    def announce_capabilities(
        self,
        owner_subject: str,
        device_id: str,
        capabilities: Iterable[CapabilityDescriptor],
        *,
        replace_existing: bool = True,
    ) -> DeviceFabricRecord:
        key = self._key(owner_subject, device_id)
        current = self._require_record(key)
        incoming = {item.capability_id: item for item in capabilities}
        if replace_existing:
            merged = incoming
        else:
            merged = {item.capability_id: item for item in current.capabilities}
            merged.update(incoming)
        updated = replace(
            current,
            capabilities=tuple(merged[name] for name in sorted(merged)),
        )
        self._records[key] = updated
        return updated

    def list_devices(self, owner_subject: str, *, online_only: bool = False) -> tuple[DeviceFabricRecord, ...]:
        owner = _required(owner_subject, "owner_subject")
        records = [
            record
            for (record_owner, _), record in self._records.items()
            if record_owner == owner and (record.presence.online or not online_only)
        ]
        return tuple(sorted(records, key=lambda record: record.identity.device_id))

    def match_capability(
        self,
        owner_subject: str,
        capability_id: str,
        *,
        online_only: bool = True,
        available_only: bool = True,
    ) -> tuple[DeviceFabricRecord, ...]:
        capability = _required(capability_id, "capability_id").lower()
        matches: list[DeviceFabricRecord] = []
        for record in self.list_devices(owner_subject, online_only=online_only):
            descriptors = [item for item in record.capabilities if item.capability_id == capability]
            if not descriptors:
                continue
            if available_only and all(item.state != "available" for item in descriptors):
                continue
            matches.append(record)
        return tuple(matches)

    def snapshot(self, owner_subject: str) -> dict[str, Any]:
        return {
            "registry_version": FORGE_DEVICE_FABRIC_REGISTRY_VERSION,
            "owner_subject": _required(owner_subject, "owner_subject"),
            "devices": [record.as_dict() for record in self.list_devices(owner_subject)],
        }

    @staticmethod
    def _key(owner_subject: str, device_id: str) -> tuple[str, str]:
        return (
            _required(owner_subject, "owner_subject"),
            _required(device_id, "device_id"),
        )

    def _require_record(self, key: tuple[str, str]) -> DeviceFabricRecord:
        record = self._records.get(key)
        if record is None:
            raise KeyError("device_not_registered")
        return record


__all__ = [
    "FORGE_DEVICE_FABRIC_REGISTRY_VERSION",
    "CapabilityDescriptor",
    "DeviceIdentity",
    "DevicePresence",
    "DeviceFabricRecord",
    "DeviceFabricRegistry",
]
