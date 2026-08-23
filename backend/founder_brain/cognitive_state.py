from __future__ import annotations

from dataclasses import dataclass

from .cognitive_memory import FounderCognitiveProfile
from .cognitive_patterns import FounderPatternReport, analyze_founder_patterns
from .cognitive_projection import FounderLearningProjection, project_founder_learning
from .cognitive_reflection import DecisionReflection, reflect_on_decision

FOUNDER_COGNITIVE_STATE_VERSION = "forgebrain.cognitive-state.v1"


@dataclass(frozen=True, slots=True)
class FounderCognitiveState:
    founder_id: str
    generated_at: str
    active_preference_ids: tuple[str, ...]
    supported_assumption_ids: tuple[str, ...]
    refuted_assumption_ids: tuple[str, ...]
    unresolved_assumption_ids: tuple[str, ...]
    active_lesson_ids: tuple[str, ...]
    decisions_awaiting_outcomes: tuple[str, ...]
    reflected_decision_ids: tuple[str, ...]
    high_error_decision_ids: tuple[str, ...]
    confidence_calibration_gap: float | None
    evidence_count: int
    source_decision_ids: tuple[str, ...]
    source_evidence_ids: tuple[str, ...]
    advisory_only: bool = True
    execution_allowed: bool = False
    schema_version: str = FOUNDER_COGNITIVE_STATE_VERSION


def _reflections(profile: FounderCognitiveProfile) -> tuple[DecisionReflection, ...]:
    return tuple(
        reflect_on_decision(profile, item.decision_id)
        for item in profile.decisions
        if item.actual_outcome is not None
    )


def synthesize_founder_cognitive_state(
    profile: FounderCognitiveProfile,
    *,
    learning: FounderLearningProjection | None = None,
    patterns: FounderPatternReport | None = None,
) -> FounderCognitiveState:
    learning = learning or project_founder_learning(profile)
    patterns = patterns or analyze_founder_patterns(profile)
    reflections = _reflections(profile)
    high_error = tuple(sorted(
        item.decision_id for item in reflections
        if item.prediction_error is not None and item.prediction_error >= 0.5
    ))
    source_decisions = tuple(sorted(item.decision_id for item in profile.decisions))
    source_evidence = tuple(sorted(item.evidence_id for item in profile.evidence))
    return FounderCognitiveState(
        founder_id=profile.founder_id,
        generated_at=profile.generated_at,
        active_preference_ids=learning.active_preference_ids,
        supported_assumption_ids=learning.supported_assumption_ids,
        refuted_assumption_ids=learning.refuted_assumption_ids,
        unresolved_assumption_ids=learning.unresolved_assumption_ids,
        active_lesson_ids=learning.active_lesson_ids,
        decisions_awaiting_outcomes=learning.decisions_awaiting_outcomes,
        reflected_decision_ids=tuple(sorted(item.decision_id for item in reflections)),
        high_error_decision_ids=high_error,
        confidence_calibration_gap=patterns.confidence.calibration_gap,
        evidence_count=learning.evidence_count,
        source_decision_ids=source_decisions,
        source_evidence_ids=source_evidence,
    )


__all__ = [
    "FOUNDER_COGNITIVE_STATE_VERSION",
    "FounderCognitiveState",
    "synthesize_founder_cognitive_state",
]
