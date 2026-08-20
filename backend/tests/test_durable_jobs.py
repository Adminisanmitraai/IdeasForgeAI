from dataclasses import replace

import pytest

from backend.durable_job_store import DurableJobConflictError, DurableJobStore
from backend.platform.durable_jobs import (
    DurableJob,
    DurableJobError,
    acquire_lease,
    assert_job_transition,
    release_expired_lease,
    start_attempt,
)


def _job() -> DurableJob:
    return DurableJob(
        job_id="job-1",
        idempotency_key="idem-1",
        correlation_id="corr-1",
        operation="inspect",
        payload_digest="abc",
        created_at="2026-08-19T15:45:00+05:30",
    )

def test_valid_and_invalid_job_transitions():
    assert_job_transition("queued", "leased")
    with pytest.raises(DurableJobError):
        assert_job_transition("queued", "completed")


def test_lease_owner_required_for_attempt():
    leased = acquire_lease(
        _job(), worker_id="worker-a", acquired_at="t1", expires_at="t2"
    )
    with pytest.raises(DurableJobError):
        start_attempt(leased, worker_id="worker-b", started_at="t1")
    running = start_attempt(leased, worker_id="worker-a", started_at="t1")
    assert running.status == "running"
    assert running.attempts[0].attempt_number == 1


def test_expired_lease_requeues_job():
    leased = acquire_lease(
        _job(), worker_id="worker-a", acquired_at="t1", expires_at="t2"
    )
    queued = release_expired_lease(leased)
    assert queued.status == "queued"
    assert queued.lease is None

def test_store_round_trip_and_idempotent_submit(tmp_path):
    store = DurableJobStore(tmp_path)
    first = store.submit(
        job_id="job-1", idempotency_key="idem-1", correlation_id="corr-1",
        operation="inspect", payload={"x": 1}, created_at="t1",
    )
    second = store.submit(
        job_id="job-2", idempotency_key="idem-1", correlation_id="corr-2",
        operation="inspect", payload={"x": 1}, created_at="t2",
    )
    assert second == first
    assert store.get(first.job_id) == first


def test_store_rejects_idempotency_collision(tmp_path):
    store = DurableJobStore(tmp_path)
    store.submit(
        job_id="job-1", idempotency_key="idem-1", correlation_id="corr-1",
        operation="inspect", payload={"x": 1}, created_at="t1",
    )
    with pytest.raises(DurableJobConflictError):
        store.submit(
            job_id="job-2", idempotency_key="idem-1", correlation_id="corr-2",
            operation="inspect", payload={"x": 2}, created_at="t2",
        )
