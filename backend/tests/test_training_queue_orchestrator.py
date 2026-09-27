from backend.platform.training_jobs import TrainingJobSpec
from backend.training_job_registry import TrainingJobRegistry
from backend.training_queue_orchestrator import TrainingQueueOrchestrator
from backend.worker_registry import WorkerRegistry


def _setup(tmp_path):
    jobs = TrainingJobRegistry(tmp_path / "jobs")
    workers = WorkerRegistry(tmp_path / "workers", offline_after_seconds=90)
    jobs.submit(
        TrainingJobSpec(
            job_id="train-resume-001", model_ref="model:qwen",
            dataset_ref="dataset:cad-v1", requested_accelerator="cuda",
            requested_vram_mb=12000,
        ),
        idempotency_key="idem-resume-001",
        correlation_id="corr-resume-001", created_at="t0",
    )
    return jobs, workers, TrainingQueueOrchestrator(jobs, workers)


def test_offline_worker_keeps_queue_waiting(tmp_path):
    jobs, workers, orchestrator = _setup(tmp_path)
    workers.heartbeat(
        worker_id="rtx", role="ai_factory_gpu_worker",
        observed_at="2026-09-27T02:00:00+00:00",
        accelerator="cuda", vram_mb=16303,
    )
    result = orchestrator.reconcile_job(
        job_id="train-resume-001",
        observed_at="2026-09-27T02:02:00+00:00",
        acquired_at="t1", expires_at="t2",
    )
    assert result.status == "queued"
    assert result.worker_id is None
    assert result.reason == "no_online_workers"
    assert jobs.get(result.job_id).status == "queued"


def test_fresh_reconnect_automatically_leases_queued_job(tmp_path):
    jobs, workers, orchestrator = _setup(tmp_path)
    workers.heartbeat(
        worker_id="rtx", role="ai_factory_gpu_worker",
        observed_at="2026-09-27T02:02:01+00:00",
        accelerator="cuda", device_name="NVIDIA GeForce RTX 5080",
        vram_mb=16303,
    )
    result = orchestrator.reconcile_job(
        job_id="train-resume-001",
        observed_at="2026-09-27T02:02:02+00:00",
        acquired_at="t1", expires_at="t2",
    )
    assert result.status == "leased"
    assert result.worker_id == "rtx"
    restored = TrainingJobRegistry(tmp_path / "jobs").get(result.job_id)
    assert restored.lease.worker_id == "rtx"


def test_reconnect_with_insufficient_vram_keeps_job_queued(tmp_path):
    jobs, workers, orchestrator = _setup(tmp_path)
    workers.heartbeat(
        worker_id="small", role="ai_factory_gpu_worker",
        observed_at="2026-09-27T02:02:01+00:00",
        accelerator="cuda", vram_mb=8000,
    )
    result = orchestrator.reconcile_job(
        job_id="train-resume-001",
        observed_at="2026-09-27T02:02:02+00:00",
        acquired_at="t1", expires_at="t2",
    )
    assert result.status == "queued"
    assert result.reason == "insufficient_vram"


def test_queue_reconciliation_is_deterministic(tmp_path):
    jobs = TrainingJobRegistry(tmp_path / "jobs")
    workers = WorkerRegistry(tmp_path / "workers")
    for job_id in ("train-b", "train-a"):
        jobs.submit(
            TrainingJobSpec(
                job_id=job_id, model_ref="model:qwen",
                dataset_ref="dataset:cad-v1", requested_accelerator="cuda",
                requested_vram_mb=12000,
            ),
            idempotency_key=f"idem-{job_id}",
            correlation_id=f"corr-{job_id}", created_at="t0",
        )
    orchestrator = TrainingQueueOrchestrator(jobs, workers)
    results = orchestrator.reconcile_queue(
        job_ids=("train-b", "train-a"),
        observed_at="2026-09-27T02:02:02+00:00",
        acquired_at="t1", expires_at="t2",
    )
    assert [item.job_id for item in results] == ["train-a", "train-b"]
    assert all(item.status == "queued" for item in results)
