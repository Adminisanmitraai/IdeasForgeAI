from backend.platform.training_jobs import (
    TRAINING_JOB_CONTRACT_VERSION,
    TrainingJobLifecycleError,
    TrainingJobSpec,
    assert_training_transition,
    can_wait_for_worker,
)


def test_training_spec_captures_dispatch_requirements():
    spec = TrainingJobSpec(
        job_id="train-001",
        model_ref="model:qwen",
        dataset_ref="dataset:cad-v1",
        requested_accelerator="cuda",
        requested_vram_mb=12000,
    )
    assert spec.contract_version == TRAINING_JOB_CONTRACT_VERSION
    assert spec.requested_vram_mb == 12000


def test_offline_worker_does_not_fail_queued_job():
    assert can_wait_for_worker("queued") is True


def test_training_lifecycle_happy_path():
    path = [
        ("queued", "assigned"),
        ("assigned", "running"),
        ("running", "checkpointing"),
        ("checkpointing", "running"),
        ("running", "evaluating"),
        ("evaluating", "completed"),
    ]
    for current, target in path:
        assert_training_transition(current, target)


def test_invalid_terminal_transition_is_rejected():
    try:
        assert_training_transition("completed", "running")
    except TrainingJobLifecycleError:
        return
    raise AssertionError("terminal training job was allowed to restart")
