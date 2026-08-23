import pytest

from backend.founder_brain.cognitive_ingestion import (
    CandidateMemoryKind, CognitiveMemoryCandidate,
)
from backend.founder_brain.cognitive_memory import FounderCognitiveProfile
from backend.founder_brain.cognitive_conflicts import ConflictResolutionAction
from backend.founder_brain.cognitive_review import (
    CandidateReviewDecision, CandidateReviewDisposition,
    CognitiveReviewError, PromotionMetadata, review_and_promote_candidate,
)


def _profile():
    return FounderCognitiveProfile(founder_id="f1", generated_at="t0")


def _candidate(kind=CandidateMemoryKind.PREFERENCE, **updates):
    data = dict(
        candidate_id="c1", kind=kind, statement="I prefer reusable systems",
        confidence=0.85, source_type="conversation", source_id="msg-1",
        observed_at="t1", project_ids=("forgebrain",),
    )
    data.update(updates)
    return CognitiveMemoryCandidate(**data)


def _review(disposition=CandidateReviewDisposition.ACCEPT, **updates):
    data = dict(
        candidate_id="c1", disposition=disposition, reviewer_id="founder",
        reviewed_at="t2", rationale="Reviewed explicitly",
    )
    data.update(updates)
    return CandidateReviewDecision(**data)


def test_reject_and_defer_do_not_mutate_or_snapshot():
    for disposition in (CandidateReviewDisposition.REJECT, CandidateReviewDisposition.DEFER):
        result = review_and_promote_candidate(_profile(), _candidate(), _review(disposition))
        assert result.profile == _profile()
        assert result.snapshot is None
        assert result.promoted_memory_id is None


def test_accept_preference_creates_evidence_entity_and_snapshot():
    result = review_and_promote_candidate(
        _profile(), _candidate(), _review(),
        PromotionMetadata(memory_id="pref-new", domain_or_scope="architecture", strength_or_confidence=0.9),
    )
    assert result.profile.preferences[0].preference_id == "pref-new"
    assert result.profile.preferences[0].evidence_ids == ("evidence:c1",)
    assert result.profile.evidence[0].source_id == "msg-1"
    assert result.snapshot.version == 1


def test_second_promotion_chains_snapshot_integrity():
    first = review_and_promote_candidate(
        _profile(), _candidate(), _review(),
        PromotionMetadata(memory_id="pref-1", domain_or_scope="architecture"),
    )
    second_candidate = _candidate(
        kind=CandidateMemoryKind.ASSUMPTION, candidate_id="c2",
        statement="I believe shared systems reduce duplication", source_id="msg-2",
    )
    second_review = _review(candidate_id="c2", reviewed_at="t3")
    second = review_and_promote_candidate(
        first.profile, second_candidate, second_review,
        PromotionMetadata(memory_id="asm-1", domain_or_scope="architecture"),
        previous_snapshot=first.snapshot,
    )
    assert second.snapshot.version == 2
    assert second.snapshot.previous_snapshot_sha256 == first.snapshot.snapshot_sha256
    assert second.profile.assumptions[0].assumption_id == "asm-1"


def test_conflicted_candidate_requires_explicit_resolution():
    candidate = _candidate(duplicate_memory_ids=("pref-old",))
    with pytest.raises(CognitiveReviewError, match="conflict resolution"):
        review_and_promote_candidate(
            _profile(), candidate, _review(), PromotionMetadata(memory_id="pref-new")
        )


def test_unknown_candidate_cannot_be_promoted():
    with pytest.raises(CognitiveReviewError, match="unknown candidate"):
        review_and_promote_candidate(
            _profile(), _candidate(kind=CandidateMemoryKind.UNKNOWN), _review(),
            PromotionMetadata(memory_id="x1"),
        )


def test_decision_promotion_requires_structured_review_metadata():
    candidate = _candidate(
        kind=CandidateMemoryKind.DECISION,
        statement="I decided to use the shared gateway",
    )
    with pytest.raises(CognitiveReviewError, match="title and problem"):
        review_and_promote_candidate(
            _profile(), candidate, _review(), PromotionMetadata(memory_id="d1")
        )
    result = review_and_promote_candidate(
        _profile(), candidate, _review(),
        PromotionMetadata(
            memory_id="d1", title="Shared gateway", problem="Duplicate integrations",
            options_considered=("gateway", "direct"), chosen_option="gateway",
            rationale="Reuse capability", expected_outcome="Reduce duplication",
        ),
    )
    assert result.profile.decisions[0].decision_id == "d1"
    assert result.profile.decisions[0].related_project_ids == ("forgebrain",)


def test_contradiction_supersede_marks_old_memory_and_promotes_new():
    from backend.founder_brain.cognitive_memory import FounderPreferenceMemory
    profile = FounderCognitiveProfile(
        founder_id="f1", generated_at="t0",
        preferences=(FounderPreferenceMemory(
            preference_id="pref-old", domain="architecture",
            statement="I prefer direct integrations", strength=0.8, updated_at="t0",
        ),),
    )
    candidate = _candidate(
        statement="I no longer prefer direct integrations",
        contradiction_memory_ids=("pref-old",),
    )
    review = _review(
        conflict_resolution="shared gateway supersedes direct integrations",
        conflict_action=ConflictResolutionAction.SUPERSEDE,
        conflict_target_memory_ids=("pref-old",),
    )
    result = review_and_promote_candidate(
        profile, candidate, review,
        PromotionMetadata(memory_id="pref-new", domain_or_scope="architecture"),
    )
    old = next(x for x in result.profile.preferences if x.preference_id == "pref-old")
    new = next(x for x in result.profile.preferences if x.preference_id == "pref-new")
    assert old.status == "superseded"
    assert new.status == "active"


def test_contradiction_clarification_cannot_be_accepted():
    candidate = _candidate(contradiction_memory_ids=("pref-old",))
    review = _review(
        conflict_resolution="needs founder clarification",
        conflict_action=ConflictResolutionAction.REQUIRE_CLARIFICATION,
        conflict_target_memory_ids=("pref-old",),
    )
    with pytest.raises(CognitiveReviewError, match="clarification requires defer"):
        review_and_promote_candidate(
            _profile(), candidate, review, PromotionMetadata(memory_id="pref-new")
        )
