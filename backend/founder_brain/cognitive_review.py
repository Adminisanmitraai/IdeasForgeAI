from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping

from .cognitive_ingestion import CandidateMemoryKind, CognitiveMemoryCandidate
from .cognitive_memory import (
    CognitiveEvidence,
    FounderAssumptionMemory,
    FounderCognitiveProfile,
    FounderDecisionMemory,
    FounderLessonMemory,
    FounderPreferenceMemory,
    validate_cognitive_profile,
)
from .cognitive_memory_repository import (
    CognitiveMemorySnapshot,
    build_cognitive_memory_snapshot,
)

FOUNDER_COGNITIVE_REVIEW_VERSION = "forgebrain.cognitive-review.v1"


class CandidateReviewDisposition(str, Enum):
    ACCEPT = "accept"
    REJECT = "reject"
    DEFER = "defer"


@dataclass(frozen=True, slots=True)
class CandidateReviewDecision:
    candidate_id: str
    disposition: CandidateReviewDisposition
    reviewer_id: str
    reviewed_at: str
    rationale: str
    conflict_resolution: str = ""


@dataclass(frozen=True, slots=True)
class PromotionMetadata:
    memory_id: str
    domain_or_scope: str = ""
    strength_or_confidence: float = 0.7
    title: str = ""
    problem: str = ""
    options_considered: tuple[str, ...] = ()
    chosen_option: str = ""
    rationale: str = ""
    expected_outcome: str = ""
    related_decision_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ControlledPromotionResult:
    candidate_id: str
    disposition: CandidateReviewDisposition
    promoted_memory_id: str | None
    profile: FounderCognitiveProfile
    snapshot: CognitiveMemorySnapshot | None
    review_required: bool = False
    schema_version: str = FOUNDER_COGNITIVE_REVIEW_VERSION


class CognitiveReviewError(ValueError):
    pass


def _validate_review(candidate: CognitiveMemoryCandidate, review: CandidateReviewDecision) -> None:
    if candidate.candidate_id != review.candidate_id:
        raise CognitiveReviewError("review candidate id mismatch")
    if not review.reviewer_id.strip() or not review.rationale.strip():
        raise CognitiveReviewError("reviewer and rationale are required")
    if review.disposition is CandidateReviewDisposition.ACCEPT:
        if candidate.kind is CandidateMemoryKind.UNKNOWN:
            raise CognitiveReviewError("unknown candidate cannot be promoted")
        if (candidate.duplicate_memory_ids or candidate.contradiction_memory_ids) and not review.conflict_resolution.strip():
            raise CognitiveReviewError("duplicate or contradiction requires explicit conflict resolution")


def _append_evidence(
    profile: FounderCognitiveProfile,
    candidate: CognitiveMemoryCandidate,
) -> tuple[FounderCognitiveProfile, str]:
    evidence_id = f"evidence:{candidate.candidate_id}"
    if any(item.evidence_id == evidence_id for item in profile.evidence):
        raise CognitiveReviewError("promotion evidence id already exists")
    evidence = CognitiveEvidence(
        evidence_id=evidence_id,
        source_type="conversation" if candidate.source_type == "conversation" else "external_evidence",
        source_id=candidate.source_id,
        observed_at=candidate.observed_at,
        confidence=candidate.confidence,
        note=candidate.statement,
    )
    evolved = profile.model_copy(update={"evidence": profile.evidence + (evidence,)})
    return validate_cognitive_profile(evolved), evidence_id


def _ensure_new_memory_id(profile: FounderCognitiveProfile, memory_id: str) -> None:
    ids = {
        *(item.preference_id for item in profile.preferences),
        *(item.assumption_id for item in profile.assumptions),
        *(item.decision_id for item in profile.decisions),
        *(item.lesson_id for item in profile.lessons),
    }
    if not memory_id.strip() or memory_id in ids:
        raise CognitiveReviewError("promotion memory id is empty or already exists")


def _promote_entity(
    profile: FounderCognitiveProfile,
    candidate: CognitiveMemoryCandidate,
    metadata: PromotionMetadata,
    *,
    evidence_id: str,
    reviewed_at: str,
) -> FounderCognitiveProfile:
    _ensure_new_memory_id(profile, metadata.memory_id)
    confidence = metadata.strength_or_confidence
    if not 0.0 <= confidence <= 1.0:
        raise CognitiveReviewError("promotion confidence must be between 0 and 1")
    if candidate.kind is CandidateMemoryKind.EVIDENCE:
        return profile
    if candidate.kind is CandidateMemoryKind.PREFERENCE:
        entity = FounderPreferenceMemory(
            preference_id=metadata.memory_id,
            domain=metadata.domain_or_scope or "general",
            statement=candidate.statement,
            strength=confidence,
            evidence_ids=(evidence_id,),
            updated_at=reviewed_at,
        )
        return validate_cognitive_profile(profile.model_copy(update={"preferences": profile.preferences + (entity,)}))
    if candidate.kind is CandidateMemoryKind.ASSUMPTION:
        entity = FounderAssumptionMemory(
            assumption_id=metadata.memory_id,
            statement=candidate.statement,
            scope=metadata.domain_or_scope or "general",
            status="untested",
            confidence=confidence,
            evidence_ids=(evidence_id,),
            related_decision_ids=metadata.related_decision_ids,
            updated_at=reviewed_at,
        )
        return validate_cognitive_profile(profile.model_copy(update={"assumptions": profile.assumptions + (entity,)}))
    if candidate.kind is CandidateMemoryKind.LESSON:
        entity = FounderLessonMemory(
            lesson_id=metadata.memory_id,
            statement=candidate.statement,
            applicability=metadata.domain_or_scope or "general",
            confidence=confidence,
            source_decision_ids=metadata.related_decision_ids,
            evidence_ids=(evidence_id,),
            updated_at=reviewed_at,
        )
        return validate_cognitive_profile(profile.model_copy(update={"lessons": profile.lessons + (entity,)}))
    if candidate.kind is CandidateMemoryKind.DECISION:
        if not metadata.title.strip() or not metadata.problem.strip():
            raise CognitiveReviewError("decision promotion requires title and problem")
        if not metadata.options_considered or not metadata.chosen_option.strip():
            raise CognitiveReviewError("decision promotion requires options and chosen option")
        entity = FounderDecisionMemory(
            decision_id=metadata.memory_id,
            title=metadata.title,
            problem=metadata.problem,
            options_considered=metadata.options_considered,
            chosen_option=metadata.chosen_option,
            rationale=metadata.rationale or candidate.statement,
            expected_outcome=metadata.expected_outcome,
            confidence_at_decision=confidence,
            related_project_ids=candidate.project_ids,
            evidence_ids=(evidence_id,),
            created_at=reviewed_at,
        )
        return validate_cognitive_profile(profile.model_copy(update={"decisions": profile.decisions + (entity,)}))
    raise CognitiveReviewError("candidate kind is not promotable")


def review_and_promote_candidate(
    profile: FounderCognitiveProfile,
    candidate: CognitiveMemoryCandidate,
    review: CandidateReviewDecision,
    metadata: PromotionMetadata | None = None,
    *,
    previous_snapshot: CognitiveMemorySnapshot | None = None,
) -> ControlledPromotionResult:
    _validate_review(candidate, review)
    if review.disposition is not CandidateReviewDisposition.ACCEPT:
        return ControlledPromotionResult(
            candidate_id=candidate.candidate_id,
            disposition=review.disposition,
            promoted_memory_id=None,
            profile=profile,
            snapshot=None,
        )
    if metadata is None:
        raise CognitiveReviewError("accepted candidate requires promotion metadata")
    evolved, evidence_id = _append_evidence(profile, candidate)
    evolved = _promote_entity(
        evolved, candidate, metadata, evidence_id=evidence_id, reviewed_at=review.reviewed_at
    )
    evolved = validate_cognitive_profile(evolved.model_copy(update={"generated_at": review.reviewed_at}))
    version = 1 if previous_snapshot is None else previous_snapshot.version + 1
    previous_hash = None if previous_snapshot is None else previous_snapshot.snapshot_sha256
    snapshot = build_cognitive_memory_snapshot(
        evolved,
        version=version,
        stored_at=review.reviewed_at,
        previous_snapshot_sha256=previous_hash,
    )
    promoted_id = evidence_id if candidate.kind is CandidateMemoryKind.EVIDENCE else metadata.memory_id
    return ControlledPromotionResult(
        candidate_id=candidate.candidate_id,
        disposition=review.disposition,
        promoted_memory_id=promoted_id,
        profile=evolved,
        snapshot=snapshot,
    )


__all__ = [
    "FOUNDER_COGNITIVE_REVIEW_VERSION",
    "CandidateReviewDisposition",
    "CandidateReviewDecision",
    "PromotionMetadata",
    "ControlledPromotionResult",
    "CognitiveReviewError",
    "review_and_promote_candidate",
]
