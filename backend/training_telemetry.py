from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

TRAINING_TELEMETRY_CONTRACT_VERSION = "forge-ai-factory.training-telemetry.v1"


@dataclass(frozen=True)
class TrainingTelemetry:
    job_id: str
    worker_id: str
    recorded_at: str
    epoch: int = 0
    step: int = 0
    total_steps: int = 0
    progress_percent: float = 0.0
    loss: float | None = None
    metrics: dict[str, float] | None = None
    checkpoint_id: str = ""
    checkpoint_ref: str = ""
    gpu_utilization_percent: float | None = None
    gpu_memory_used_mb: int | None = None
    gpu_memory_total_mb: int | None = None
    contract_version: str = TRAINING_TELEMETRY_CONTRACT_VERSION

    def __post_init__(self) -> None:
        if not self.job_id or not self.worker_id:
            raise ValueError("job_id and worker_id are required")
        if self.epoch < 0 or self.step < 0 or self.total_steps < 0:
            raise ValueError("epoch and step values cannot be negative")
        if not 0.0 <= self.progress_percent <= 100.0:
            raise ValueError("progress_percent must be between 0 and 100")
        if self.gpu_utilization_percent is not None and not 0.0 <= self.gpu_utilization_percent <= 100.0:
            raise ValueError("gpu utilization must be between 0 and 100")
        if self.gpu_memory_used_mb is not None and self.gpu_memory_used_mb < 0:
            raise ValueError("gpu memory used cannot be negative")
        if self.gpu_memory_total_mb is not None and self.gpu_memory_total_mb < 0:
            raise ValueError("gpu memory total cannot be negative")


class TrainingTelemetryStore:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root) / "training_telemetry"

    def _path(self, job_id: str) -> Path:
        return self.root / f"{job_id}.json"

    def put(self, telemetry: TrainingTelemetry) -> TrainingTelemetry:
        path = self._path(telemetry.job_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = path.with_suffix(".tmp")
        encoded = json.dumps(asdict(telemetry), sort_keys=True, separators=(",", ":")) + "\n"
        descriptor = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
                descriptor = -1
                stream.write(encoded)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp, path)
        finally:
            if descriptor != -1:
                os.close(descriptor)
            if temp.exists():
                temp.unlink()
        return telemetry

    def get(self, job_id: str) -> TrainingTelemetry:
        path = self._path(job_id)
        if not path.exists():
            raise ValueError("training telemetry not found")
        return TrainingTelemetry(**json.loads(path.read_text(encoding="utf-8")))

    def resume_checkpoint(self, job_id: str) -> dict[str, Any] | None:
        telemetry = self.get(job_id)
        if not telemetry.checkpoint_id:
            return None
        return {
            "checkpoint_id": telemetry.checkpoint_id,
            "checkpoint_ref": telemetry.checkpoint_ref,
            "epoch": telemetry.epoch,
            "step": telemetry.step,
            "progress_percent": telemetry.progress_percent,
        }


__all__ = [
    "TRAINING_TELEMETRY_CONTRACT_VERSION", "TrainingTelemetry",
    "TrainingTelemetryStore",
]
