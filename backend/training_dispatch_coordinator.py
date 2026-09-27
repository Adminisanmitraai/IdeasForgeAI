from __future__ import annotations

from backend.platform.durable_jobs import DurableJob, acquire_lease, start_attempt
from backend.platform.durable_job_runtime import recover_orphan
from backend.platform.training_jobs import TrainingJobSpec
from backend.training_dispatcher import DispatchDecision, select_worker
from backend.training_job_registry import TrainingJobRegistry
from backend.worker_registry import WorkerRecord

ASSIGNMENT_CONTRACT_VERSION = "forge-ai-factory.dispatch-assignment.v1"


class TrainingDispatchCoordinator:
    """Bind capability selection to durable lease assignment and recovery."""

    def __init__(self, registry: TrainingJobRegistry) -> None:
        self.registry = registry

    def assign(
        self, *, spec: TrainingJobSpec, workers: tuple[WorkerRecord, ...],
        acquired_at: str, expires_at: str,
    ) -> tuple[DispatchDecision, DurableJob]:
        job = self.registry.get(spec.job_id)
        if job.status != "queued":
            return (
                DispatchDecision(spec.job_id, False, None, f"job_not_queued:{job.status}"),
                job,
            )
        decision = select_worker(spec, workers)
        if not decision.eligible or decision.worker_id is None:
            return decision, job
        leased = acquire_lease(
            job, worker_id=decision.worker_id,
            acquired_at=acquired_at, expires_at=expires_at,
        )
        return decision, self.registry.replace(leased)

    def start(self, *, job_id: str, worker_id: str, started_at: str) -> DurableJob:
        job = self.registry.get(job_id)
        running = start_attempt(job, worker_id=worker_id, started_at=started_at)
        return self.registry.replace(running)

    def recover_disconnected(self, *, job_id: str, observed_at: str) -> DurableJob:
        job = self.registry.get(job_id)
        if job.status == "leased":
            from backend.platform.durable_jobs import release_expired_lease
            recovered = release_expired_lease(job)
        elif job.status == "running":
            recovered = recover_orphan(job, observed_at=observed_at)
        else:
            return job
        return self.registry.replace(recovered)


__all__ = ["ASSIGNMENT_CONTRACT_VERSION", "TrainingDispatchCoordinator"]
