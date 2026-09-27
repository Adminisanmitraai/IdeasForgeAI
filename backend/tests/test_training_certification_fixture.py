import os

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.interfaces.founder_os.training_router import create_training_certification_router, create_training_read_router


def test_certification_fixture_is_gated_synthetic_readable_and_deletable(tmp_path, monkeypatch):
    monkeypatch.setenv("FORGE_AI_FACTORY_CERTIFICATION_TOKEN", "test-cert-token")
    app = FastAPI()
    app.include_router(create_training_read_router(tmp_path))
    app.include_router(create_training_certification_router(tmp_path))
    client = TestClient(app)
    job_id = "cert-r11-r2a"
    url = f"/api/founder-os/v1/training/certification-fixtures/{job_id}"

    assert client.post(url).status_code == 401
    created = client.post(url, headers={"X-Forge-Certification-Token": "test-cert-token"})
    assert created.status_code == 200
    assert created.json()["gpu_dispatched"] is False

    status = client.get(f"/api/founder-os/v1/training/jobs/{job_id}")
    progress = client.get(f"/api/founder-os/v1/training/jobs/{job_id}/progress")
    history = client.get(f"/api/founder-os/v1/training/jobs/{job_id}/history")
    assert status.status_code == 200
    assert history.status_code == 200
    assert progress.status_code == 200
    body = progress.json()
    assert body["progress_percent"] == 70.0
    assert body["loss"] == 0.21
    assert body["resume"]["checkpoint_id"] == "cert-checkpoint-70"
    assert body["gpu"]["memory_used_mb"] == 0

    deleted = client.delete(url, headers={"X-Forge-Certification-Token": "test-cert-token"})
    assert deleted.status_code == 200
    assert deleted.json()["files_removed"] == 3
    assert client.get(f"/api/founder-os/v1/training/jobs/{job_id}").status_code == 404


def test_certification_fixture_rejects_unsafe_job_id(tmp_path, monkeypatch):
    monkeypatch.setenv("FORGE_AI_FACTORY_CERTIFICATION_TOKEN", "test-cert-token")
    app = FastAPI()
    app.include_router(create_training_read_router(tmp_path))
    app.include_router(create_training_certification_router(tmp_path))
    client = TestClient(app)
    response = client.post("/api/founder-os/v1/training/certification-fixtures/cert-bad..id", headers={"X-Forge-Certification-Token": "test-cert-token"})
    assert response.status_code == 400