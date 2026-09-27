from __future__ import annotations

import json
import os
from dataclasses import asdict
from pathlib import Path
from typing import Any

from backend.durable_job_store import DurableJobStore
from backend.platform.durable_jobs import DurableJob, digest_payload
from backend.platform.training_jobs import TrainingJobSpec

TRAINING_OPERATION = "forge_ai_factory.train.v1"
TRAINING_SPEC_STORE_VERSION = "forge-ai-factory.training-spec-store.v1"


class TrainingJobRegistry:
    """Durable AI Factory job state plus recoverable training specifications."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.store = DurableJobStore(self.root)
        self.specs_root = self.root / "training_specs"

    def _spec_path(self, job_id: str) -> Path:
        return self.specs_root / f"{job_id}.json"

    def _write_spec(self, spec: TrainingJobSpec) -> None:
        path = self._spec_path(spec.job_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = path.with_suffix(".tmp")
        payload = {
            "store_version": TRAINING_SPEC_STORE_VERSION,
            "spec": asdict(spec),
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n"
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

    def submit(
        self, spec: TrainingJobSpec, *, idempotency_key: str,
        correlation_id: str, created_at: str,
    ) -> DurableJob:
        payload: dict[str, Any] = asdict(spec)
        job = self.store.submit(
            job_id=spec.job_id,
            idempotency_key=idempotency_key,
            correlation_id=correlation_id,
            operation=TRAINING_OPERATION,
            payload=payload,
            created_at=created_at,
        )
        path = self._spec_path(spec.job_id)
        if path.exists():
            restored = self.get_spec(spec.job_id)
            if digest_payload(asdict(restored)) != job.payload_digest:
                raise ValueError("persisted training spec does not match durable job")
        else:
            self._write_spec(spec)
        return job

    def get(self, job_id: str) -> DurableJob:
        job = self.store.get(job_id)
        if job.operation != TRAINING_OPERATION:
            raise ValueError("job is not an AI Factory training job")
        return job

    def get_spec(self, job_id: str) -> TrainingJobSpec:
        job = self.get(job_id)
        path = self._spec_path(job_id)
        if not path.exists():
            raise ValueError("recoverable training spec is missing")
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("store_version") != TRAINING_SPEC_STORE_VERSION:
            raise ValueError("unsupported training spec store version")
        spec = TrainingJobSpec(**payload["spec"])
        if digest_payload(asdict(spec)) != job.payload_digest:
            raise ValueError("training spec integrity mismatch")
        return spec

    def replace(self, job: DurableJob) -> DurableJob:
        if job.operation != TRAINING_OPERATION:
            raise ValueError("job is not an AI Factory training job")
        return self.store.replace(job)


__all__ = [
    "TRAINING_OPERATION", "TRAINING_SPEC_STORE_VERSION", "TrainingJobRegistry",
]
