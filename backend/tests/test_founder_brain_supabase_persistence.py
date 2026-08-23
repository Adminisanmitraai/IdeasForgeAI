import pytest

from backend.founder_brain.cognitive_ingestion import (
    CandidateMemoryKind, CognitiveMemoryCandidate,
)
from backend.founder_brain.cognitive_memory import FounderCognitiveProfile
from backend.founder_brain.cognitive_memory_repository import build_cognitive_memory_snapshot
from backend.founder_brain.cognitive_review import (
    CandidateReviewDecision, CandidateReviewDisposition,
)
from backend.founder_brain.supabase_persistence import (
    SupabaseCognitiveMemoryRepository, SupabasePersistenceConfig,
    SupabasePersistenceError,
)


def _repo():
    return SupabaseCognitiveMemoryRepository(
        SupabasePersistenceConfig("https://example.supabase.co", "service-secret")
    )


def test_environment_config_fails_closed_without_secrets(monkeypatch):
    monkeypatch.delenv("FORGEBRAIN_SUPABASE_URL", raising=False)
    monkeypatch.delenv("FORGEBRAIN_SUPABASE_SERVICE_ROLE_KEY", raising=False)
    with pytest.raises(SupabasePersistenceError, match="not configured"):
        SupabaseCognitiveMemoryRepository()


def test_snapshot_write_uses_integrity_fields(monkeypatch):
    captured = {}
    def fake_post(config, table, payload):
        captured.update({"table": table, "payload": payload})
        return [payload]
    monkeypatch.setattr(
        "backend.founder_brain.supabase_persistence._post_json", fake_post
    )
    profile = FounderCognitiveProfile(founder_id="founder-1", generated_at="now")
    snapshot = build_cognitive_memory_snapshot(profile, version=1, stored_at="now")
    result = _repo().save_snapshot(snapshot)
    assert result.table == "fb_cognitive_snapshots"
    assert captured["payload"]["snapshot_sha256"] == snapshot.snapshot_sha256
    assert captured["payload"]["profile_sha256"] == snapshot.profile_sha256
    assert captured["payload"]["previous_snapshot_sha256"] is None


def test_candidate_write_defaults_to_pending_review(monkeypatch):
    captured = {}
    monkeypatch.setattr(
        "backend.founder_brain.supabase_persistence._post_json",
        lambda config, table, payload: captured.update({"table": table, "payload": payload}) or [payload],
    )
    candidate = CognitiveMemoryCandidate(
        candidate_id="c1", kind=CandidateMemoryKind.PREFERENCE,
        statement="I prefer reusable systems", confidence=0.8,
        source_type="conversation", source_id="m1", observed_at="now",
        project_ids=("forgebrain",),
    )
    _repo().save_candidate("founder-1", candidate)
    assert captured["table"] == "fb_cognitive_candidates"
    assert captured["payload"]["review_status"] == "pending"
    assert captured["payload"]["founder_id"] == "founder-1"


def test_review_write_links_promotion_and_snapshot(monkeypatch):
    captured = {}
    monkeypatch.setattr(
        "backend.founder_brain.supabase_persistence._post_json",
        lambda config, table, payload: captured.update({"table": table, "payload": payload}) or [payload],
    )
    review = CandidateReviewDecision(
        candidate_id="c1", disposition=CandidateReviewDisposition.ACCEPT,
        reviewer_id="founder-1", reviewed_at="now", rationale="confirmed",
    )
    result = _repo().save_review(
        "founder-1", review, promoted_memory_id="pref-2", snapshot_sha256="abc"
    )
    assert result.table == "fb_cognitive_reviews"
    assert captured["payload"]["promoted_memory_id"] == "pref-2"
    assert captured["payload"]["snapshot_sha256"] == "abc"


def test_latest_snapshot_validates_integrity(monkeypatch):
    profile = FounderCognitiveProfile(founder_id="founder-1", generated_at="now")
    snapshot = build_cognitive_memory_snapshot(profile, version=1, stored_at="now")
    row = snapshot.to_dict()
    row["profile_json"] = row.pop("profile")
    monkeypatch.setattr(
        "backend.founder_brain.supabase_persistence._get_json",
        lambda config, table, query: [row],
    )
    restored = _repo().latest_snapshot("founder-1")
    assert restored == snapshot


def test_bootstrap_empty_profile_writes_only_when_missing(monkeypatch):
    calls = []
    repo = _repo()
    monkeypatch.setattr(repo, "latest_snapshot", lambda founder_id: None)
    monkeypatch.setattr(repo, "save_snapshot", lambda snapshot: calls.append(snapshot))
    snapshot = repo.bootstrap_empty_profile(founder_id="founder-1", stored_at="now")
    assert snapshot.version == 1
    assert snapshot.profile.founder_id == "founder-1"
    assert snapshot.profile.evidence == ()
    assert len(calls) == 1
