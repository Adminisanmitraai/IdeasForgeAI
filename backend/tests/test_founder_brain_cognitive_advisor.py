import pytest

from backend.founder_brain.cognitive_advisor import DecisionProposal, advise_decision
from backend.founder_brain.cognitive_memory import (
    CognitiveEvidence, FounderAssumptionMemory, FounderCognitiveProfile,
    FounderDecisionMemory, FounderLessonMemory, FounderPreferenceMemory,
)


def _profile():
    evidence = (
        CognitiveEvidence(evidence_id="e1", source_type="project_outcome", source_id="s1", observed_at="t1", confidence=0.9),
        CognitiveEvidence(evidence_id="e2", source_type="project_outcome", source_id="s2", observed_at="t2", confidence=0.9),
    )
    decisions = (
        FounderDecisionMemory(
            decision_id="d1", title="Use shared voice gateway", problem="Duplicate voice integrations",
            options_considered=("direct provider", "shared gateway"), chosen_option="shared gateway",
            rationale="Central governance and reuse", expected_outcome="Reduce duplicate integrations",
            actual_outcome="Worked successfully and improved reuse", confidence_at_decision=0.9,
            evidence_ids=("e1",), created_at="t1",
        ),
    )
    assumptions = (
        FounderAssumptionMemory(
            assumption_id="a1", statement="Shared gateway will lower duplicate integrations",
            scope="product", status="refuted", confidence=0.7, evidence_ids=("e2",),
            related_decision_ids=("d1",), updated_at="t2",
        ),
    )
    preferences = (
        FounderPreferenceMemory(
            preference_id="p1", domain="architecture", statement="Prefer reusable shared capabilities",
            strength=0.9, evidence_ids=("e1",), updated_at="t1",
        ),
    )
    lessons = (
        FounderLessonMemory(
            lesson_id="l1", statement="Centralize reusable capabilities behind shared gateways",
            applicability="cross-product architecture", confidence=0.85,
            source_decision_ids=("d1",), evidence_ids=("e1",), updated_at="t2",
        ),
    )
    return FounderCognitiveProfile(
        founder_id="f1", generated_at="now", evidence=evidence,
        preferences=preferences, assumptions=assumptions, decisions=decisions, lessons=lessons,
    )


def test_advisor_flags_risky_assumption_and_prior_decision():
    proposal = DecisionProposal(
        proposal_id="x1", title="Use shared gateway again", problem="Duplicate integrations",
        proposed_option="shared gateway", rationale="Central governance and reuse",
        expected_outcome="Reduce duplicate integrations", assumption_ids=("a1",),
    )
    advice = advise_decision(_profile(), proposal)
    assert advice.advisory_only is True
    assert advice.execution_allowed is False
    assert advice.risky_assumption_ids == ("a1",)
    assert advice.matching_decision_ids == ("d1",)
    assert "p1" in advice.active_preference_ids
    assert "l1" in advice.relevant_lesson_ids
    assert any(item.finding_type == "assumption_risk" for item in advice.findings)


def test_advisor_rejects_unknown_assumption_reference():
    proposal = DecisionProposal(
        proposal_id="x2", title="Test", problem="p", proposed_option="o",
        rationale="r", expected_outcome="e", assumption_ids=("missing",),
    )
    with pytest.raises(ValueError, match="unknown assumptions"):
        advise_decision(_profile(), proposal)
