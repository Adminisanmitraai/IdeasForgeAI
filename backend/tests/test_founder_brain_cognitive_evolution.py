import pytest

from backend.founder_brain.cognitive_evolution import (
    CognitiveEvolutionError,
    add_evidence,
    promote_candidate_lesson,
    propose_candidate_lesson,
    record_decision_outcome,
    supersede_assumption,
    supersede_preference,
)
from backend.founder_brain.cognitive_memory import (
    CognitiveEvidence,
    FounderAssumptionMemory,
    FounderCognitiveProfile,
    FounderDecisionMemory,
    FounderPreferenceMemory,
)


def _profile():
    evidence = CognitiveEvidence(evidence_id="ev-1", source_type="founder_statement", source_id="m1", observed_at="t1", confidence=0.9)
    pref = FounderPreferenceMemory(preference_id="p1", domain="strategy", statement="Prefer reusable systems", strength=0.8, evidence_ids=("ev-1",), updated_at="t1")
    assumption = FounderAssumptionMemory(assumption_id="a1", statement="Reuse saves time", scope="product", confidence=0.7, evidence_ids=("ev-1",), related_decision_ids=("d1",), updated_at="t1")
    decision = FounderDecisionMemory(decision_id="d1", title="Use gateway", problem="Duplication", options_considered=("direct", "gateway"), chosen_option="gateway", rationale="Reuse", expected_outcome="Lower duplication", confidence_at_decision=0.8, assumption_ids=("a1",), evidence_ids=("ev-1",), created_at="t1")
    return FounderCognitiveProfile(founder_id="f1", generated_at="t1", evidence=(evidence,), preferences=(pref,), assumptions=(assumption,), decisions=(decision,))


def test_add_evidence_and_record_outcome_preserve_original_profile():
    original = _profile()
    evolved = add_evidence(original, CognitiveEvidence(evidence_id="ev-2", source_type="project_outcome", source_id="o1", observed_at="t2", confidence=1.0), generated_at="t2")
    evolved = record_decision_outcome(evolved, decision_id="d1", actual_outcome="Duplication reduced", evidence_ids=("ev-2",), generated_at="t3")
    assert original.decisions[0].actual_outcome is None
    assert evolved.decisions[0].actual_outcome == "Duplication reduced"
    assert evolved.decisions[0].evidence_ids == ("ev-1", "ev-2")


def test_outcome_cannot_be_silently_overwritten():
    evolved = add_evidence(_profile(), CognitiveEvidence(evidence_id="ev-2", source_type="project_outcome", source_id="o1", observed_at="t2", confidence=1.0), generated_at="t2")
    evolved = record_decision_outcome(evolved, decision_id="d1", actual_outcome="Worked", evidence_ids=("ev-2",), generated_at="t3")
    with pytest.raises(CognitiveEvolutionError, match="already recorded"):
        record_decision_outcome(evolved, decision_id="d1", actual_outcome="Changed", evidence_ids=("ev-2",), generated_at="t4")


def test_supersession_keeps_old_memory_and_adds_replacement():
    profile = _profile()
    replacement_pref = FounderPreferenceMemory(preference_id="p2", domain="strategy", statement="Prefer reuse when evidence supports it", strength=0.9, evidence_ids=("ev-1",), updated_at="t2")
    evolved = supersede_preference(profile, old_preference_id="p1", replacement=replacement_pref, generated_at="t2")
    assert [item.status for item in evolved.preferences] == ["superseded", "active"]
    replacement_assumption = FounderAssumptionMemory(assumption_id="a2", statement="Reuse saves time when interfaces are stable", scope="product", confidence=0.8, evidence_ids=("ev-1",), related_decision_ids=("d1",), updated_at="t3")
    evolved = supersede_assumption(evolved, old_assumption_id="a1", replacement=replacement_assumption, generated_at="t3")
    assert [item.status for item in evolved.assumptions] == ["superseded", "untested"]


def test_candidate_lesson_requires_real_outcome_then_can_be_promoted():
    profile = _profile()
    with pytest.raises(CognitiveEvolutionError, match="recorded decision outcomes"):
        propose_candidate_lesson(profile, lesson_id="l1", statement="Reuse gateways", applicability="cross-product", source_decision_ids=("d1",), evidence_ids=("ev-1",), confidence=0.8, reason="Outcome")
    profile = record_decision_outcome(profile, decision_id="d1", actual_outcome="Worked", evidence_ids=("ev-1",), generated_at="t2")
    candidate = propose_candidate_lesson(profile, lesson_id="l1", statement="Reuse gateways", applicability="cross-product", source_decision_ids=("d1",), evidence_ids=("ev-1",), confidence=0.8, reason="Observed outcome")
    evolved = promote_candidate_lesson(profile, candidate, updated_at="t3")
    assert evolved.lessons[0].lesson_id == "l1"
    assert evolved.lessons[0].status == "active"
