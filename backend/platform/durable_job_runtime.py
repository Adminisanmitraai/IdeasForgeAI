from __future__ import annotations

from dataclasses import replace
from hashlib import sha256
from typing import Any, Mapping

from .durable_jobs import (
    DurableJob,
    DurableJobError,
    JobAttempt,
    JobCheckpoint,
    JobLease,
    acquire_lease,
    assert_job_transition,
)


class DurableJobFenceError(DurableJobError):
    pass


def _require_active_lease(
    job: DurableJob, *, worker_id: str, generation: int
) -> JobLease:
    lease = job.lease
    if lease is None:
        raise DurableJobFenceError("job has no active lease")
    if lease.worker_id != worker_id or lease.generation != generation:
        raise DurableJobFenceError("stale or foreign worker lease")
    return lease

def pause_job(
    job: DurableJob, *, worker_id: str, generation: int
) -> DurableJob:
    _require_active_lease(job, worker_id=worker_id, generation=generation)
    assert_job_transition(job.status, "paused")
    return replace(job, status="paused")


def resume_job(
    job: DurableJob, *, worker_id: str, acquired_at: str, expires_at: str
) -> DurableJob:
    if job.status != "paused":
        raise DurableJobError("only paused jobs may resume")
    queued = replace(job, status="queued", lease=None)
    return acquire_lease(
        queued,
        worker_id=worker_id,
        acquired_at=acquired_at,
        expires_at=expires_at,
    )


def cancel_job(job: DurableJob) -> DurableJob:
    if job.terminal:
        raise DurableJobError("terminal jobs cannot be cancelled")
    assert_job_transition(job.status, "cancelled")
    return replace(job, status="cancelled", lease=None)

def record_checkpoint(
    job: DurableJob,
    *,
    worker_id: str,
    generation: int,
    recorded_at: str,
    state: Mapping[str, Any],
) -> DurableJob:
    _require_active_lease(job, worker_id=worker_id, generation=generation)
    if job.status not in {"leased", "running", "paused"}:
        raise DurableJobError("job state does not allow checkpoints")
    sequence = len(job.checkpoints) + 1
    digest = sha256(
        repr(sorted(state.items())).encode("utf-8")
    ).hexdigest()[:16]
    checkpoint = JobCheckpoint(
        checkpoint_id=f"checkpoint-{job.job_id}-{sequence}-{digest}",
        sequence=sequence,
        recorded_at=recorded_at,
        state=dict(state),
    )
    return replace(job, checkpoints=job.checkpoints + (checkpoint,))


def _close_current_attempt(
    job: DurableJob, *, completed_at: str, status: str, error_code: str = ""
) -> tuple[JobAttempt, ...]:
    if not job.attempts:
        return job.attempts
    current = job.attempts[-1]
    closed = replace(
        current,
        completed_at=completed_at,
        status=status,
        error_code=error_code,
    )
    return job.attempts[:-1] + (closed,)


def complete_job(
    job: DurableJob,
    *,
    worker_id: str,
    generation: int,
    completed_at: str,
    result_digest: str,
) -> DurableJob:
    _require_active_lease(job, worker_id=worker_id, generation=generation)
    assert_job_transition(job.status, "completed")
    return replace(
        job,
        status="completed",
        lease=None,
        attempts=_close_current_attempt(job, completed_at=completed_at, status="completed"),
        result_digest=result_digest,
        failure_code="",
    )

def fail_job(
    job: DurableJob,
    *,
    worker_id: str,
    generation: int,
    completed_at: str,
    error_code: str,
) -> DurableJob:
    _require_active_lease(job, worker_id=worker_id, generation=generation)
    if job.status != "running":
        raise DurableJobError("only running jobs may fail")
    attempts = _close_current_attempt(
        job, completed_at=completed_at, status="failed", error_code=error_code
    )
    if len(attempts) >= job.retry_policy.max_attempts:
        return replace(
            job,
            status="failed",
            lease=None,
            attempts=attempts,
            failure_code=error_code,
        )
    return replace(
        job,
        status="queued",
        lease=None,
        attempts=attempts,
        failure_code=error_code,
    )

def timeout_job(
    job: DurableJob,
    *,
    worker_id: str,
    generation: int,
    timed_out_at: str,
) -> DurableJob:
    _require_active_lease(job, worker_id=worker_id, generation=generation)
    if job.status not in {"leased", "running"}:
        raise DurableJobError("only leased or running jobs may time out")
    attempts = _close_current_attempt(
        job, completed_at=timed_out_at, status="timed_out", error_code="timeout"
    )
    if len(attempts) >= job.retry_policy.max_attempts:
        return replace(
            job,
            status="timed_out",
            lease=None,
            attempts=attempts,
            failure_code="timeout",
        )
    return replace(
        job,
        status="queued",
        lease=None,
        attempts=attempts,
        failure_code="timeout",
    )


def recover_orphan(job: DurableJob, *, observed_at: str) -> DurableJob:
    if job.status not in {"leased", "running", "paused"}:
        return job
    if job.terminal:
        return job
    return replace(job, status="queued", lease=None)

def append_audit_event(
    job: DurableJob,
    *,
    event_type: str,
    recorded_at: str,
) -> DurableJob:
    from .durable_jobs import JobAuditEvent

    sequence = len(job.audit_events) + 1
    previous = job.audit_events[-1].event_digest if job.audit_events else ""
    material = "|".join(
        (job.job_id, str(sequence), event_type, recorded_at, job.correlation_id, previous)
    )
    digest = sha256(material.encode("utf-8")).hexdigest()
    event = JobAuditEvent(
        event_id=f"job-audit-{digest[:16]}",
        sequence=sequence,
        event_type=event_type,
        recorded_at=recorded_at,
        correlation_id=job.correlation_id,
        previous_digest=previous,
        event_digest=digest,
    )
    return replace(job, audit_events=job.audit_events + (event,))
