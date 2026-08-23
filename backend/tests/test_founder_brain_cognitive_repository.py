import json

import pytest

from backend.founder_brain.cognitive_memory import (
    CognitiveEvidence,
    FounderAssumptionMemory,
    FounderCognitiveProfile,
    FounderDecisionMemory,
    FounderLessonMemory,
    FounderPreferenceMemory,
)
from backend.founder_brain.cognitive_memory_repository import (
    CognitiveMemoryCorruptionError,
    CognitiveMemoryRepositoryError,
    build_cognitive_memory_snapshot,
    canonical_cognitive_json,
    restore_cognitive_memory_snapshot,
    validate_snapshot_chain,
)
from backend.founder_brain.cognitive_projection import project_founder_learning


def _profile(*, outcome=None, assumption_status="untested"):
    evidence = CognitiveEvidence(
        evidence_id="ev-1", source_type="founder_statement", source_id="msg-1",
        observed_at="2026-08-23T10:00:00Z", confidence=0.9,
    )
    preference = FounderPreferenceMemory(
        preference_id="pref-1", domain="strategy", statement="Prefer reusable systems",
        strength=0.8, evidence_ids=("ev-1",), updated_at="2026-08-23T10:00:00Z",
    )
    assumption = FounderAssumptionMemory(
        assumption_id="asm-1", statement="Reuse lowers delivery time", scope="product",
        status=assumption_status, confidence=0.7, evidence_ids=("ev-1",),
        related_decision_ids=("dec-1",), updated_at="2026-08-23T10:00:00Z",
    )
    decision = FounderDecisionMemory(
        decision_id="dec-1", title="Reuse voice", problem="Duplicate integrations",
        options_considered=("direct", "gateway"), chosen_option="gateway",
        rationale="Central governance", expected_outcome="Lower duplication",
        actual_outcome=outcome, confidence_at_decision=0.85,
        assumption_ids=("asm-1",), evidence_ids=("ev-1",),
        created_at="2026-08-23T10:00:00Z",
    )
    lesson = FounderLessonMemory(
        lesson_id="lesson-1", statement="Centralize reusable capabilities",
        applicability="cross-product", confidence=0.8,
        source_decision_ids=("dec-1",), evidence_ids=("ev-1",),
        updated_at="2026-08-23T10:00:00Z",
    )
    return FounderCognitiveProfile(
        founder_id="founder-1", generated_at="2026-08-23T10:00:00Z",
        evidence=(evidence,), preferences=(preference,), assumptions=(assumption,),
        decisions=(decision,), lessons=(lesson,),
    )


def test_snapshot_round_trip_and_hash_is_deterministic():
    snapshot = build_cognitive_memory_snapshot(
        _profile(), version=1, stored_at="2026-08-23T10:01:00Z"
    )
    restored = restore_cognitive_memory_snapshot(canonical_cognitive_json(snapshot.to_dict()))
    assert restored == snapshot
    assert len(snapshot.snapshot_sha256) == 64


def test_tampered_snapshot_fails_closed():
    snapshot = build_cognitive_memory_snapshot(
        _profile(), version=1, stored_at="2026-08-23T10:01:00Z"
    )
    payload = snapshot.to_dict()
    payload["profile"]["preferences"][0]["statement"] = "tampered"
    with pytest.raises(CognitiveMemoryCorruptionError):
        restore_cognitive_memory_snapshot(json.dumps(payload))


def test_snapshot_chain_requires_exact_previous_hash():
    first = build_cognitive_memory_snapshot(_profile(), version=1, stored_at="t1")
    second = build_cognitive_memory_snapshot(
        _profile(outcome="Worked"), version=2, stored_at="t2",
        previous_snapshot_sha256=first.snapshot_sha256,
    )
    validate_snapshot_chain((first, second))
    bad = build_cognitive_memory_snapshot(_profile(), version=2, stored_at="t2")
    with pytest.raises(CognitiveMemoryRepositoryError):
        validate_snapshot_chain((first, bad))


def test_learning_projection_separates_resolved_and_unresolved_learning():
    projection = project_founder_learning(_profile(outcome="Worked", assumption_status="supported"))
    assert projection.active_preference_ids == ("pref-1",)
    assert projection.supported_assumption_ids == ("asm-1",)
    assert projection.refuted_assumption_ids == ()
    assert projection.unresolved_assumption_ids == ()
    assert projection.active_lesson_ids == ("lesson-1",)
    assert projection.decisions_with_outcomes == ("dec-1",)
    assert projection.decisions_awaiting_outcomes == ()
    assert projection.evidence_count == 1


def test_learning_projection_marks_pending_outcomes_without_inference():
    projection = project_founder_learning(_profile())
    assert projection.unresolved_assumption_ids == ("asm-1",)
    assert projection.decisions_awaiting_outcomes == ("dec-1",)
    assert projection.decisions_with_outcomes == ()
