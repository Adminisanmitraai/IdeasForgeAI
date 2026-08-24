from types import SimpleNamespace
from unittest.mock import patch

from backend.founder_brain.cognitive_memory import (
    FounderCognitiveProfile,
    FounderPreferenceMemory,
)
from backend.founder_brain.cognitive_ingestion import CognitiveIngestionSource, ingest_cognitive_candidate
from backend.founder_brain.cognitive_memory_repository import build_cognitive_memory_snapshot
from backend.personal_brain_memory import (capture_candidate, recall_bundle, recall_context, rank_recalled_memories, list_memory_candidates, review_memory_candidate, submit_memory_correction)


def _profile():
    return FounderCognitiveProfile(
        founder_id="ranjan",
        generated_at="2026-08-24T00:00:00Z",
        preferences=(
            FounderPreferenceMemory(
                preference_id="pref-voice",
                domain="conversation",
                statement="Prefers short natural spoken replies",
                strength=0.95,
                updated_at="2026-08-24T00:00:00Z",
            ),
        ),
    )


class FakeRepo:
    saved = []
    def latest_snapshot(self, founder_id):
        return SimpleNamespace(profile=_profile())
    def save_candidate(self, founder_id, candidate):
        self.saved.append((founder_id, candidate))
        return None


def test_recall_uses_reviewed_snapshot_memory():
    with patch("backend.personal_brain_memory.SupabaseCognitiveMemoryRepository", FakeRepo):
        recalled = recall_context("Can you keep your spoken reply short?")
    assert recalled
    assert "short natural spoken replies" in recalled[0]


def test_explicit_preference_enters_candidate_queue():
    FakeRepo.saved.clear()
    with patch("backend.personal_brain_memory.SupabaseCognitiveMemoryRepository", FakeRepo):
        result = capture_candidate("I prefer concise casual replies")
    assert result is not None
    assert result["kind"] == "preference"
    assert result["review_required"] is True
    assert len(FakeRepo.saved) == 1


def test_sensitive_statement_is_not_captured():
    FakeRepo.saved.clear()
    with patch("backend.personal_brain_memory.SupabaseCognitiveMemoryRepository", FakeRepo):
        result = capture_candidate("My password is example-only")
    assert result is None
    assert FakeRepo.saved == []


class FakeReviewRepo:
    def __init__(self):
        profile = _profile()
        self.snapshot = build_cognitive_memory_snapshot(profile, version=2, stored_at="2026-08-24T00:00:00Z")
        self.candidate = ingest_cognitive_candidate(
            profile,
            CognitiveIngestionSource(source_type="conversation", source_id="turn-1", observed_at="2026-08-24T00:01:00Z", text="I prefer concise casual replies"),
            candidate_id="pb:test-pref",
        )
        self.saved_snapshots=[]; self.reviews=[]; self.statuses=[]; self.audit=[]
    def latest_snapshot(self, founder_id): return self.snapshot
    def list_candidates(self, founder_id, status="pending", limit=100): return [{"candidate_id": self.candidate.candidate_id, "review_status": status}]
    def get_candidate(self, founder_id, candidate_id): return self.candidate if candidate_id == self.candidate.candidate_id else None
    def save_snapshot(self, snapshot): self.saved_snapshots.append(snapshot)
    def save_review(self, founder_id, review, **kwargs): self.reviews.append((review, kwargs))
    def update_candidate_review_status(self, founder_id, candidate_id, disposition): self.statuses.append(disposition.value)
    def append_audit_event(self, **kwargs): self.audit.append(kwargs)


def test_pending_candidate_listing_uses_review_queue():
    with patch("backend.personal_brain_memory.SupabaseCognitiveMemoryRepository", FakeReviewRepo):
        result = list_memory_candidates("pending")
    assert result["status"] == "pending"
    assert result["count"] == 1
    assert result["candidates"][0]["candidate_id"] == "pb:test-pref"


def test_accept_promotes_preference_to_new_snapshot():
    with patch("backend.personal_brain_memory.SupabaseCognitiveMemoryRepository", FakeReviewRepo):
        result = review_memory_candidate("pb:test-pref", {
            "disposition": "accept",
            "reviewer_id": "test-reviewer",
            "reviewed_at": "2026-08-24T00:02:00Z",
            "rationale": "Confirmed preference",
            "memory_id": "pref-casual",
            "domain_or_scope": "conversation",
            "strength_or_confidence": 0.9,
        })
    assert result["disposition"] == "accept"
    assert result["promoted_memory_id"] == "pref-casual"
    assert result["snapshot_version"] == 3


def test_reject_does_not_create_snapshot():
    with patch("backend.personal_brain_memory.SupabaseCognitiveMemoryRepository", FakeReviewRepo):
        result = review_memory_candidate("pb:test-pref", {
            "disposition": "reject",
            "reviewer_id": "test-reviewer",
            "reviewed_at": "2026-08-24T00:03:00Z",
            "rationale": "Not a durable preference",
        })
    assert result["disposition"] == "reject"
    assert result["promoted_memory_id"] is None
    assert result["snapshot_version"] is None


def test_correction_is_queued_as_new_candidate():
    FakeRepo.saved.clear()
    with patch("backend.personal_brain_memory.SupabaseCognitiveMemoryRepository", FakeRepo):
        result = submit_memory_correction("I prefer more direct spoken replies", source_id="correction-1")
    assert result is not None
    assert result["review_required"] is True
    assert len(FakeRepo.saved) == 1


def test_cross_session_bundle_marks_reviewed_recall():
    with patch("backend.personal_brain_memory.SupabaseCognitiveMemoryRepository", FakeRepo):
        bundle = recall_bundle("Please keep the spoken reply short")
    assert bundle["cross_session"] is True
    assert bundle["count"] >= 1
    assert "short natural spoken replies" in bundle["memories"][0]


def test_cross_session_bundle_is_empty_without_snapshot():
    class EmptyRepo:
        def latest_snapshot(self, founder_id): return None
    with patch("backend.personal_brain_memory.SupabaseCognitiveMemoryRepository", EmptyRepo):
        bundle = recall_bundle("Anything")
    assert bundle["cross_session"] is False
    assert bundle["count"] == 0


def test_relevance_ranking_prefers_matching_memory():
    with patch("backend.personal_brain_memory.SupabaseCognitiveMemoryRepository", FakeRepo):
        rows = rank_recalled_memories("Keep the spoken reply short and natural")
    assert rows
    assert rows[0]["kind"] == "preference"
    assert rows[0]["score"] >= 0.26


def test_unrelated_memory_is_suppressed():
    with patch("backend.personal_brain_memory.SupabaseCognitiveMemoryRepository", FakeRepo):
        rows = rank_recalled_memories("What is the weather on Mars?")
    assert rows == ()
