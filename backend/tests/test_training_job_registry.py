from backend.training_job_registry import TRAINING_OPERATION, TrainingJobRegistry
from backend.platform.training_jobs import TrainingJobSpec


def _spec() -> TrainingJobSpec:
    return TrainingJobSpec(
        job_id="train-persist-001",
        model_ref="model:qwen",
        dataset_ref="dataset:cad-v1",
        requested_accelerator="cuda",
        requested_vram_mb=12000,
    )


def test_training_job_survives_registry_restart(tmp_path):
    registry = TrainingJobRegistry(tmp_path)
    created = registry.submit(
        _spec(),
        idempotency_key="train-idem-001",
        correlation_id="train-corr-001",
        created_at="t0",
    )
    assert created.status == "queued"
    assert created.operation == TRAINING_OPERATION

    restarted = TrainingJobRegistry(tmp_path)
    restored = restarted.get(created.job_id)
    assert restored == created
    assert restored.status == "queued"


def test_offline_worker_keeps_training_job_queued_after_restart(tmp_path):
    registry = TrainingJobRegistry(tmp_path)
    created = registry.submit(
        _spec(),
        idempotency_key="train-idem-offline",
        correlation_id="train-corr-offline",
        created_at="t0",
    )
    restarted = TrainingJobRegistry(tmp_path)
    assert restarted.get(created.job_id).status == "queued"


def test_training_submit_is_idempotent(tmp_path):
    registry = TrainingJobRegistry(tmp_path)
    first = registry.submit(
        _spec(),
        idempotency_key="train-idem-repeat",
        correlation_id="train-corr-repeat",
        created_at="t0",
    )
    second = registry.submit(
        _spec(),
        idempotency_key="train-idem-repeat",
        correlation_id="train-corr-repeat",
        created_at="t1",
    )
    assert second.job_id == first.job_id
    assert second.payload_digest == first.payload_digest
