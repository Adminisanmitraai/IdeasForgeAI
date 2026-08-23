from __future__ import annotations

from dataclasses import dataclass

from .cognitive_memory import FounderCognitiveProfile

FOUNDER_COGNITIVE_REFLECTION_VERSION = "forgebrain.cognitive-reflection.v1"


@dataclass(frozen=True, slots=True)
class DecisionReflection:
    decision_id: str
    expected_outcome: str
    actual_outcome: str
    outcome_match: str
    prediction_error: float | None
    implicated_assumption_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    reflection_note: str
    advisory_only: bool = True
    execution_allowed: bool = False
    schema_version: str = FOUNDER_COGNITIVE_REFLECTION_VERSION


@dataclass(frozen=True, slots=True)
class ReflectionCandidate:
    candidate_id: str
    decision_id: str
    statement: str
    assumption_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    confidence: float
    requires_review: bool = True


def _tokens(text: str) -> set[str]:
    return {
        token.strip(".,:;!?()[]{}\"'").lower()
        for token in text.split()
        if len(token.strip(".,:;!?()[]{}\"'")) >= 4
    }


def _outcome_match(expected: str, actual: str) -> tuple[str, float | None]:
    left = _tokens(expected)
    right = _tokens(actual)
    if not left or not right:
        return "unknown", None
    overlap = len(left & right)
    union = len(left | right)
    ratio = overlap / union if union else 0.0
    if ratio >= 0.5:
        return "aligned", round(1.0 - ratio, 6)
    if ratio == 0.0:
        return "diverged", 1.0
    return "partial", round(1.0 - ratio, 6)


def reflect_on_decision(profile: FounderCognitiveProfile, decision_id: str) -> DecisionReflection:
    decision = next((item for item in profile.decisions if item.decision_id == decision_id), None)
    if decision is None:
        raise ValueError("unknown decision")
    if decision.actual_outcome is None:
        raise ValueError("decision outcome has not been recorded")
    outcome_match, error = _outcome_match(decision.expected_outcome, decision.actual_outcome)
    assumption_map = {item.assumption_id: item for item in profile.assumptions}
    implicated = tuple(sorted(
        assumption_id for assumption_id in decision.assumption_ids
        if assumption_map.get(assumption_id) is not None
        and assumption_map[assumption_id].status in {"refuted", "untested", "validating"}
    ))
    evidence_ids = tuple(sorted(set(decision.evidence_ids)))
    note = (
        "Expected and actual outcomes are aligned."
        if outcome_match == "aligned"
        else "Expected and actual outcomes differ; review linked assumptions and evidence."
    )
    return DecisionReflection(
        decision_id=decision.decision_id,
        expected_outcome=decision.expected_outcome,
        actual_outcome=decision.actual_outcome,
        outcome_match=outcome_match,
        prediction_error=error,
        implicated_assumption_ids=implicated,
        evidence_ids=evidence_ids,
        reflection_note=note,
    )


def propose_reflection_candidate(
    profile: FounderCognitiveProfile,
    decision_id: str,
    *,
    candidate_id: str,
    statement: str,
    confidence: float,
) -> ReflectionCandidate:
    if not 0.0 <= confidence <= 1.0:
        raise ValueError("reflection confidence must be between 0 and 1")
    reflection = reflect_on_decision(profile, decision_id)
    if not statement.strip():
        raise ValueError("reflection statement must not be empty")
    return ReflectionCandidate(
        candidate_id=candidate_id,
        decision_id=decision_id,
        statement=statement.strip(),
        assumption_ids=reflection.implicated_assumption_ids,
        evidence_ids=reflection.evidence_ids,
        confidence=confidence,
    )


__all__ = [
    "FOUNDER_COGNITIVE_REFLECTION_VERSION",
    "DecisionReflection",
    "ReflectionCandidate",
    "reflect_on_decision",
    "propose_reflection_candidate",
]
