from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

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
                        approval_required: bool = True) -> DeviceTaskEnvelope:
    text = instruction.strip()
    if not text:
        raise ValueError("instruction is required")
    digest = sha256(
        f"{session.session_id}\n{text}\n{required_capability}".encode("utf-8")
    ).hexdigest()[:20]
    return DeviceTaskEnvelope(
        f"fc-task-{digest}", session.owner_subject, session.device_id,
        session.session_id, text, required_capability, approval_required,
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
