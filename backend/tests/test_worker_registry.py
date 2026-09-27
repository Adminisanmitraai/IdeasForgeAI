from backend.worker_registry import WorkerRegistry


def test_heartbeat_registers_online_worker(tmp_path):
    registry = WorkerRegistry(tmp_path, offline_after_seconds=90)
    worker = registry.heartbeat(
        worker_id="fc-rtx-test",
        role="ai_factory_gpu_worker",
        observed_at="2026-09-27T02:00:00+00:00",
        accelerator="cuda",
        device_name="NVIDIA GeForce RTX 5080",
    )
    assert worker.state == "online"
    assert worker.accelerator == "cuda"


def test_worker_survives_registry_restart(tmp_path):
    first = WorkerRegistry(tmp_path)
    first.heartbeat(
        worker_id="fc-rtx-test", role="ai_factory_gpu_worker",
        observed_at="2026-09-27T02:00:00+00:00",
    )
    restarted = WorkerRegistry(tmp_path)
    assert restarted.get("fc-rtx-test").worker_id == "fc-rtx-test"


def test_stale_heartbeat_projects_worker_offline(tmp_path):
    registry = WorkerRegistry(tmp_path, offline_after_seconds=90)
    registry.heartbeat(
        worker_id="fc-rtx-test", role="ai_factory_gpu_worker",
        observed_at="2026-09-27T02:00:00+00:00",
    )
    projected = registry.get(
        "fc-rtx-test", observed_at="2026-09-27T02:01:31+00:00"
    )
    assert projected.state == "offline"


def test_recent_heartbeat_projects_worker_online(tmp_path):
    registry = WorkerRegistry(tmp_path, offline_after_seconds=90)
    registry.heartbeat(
        worker_id="fc-rtx-test", role="ai_factory_gpu_worker",
        observed_at="2026-09-27T02:00:00+00:00",
    )
    assert registry.get(
        "fc-rtx-test", observed_at="2026-09-27T02:01:30+00:00"
    ).state == "online"


def test_heartbeat_recovers_offline_worker(tmp_path):
    registry = WorkerRegistry(tmp_path, offline_after_seconds=90)
    registry.heartbeat(
        worker_id="fc-rtx-test", role="ai_factory_gpu_worker",
        observed_at="2026-09-27T02:00:00+00:00",
    )
    assert registry.get(
        "fc-rtx-test", observed_at="2026-09-27T02:02:00+00:00"
    ).state == "offline"
    recovered = registry.heartbeat(
        worker_id="fc-rtx-test", role="ai_factory_gpu_worker",
        observed_at="2026-09-27T02:02:01+00:00",
    )
    assert recovered.state == "online"


def test_list_is_deterministic(tmp_path):
    registry = WorkerRegistry(tmp_path)
    registry.heartbeat(worker_id="worker-b", role="gpu", observed_at="2026-09-27T02:00:00+00:00")
    registry.heartbeat(worker_id="worker-a", role="gpu", observed_at="2026-09-27T02:00:00+00:00")
    assert [item.worker_id for item in registry.list()] == ["worker-a", "worker-b"]
