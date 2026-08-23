from __future__ import annotations

from dataclasses import dataclass

from .cognitive_memory import FounderCognitiveProfile

FOUNDER_COGNITIVE_PROJECTION_VERSION = "forgebrain.cognitive-projection.v1"


@dataclass(frozen=True, slots=True)
class FounderLearningProjection:
    founder_id: str
    generated_at: str
    active_preference_ids: tuple[str, ...]
    supported_assumption_ids: tuple[str, ...]
    refuted_assumption_ids: tuple[str, ...]
    unresolved_assumption_ids: tuple[str, ...]
    active_lesson_ids: tuple[str, ...]
    decisions_with_outcomes: tuple[str, ...]
    decisions_awaiting_outcomes: tuple[str, ...]
    evidence_count: int
    schema_version: str = FOUNDER_COGNITIVE_PROJECTION_VERSION


def _sorted_ids(values) -> tuple[str, ...]:
    return tuple(sorted(values))


def project_founder_learning(profile: FounderCognitiveProfile) -> FounderLearningProjection:
    unresolved = {"untested", "validating"}
    return FounderLearningProjection(
        founder_id=profile.founder_id,
        generated_at=profile.generated_at,
        active_preference_ids=_sorted_ids(
            item.preference_id for item in profile.preferences if item.status == "active"
        ),
        supported_assumption_ids=_sorted_ids(
            item.assumption_id for item in profile.assumptions if item.status == "supported"
        ),
        refuted_assumption_ids=_sorted_ids(
            item.assumption_id for item in profile.assumptions if item.status == "refuted"
        ),
        unresolved_assumption_ids=_sorted_ids(
            item.assumption_id for item in profile.assumptions if item.status in unresolved
        ),
        active_lesson_ids=_sorted_ids(
            item.lesson_id for item in profile.lessons if item.status == "active"
        ),
        decisions_with_outcomes=_sorted_ids(
            item.decision_id for item in profile.decisions if item.actual_outcome
        ),
        decisions_awaiting_outcomes=_sorted_ids(
            item.decision_id for item in profile.decisions if not item.actual_outcome
        ),
        evidence_count=len(profile.evidence),
    )


__all__ = [
    "FOUNDER_COGNITIVE_PROJECTION_VERSION",
    "FounderLearningProjection",
    "project_founder_learning",
]
