from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.interfaces.founder_os.training_router import ROUTE_PREFIX, create_training_read_router
from backend.platform.training_jobs import TrainingJobSpec
from backend.training_job_registry import TrainingJobRegistry


def _client(tmp_path):
    registry = TrainingJobRegistry(tmp_path)
    registry.submit(
        TrainingJobSpec(
            job_id="train-read-001",
            model_ref="model:qwen",
            dataset_ref="dataset:cad-v1",
            requested_vram_mb=12000,
        ),
        idempotency_key="idem-read-001",
        correlation_id="corr-read-001",
        created_at="t0",
    )
    app = FastAPI()
    app.include_router(create_training_read_router(tmp_path))
    return TestClient(app)


def test_status_endpoint_is_read_only_projection(tmp_path):
    response = _client(tmp_path).get(f"{ROUTE_PREFIX}/jobs/train-read-001")
    assert response.status_code == 200
    body = response.json()
    assert body["read_only"] is True
    assert body["status"] == "queued"
    assert body["terminal"] is False
    assert body["worker_id"] is None


def test_history_endpoint_returns_durable_history(tmp_path):
    response = _client(tmp_path).get(f"{ROUTE_PREFIX}/jobs/train-read-001/history")
    assert response.status_code == 200
    body = response.json()
    assert body["read_only"] is True
    assert body["attempts"] == []
    assert body["checkpoints"] == []
    assert body["audit_events"] == []


def test_training_read_router_has_get_only_methods(tmp_path):
    app = FastAPI()
    app.include_router(create_training_read_router(tmp_path))
    routes = [r for r in app.routes if getattr(r, "path", "").startswith(ROUTE_PREFIX)]
    assert routes
    assert all(r.methods == {"GET"} for r in routes)


def test_missing_job_returns_404(tmp_path):
    app = FastAPI()
    app.include_router(create_training_read_router(tmp_path))
    response = TestClient(app).get(f"{ROUTE_PREFIX}/jobs/missing")
    assert response.status_code == 404
