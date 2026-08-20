from __future__ import annotations

import json
import os
import threading
from dataclasses import asdict
from pathlib import Path
from typing import Any, Mapping

from backend.platform.durable_jobs import (
    DurableJob, DurableJobError, JobAttempt, JobAuditEvent, JobCheckpoint, JobLease, RetryPolicy,
    digest_payload,
)

STORE_VERSION = "founder-os-durable-job-store.v1"


class DurableJobStoreError(DurableJobError):
    pass


class DurableJobNotFoundError(DurableJobStoreError):
    pass


class DurableJobConflictError(DurableJobStoreError):
    pass

def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    descriptor: int | None = None
    try:
        descriptor = os.open(temp, flags, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            descriptor = None
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
    except OSError as error:
        if descriptor is not None:
            os.close(descriptor)
        try:
            temp.unlink()
        except OSError:
            pass
        raise DurableJobStoreError("atomic job write failed") from error


def _job_to_json(job: DurableJob) -> str:
    return json.dumps(asdict(job), sort_keys=True, separators=(",", ":"))

def _job_from_dict(data: dict[str, Any]) -> DurableJob:
    return DurableJob(
        job_id=data["job_id"],
        idempotency_key=data["idempotency_key"],
        correlation_id=data["correlation_id"],
        operation=data["operation"],
        payload_digest=data["payload_digest"],
        created_at=data["created_at"],
        status=data["status"],
        retry_policy=RetryPolicy(max_attempts=data["retry_policy"]["max_attempts"], backoff_seconds=tuple(data["retry_policy"]["backoff_seconds"])),
        lease_generation=data.get("lease_generation", 0),
        lease=JobLease(**data["lease"]) if data.get("lease") else None,
        attempts=tuple(JobAttempt(**item) for item in data.get("attempts", [])),
        checkpoints=tuple(JobCheckpoint(**item) for item in data.get("checkpoints", [])),
        audit_events=tuple(JobAuditEvent(**item) for item in data.get("audit_events", [])),
        result_digest=data.get("result_digest", ""),
        failure_code=data.get("failure_code", ""),
        contract_version=data.get("contract_version", "platform.durable-job.v1"),
    )


class DurableJobStore:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.jobs_root = self.root / "jobs"
        self._lock = threading.RLock()

    def _path(self, job_id: str) -> Path:
        if not job_id or any(ch not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" for ch in job_id):
            raise DurableJobStoreError("invalid job_id")
        return self.jobs_root / f"{job_id}.json"

    def put(self, job: DurableJob) -> DurableJob:
        path = self._path(job.job_id)
        encoded = _job_to_json(job) + "\n"
        with self._lock:
            if path.exists():
                current = self.get(job.job_id)
                if current == job:
                    return current
                raise DurableJobConflictError("job identity already stores different content")
            _atomic_write(path, encoded)
            restored = self.get(job.job_id)
            if restored != job:
                raise DurableJobStoreError("job round-trip verification failed")
            return restored

    def get(self, job_id: str) -> DurableJob:
        path = self._path(job_id)
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError as error:
            raise DurableJobNotFoundError(job_id) from error
        return _job_from_dict(data)

    def submit(
        self, *, job_id: str, idempotency_key: str, correlation_id: str,
        operation: str, payload: Mapping[str, Any], created_at: str,
    ) -> DurableJob:
        if not idempotency_key:
            raise DurableJobStoreError("idempotency_key is required")
        digest = digest_payload(payload)
        with self._lock:
            if self.jobs_root.exists():
                for path in self.jobs_root.glob("*.json"):
                    current = self.get(path.stem)
                    if current.idempotency_key == idempotency_key:
                        if current.payload_digest == digest and current.operation == operation:
                            return current
                        raise DurableJobConflictError("idempotency key collision")
            job = DurableJob(
                job_id=job_id,
                idempotency_key=idempotency_key,
                correlation_id=correlation_id,
                operation=operation,
                payload_digest=digest,
                created_at=created_at,
            )
            return self.put(job)

    def replace(self, job: DurableJob) -> DurableJob:
        path = self._path(job.job_id)
        with self._lock:
            if not path.exists():
                raise DurableJobNotFoundError(job.job_id)
            _atomic_write(path, _job_to_json(job) + "\n")
            return self.get(job.job_id)
