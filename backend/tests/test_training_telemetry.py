import pytest

from backend.training_telemetry import TrainingTelemetry, TrainingTelemetryStore


def _telemetry(**overrides):
    values = dict(
        job_id="train-progress-001",
        worker_id="fc-rtx-test",
        recorded_at="2026-09-27T02:30:00+00:00",
        epoch=2,
        step=450,
        total_steps=1000,
        progress_percent=45.0,
        loss=0.312,
        metrics={"learning_rate": 0.0001, "eval_loss": 0.355},
        checkpoint_id="checkpoint-450",
        checkpoint_ref="checkpoints/train-progress-001/450",
        gpu_utilization_percent=94.0,
        gpu_memory_used_mb=14200,
        gpu_memory_total_mb=16303,
    )
    values.update(overrides)
    return TrainingTelemetry(**values)


def test_training_progress_survives_restart(tmp_path):
    TrainingTelemetryStore(tmp_path).put(_telemetry())
    restored = TrainingTelemetryStore(tmp_path).get("train-progress-001")
    assert restored.progress_percent == 45.0
    assert restored.epoch == 2
    assert restored.step == 450
    assert restored.loss == 0.312


def test_gpu_telemetry_is_persisted(tmp_path):
    store = TrainingTelemetryStore(tmp_path)
    store.put(_telemetry())
    restored = store.get("train-progress-001")
    assert restored.gpu_utilization_percent == 94.0
    assert restored.gpu_memory_used_mb == 14200
    assert restored.gpu_memory_total_mb == 16303


def test_checkpoint_resume_projection_is_recoverable(tmp_path):
    store = TrainingTelemetryStore(tmp_path)
    store.put(_telemetry())
    resume = TrainingTelemetryStore(tmp_path).resume_checkpoint("train-progress-001")
    assert resume == {
        "checkpoint_id": "checkpoint-450",
        "checkpoint_ref": "checkpoints/train-progress-001/450",
        "epoch": 2,
        "step": 450,
        "progress_percent": 45.0,
    }


def test_no_checkpoint_returns_none(tmp_path):
    store = TrainingTelemetryStore(tmp_path)
    store.put(_telemetry(checkpoint_id="", checkpoint_ref=""))
    assert store.resume_checkpoint("train-progress-001") is None


@pytest.mark.parametrize("progress", [-0.1, 100.1])
def test_invalid_progress_fails_closed(progress):
    with pytest.raises(ValueError):
        _telemetry(progress_percent=progress)


def test_latest_telemetry_replaces_previous_snapshot_atomically(tmp_path):
    store = TrainingTelemetryStore(tmp_path)
    store.put(_telemetry(step=100, progress_percent=10.0))
    store.put(_telemetry(step=500, progress_percent=50.0, checkpoint_id="checkpoint-500"))
    restored = store.get("train-progress-001")
    assert restored.step == 500
    assert restored.progress_percent == 50.0
    assert restored.checkpoint_id == "checkpoint-500"
