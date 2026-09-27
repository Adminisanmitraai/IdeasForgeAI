from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

TRAINING_JOB_CONTRACT_VERSION = "forge-ai-factory.training-job.v1"

TrainingPhase = Literal[
    "queued", "assigned", "running", "checkpointing", "evaluating",
    "completed", "failed", "cancelled",
]

_ALLOWED: dict[str, set[str]] = {
    "queued": {"assigned", "cancelled"},
    "assigned": {"running", "queued", "cancelled"},
    "running": {"checkpointing", "evaluating", "completed", "failed", "cancelled"},
    "checkpointing": {"running", "evaluating", "failed", "cancelled"},
    "evaluating": {"running", "completed", "failed", "cancelled"},
    "completed": set(),
    "failed": set(),
    "cancelled": set(),
}


class TrainingJobLifecycleError(RuntimeError):
    pass


@dataclass(frozen=True)
class TrainingJobSpec:
    job_id: str
    model_ref: str
    dataset_ref: str
    requested_accelerator: str = "cuda"
    requested_vram_mb: int = 0
    priority: int = 100
    contract_version: str = TRAINING_JOB_CONTRACT_VERSION

    def __post_init__(self) -> None:
        if not self.job_id:
            raise TrainingJobLifecycleError("job_id is required")
        if not self.model_ref:
            raise TrainingJobLifecycleError("model_ref is required")
        if not self.dataset_ref:
            raise TrainingJobLifecycleError("dataset_ref is required")
        if self.requested_vram_mb < 0:
            raise TrainingJobLifecycleError("requested_vram_mb cannot be negative")


def assert_training_transition(current: TrainingPhase, target: TrainingPhase) -> None:
    if target not in _ALLOWED[current]:
        raise TrainingJobLifecycleError(
            f"invalid training job transition: {current} -> {target}"
        )


def can_wait_for_worker(status: TrainingPhase) -> bool:
    return status == "queued"


__all__ = [
    "TRAINING_JOB_CONTRACT_VERSION",
    "TrainingJobLifecycleError",
    "TrainingJobSpec",
    "TrainingPhase",
    "assert_training_transition",
    "can_wait_for_worker",
]
