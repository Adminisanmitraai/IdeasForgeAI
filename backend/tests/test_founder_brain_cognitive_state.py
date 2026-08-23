from backend.founder_brain.cognitive_memory import (
    CognitiveEvidence, FounderAssumptionMemory, FounderCognitiveProfile,
    FounderDecisionMemory, FounderLessonMemory, FounderPreferenceMemory,
)
from backend.founder_brain.cognitive_state import synthesize_founder_cognitive_state


def _profile():
    evidence = tuple(
        CognitiveEvidence(
            evidence_id=f"ev-{i}", source_type="project_outcome", source_id=f"src-{i}",
            observed_at="2026-08-23T10:00:00Z", confidence=0.9,
        ) for i in range(1, 5)
    )
    preferences = (
        FounderPreferenceMemory(
            preference_id="p1", domain="architecture", statement="Prefer reusable systems",
            strength=0.9, evidence_ids=("ev-1",), updated_at="t1",
        ),
    )
    assumptions = (
        FounderAssumptionMemory(
            assumption_id="a1", statement="Reuse lowers duplication", scope="product",
            status="supported", confidence=0.8, evidence_ids=("ev-1",), updated_at="t1",
        ),
    )
    decisions = (
        FounderDecisionMemory(
            decision_id="d1", title="Gateway", problem="duplication", options_considered=("gateway",),
            chosen_option="gateway", rationale="reuse", expected_outcome="Reduce duplicate integrations",
            actual_outcome="Duplicate integrations increased", confidence_at_decision=0.8,
            assumption_ids=("a1",), evidence_ids=("ev-2",), created_at="t2",
        ),
        FounderDecisionMemory(
            decision_id="d2", title="Pending", problem="latency", options_considered=("local",),
            chosen_option="local", rationale="speed", expected_outcome="Lower latency",
            confidence_at_decision=0.7, evidence_ids=("ev-3",), created_at="t3",
        ),
    )
    lessons = (
        FounderLessonMemory(
            lesson_id="l1", statement="Measure outcomes", applicability="all",
            confidence=0.8, source_decision_ids=("d1",), evidence_ids=("ev-4",), updated_at="t4",
        ),
    )
    return FounderCognitiveProfile(
        founder_id="f1", generated_at="now", evidence=evidence, preferences=preferences,
        assumptions=assumptions, decisions=decisions, lessons=lessons,
    )


def test_state_synthesizes_current_cognition_without_raw_text_duplication():
    state = synthesize_founder_cognitive_state(_profile())
    assert state.active_preference_ids == ("p1",)
    assert state.supported_assumption_ids == ("a1",)
    assert state.active_lesson_ids == ("l1",)
    assert state.decisions_awaiting_outcomes == ("d2",)
    assert state.reflected_decision_ids == ("d1",)
    assert state.high_error_decision_ids == ("d1",)
    assert state.evidence_count == 4
    assert state.source_decision_ids == ("d1", "d2")
    assert state.source_evidence_ids == ("ev-1", "ev-2", "ev-3", "ev-4")
    assert state.advisory_only is True
    assert state.execution_allowed is False


def test_state_is_deterministic_for_same_profile():
    profile = _profile()
    assert synthesize_founder_cognitive_state(profile) == synthesize_founder_cognitive_state(profile)
