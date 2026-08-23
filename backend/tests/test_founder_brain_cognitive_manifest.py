from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.founder_brain.cognitive_manifest import cognitive_capability_manifest
from backend.founder_brain.router import create_founder_brain_router


def test_cognitive_manifest_reports_fb21_capabilities():
    manifest = cognitive_capability_manifest()
    ids = {item["capability_id"] for item in manifest["capabilities"]}
    assert manifest["program"] == "ForgeBrain 2.0"
    assert manifest["phase"].startswith("FB-2.1")
    assert {"memory", "advisor", "reflection", "context", "review"}.issubset(ids)
    assert manifest["execution_allowed"] is False


def test_cognitive_manifest_route_is_public_read_only_contract():
    app = FastAPI()
    app.include_router(create_founder_brain_router())
    response = TestClient(app).get("/api/founder-brain/v1/cognitive/manifest")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["program"] == "ForgeBrain 2.0"
    assert data["capability_count"] >= 12
    assert data["execution_allowed"] is False
