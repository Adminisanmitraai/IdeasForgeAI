from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from secrets import token_hex

from .cloud_device_registry import DeviceSession

FORGE_COMMANDER_CLOUD_TASK_CHANNEL_VERSION = "forge-commander.cloud-task-channel.v1"

@dataclass(frozen=True, slots=True)
class DeviceTaskEnvelope:
    task_id: str
    owner_subject: str
    device_id: str
    session_id: str
    instruction: str
    required_capability: str
    approval_required: bool
    request: dict | None = None
    approval_granted: bool = False
    task_authorization: str | None = None

@dataclass(frozen=True, slots=True)
class DeviceTaskResultEnvelope:
    task_id: str
    device_id: str
    session_id: str
    succeeded: bool
    reason: str
    output: str | None = None


def build_task_envelope(session: DeviceSession, *, instruction: str,
                        required_capability: str,
                        approval_required: bool = True,
                        request: dict | None = None,
                        approval_granted: bool = False,
                        task_authorization: str | None = None) -> DeviceTaskEnvelope:
    text = instruction.strip()
    if not text:
        raise ValueError("instruction is required")
    # Approval-bound writes keep deterministic identity across pending -> approved
    # retries. Read-only dispatches are fresh so delayed prior results cannot
    # satisfy later identical probes in the same live session.
    if approval_required:
        digest = sha256(
            f"{session.session_id}\n{text}\n{required_capability}\n{approval_required}".encode("utf-8")
        ).hexdigest()[:20]
    else:
        digest = sha256(
            f"{session.session_id}\n{text}\n{required_capability}\n{approval_required}\n{token_hex(16)}".encode("utf-8")
        ).hexdigest()[:20]
    return DeviceTaskEnvelope(
        f"fc-task-{digest}", session.owner_subject, session.device_id,
        session.session_id, text, required_capability, approval_required, request,
        approval_granted, task_authorization,
    )

def validate_task_result(task: DeviceTaskEnvelope,
                         result: DeviceTaskResultEnvelope) -> bool:
    return (
        result.task_id == task.task_id and
        result.device_id == task.device_id and
        result.session_id == task.session_id
    )

__all__ = [
    "FORGE_COMMANDER_CLOUD_TASK_CHANNEL_VERSION",
    "DeviceTaskEnvelope", "DeviceTaskResultEnvelope",
    "build_task_envelope", "validate_task_result",
]
