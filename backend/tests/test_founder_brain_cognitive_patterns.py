from backend.founder_brain.cognitive_memory import (
    CognitiveEvidence, FounderAssumptionMemory, FounderCognitiveProfile,
    FounderDecisionMemory, FounderPreferenceMemory,
)
from backend.founder_brain.cognitive_patterns import analyze_founder_patterns


def _profile():
    evidence = tuple(
        CognitiveEvidence(
            evidence_id=f"ev-{i}", source_type="project_outcome", source_id=f"src-{i}",
            observed_at="2026-08-23T10:00:00Z", confidence=0.9,
        ) for i in range(1, 5)
    )
    decisions = (
        FounderDecisionMemory(
            decision_id="d1", title="A", problem="p", options_considered=("a",),
            chosen_option="a", rationale="r", expected_outcome="x", actual_outcome="Worked successfully",
            confidence_at_decision=0.8, evidence_ids=("ev-1",), created_at="t1",
        ),
        FounderDecisionMemory(
            decision_id="d2", title="B", problem="p", options_considered=("b",),
            chosen_option="b", rationale="r", expected_outcome="x", actual_outcome="Failed target",
            confidence_at_decision=0.6, evidence_ids=("ev-2",), created_at="t2",
        ),
    )
    assumptions = (
        FounderAssumptionMemory(
            assumption_id="a1", statement="x", scope="product", status="refuted",
            confidence=0.7, evidence_ids=("ev-3",), related_decision_ids=("d2",), updated_at="t3",
        ),
    )
    preferences = (
        FounderPreferenceMemory(
            preference_id="p1", domain="strategy", statement="reuse", strength=0.8,
            status="active", evidence_ids=("ev-1",), updated_at="t1",
        ),
        FounderPreferenceMemory(
            preference_id="p0", domain="strategy", statement="old", strength=0.7,
            status="superseded", evidence_ids=("ev-4",), updated_at="t0",
        ),
    )
    return FounderCognitiveProfile(
        founder_id="f1", generated_at="now", evidence=evidence,
        preferences=preferences, assumptions=assumptions, decisions=decisions,
    )


def test_pattern_report_is_traceable_and_deterministic():
    report = analyze_founder_patterns(_profile())
    assert report.confidence.resolved_decisions == 2
    assert report.confidence.average_confidence == 0.7
    assert report.confidence.positive_outcome_rate == 0.5
    assert report.confidence.calibration_gap == 0.2
    assert report.confidence.trace.decision_ids == ("d1", "d2")
    assert report.assumption_failures.refuted_assumption_ids == ("a1",)
    assert report.assumption_failures.related_decision_ids == ("d2",)
    assert report.preference_stability.stability_ratio == 0.5
    assert report.preference_stability.trace.preference_ids == ("p0", "p1")


def test_ambiguous_outcome_is_not_scored_as_success_or_failure():
    profile = _profile()
    ambiguous = profile.decisions[0].model_copy(update={"actual_outcome": "Observed mixed result"})
    profile = profile.model_copy(update={"decisions": (ambiguous, profile.decisions[1])})
    report = analyze_founder_patterns(profile)
    assert report.confidence.resolved_decisions == 1
    assert report.confidence.positive_outcome_rate == 0.0
    assert report.confidence.trace.decision_ids == ("d2",)
