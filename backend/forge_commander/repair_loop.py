from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Callable

from .error_feedback import ErrorFeedback
from .powershell_executor import execute_powershell_command
from .powershell_runtime import PowerShellCommandRecord, PowerShellSessionState

FORGE_COMMANDER_REPAIR_LOOP_VERSION = "forge-commander.repair-loop.v1"


@dataclass(frozen=True, slots=True)
class RepairProposal:
    proposal_id: str
    error_fingerprint: str
    corrected_command: str
    rationale: str
    confidence: float
    requires_approval: bool = False


@dataclass(frozen=True, slots=True)
class RepairAttempt:
    attempt: int
    command: str
    record: PowerShellCommandRecord
    proposal_id: str | None = None

@dataclass(frozen=True, slots=True)
class RepairLoopResult:
    state: str
    session: PowerShellSessionState
    attempts: tuple[RepairAttempt, ...]
    final_record: PowerShellCommandRecord
    approval_required: bool = False


def build_repair_proposal(
    *, feedback: ErrorFeedback, corrected_command: str,
    rationale: str, confidence: float,
    requires_approval: bool = False,
) -> RepairProposal:
    command = corrected_command.strip()
    if not command:
        raise ValueError("corrected_command is required")
    score = max(0.0, min(1.0, float(confidence)))
    digest = sha256(
        f"{feedback.fingerprint}\n{command}\n{rationale}".encode("utf-8")
    ).hexdigest()[:20]
    return RepairProposal(
        proposal_id=f"fc-repair-{digest}",
        error_fingerprint=feedback.fingerprint,
        corrected_command=command, rationale=rationale.strip(),
        confidence=score, requires_approval=requires_approval,
    )

def run_repair_loop(
    *, session: PowerShellSessionState,
    initial_command: str,
    feedback_builder: Callable[[PowerShellCommandRecord, int], ErrorFeedback | None],
    proposer: Callable[[ErrorFeedback], RepairProposal],
    max_attempts: int = 3,
) -> RepairLoopResult:
    current_session = session
    command = initial_command.strip()
    attempts: list[RepairAttempt] = []
    limit = max(1, int(max_attempts))
    proposal_id: str | None = None

    for attempt in range(1, limit + 1):
        execution = execute_powershell_command(current_session, command=command)
        current_session = execution.session
        record = execution.record
        attempts.append(RepairAttempt(attempt, command, record, proposal_id))
        if record.succeeded:
            return RepairLoopResult("succeeded", current_session, tuple(attempts), record)

        feedback = feedback_builder(record, attempt)
        if feedback is None or not feedback.retry_allowed or attempt >= limit:
            return RepairLoopResult("failed", current_session, tuple(attempts), record)
        proposal = proposer(feedback)
        if proposal.requires_approval:
            return RepairLoopResult(
                "approval_required", current_session, tuple(attempts), record, True
            )
        command = proposal.corrected_command
        proposal_id = proposal.proposal_id

    return RepairLoopResult("failed", current_session, tuple(attempts), attempts[-1].record)
