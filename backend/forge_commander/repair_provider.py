from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Protocol

from .error_feedback import ErrorFeedback
from .repair_loop import RepairProposal, build_repair_proposal

FORGE_COMMANDER_REPAIR_PROVIDER_VERSION = "forge-commander.repair-provider.v1"


@dataclass(frozen=True, slots=True)
class RepairDiagnosisRequest:
    request_id: str
    fingerprint: str
    summary: str
    command: str
    working_directory: str
    stderr: str
    stdout_tail: str
    attempt: int


@dataclass(frozen=True, slots=True)
class RepairDiagnosisResponse:
    corrected_command: str
    rationale: str
    confidence: float
    requires_approval: bool = False

class RepairProvider(Protocol):
    def diagnose(self, request: RepairDiagnosisRequest) -> RepairDiagnosisResponse: ...


def build_diagnosis_request(feedback: ErrorFeedback) -> RepairDiagnosisRequest:
    digest = sha256(
        f"{feedback.fingerprint}\n{feedback.attempt}\n{feedback.command}".encode("utf-8")
    ).hexdigest()[:20]
    return RepairDiagnosisRequest(
        request_id=f"fc-diagnosis-{digest}",
        fingerprint=feedback.fingerprint,
        summary=feedback.summary,
        command=feedback.command,
        working_directory=feedback.working_directory,
        stderr=feedback.stderr,
        stdout_tail=feedback.stdout_tail,
        attempt=feedback.attempt,
    )

def propose_with_provider(
    feedback: ErrorFeedback, *, provider: RepairProvider
) -> RepairProposal:
    response = provider.diagnose(build_diagnosis_request(feedback))
    return build_repair_proposal(
        feedback=feedback,
        corrected_command=response.corrected_command,
        rationale=response.rationale,
        confidence=response.confidence,
        requires_approval=response.requires_approval,
    )


__all__ = [
    "FORGE_COMMANDER_REPAIR_PROVIDER_VERSION", "RepairDiagnosisRequest",
    "RepairDiagnosisResponse", "RepairProvider", "build_diagnosis_request",
    "propose_with_provider",
]
