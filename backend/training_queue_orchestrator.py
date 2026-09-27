from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from backend.training_dispatch_coordinator import TrainingDispatchCoordinator
from backend.training_job_registry import TrainingJobRegistry
from backend.worker_registry import WorkerRegistry

QUEUE_RESUME_CONTRACT_VERSION = "forge-ai-factory.queue-resume.v1"


@dataclass(frozen=True)
class QueueResumeResult:
    job_id: str
    status: str
    worker_id: str | None
    reason: str
    contract_version: str = QUEUE_RESUME_CONTRACT_VERSION


class TrainingQueueOrchestrator:
    """Resume durable queued training work when compatible workers reconnect."""

    def __init__(
        self,
        job_registry: TrainingJobRegistry,
        worker_registry: WorkerRegistry,
    ) -> None:
        self.jobs = job_registry
        self.workers = worker_registry
        self.dispatch = TrainingDispatchCoordinator(job_registry)

    def reconcile_job(
        self, *, job_id: str, observed_at: str,
        acquired_at: str, expires_at: str,
    ) -> QueueResumeResult:
        job = self.jobs.get(job_id)
        if job.status != "queued":
            worker_id = job.lease.worker_id if job.lease else None
            return QueueResumeResult(job_id, job.status, worker_id, "job_not_queued")

        spec = self.jobs.get_spec(job_id)
        workers = self.workers.list(observed_at=observed_at)
        decision, updated = self.dispatch.assign(
            spec=spec,
            workers=workers,
            acquired_at=acquired_at,
            expires_at=expires_at,
        )
        return QueueResumeResult(
            job_id=job_id,
            status=updated.status,
            worker_id=decision.worker_id,
            reason=decision.reason,
        )

    def reconcile_queue(
        self, *, job_ids: Iterable[str], observed_at: str,
        acquired_at: str, expires_at: str,
    ) -> tuple[QueueResumeResult, ...]:
        return tuple(
            self.reconcile_job(
                job_id=job_id,
                observed_at=observed_at,
                acquired_at=acquired_at,
                expires_at=expires_at,
            )
            for job_id in sorted(set(job_ids))
        )


__all__ = [
    "QUEUE_RESUME_CONTRACT_VERSION", "QueueResumeResult",
    "TrainingQueueOrchestrator",
]
