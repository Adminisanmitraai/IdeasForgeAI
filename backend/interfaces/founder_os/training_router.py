from pathlib import Path

from fastapi import APIRouter, HTTPException

from backend.durable_job_store import DurableJobNotFoundError
from backend.training_job_read_service import TrainingJobReadService

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


__all__ = ["ROUTE_PREFIX", "create_training_read_router"]
