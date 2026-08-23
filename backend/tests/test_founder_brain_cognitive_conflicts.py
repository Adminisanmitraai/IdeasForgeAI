import pytest

from backend.founder_brain.cognitive_conflicts import (
    CognitiveConflictError,
    CognitiveConflictResolution,
    ConflictResolutionAction,
    resolve_candidate_conflicts,
)
from backend.founder_brain.cognitive_ingestion import CandidateMemoryKind, CognitiveMemoryCandidate
from backend.founder_brain.cognitive_memory import FounderCognitiveProfile, FounderPreferenceMemory


def _profile():
    return FounderCognitiveProfile(
        founder_id="f1", generated_at="t1",
        preferences=(FounderPreferenceMemory(
            preference_id="pref-old", domain="architecture",
            statement="I prefer reusable shared systems", strength=0.9,
            updated_at="t1",
        ),),
    )


def _candidate():
    return CognitiveMemoryCandidate(
        candidate_id="c1", kind=CandidateMemoryKind.PREFERENCE,
        statement="I no longer prefer reusable shared systems", confidence=0.6,
        source_type="conversation", source_id="m2", observed_at="t2",
        project_ids=("forgebrain",), contradiction_memory_ids=("pref-old",),
    )


def test_supersede_marks_old_memory_superseded():
    result = resolve_candidate_conflicts(
        _profile(), _candidate(),
        CognitiveConflictResolution(
            action=ConflictResolutionAction.SUPERSEDE,
            target_memory_ids=("pref-old",), rationale="new preference replaces old",
        ),
    )
    assert result.promotion_allowed is True
    assert result.profile.preferences[0].status == "superseded"


def test_contextual_exception_preserves_old_memory():
    result = resolve_candidate_conflicts(
        _profile(), _candidate(),
        CognitiveConflictResolution(
            action=ConflictResolutionAction.CONTEXTUAL_EXCEPTION,
            target_memory_ids=("pref-old",), rationale="different context",
            context_note="Only applies to rapid prototypes",
        ),
    )
    assert result.profile.preferences[0].status == "active"
    assert result.promotion_allowed is True


def test_clarification_blocks_promotion_without_mutation():
    profile = _profile()
    result = resolve_candidate_conflicts(
        profile, _candidate(),
        CognitiveConflictResolution(
            action=ConflictResolutionAction.REQUIRE_CLARIFICATION,
            target_memory_ids=("pref-old",), rationale="meaning is ambiguous",
        ),
    )
    assert result.profile == profile
    assert result.promotion_allowed is False


def test_invalid_target_is_rejected():
    with pytest.raises(CognitiveConflictError, match="resolution targets"):
        resolve_candidate_conflicts(
            _profile(), _candidate(),
            CognitiveConflictResolution(
                action=ConflictResolutionAction.RETAIN_BOTH,
                target_memory_ids=("not-a-conflict",), rationale="keep both",
            ),
        )
