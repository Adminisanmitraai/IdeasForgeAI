from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .cognitive_ingestion import CognitiveMemoryCandidate
from .cognitive_memory import FounderCognitiveProfile, validate_cognitive_profile

FOUNDER_COGNITIVE_CONFLICT_VERSION = "forgebrain.cognitive-conflict.v1"


class ConflictResolutionAction(str, Enum):
    SUPERSEDE = "supersede"
    CONTEXTUAL_EXCEPTION = "contextual_exception"
    RETAIN_BOTH = "retain_both"
    REQUIRE_CLARIFICATION = "require_clarification"


@dataclass(frozen=True, slots=True)
class CognitiveConflictResolution:
    action: ConflictResolutionAction
    target_memory_ids: tuple[str, ...]
    rationale: str
    context_note: str = ""


@dataclass(frozen=True, slots=True)
class CognitiveConflictResult:
    profile: FounderCognitiveProfile
    resolved_memory_ids: tuple[str, ...]
    promotion_allowed: bool
    action: ConflictResolutionAction


class CognitiveConflictError(ValueError):
    pass


def _supersede(profile: FounderCognitiveProfile, target_ids: set[str]) -> FounderCognitiveProfile:
    preferences = tuple(
        item.model_copy(update={"status": "superseded"}) if item.preference_id in target_ids else item
        for item in profile.preferences
    )
    assumptions = tuple(
        item.model_copy(update={"status": "superseded"}) if item.assumption_id in target_ids else item
        for item in profile.assumptions
    )
    lessons = tuple(
        item.model_copy(update={"status": "superseded"}) if item.lesson_id in target_ids else item
        for item in profile.lessons
    )
    decision_ids = {item.decision_id for item in profile.decisions}
    unsupported = target_ids & decision_ids
    if unsupported:
        raise CognitiveConflictError("decision memories cannot be superseded by conflict resolver")
    return validate_cognitive_profile(profile.model_copy(update={
        "preferences": preferences,
        "assumptions": assumptions,
        "lessons": lessons,
    }))


def resolve_candidate_conflicts(
    profile: FounderCognitiveProfile,
    candidate: CognitiveMemoryCandidate,
    resolution: CognitiveConflictResolution,
) -> CognitiveConflictResult:
    if not resolution.rationale.strip():
        raise CognitiveConflictError("conflict resolution rationale is required")
    contradictions = set(candidate.contradiction_memory_ids)
    targets = set(resolution.target_memory_ids)
    if not contradictions:
        raise CognitiveConflictError("candidate has no contradiction to resolve")
    if not targets or not targets.issubset(contradictions):
        raise CognitiveConflictError("resolution targets must be candidate contradiction memories")
    if resolution.action is ConflictResolutionAction.REQUIRE_CLARIFICATION:
        return CognitiveConflictResult(
            profile=profile,
            resolved_memory_ids=tuple(sorted(targets)),
            promotion_allowed=False,
            action=resolution.action,
        )
    if resolution.action is ConflictResolutionAction.CONTEXTUAL_EXCEPTION and not resolution.context_note.strip():
        raise CognitiveConflictError("contextual exception requires context note")
    evolved = profile
    if resolution.action is ConflictResolutionAction.SUPERSEDE:
        evolved = _supersede(profile, targets)
    return CognitiveConflictResult(
        profile=evolved,
        resolved_memory_ids=tuple(sorted(targets)),
        promotion_allowed=True,
        action=resolution.action,
    )


__all__ = [
    "FOUNDER_COGNITIVE_CONFLICT_VERSION",
    "ConflictResolutionAction",
    "CognitiveConflictResolution",
    "CognitiveConflictResult",
    "CognitiveConflictError",
    "resolve_candidate_conflicts",
]
