from __future__ import annotations

from dataclasses import dataclass

from .cognitive_memory import FounderCognitiveProfile
from .cognitive_state import FounderCognitiveState, synthesize_founder_cognitive_state

FOUNDER_COGNITIVE_CONTEXT_VERSION = "forgebrain.cognitive-context.v1"


@dataclass(frozen=True, slots=True)
class CognitiveContextQuery:
    message: str
    project_ids: tuple[str, ...] = ()
    max_items_per_category: int = 5


@dataclass(frozen=True, slots=True)
class FounderCognitiveContext:
    founder_id: str
    query: str
    preference_ids: tuple[str, ...]
    assumption_ids: tuple[str, ...]
    lesson_ids: tuple[str, ...]
    decision_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    high_error_decision_ids: tuple[str, ...]
    confidence_calibration_gap: float | None
    source_state_version: str = ""
    advisory_only: bool = True
    execution_allowed: bool = False
    schema_version: str = FOUNDER_COGNITIVE_CONTEXT_VERSION


def _tokens(value: str) -> set[str]:
    return {
        token.strip(".,:;!?()[]{}\"'").lower()
        for token in value.split()
        if len(token.strip(".,:;!?()[]{}\"'")) >= 4
    }


def _score(query_tokens: set[str], *values: str) -> int:
    corpus = _tokens(" ".join(values))
    return len(query_tokens & corpus)


def _limited(scored, limit: int) -> tuple[str, ...]:
    ranked = sorted(scored, key=lambda row: (-row[0], row[1]))
    return tuple(item_id for score, item_id in ranked if score > 0)[:limit]


def build_cognitive_context(
    profile: FounderCognitiveProfile,
    query: CognitiveContextQuery,
    *,
    state: FounderCognitiveState | None = None,
) -> FounderCognitiveContext:
    if query.max_items_per_category < 1:
        raise ValueError("max_items_per_category must be positive")
    message = query.message.strip()
    if not message:
        raise ValueError("cognitive context query must not be empty")
    state = state or synthesize_founder_cognitive_state(profile)
    tokens = _tokens(message)
    project_ids = set(query.project_ids)

    preferences = _limited(
        ((_score(tokens, item.domain, item.statement), item.preference_id)
         for item in profile.preferences if item.status == "active"),
        query.max_items_per_category,
    )
    assumptions = _limited(
        ((_score(tokens, item.scope, item.statement), item.assumption_id)
         for item in profile.assumptions if item.status != "superseded"),
        query.max_items_per_category,
    )
    lessons = _limited(
        ((_score(tokens, item.applicability, item.statement), item.lesson_id)
         for item in profile.lessons if item.status == "active"),
        query.max_items_per_category,
    )
    decisions = _limited(
        ((_score(tokens, item.title, item.problem, item.rationale, item.expected_outcome,
                 item.actual_outcome or ""), item.decision_id)
         for item in profile.decisions
         if not project_ids or project_ids.intersection(item.related_project_ids)),
        query.max_items_per_category,
    )
    selected = set(preferences) | set(assumptions) | set(lessons) | set(decisions)
    evidence_ids = tuple(sorted({
        evidence_id
        for item in (*profile.preferences, *profile.assumptions, *profile.decisions, *profile.lessons)
        if getattr(item, "preference_id", getattr(item, "assumption_id", getattr(item, "decision_id", getattr(item, "lesson_id", "")))) in selected
        for evidence_id in item.evidence_ids
    }))
    high_error = tuple(item for item in state.high_error_decision_ids if item in decisions)
    return FounderCognitiveContext(
        founder_id=profile.founder_id,
        query=message,
        preference_ids=preferences,
        assumption_ids=assumptions,
        lesson_ids=lessons,
        decision_ids=decisions,
        evidence_ids=evidence_ids,
        high_error_decision_ids=high_error,
        confidence_calibration_gap=state.confidence_calibration_gap,
        source_state_version=state.schema_version,
    )


__all__ = [
    "FOUNDER_COGNITIVE_CONTEXT_VERSION",
    "CognitiveContextQuery",
    "FounderCognitiveContext",
    "build_cognitive_context",
]


def safe_empty_cognitive_context(query: str = "") -> FounderCognitiveContext:
    return FounderCognitiveContext(
        founder_id="",
        query=query.strip(),
        preference_ids=(), assumption_ids=(), lesson_ids=(), decision_ids=(),
        evidence_ids=(), high_error_decision_ids=(), confidence_calibration_gap=None,
        source_state_version="",
    )


__all__.append("safe_empty_cognitive_context")
