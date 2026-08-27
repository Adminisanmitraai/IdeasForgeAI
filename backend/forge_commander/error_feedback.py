from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from .contracts import ForgeCommanderTask, ForgeCommanderTaskResult

FORGE_COMMANDER_ERROR_FEEDBACK_VERSION = "forge-commander.error-feedback.v1"


@dataclass(frozen=True, slots=True)
class ErrorFeedback:
    task_id: str
    fingerprint: str
    summary: str
    command: str
    working_directory: str
    stderr: str
    stdout_tail: str
    attempt: int
    retry_allowed: bool
    contract_version: str = FORGE_COMMANDER_ERROR_FEEDBACK_VERSION


def build_error_feedback(
    task: ForgeCommanderTask,
    result: ForgeCommanderTaskResult,
) -> ErrorFeedback | None:
    if result.state != "failed":
        return None
    normalized = " ".join((result.stderr or result.stdout).split()).lower()
    digest = sha256(
        f"{task.action}\n{task.command}\n{normalized}".encode("utf-8")
    ).hexdigest()[:20]
    summary = normalized[:240] or "command failed without diagnostic output"
    return ErrorFeedback(
        task_id=task.task_id,
        fingerprint=f"fc-error-{digest}",
        summary=summary,
        command=task.command,
        working_directory=task.working_directory,
        stderr=result.stderr,
        stdout_tail=result.stdout[-2000:],
        attempt=result.attempt,
        retry_allowed=task.allow_retry,
    )


__all__ = [
    "FORGE_COMMANDER_ERROR_FEEDBACK_VERSION",
    "ErrorFeedback",
    "build_error_feedback",
]
