from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from typing import Literal

from .identity import DeviceIdentity
from .startup import ReconnectPolicy, next_reconnect_delay

FORGE_COMMANDER_PERSISTENT_RUNTIME_VERSION = "forge-commander.persistent-runtime.v1"
RuntimeHealth = Literal["healthy", "stale", "offline"]

@dataclass(frozen=True, slots=True)
class RuntimeLease:
    lease_id: str
    device_id: str
    instance_id: str
    pid: int
    acquired_at: str
    heartbeat_at: str

@dataclass(frozen=True, slots=True)
class RuntimeDecision:
    health: RuntimeHealth
    should_reconnect: bool
    reconnect_delay_seconds: int | None
    duplicate_instance: bool
    reason: str

def _parse(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def build_runtime_lease(
    identity: DeviceIdentity, *, instance_id: str, pid: int,
    acquired_at: str, heartbeat_at: str | None = None,
) -> RuntimeLease:
    if pid <= 0:
        raise ValueError("pid must be positive")
    if not instance_id.strip():
        raise ValueError("instance_id is required")
    beat = heartbeat_at or acquired_at
    digest = sha256(
        f"{identity.device_id}\n{instance_id}\n{pid}\n{acquired_at}".encode("utf-8")
    ).hexdigest()[:20]
    return RuntimeLease(
        f"fc-lease-{digest}", identity.device_id, instance_id.strip(),
        pid, acquired_at, beat,
    )

def refresh_runtime_lease(lease: RuntimeLease, *, heartbeat_at: str) -> RuntimeLease:
    return RuntimeLease(
        lease.lease_id, lease.device_id, lease.instance_id,
        lease.pid, lease.acquired_at, heartbeat_at,
    )


def evaluate_runtime(
    lease: RuntimeLease, *, now: str, reconnect_attempt: int = 0,
    stale_after_seconds: int = 45, offline_after_seconds: int = 120,
    active_instance_id: str | None = None,
    reconnect_policy: ReconnectPolicy = ReconnectPolicy(),
) -> RuntimeDecision:
    age = max(0.0, (_parse(now) - _parse(lease.heartbeat_at)).total_seconds())
    duplicate = bool(active_instance_id and active_instance_id != lease.instance_id)
    if duplicate:
        return RuntimeDecision("healthy", False, None, True, "duplicate_instance_detected")
    if age > max(1, offline_after_seconds):
        return RuntimeDecision(
            "offline", True,
            next_reconnect_delay(reconnect_policy, reconnect_attempt),
            False, "heartbeat_offline",
        )
    if age > max(1, stale_after_seconds):
        return RuntimeDecision(
            "stale", True,
            next_reconnect_delay(reconnect_policy, reconnect_attempt),
            False, "heartbeat_stale",
        )
    return RuntimeDecision("healthy", False, None, False, "heartbeat_healthy")
