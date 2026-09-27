from backend.platform.training_jobs import TrainingJobSpec
from backend.training_dispatcher import select_worker, worker_matches
from backend.worker_registry import WorkerRecord


def _spec(vram=12000):
    return TrainingJobSpec(
        job_id="train-dispatch-1", model_ref="model:qwen",
        dataset_ref="dataset:cad-v1", requested_accelerator="cuda",
        requested_vram_mb=vram,
    )


def _worker(worker_id="rtx", state="online", accelerator="cuda", vram=16303):
    return WorkerRecord(
        worker_id=worker_id, role="ai_factory_gpu_worker",
        last_heartbeat_at="2026-09-27T02:00:00+00:00",
        state=state, accelerator=accelerator,
        device_name="NVIDIA GeForce RTX 5080", vram_mb=vram,
    )


def test_offline_worker_leaves_job_unassigned():
    decision = select_worker(_spec(), [_worker(state="offline")])
    assert decision.eligible is False
    assert decision.worker_id is None
    assert decision.reason == "no_online_workers"


def test_cuda_worker_with_enough_vram_matches():
    assert worker_matches(_spec(), _worker()) is True
    decision = select_worker(_spec(), [_worker()])
    assert decision.eligible is True
    assert decision.worker_id == "rtx"


def test_wrong_accelerator_is_rejected():
    decision = select_worker(_spec(), [_worker(accelerator="cpu")])
    assert decision.reason == "no_compatible_accelerator"


def test_insufficient_vram_is_rejected():
    decision = select_worker(_spec(vram=16000), [_worker(vram=12000)])
    assert decision.reason == "insufficient_vram"


def test_best_capable_worker_is_deterministic():
    workers = [
        _worker("worker-b", vram=16000),
        _worker("worker-a", vram=16000),
        _worker("worker-c", vram=24000),
    ]
    assert select_worker(_spec(), workers).worker_id == "worker-c"


def test_equal_capacity_tiebreaks_by_worker_id():
    workers = [_worker("worker-b"), _worker("worker-a")]
    assert select_worker(_spec(), workers).worker_id == "worker-a"
