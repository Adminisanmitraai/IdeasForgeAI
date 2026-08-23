from backend.founder_brain.cognitive_memory import (
    FounderAssumptionMemory,
    FounderCognitiveProfile,
    FounderDecisionMemory,
    FounderPreferenceMemory,
)
from backend.founder_brain.cognitive_memory_repository import build_cognitive_memory_snapshot
from backend.founder_brain.cognitive_temporal import analyze_cognitive_timeline


def _snapshot(profile, version, stored_at, previous=None):
    return build_cognitive_memory_snapshot(
        profile, version=version, stored_at=stored_at,
        previous_snapshot_sha256=None if previous is None else previous.snapshot_sha256,
    )


def test_temporal_report_detects_additions_and_confidence_change():
    p1 = FounderCognitiveProfile(founder_id="f1", generated_at="t1")
    s1 = _snapshot(p1, 1, "t1")
    p2 = FounderCognitiveProfile(
        founder_id="f1", generated_at="t2",
        preferences=(FounderPreferenceMemory(
            preference_id="p1", domain="build", statement="Prefer reusable systems",
            strength=0.8, updated_at="t2",
        ),),
    )
    s2 = _snapshot(p2, 2, "t2", s1)
    p3 = p2.model_copy(update={"generated_at": "t3", "preferences": (
        p2.preferences[0].model_copy(update={"strength": 0.95, "updated_at": "t3"}),
    )})
    s3 = _snapshot(p3, 3, "t3", s2)
    report = analyze_cognitive_timeline((s1, s2, s3))
    kinds = [(c.memory_type, c.memory_id, c.change_type) for c in report.changes]
    assert ("preference", "p1", "added") in kinds
    assert ("preference", "p1", "confidence_increased") in kinds
    assert report.from_version == 1
    assert report.to_version == 3


def test_temporal_report_detects_assumption_status_and_drop():
    a1 = FounderAssumptionMemory(
        assumption_id="a1", statement="Demand exists", scope="market",
        status="supported", confidence=0.9, updated_at="t1",
    )
    p1 = FounderCognitiveProfile(founder_id="f1", generated_at="t1", assumptions=(a1,))
    s1 = _snapshot(p1, 1, "t1")
    a2 = a1.model_copy(update={"status": "refuted", "confidence": 0.3, "updated_at": "t2"})
    s2 = _snapshot(p1.model_copy(update={"generated_at": "t2", "assumptions": (a2,)}), 2, "t2", s1)
    report = analyze_cognitive_timeline((s1, s2))
    kinds = [c.change_type for c in report.changes]
    assert "status_changed" in kinds
    assert "confidence_decreased" in kinds


def test_temporal_report_detects_decision_outcome_recorded():
    d1 = FounderDecisionMemory(
        decision_id="d1", title="Choose path", problem="Which path?",
        options_considered=("A", "B"), chosen_option="A", rationale="Test",
        expected_outcome="Works", confidence_at_decision=0.7, created_at="t1",
    )
    p1 = FounderCognitiveProfile(founder_id="f1", generated_at="t1", decisions=(d1,))
    s1 = _snapshot(p1, 1, "t1")
    d2 = d1.model_copy(update={"actual_outcome": "Worked"})
    s2 = _snapshot(p1.model_copy(update={"generated_at": "t2", "decisions": (d2,)}), 2, "t2", s1)
    report = analyze_cognitive_timeline((s1, s2))
    assert any(c.change_type == "outcome_recorded" and c.memory_id == "d1" for c in report.changes)


def test_temporal_report_rejects_empty_history():
    try:
        analyze_cognitive_timeline(())
    except ValueError as exc:
        assert "at least one snapshot" in str(exc)
    else:
        raise AssertionError("empty temporal history must fail")


def test_temporal_route_requires_private_review_key(monkeypatch):
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from backend.founder_brain.router import create_founder_brain_router

    monkeypatch.setenv("FORGEBRAIN_REVIEW_API_KEY", "secret")
    app = FastAPI()
    app.include_router(create_founder_brain_router())
    response = TestClient(app).get("/api/founder-brain/v1/cognitive/temporal")
    assert response.status_code == 403


def test_temporal_route_reads_persistent_snapshot_chain(monkeypatch):
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from backend.founder_brain.router import create_founder_brain_router

    p1 = FounderCognitiveProfile(founder_id="ranjan", generated_at="t1")
    s1 = _snapshot(p1, 1, "t1")
    p2 = FounderCognitiveProfile(founder_id="ranjan", generated_at="t2")
    s2 = _snapshot(p2, 2, "t2", s1)
    class Repo:
        def list_snapshots(self, founder_id):
            assert founder_id == "ranjan"
            return (s1, s2)

    monkeypatch.setenv("FORGEBRAIN_REVIEW_API_KEY", "secret")
    monkeypatch.setenv("FORGEBRAIN_FOUNDER_ID", "ranjan")
    monkeypatch.setattr(
        "backend.founder_brain.router.SupabaseCognitiveMemoryRepository",
        lambda: Repo(),
    )
    app = FastAPI()
    app.include_router(create_founder_brain_router())
    response = TestClient(app).get(
        "/api/founder-brain/v1/cognitive/temporal",
        headers={"x-forgebrain-review-key": "secret"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["from_version"] == 1
    assert data["to_version"] == 2
    assert data["change_count"] == 0
