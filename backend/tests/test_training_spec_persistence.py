from dataclasses import replace

import pytest

from backend.platform.training_jobs import TrainingJobSpec
from backend.training_job_registry import TrainingJobRegistry


def _spec():
    return TrainingJobSpec(
        job_id="train-spec-001",
        model_ref="model:qwen3-vl:rev-7",
        dataset_ref="dataset:cad-d5:v3",
        requested_accelerator="cuda",
        requested_vram_mb=12000,
        priority=80,
    )


def _submit(registry):
    return registry.submit(
        _spec(), idempotency_key="idem-spec-001",
        correlation_id="corr-spec-001", created_at="t0",
    )


def test_full_training_spec_survives_restart(tmp_path):
    _submit(TrainingJobRegistry(tmp_path))
    restored = TrainingJobRegistry(tmp_path).get_spec("train-spec-001")
    assert restored == _spec()
    assert restored.model_ref == "model:qwen3-vl:rev-7"
    assert restored.dataset_ref == "dataset:cad-d5:v3"
    assert restored.requested_accelerator == "cuda"
    assert restored.requested_vram_mb == 12000
    assert restored.priority == 80


def test_spec_persistence_is_idempotent(tmp_path):
    first = TrainingJobRegistry(tmp_path)
    first_job = _submit(first)
    restarted = TrainingJobRegistry(tmp_path)
    second_job = _submit(restarted)
    assert second_job.job_id == first_job.job_id
    assert restarted.get_spec(first_job.job_id) == _spec()


def test_missing_spec_fails_closed(tmp_path):
    registry = TrainingJobRegistry(tmp_path)
    job = _submit(registry)
    registry._spec_path(job.job_id).unlink()
    with pytest.raises(ValueError, match="spec is missing"):
        TrainingJobRegistry(tmp_path).get_spec(job.job_id)


def test_tampered_spec_fails_integrity_check(tmp_path):
    registry = TrainingJobRegistry(tmp_path)
    job = _submit(registry)
    path = registry._spec_path(job.job_id)
    text = path.read_text(encoding="utf-8").replace(
        "dataset:cad-d5:v3", "dataset:tampered"
    )
    path.write_text(text, encoding="utf-8")
    with pytest.raises(ValueError, match="integrity mismatch"):
        TrainingJobRegistry(tmp_path).get_spec(job.job_id)
