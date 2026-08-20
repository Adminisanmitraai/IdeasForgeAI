from __future__ import annotations

from dataclasses import dataclass, field, replace
from hashlib import sha256
from typing import Any, Literal, Mapping

JOB_CONTRACT_VERSION = "platform.durable-job.v1"
JobStatus = Literal[
    "queued", "leased", "running", "paused", "completed",
    "failed", "cancelled", "timed_out",
]


class DurableJobError(RuntimeError):
    pass


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3
    backoff_seconds: tuple[int, ...] = (5, 30, 120)

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise DurableJobError("max_attempts must be at least 1")

@dataclass(frozen=True)
class JobLease:
    lease_id: str
    worker_id: str
    generation: int
    acquired_at: str
    expires_at: str


@dataclass(frozen=True)
class JobAttempt:
    attempt_id: str
    attempt_number: int
    worker_id: str
    started_at: str
    completed_at: str = ""
    status: str = "running"
    error_code: str = ""


@dataclass(frozen=True)
class JobAuditEvent:
    event_id: str
    sequence: int
    event_type: str
    recorded_at: str
    correlation_id: str
    previous_digest: str = ""
    event_digest: str = ""


@dataclass(frozen=True)
class JobCheckpoint:
    checkpoint_id: str
    sequence: int
    recorded_at: str
    state: Mapping[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class DurableJob:
    job_id: str
    idempotency_key: str
    correlation_id: str
    operation: str
    payload_digest: str
    created_at: str
    status: JobStatus = "queued"
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    lease_generation: int = 0
    lease: JobLease | None = None
    attempts: tuple[JobAttempt, ...] = ()
    checkpoints: tuple[JobCheckpoint, ...] = ()
    audit_events: tuple[JobAuditEvent, ...] = ()
    result_digest: str = ""
    failure_code: str = ""
    contract_version: str = JOB_CONTRACT_VERSION

    @property
    def terminal(self) -> bool:
        return self.status in {"completed", "failed", "cancelled", "timed_out"}

_ALLOWED: dict[str, set[str]] = {
    "queued": {"leased", "cancelled"},
    "leased": {"running", "queued", "cancelled", "timed_out"},
    "running": {"paused", "completed", "failed", "cancelled", "timed_out"},
    "paused": {"queued", "cancelled"},
    "completed": set(),
    "failed": set(),
    "cancelled": set(),
    "timed_out": set(),
}


def assert_job_transition(current: JobStatus, target: JobStatus) -> None:
    if target not in _ALLOWED[current]:
        raise DurableJobError(f"invalid job transition: {current} -> {target}")


def digest_payload(payload: Mapping[str, Any]) -> str:
    material = repr(sorted(payload.items())).encode("utf-8")
    return sha256(material).hexdigest()

def acquire_lease(
    job: DurableJob, *, worker_id: str, acquired_at: str, expires_at: str
) -> DurableJob:
    assert_job_transition(job.status, "leased")
    generation = job.lease_generation + 1
    lease = JobLease(
        lease_id=f"lease-{job.job_id}-{generation}",
        worker_id=worker_id,
        generation=generation,
        acquired_at=acquired_at,
        expires_at=expires_at,
    )
    return replace(job, status="leased", lease_generation=generation, lease=lease)


def start_attempt(job: DurableJob, *, worker_id: str, started_at: str) -> DurableJob:
    if job.lease is None or job.lease.worker_id != worker_id:
        raise DurableJobError("worker does not own the active lease")
    assert_job_transition(job.status, "running")
    number = len(job.attempts) + 1
    if number > job.retry_policy.max_attempts:
        raise DurableJobError("retry attempts exhausted")
    attempt = JobAttempt(
        attempt_id=f"attempt-{job.job_id}-{number}",
        attempt_number=number,
        worker_id=worker_id,
        started_at=started_at,
    )
    return replace(job, status="running", attempts=job.attempts + (attempt,))


def release_expired_lease(job: DurableJob) -> DurableJob:
    if job.status != "leased":
        raise DurableJobError("only leased jobs may be requeued from lease expiry")
    return replace(job, status="queued", lease=None)


__all__ = [
    "JOB_CONTRACT_VERSION", "DurableJob", "DurableJobError", "JobAttempt",
    "JobAuditEvent", "JobCheckpoint", "JobLease", "JobStatus", "RetryPolicy",
    "acquire_lease", "assert_job_transition", "digest_payload",
    "release_expired_lease", "start_attempt",
]
