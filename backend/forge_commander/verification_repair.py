from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from .verification_gate import CommitReadiness, VerificationCommandResult

FORGE_COMMANDER_VERIFICATION_REPAIR_VERSION = "forge-commander.verification-repair.v1"


@dataclass(frozen=True, slots=True)
class VerificationRepairRequest:
    request_id: str
    repo_root: str
    command: str
    exit_code: int
    stdout_tail: str
    stderr: str
    reason: str


def build_verification_repair_request(
    readiness: CommitReadiness,
) -> VerificationRepairRequest | None:
    failed = next((r for r in readiness.verification_results if not r.succeeded), None)
    if failed is None:
        return None
    digest = sha256(
        f"{readiness.readiness_id}\n{failed.command}\n{failed.exit_code}".encode("utf-8")
    ).hexdigest()[:20]
    return VerificationRepairRequest(
        request_id=f"fc-verify-repair-{digest}",
        repo_root=readiness.repo_root,
        command=failed.command,
        exit_code=failed.exit_code,
        stdout_tail=failed.stdout[-2000:],
        stderr=failed.stderr,
        reason=readiness.failure_reason or "verification failed",
    )


__all__ = [
    "FORGE_COMMANDER_VERIFICATION_REPAIR_VERSION",
    "VerificationRepairRequest",
    "build_verification_repair_request",
]
