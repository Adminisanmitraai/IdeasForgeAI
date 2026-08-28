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
    request: dict | None = None
    approval_granted: bool = False

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
                        approval_granted: bool = False) -> DeviceTaskEnvelope:
    text = instruction.strip()
    if not text:
        raise ValueError("instruction is required")
    # Approval is a state transition for the same request, not a new task.
    # Keep the task identity stable when approval_granted changes so the
    # approved retry resumes the audit/task the owner actually reviewed.
    digest = sha256(
        f"{session.session_id}\n{text}\n{required_capability}\n{approval_required}".encode("utf-8")
    ).hexdigest()[:20]
    return DeviceTaskEnvelope(
        f"fc-task-{digest}", session.owner_subject, session.device_id,
        session.session_id, text, required_capability, approval_required, request,
        approval_granted,
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
