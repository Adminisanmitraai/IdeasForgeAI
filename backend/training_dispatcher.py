from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from backend.platform.training_jobs import TrainingJobSpec
from backend.worker_registry import WorkerRecord

DISPATCH_CONTRACT_VERSION = "forge-ai-factory.dispatch.v1"
TRAINING_WORKER_ROLE = "ai_factory_gpu_worker"


@dataclass(frozen=True)
class DispatchDecision:
    job_id: str
    eligible: bool
    worker_id: str | None
    reason: str
    contract_version: str = DISPATCH_CONTRACT_VERSION


def worker_matches(spec: TrainingJobSpec, worker: WorkerRecord) -> bool:
    if worker.state != "online":
        return False
    if worker.role != TRAINING_WORKER_ROLE:
        return False
    requested = spec.requested_accelerator.strip().lower()
    available = worker.accelerator.strip().lower()
    if requested and requested != available:
        return False
    worker_vram_mb = getattr(worker, "vram_mb", 0)
    if spec.requested_vram_mb and worker_vram_mb < spec.requested_vram_mb:
        return False
    return True


def select_worker(
    spec: TrainingJobSpec,
    workers: Iterable[WorkerRecord],
) -> DispatchDecision:
    online = [worker for worker in workers if worker.state == "online"]
    if not online:
        return DispatchDecision(spec.job_id, False, None, "no_online_workers")

    role_eligible = [worker for worker in online if worker.role == TRAINING_WORKER_ROLE]
    if not role_eligible:
        return DispatchDecision(spec.job_id, False, None, "no_training_role_workers")

    accelerator = [
        worker for worker in role_eligible
        if not spec.requested_accelerator
        or worker.accelerator.lower() == spec.requested_accelerator.lower()
    ]
    if not accelerator:
        return DispatchDecision(spec.job_id, False, None, "no_compatible_accelerator")

    capable = [worker for worker in accelerator if worker_matches(spec, worker)]
    if not capable:
        return DispatchDecision(spec.job_id, False, None, "insufficient_vram")

    capable.sort(key=lambda worker: (-getattr(worker, "vram_mb", 0), worker.worker_id))
    return DispatchDecision(spec.job_id, True, capable[0].worker_id, "matched")


__all__ = [
    "DISPATCH_CONTRACT_VERSION", "TRAINING_WORKER_ROLE", "DispatchDecision", "select_worker", "worker_matches",
]
