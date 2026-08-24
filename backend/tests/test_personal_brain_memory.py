from types import SimpleNamespace
from unittest.mock import patch

from backend.founder_brain.cognitive_memory import (
    FounderCognitiveProfile,
    FounderPreferenceMemory,
)
from backend.personal_brain_memory import capture_candidate, recall_context


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
