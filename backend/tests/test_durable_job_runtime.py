import pytest

from backend.platform.durable_jobs import DurableJob, RetryPolicy, acquire_lease, start_attempt
from backend.platform.durable_job_runtime import (
    DurableJobFenceError,
    cancel_job,
    complete_job,
    fail_job,
    pause_job,
    record_checkpoint,
    recover_orphan,
    resume_job,
    timeout_job,
)


def _job(max_attempts: int = 3) -> DurableJob:
    return DurableJob(
        job_id="job-runtime-1",
        idempotency_key="idem-runtime-1",
        correlation_id="corr-runtime-1",
        operation="inspect",
        payload_digest="abc",
        created_at="t0",
        retry_policy=RetryPolicy(max_attempts=max_attempts),
    )

def test_lease_fencing_rejects_stale_generation():
    first = acquire_lease(_job(), worker_id="worker-a", acquired_at="t1", expires_at="t2")
    with pytest.raises(DurableJobFenceError):
        pause_job(first, worker_id="worker-a", generation=first.lease_generation + 1)


def test_pause_resume_advances_lease_generation():
    first = acquire_lease(_job(), worker_id="worker-a", acquired_at="t1", expires_at="t2")
    running = start_attempt(first, worker_id="worker-a", started_at="t1")
    paused = pause_job(running, worker_id="worker-a", generation=first.lease_generation)
    resumed = resume_job(paused, worker_id="worker-b", acquired_at="t3", expires_at="t4")
    assert resumed.status == "leased"
    assert resumed.lease is not None
    assert resumed.lease.worker_id == "worker-b"
    assert resumed.lease_generation == first.lease_generation + 1


def test_checkpoint_requires_current_lease():
    leased = acquire_lease(_job(), worker_id="worker-a", acquired_at="t1", expires_at="t2")
    checkpointed = record_checkpoint(
        leased, worker_id="worker-a", generation=leased.lease_generation,
        recorded_at="t1", state={"cursor": 4},
    )
    assert checkpointed.checkpoints[0].sequence == 1

def test_failure_requeues_until_retry_exhaustion():
    leased = acquire_lease(_job(max_attempts=2), worker_id="worker-a", acquired_at="t1", expires_at="t2")
    running = start_attempt(leased, worker_id="worker-a", started_at="t1")
    retry = fail_job(
        running, worker_id="worker-a", generation=running.lease_generation,
        completed_at="t2", error_code="boom",
    )
    assert retry.status == "queued"
    second_lease = acquire_lease(retry, worker_id="worker-b", acquired_at="t3", expires_at="t4")
    second = start_attempt(second_lease, worker_id="worker-b", started_at="t3")
    terminal = fail_job(
        second, worker_id="worker-b", generation=second.lease_generation,
        completed_at="t4", error_code="boom",
    )
    assert terminal.status == "failed"
    assert terminal.terminal is True


def test_timeout_retries_then_terminal():
    leased = acquire_lease(_job(max_attempts=1), worker_id="worker-a", acquired_at="t1", expires_at="t2")
    running = start_attempt(leased, worker_id="worker-a", started_at="t1")
    timed_out = timeout_job(
        running, worker_id="worker-a", generation=running.lease_generation,
        timed_out_at="t2",
    )
    assert timed_out.status == "timed_out"
    assert timed_out.failure_code == "timeout"

def test_cancel_and_orphan_recovery():
    leased = acquire_lease(_job(), worker_id="worker-a", acquired_at="t1", expires_at="t2")
    cancelled = cancel_job(leased)
    assert cancelled.status == "cancelled"
    assert cancelled.lease is None

    leased2 = acquire_lease(_job(), worker_id="worker-a", acquired_at="t1", expires_at="t2")
    running = start_attempt(leased2, worker_id="worker-a", started_at="t1")
    recovered = recover_orphan(running, observed_at="t3")
    assert recovered.status == "queued"
    assert recovered.lease is None


def test_completion_is_fenced_and_terminal():
    leased = acquire_lease(_job(), worker_id="worker-a", acquired_at="t1", expires_at="t2")
    running = start_attempt(leased, worker_id="worker-a", started_at="t1")
    completed = complete_job(
        running, worker_id="worker-a", generation=running.lease_generation,
        completed_at="t2", result_digest="result-123",
    )
    assert completed.status == "completed"
    assert completed.result_digest == "result-123"
    assert completed.attempts[-1].status == "completed"

def test_audit_lineage_survives_store_restart(tmp_path):
    from backend.durable_job_store import DurableJobStore
    from backend.platform.durable_job_runtime import append_audit_event

    store = DurableJobStore(tmp_path)
    job = store.submit(
        job_id="job-audit-1", idempotency_key="idem-audit-1",
        correlation_id="corr-audit-1", operation="inspect",
        payload={"x": 1}, created_at="t0",
    )
    job = append_audit_event(job, event_type="submitted", recorded_at="t0")
    job = append_audit_event(job, event_type="leased", recorded_at="t1")
    store.replace(job)

    restarted = DurableJobStore(tmp_path)
    restored = restarted.get(job.job_id)
    assert len(restored.audit_events) == 2
    assert restored.audit_events[1].previous_digest == restored.audit_events[0].event_digest
    assert restored.audit_events[0].correlation_id == "corr-audit-1"
