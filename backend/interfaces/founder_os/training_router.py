from pathlib import Path
from datetime import datetime, timezone
import hmac
import os
import re

from fastapi import APIRouter, Header, HTTPException

from backend.durable_job_store import DurableJobNotFoundError
from backend.platform.training_jobs import TrainingJobSpec
from backend.training_job_read_service import TrainingJobReadService
from backend.training_job_registry import TrainingJobRegistry
from backend.training_telemetry import TrainingTelemetry, TrainingTelemetryStore

ROUTE_PREFIX = "/api/founder-os/v1/training"


def create_training_read_router(root: str | Path) -> APIRouter:
    service = TrainingJobReadService(root)
    router = APIRouter(prefix=ROUTE_PREFIX, tags=["Forge AI Factory"])

    @router.get("/jobs/{job_id}")
    def training_job_status(job_id: str):
        try:
            return service.status(job_id)
        except DurableJobNotFoundError as exc:
            raise HTTPException(status_code=404, detail="training job not found") from exc

    @router.get("/jobs/{job_id}/history")
    def training_job_history(job_id: str):
        try:
            return service.history(job_id)
        except DurableJobNotFoundError as exc:
            raise HTTPException(status_code=404, detail="training job not found") from exc

    @router.get("/jobs/{job_id}/progress")
    def training_job_progress(job_id: str):
        try:
            return service.progress(job_id)
        except DurableJobNotFoundError as exc:
            raise HTTPException(status_code=404, detail="training job not found") from exc
        except ValueError as exc:
            raise HTTPException(status_code=404, detail="training telemetry not found") from exc

    return router



def create_training_certification_router(root: str | Path) -> APIRouter:
    root = Path(root)
    registry = TrainingJobRegistry(root)
    telemetry = TrainingTelemetryStore(root)
    router = APIRouter(prefix=ROUTE_PREFIX, tags=["Forge AI Factory Certification"])

    bootstrap_job_id = os.getenv("FORGE_AI_FACTORY_CERTIFICATION_JOB_ID", "").strip()
    bootstrap_action = os.getenv("FORGE_AI_FACTORY_CERTIFICATION_ACTION", "").strip().lower()
    if bootstrap_job_id and re.fullmatch(r"cert-[A-Za-z0-9_-]+", bootstrap_job_id):
        paths = [root / "jobs" / f"{bootstrap_job_id}.json", root / "training_specs" / f"{bootstrap_job_id}.json", root / "training_telemetry" / f"{bootstrap_job_id}.json"]
        if bootstrap_action == "delete":
            for path in paths:
                if path.exists():
                    path.unlink()
        elif bootstrap_action == "create":
            now = datetime.now(timezone.utc).isoformat()
            spec = TrainingJobSpec(job_id=bootstrap_job_id, model_ref="certification://synthetic-model", dataset_ref="certification://synthetic-dataset", requested_accelerator="cuda", requested_vram_mb=0)
            registry.submit(spec, idempotency_key=f"certification:{bootstrap_job_id}", correlation_id=f"certification:{bootstrap_job_id}", created_at=now)
            try:
                telemetry.get(bootstrap_job_id)
            except ValueError:
                telemetry.put(TrainingTelemetry(job_id=bootstrap_job_id, worker_id="certification-fixture", recorded_at=now, epoch=2, step=70, total_steps=100, progress_percent=70.0, loss=0.21, metrics={"accuracy": 0.88}, checkpoint_id="cert-checkpoint-70", checkpoint_ref="certification://checkpoint/70", gpu_utilization_percent=0.0, gpu_memory_used_mb=0, gpu_memory_total_mb=0))

    def require_token(value: str | None) -> None:
        configured = os.getenv("FORGE_AI_FACTORY_CERTIFICATION_TOKEN", "").strip()
        if not configured or not value or not hmac.compare_digest(value, configured):
            raise HTTPException(status_code=401, detail="certification authorization required")

    def validate_job_id(job_id: str) -> None:
        if not re.fullmatch(r"cert-[A-Za-z0-9_-]+", job_id):
            raise HTTPException(status_code=400, detail="invalid certification job_id")

    @router.post("/certification-fixtures/{job_id}")
    def create_fixture(job_id: str, x_forge_certification_token: str | None = Header(default=None)):
        require_token(x_forge_certification_token)
        validate_job_id(job_id)
        now = datetime.now(timezone.utc).isoformat()
        spec = TrainingJobSpec(job_id=job_id, model_ref="certification://synthetic-model", dataset_ref="certification://synthetic-dataset", requested_accelerator="cuda", requested_vram_mb=0)
        registry.submit(spec, idempotency_key=f"certification:{job_id}", correlation_id=f"certification:{job_id}", created_at=now)
        telemetry.put(TrainingTelemetry(job_id=job_id, worker_id="certification-fixture", recorded_at=now, epoch=2, step=70, total_steps=100, progress_percent=70.0, loss=0.21, metrics={"accuracy": 0.88}, checkpoint_id="cert-checkpoint-70", checkpoint_ref="certification://checkpoint/70", gpu_utilization_percent=0.0, gpu_memory_used_mb=0, gpu_memory_total_mb=0))
        return {"created": True, "synthetic": True, "gpu_dispatched": False, "job_id": job_id}

    @router.delete("/certification-fixtures/{job_id}")
    def delete_fixture(job_id: str, x_forge_certification_token: str | None = Header(default=None)):
        require_token(x_forge_certification_token)
        validate_job_id(job_id)
        paths = [root / "jobs" / f"{job_id}.json", root / "training_specs" / f"{job_id}.json", root / "training_telemetry" / f"{job_id}.json"]
        removed = 0
        for path in paths:
            if path.exists():
                path.unlink()
                removed += 1
        return {"deleted": True, "job_id": job_id, "files_removed": removed}

    return router


__all__ = ["ROUTE_PREFIX", "create_training_read_router", "create_training_certification_router"]
