from types import SimpleNamespace
from unittest.mock import patch

from backend.founder_brain.cognitive_memory import (
    FounderCognitiveProfile,
    FounderPreferenceMemory,
)
from backend.founder_brain.cognitive_ingestion import CognitiveIngestionSource, ingest_cognitive_candidate
from backend.founder_brain.cognitive_memory_repository import build_cognitive_memory_snapshot
from backend.personal_brain_memory import (capture_candidate, recall_bundle, recall_context, rank_recalled_memories, relationship_continuity, proactive_signals, parse_memory_command, handle_memory_command, list_memory_candidates, review_memory_candidate, submit_memory_correction)


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


def test_parse_explicit_memory_commands():
    assert parse_memory_command("Remember that I prefer concise answers") == {"action":"remember","subject":"I prefer concise answers","explicit":True}
    assert parse_memory_command("What do you remember about voice replies?")["action"] == "recall"
    assert parse_memory_command("Forget that old preference")["action"] == "forget"
    assert parse_memory_command("That's no longer true: I prefer long replies")["action"] == "correct"


def test_normal_chat_is_not_a_memory_command():
    assert parse_memory_command("Tell me what we should build next") is None


def test_recall_command_uses_reviewed_memory_only():
    with patch("backend.personal_brain_memory.SupabaseCognitiveMemoryRepository", FakeRepo):
        result = handle_memory_command("What do you remember about spoken replies?")
    assert result["action"] == "recall"
    assert result["count"] >= 1


def test_forget_requires_reviewed_supersession():
    result = handle_memory_command("Forget that old preference")
    assert result["requires_review"] is True
    assert result["mutation"] == "supersession"
    assert result["queued"] is False


def test_companion_remember_command_uses_memory_control_path():
    from backend import main as main_module
    request = SimpleNamespace(message="Remember that I prefer concise replies", history=[])
    with patch.object(main_module, "handle_memory_command", return_value={"action":"remember","queued":True}):
        result = main_module.personal_brain_companion(request)
    assert result["model"] == "memory-control"
    assert "queued" in result["message"].lower()


def test_companion_normal_chat_falls_through_to_provider():
    from backend import main as main_module
    request = SimpleNamespace(message="What should we build next?", history=[])
    fake_provider = SimpleNamespace(chat=lambda messages: {"status":"success","message":"normal reply"})
    with patch.object(main_module, "handle_memory_command", return_value=None), patch.object(main_module, "OpenAIProvider", return_value=fake_provider), patch.object(main_module, "recall_bundle", return_value={"memories":(),"count":0,"cross_session":False}):
        result = main_module.personal_brain_companion(request)
    assert result["message"] == "normal reply"
    assert result["persistent_memory_used"] is False


def test_relationship_continuity_groups_relevant_long_term_memory():
    with patch("backend.personal_brain_memory.SupabaseCognitiveMemoryRepository", FakeRepo):
        result = relationship_continuity("spoken replies")
    assert result["continuity_available"] is True
    assert result["count"] >= 1
    assert any("short natural spoken replies" in x for x in result["context"]["preferences"])


def test_relationship_continuity_does_not_force_unrelated_history():
    with patch("backend.personal_brain_memory.SupabaseCognitiveMemoryRepository", FakeRepo):
        result = relationship_continuity("quantum submarine maintenance")
    assert result["continuity_available"] is False
    assert result["count"] == 0


def test_proactive_signals_surface_only_strong_relevant_context():
    with patch("backend.personal_brain_memory.SupabaseCognitiveMemoryRepository", FakeRepo):
        result = proactive_signals("spoken replies")
    assert result["should_surface"] is True
    assert result["count"] >= 1
    assert all(item["score"] >= 0.58 for item in result["signals"])


def test_proactive_signals_suppress_unrelated_memory():
    with patch("backend.personal_brain_memory.SupabaseCognitiveMemoryRepository", FakeRepo):
        result = proactive_signals("quantum submarine maintenance")
    assert result["should_surface"] is False
    assert result["count"] == 0
