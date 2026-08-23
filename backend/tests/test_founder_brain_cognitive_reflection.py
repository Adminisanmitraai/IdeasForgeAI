import pytest

from backend.founder_brain.cognitive_memory import (
    CognitiveEvidence, FounderAssumptionMemory, FounderCognitiveProfile,
    FounderDecisionMemory,
)
from backend.founder_brain.cognitive_reflection import (
    propose_reflection_candidate, reflect_on_decision,
)


def _profile(*, actual="Reduce duplication and improve reuse"):
    evidence = CognitiveEvidence(
        evidence_id="ev-1", source_type="project_outcome", source_id="outcome-1",
        observed_at="2026-08-23T12:00:00Z", confidence=0.95,
    )
    assumption = FounderAssumptionMemory(
        assumption_id="asm-1", statement="Reuse lowers duplication", scope="architecture",
        status="validating", confidence=0.7, evidence_ids=("ev-1",),
        related_decision_ids=("dec-1",), updated_at="t1",
    )
    decision = FounderDecisionMemory(
        decision_id="dec-1", title="Use gateway", problem="Duplicate integration",
        options_considered=("gateway", "direct"), chosen_option="gateway", rationale="reuse",
        expected_outcome="Reduce duplication and improve reuse", actual_outcome=actual,
        confidence_at_decision=0.8, assumption_ids=("asm-1",),
        evidence_ids=("ev-1",), created_at="t1",
    )
    return FounderCognitiveProfile(
        founder_id="f1", generated_at="now", evidence=(evidence,),
        assumptions=(assumption,), decisions=(decision,),
    )


def test_reflection_aligned_outcome_has_low_error():
    reflection = reflect_on_decision(_profile(), "dec-1")
    assert reflection.outcome_match == "aligned"
    assert reflection.prediction_error == 0.0
    assert reflection.implicated_assumption_ids == ("asm-1",)
    assert reflection.evidence_ids == ("ev-1",)
    assert reflection.advisory_only is True
    assert reflection.execution_allowed is False


def test_reflection_divergence_is_visible_not_rewritten():
    reflection = reflect_on_decision(_profile(actual="Costs increased and duplication remained"), "dec-1")
    assert reflection.outcome_match == "partial"
    assert reflection.prediction_error is not None
    assert reflection.prediction_error > 0.0


def test_reflection_candidate_requires_recorded_outcome_and_review():
    candidate = propose_reflection_candidate(
        _profile(), "dec-1", candidate_id="rc-1",
        statement="Validate reuse assumptions against delivery metrics", confidence=0.75,
    )
    assert candidate.decision_id == "dec-1"
    assert candidate.assumption_ids == ("asm-1",)
    assert candidate.evidence_ids == ("ev-1",)
    assert candidate.requires_review is True


def test_missing_outcome_fails_closed():
    with pytest.raises(ValueError, match="has not been recorded"):
        reflect_on_decision(_profile(actual=None), "dec-1")


def test_unknown_decision_and_bad_confidence_fail_closed():
    with pytest.raises(ValueError, match="unknown decision"):
        reflect_on_decision(_profile(), "missing")
    with pytest.raises(ValueError, match="between 0 and 1"):
        propose_reflection_candidate(
            _profile(), "dec-1", candidate_id="rc", statement="x", confidence=1.2,
        )
