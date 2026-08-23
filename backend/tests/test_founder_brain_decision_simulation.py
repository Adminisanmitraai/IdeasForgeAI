import pytest

from backend.founder_brain.cognitive_memory import (
    CognitiveEvidence, FounderAssumptionMemory, FounderCognitiveProfile,
    FounderDecisionMemory, FounderLessonMemory, FounderPreferenceMemory,
)
from backend.founder_brain.decision_simulation import (
    DecisionAlternative, compare_decision_alternatives,
)


def _profile():
    evidence = tuple(
        CognitiveEvidence(
            evidence_id=f"ev-{i}", source_type="project_outcome", source_id=f"src-{i}",
            observed_at="2026-08-23T10:00:00Z", confidence=0.9,
        ) for i in range(1, 5)
    )
    assumptions = (
        FounderAssumptionMemory(
            assumption_id="safe", statement="Reuse reduces duplication", scope="product",
            status="supported", confidence=0.8, evidence_ids=("ev-1",), updated_at="t1",
        ),
        FounderAssumptionMemory(
            assumption_id="risky", statement="Direct integration will scale", scope="product",
            status="refuted", confidence=0.7, evidence_ids=("ev-2",), updated_at="t2",
        ),
    )
    decisions = (
        FounderDecisionMemory(
            decision_id="d1", title="Reusable voice gateway", problem="Duplicate voice integrations",
            options_considered=("gateway", "direct"), chosen_option="gateway",
            rationale="Reuse central capability", expected_outcome="Reduce duplication",
            actual_outcome="Worked successfully", confidence_at_decision=0.8,
            assumption_ids=("safe",), evidence_ids=("ev-3",), created_at="t3",
        ),
    )
    preferences = (
        FounderPreferenceMemory(
            preference_id="p1", domain="architecture", statement="Prefer reusable systems",
            strength=0.9, evidence_ids=("ev-1",), updated_at="t1",
        ),
    )
    lessons = (
        FounderLessonMemory(
            lesson_id="l1", statement="Reuse shared capabilities to reduce duplication",
            applicability="architecture", confidence=0.9, source_decision_ids=("d1",),
            evidence_ids=("ev-4",), updated_at="t4",
        ),
    )
    return FounderCognitiveProfile(
        founder_id="f1", generated_at="now", evidence=evidence, preferences=preferences,
        assumptions=assumptions, decisions=decisions, lessons=lessons,
    )


def test_comparison_exposes_tradeoffs_without_selecting_winner():
    alternatives = (
        DecisionAlternative(
            alternative_id="gateway", title="Reusable gateway", rationale="Reuse shared capability",
            expected_outcome="Reduce duplication", assumption_ids=("safe",),
        ),
        DecisionAlternative(
            alternative_id="direct", title="Direct integration", rationale="Integrate directly",
            expected_outcome="Scale integration", assumption_ids=("risky",),
        ),
    )
    result = compare_decision_alternatives(
        _profile(), comparison_id="cmp-1", problem="Duplicate voice integrations",
        alternatives=alternatives,
    )
    assert result.final_choice is None
    assert result.advisory_only is True
    assert result.execution_allowed is False
    by_id = {item.alternative_id: item for item in result.assessments}
    assert by_id["direct"].risky_assumption_ids == ("risky",)
    assert by_id["gateway"].risky_assumption_ids == ()
    assert "d1" in by_id["gateway"].matching_decision_ids
    assert "l1" in by_id["gateway"].relevant_lesson_ids


def test_comparison_requires_multiple_unique_alternatives():
    one = (DecisionAlternative("a", "A", "r", "o"),)
    with pytest.raises(ValueError, match="at least two"):
        compare_decision_alternatives(_profile(), comparison_id="c", problem="p", alternatives=one)
    duplicate = (
        DecisionAlternative("a", "A", "r", "o"),
        DecisionAlternative("a", "B", "r", "o"),
    )
    with pytest.raises(ValueError, match="unique"):
        compare_decision_alternatives(_profile(), comparison_id="c", problem="p", alternatives=duplicate)


def test_unknown_assumption_fails_closed_through_advisor():
    alternatives = (
        DecisionAlternative("a", "A", "r", "o", assumption_ids=("missing",)),
        DecisionAlternative("b", "B", "r", "o"),
    )
    with pytest.raises(ValueError, match="unknown assumptions"):
        compare_decision_alternatives(_profile(), comparison_id="c", problem="p", alternatives=alternatives)
