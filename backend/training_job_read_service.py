from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

from backend.training_job_registry import TrainingJobRegistry
from backend.training_telemetry import TrainingTelemetryStore

TRAINING_READ_API_CONTRACT_VERSION = "forge-ai-factory.training-read-api.v1"


class TrainingJobReadService:
    """Read-only projection over durable training jobs and live telemetry."""

    def __init__(self, root: str | Path) -> None:
        self.registry = TrainingJobRegistry(root)
        self.telemetry = TrainingTelemetryStore(root)

    def status(self, job_id: str) -> dict[str, Any]:
        job = self.registry.get(job_id)
        return {
            "contract_version": TRAINING_READ_API_CONTRACT_VERSION,
            "read_only": True,
            "job_id": job.job_id,
            "status": job.status,
            "operation": job.operation,
            "created_at": job.created_at,
            "lease_generation": job.lease_generation,
            "worker_id": job.lease.worker_id if job.lease else None,
            "attempt_count": len(job.attempts),
            "checkpoint_count": len(job.checkpoints),
            "terminal": job.terminal,
            "failure_code": job.failure_code,
            "result_digest": job.result_digest,
        }

    def history(self, job_id: str) -> dict[str, Any]:
        job = self.registry.get(job_id)
        return {
            "contract_version": TRAINING_READ_API_CONTRACT_VERSION,
            "read_only": True,
            "job_id": job.job_id,
            "status": job.status,
            "attempts": [asdict(item) for item in job.attempts],
            "checkpoints": [asdict(item) for item in job.checkpoints],
            "audit_events": [asdict(item) for item in job.audit_events],
        }

    def progress(self, job_id: str) -> dict[str, Any]:
        job = self.registry.get(job_id)
        telemetry = self.telemetry.get(job_id)
        resume = self.telemetry.resume_checkpoint(job_id)
        return {
            "contract_version": TRAINING_READ_API_CONTRACT_VERSION,
            "read_only": True,
            "job_id": job.job_id,
            "status": job.status,
            "worker_id": telemetry.worker_id,
            "recorded_at": telemetry.recorded_at,
            "epoch": telemetry.epoch,
            "step": telemetry.step,
            "total_steps": telemetry.total_steps,
            "progress_percent": telemetry.progress_percent,
            "loss": telemetry.loss,
            "metrics": telemetry.metrics or {},
            "gpu": {
                "utilization_percent": telemetry.gpu_utilization_percent,
                "memory_used_mb": telemetry.gpu_memory_used_mb,
                "memory_total_mb": telemetry.gpu_memory_total_mb,
            },
            "resume": resume,
        }


__all__ = ["TRAINING_READ_API_CONTRACT_VERSION", "TrainingJobReadService"]
