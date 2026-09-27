import pytest

from backend.platform.durable_jobs import DurableJobError
from backend.platform.training_jobs import TrainingJobSpec
from backend.training_dispatch_coordinator import TrainingDispatchCoordinator
from backend.training_job_registry import TrainingJobRegistry
from backend.worker_registry import WorkerRecord


def _spec():
    return TrainingJobSpec(
        job_id="train-lease-001", model_ref="model:qwen",
        dataset_ref="dataset:cad-v1", requested_accelerator="cuda",
        requested_vram_mb=12000,
    )


def _worker(state="online"):
    return WorkerRecord(
        worker_id="fc-rtx-test", role="ai_factory_gpu_worker",
        last_heartbeat_at="2026-09-27T02:00:00+00:00",
        state=state, accelerator="cuda",
        device_name="NVIDIA GeForce RTX 5080", vram_mb=16303,
    )


def _coordinator(tmp_path):
    registry = TrainingJobRegistry(tmp_path)
    registry.submit(
        _spec(), idempotency_key="idem-lease-001",
        correlation_id="corr-lease-001", created_at="t0",
    )
    return registry, TrainingDispatchCoordinator(registry)


def test_offline_worker_keeps_job_durably_queued(tmp_path):
    registry, coordinator = _coordinator(tmp_path)
    decision, job = coordinator.assign(
        spec=_spec(), workers=(_worker("offline"),),
        acquired_at="t1", expires_at="t2",
    )
    assert decision.eligible is False
    assert job.status == "queued"
    assert TrainingJobRegistry(tmp_path).get(job.job_id).status == "queued"


def test_assignment_is_persisted_as_lease(tmp_path):
    registry, coordinator = _coordinator(tmp_path)
    decision, job = coordinator.assign(
        spec=_spec(), workers=(_worker(),),
        acquired_at="t1", expires_at="t2",
    )
    assert decision.worker_id == "fc-rtx-test"
    assert job.status == "leased"
    restored = TrainingJobRegistry(tmp_path).get(job.job_id)
    assert restored.lease.worker_id == "fc-rtx-test"
    assert restored.lease_generation == 1


def test_assigned_worker_can_start_and_restart_preserves_running(tmp_path):
    registry, coordinator = _coordinator(tmp_path)
    _, leased = coordinator.assign(
        spec=_spec(), workers=(_worker(),),
        acquired_at="t1", expires_at="t2",
    )
    running = coordinator.start(
        job_id=leased.job_id, worker_id="fc-rtx-test", started_at="t1",
    )
    assert running.status == "running"
    assert TrainingJobRegistry(tmp_path).get(running.job_id).status == "running"


def test_wrong_worker_is_fenced_from_start(tmp_path):
    _, coordinator = _coordinator(tmp_path)
    _, leased = coordinator.assign(
        spec=_spec(), workers=(_worker(),),
        acquired_at="t1", expires_at="t2",
    )
    with pytest.raises(DurableJobError):
        coordinator.start(job_id=leased.job_id, worker_id="other", started_at="t1")


def test_disconnected_leased_worker_requeues_job(tmp_path):
    _, coordinator = _coordinator(tmp_path)
    _, leased = coordinator.assign(
        spec=_spec(), workers=(_worker(),),
        acquired_at="t1", expires_at="t2",
    )
    recovered = coordinator.recover_disconnected(job_id=leased.job_id, observed_at="t3")
    assert recovered.status == "queued"
    assert recovered.lease is None


def test_disconnected_running_worker_recovers_orphan(tmp_path):
    _, coordinator = _coordinator(tmp_path)
    _, leased = coordinator.assign(
        spec=_spec(), workers=(_worker(),),
        acquired_at="t1", expires_at="t2",
    )
    running = coordinator.start(
        job_id=leased.job_id, worker_id="fc-rtx-test", started_at="t1",
    )
    recovered = coordinator.recover_disconnected(job_id=running.job_id, observed_at="t3")
    assert recovered.status == "queued"
    assert recovered.lease is None
