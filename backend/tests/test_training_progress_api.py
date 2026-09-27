from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.interfaces.founder_os.training_router import create_training_read_router
from backend.platform.training_jobs import TrainingJobSpec
from backend.training_job_registry import TrainingJobRegistry
from backend.training_telemetry import TrainingTelemetry, TrainingTelemetryStore


def _client(tmp_path, with_telemetry=True):
    registry = TrainingJobRegistry(tmp_path)
    registry.submit(
        TrainingJobSpec(
            job_id="train-live-001", model_ref="model:qwen",
            dataset_ref="dataset:cad-v1", requested_accelerator="cuda",
            requested_vram_mb=12000,
        ),
        idempotency_key="idem-live-001",
        correlation_id="corr-live-001", created_at="t0",
    )
    if with_telemetry:
        TrainingTelemetryStore(tmp_path).put(TrainingTelemetry(
            job_id="train-live-001", worker_id="fc-rtx-test",
            recorded_at="2026-09-27T03:00:00+00:00",
            epoch=3, step=700, total_steps=1000, progress_percent=70.0,
            loss=0.21, metrics={"eval_loss": 0.24},
            checkpoint_id="checkpoint-700",
            checkpoint_ref="checkpoints/train-live-001/700",
            gpu_utilization_percent=96.0,
            gpu_memory_used_mb=14500, gpu_memory_total_mb=16303,
        ))
    app = FastAPI()
    app.include_router(create_training_read_router(tmp_path))
    return TestClient(app)


def test_progress_endpoint_exposes_forgewa_ready_projection(tmp_path):
    response = _client(tmp_path).get(
        "/api/founder-os/v1/training/jobs/train-live-001/progress"
    )
    assert response.status_code == 200
    body = response.json()
    assert body["read_only"] is True
    assert body["progress_percent"] == 70.0
    assert body["loss"] == 0.21
    assert body["gpu"]["memory_used_mb"] == 14500
    assert body["resume"]["checkpoint_id"] == "checkpoint-700"


def test_progress_survives_service_restart(tmp_path):
    first = _client(tmp_path)
    assert first.get("/api/founder-os/v1/training/jobs/train-live-001/progress").status_code == 200
    app = FastAPI()
    app.include_router(create_training_read_router(tmp_path))
    restored = TestClient(app).get(
        "/api/founder-os/v1/training/jobs/train-live-001/progress"
    )
    assert restored.json()["step"] == 700


def test_missing_telemetry_returns_404(tmp_path):
    response = _client(tmp_path, with_telemetry=False).get(
        "/api/founder-os/v1/training/jobs/train-live-001/progress"
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "training telemetry not found"


def test_training_progress_router_remains_get_only(tmp_path):
    router = create_training_read_router(tmp_path)
    methods = {
        method
        for route in router.routes
        for method in getattr(route, "methods", set())
    }
    assert methods <= {"GET"}
