from backend.founder_brain.cognitive_confidence import ConfidenceSignal, apply_confidence_adjustment, assess_memory_confidence
from backend.founder_brain.cognitive_memory import CognitiveEvidence, FounderAssumptionMemory, FounderCognitiveProfile, FounderLessonMemory, FounderPreferenceMemory


def _profile():
    return FounderCognitiveProfile(
        founder_id="f1", generated_at="2026-08-23T00:00:00Z",
        evidence=(
            CognitiveEvidence(evidence_id="e1", source_type="conversation", source_id="m1", observed_at="2026-08-01T00:00:00Z", confidence=0.8),
            CognitiveEvidence(evidence_id="e2", source_type="project_outcome", source_id="p1", observed_at="2026-08-10T00:00:00Z", confidence=0.9),
            CognitiveEvidence(evidence_id="e3", source_type="decision_record", source_id="d1", observed_at="2026-08-15T00:00:00Z", confidence=0.9),
        ),
        preferences=(
            FounderPreferenceMemory(preference_id="p1", domain="architecture", statement="Prefer reuse", strength=0.7, evidence_ids=("e1","e2","e3"), updated_at="2026-08-01T00:00:00Z"),
            FounderPreferenceMemory(preference_id="p2", domain="design", statement="Old preference", strength=0.7, updated_at="2025-01-01T00:00:00Z"),
        ),
        assumptions=(FounderAssumptionMemory(assumption_id="a1", statement="Old assumption", scope="general", status="refuted", confidence=0.8, evidence_ids=("e1",), updated_at="2026-08-01T00:00:00Z"),),
        lessons=(FounderLessonMemory(lesson_id="l1", statement="Keep audit trail", applicability="all", confidence=0.8, evidence_ids=("e1","e2"), updated_at="2026-08-01T00:00:00Z"),),
    )


def test_recent_multi_evidence_memory_reinforces():
    rows = {x.memory_id: x for x in assess_memory_confidence(_profile(), as_of="2026-08-23T00:00:00Z")}
    assert rows["p1"].signal is ConfidenceSignal.REINFORCE
    assert rows["p1"].recommended_confidence > rows["p1"].current_confidence


def test_old_unsupported_memory_decays():
    rows = {x.memory_id: x for x in assess_memory_confidence(_profile(), as_of="2026-08-23T00:00:00Z")}
    assert rows["p2"].signal is ConfidenceSignal.DECAY
    assert rows["p2"].recommended_confidence < 0.7


def test_refuted_assumption_is_sharply_reduced():
    rows = {x.memory_id: x for x in assess_memory_confidence(_profile(), as_of="2026-08-23T00:00:00Z")}
    assert rows["a1"].signal is ConfidenceSignal.REFUTED
    assert rows["a1"].recommended_confidence <= 0.2


def test_governed_adjustment_updates_only_target():
    evolved = apply_confidence_adjustment(_profile(), memory_type="preference", memory_id="p1", new_confidence=0.91, updated_at="2026-08-23T12:00:00Z")
    assert evolved.preferences[0].strength == 0.91
    assert evolved.preferences[1].strength == 0.7
    assert evolved.generated_at == "2026-08-23T12:00:00Z"


def test_confidence_route_requires_review_key(monkeypatch):
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from backend.founder_brain.router import create_founder_brain_router
    monkeypatch.setenv("FORGEBRAIN_REVIEW_API_KEY", "secret")
    app = FastAPI()
    app.include_router(create_founder_brain_router())
    response = TestClient(app).get("/api/founder-brain/v1/cognitive/confidence")
    assert response.status_code == 403


def test_confidence_adjustment_creates_next_snapshot(monkeypatch):
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from backend.founder_brain.cognitive_memory_repository import build_cognitive_memory_snapshot
    from backend.founder_brain.router import create_founder_brain_router
    previous = build_cognitive_memory_snapshot(_profile(), version=1, stored_at="2026-08-23T00:00:00Z")
    saved = []
    audits = []
    monkeypatch.setenv("FORGEBRAIN_REVIEW_API_KEY", "secret")
    monkeypatch.setenv("FORGEBRAIN_SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("FORGEBRAIN_SUPABASE_SERVICE_ROLE_KEY", "service-secret")
    monkeypatch.setattr("backend.founder_brain.router.SupabaseCognitiveMemoryRepository.latest_snapshot", lambda self, founder_id: previous)
    monkeypatch.setattr("backend.founder_brain.router.SupabaseCognitiveMemoryRepository.save_snapshot", lambda self, snapshot: saved.append(snapshot))
    monkeypatch.setattr("backend.founder_brain.router.SupabaseCognitiveMemoryRepository.append_audit_event", lambda self, **kwargs: audits.append(kwargs))
    app = FastAPI()
    app.include_router(create_founder_brain_router())
    response = TestClient(app).post(
        "/api/founder-brain/v1/cognitive/confidence/adjust",
        headers={"x-forgebrain-review-key": "secret"},
        json={
            "memory_type": "preference",
            "memory_id": "p1",
            "new_confidence": 0.91,
            "approved_at": "2026-08-23T12:00:00Z",
            "reviewer_id": "founder",
            "rationale": "corroborated",
        },
    )
    assert response.status_code == 200
    assert response.json()["data"]["snapshot_version"] == 2
    assert saved[0].previous_snapshot_sha256 == previous.snapshot_sha256
    assert audits[0]["event_type"] == "memory.confidence_adjusted"
