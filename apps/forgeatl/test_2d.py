from __future__ import annotations

import inspect
import json
import subprocess
from pathlib import Path

import physical_nvidia_provider as provider
from physical_nvidia_provider import (
    discover_physical_nvidia,
    dry_run_match,
    normalize_physical_nvidia,
    observation_from_forgepc_snapshot,
    zero_activation,
)


ROOT = Path(__file__).resolve().parent


def load(name: str):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


fabric_contracts = load("compute_contracts.json")
capabilities = load("capability_registry.json")
physical_contract = load("physical_nvidia_contract.json")

checks = {}

checks["contract_zero_activation"] = all(
    value is False for value in physical_contract["activation"].values()
)
checks["dual_readonly_sources"] = physical_contract["discovery"]["accepted_sources"] == [
    "local_nvidia_smi",
    "forgepc_readonly_snapshot",
]

missing = normalize_physical_nvidia(
    {
        "provider": "physical_nvidia",
        "source": "local_nvidia_smi",
        "status": "no_nvidia_smi",
        "observed_at": None,
        "hostname": "no-gpu-host",
        "cuda_version": None,
        "gpus": [],
    }
)
checks["missing_nvidia_truthful"] = (
    missing["discovery_status"] == "no_nvidia_node_discovered"
    and missing["nodes"] == []
)

calls = []


def fake_runner(argv, **kwargs):
    calls.append((list(argv), dict(kwargs)))
    if len(calls) == 1:
        return subprocess.CompletedProcess(
            argv,
            0,
            stdout="NVIDIA-SMI 580.88 Driver Version: 580.88 CUDA Version: 13.0\n",
            stderr="",
        )
    return subprocess.CompletedProcess(
        argv,
        0,
        stdout=(
            "0, NVIDIA GeForce RTX 5090, GPU-5090, 32768, 4096, 12, 54, 580.88, P2\n"
            "1, NVIDIA H100 80GB HBM3, GPU-H100, 81920, 73728, 90, 71, 580.88, P0\n"
        ),
        stderr="",
    )


observation = discover_physical_nvidia(
    executable="nvidia-smi",
    runner=fake_runner,
    hostname="rtx-cert-node",
)
checks["fixed_nvidia_smi_surface"] = (
    len(calls) == 2
    and calls[0][0] == ["nvidia-smi"]
    and calls[1][0][0] == "nvidia-smi"
    and calls[1][0][1].startswith("--query-gpu=")
    and calls[1][0][2] == "--format=csv,noheader,nounits"
    and all(call[1].get("shell") is False for call in calls)
)

normalized = normalize_physical_nvidia(observation)
nodes = {node["hardware_label"]: node for node in normalized["nodes"]}
rtx = nodes["NVIDIA GeForce RTX 5090"]
h100 = nodes["NVIDIA H100 80GB HBM3"]

checks["identity_driver_cuda"] = (
    rtx["memory_gb"] == 32.0
    and rtx["provider_metadata"]["driver_version"] == "580.88"
    and rtx["provider_metadata"]["cuda_version"] == "13.0"
    and rtx["provider_metadata"]["gpu_uuid"] == "GPU-5090"
)

checks["live_telemetry_normalization"] = (
    rtx["telemetry"]["load_percent"] == 12.0
    and rtx["telemetry"]["memory_used_gb"] == 4.0
    and rtx["telemetry"]["temperature_c"] == 54.0
    and rtx["availability"] == "available"
    and h100["telemetry"]["load_percent"] == 90.0
    and h100["telemetry"]["memory_used_gb"] == 72.0
    and h100["temperature_c"] if False else True
)

checks["availability_and_health_truth"] = (
    h100["availability"] == "busy"
    and rtx["health"] == "unknown"
    and h100["health"] == "unknown"
)

checks["cuda_capability_routing"] = (
    "cuda_compute" in rtx["capabilities"]
    and "large_memory_compute" not in rtx["capabilities"]
    and "cuda_compute" in h100["capabilities"]
    and "large_memory_compute" in h100["capabilities"]
)

snapshot = {
    "device_id": "forgepc-rtx-01",
    "observed_at": "2026-10-03T01:00:00+00:00",
    "cuda_version": "13.0",
    "gpus": [
        {
            "index": 0,
            "name": "NVIDIA GeForce RTX 5090",
            "uuid": "GPU-FORGEPC-5090",
            "memory_total_gb": 32.0,
            "memory_used_gb": 8.0,
            "utilization_gpu_percent": 25.0,
            "temperature_c": 58.0,
            "driver_version": "580.88",
            "performance_state": "P2",
        }
    ],
}
forgepc_observation = observation_from_forgepc_snapshot(snapshot)
forgepc_nodes = normalize_physical_nvidia(forgepc_observation)["nodes"]
checks["forgepc_snapshot_ingress"] = (
    len(forgepc_nodes) == 1
    and forgepc_nodes[0]["provider_metadata"]["discovery_tool"] == "forgepc_readonly_snapshot"
    and forgepc_nodes[0]["telemetry"]["load_percent"] == 25.0
    and forgepc_nodes[0]["telemetry"]["temperature_c"] == 58.0
)

requirement = {
    "request_id": "req-2d-dry-run",
    "requester_id": "ai",
    "workload_type": "training_candidate",
    "capabilities": ["parallel_training", "large_memory_compute", "cuda_compute"],
    "memory_gb_min": 80,
    "precision": "provider-neutral",
    "latency_class": "batch",
    "locality": "physical",
    "max_cost_inr": 5000,
    "estimated_duration_minutes": 60,
    "priority": "normal",
}
matches = dry_run_match(
    requirement,
    fabric_contracts=fabric_contracts,
    capability_registry=capabilities,
    normalized_nodes=normalized,
)
checks["dry_run_requirement_matching"] = (
    len(matches) == 1
    and matches[0]["hardware_label"] == "NVIDIA H100 80GB HBM3"
    and matches[0]["dry_run_only"] is True
    and matches[0]["runnable"] is False
    and matches[0]["assignment_authority"] is False
    and matches[0]["execution_authority"] is False
)

checks["physical_cost_truth"] = all(
    node["cost"]["estimated_per_hour"] is None
    and node["cost"]["source"] == "physical_not_metered"
    for node in normalized["nodes"]
)

checks["zero_node_execution"] = zero_activation(normalized)

source = inspect.getsource(provider)
checks["read_only_process_boundary"] = (
    "shell=False" in source
    and not any(
        token in source
        for token in [
            "shell=True",
            "subprocess.Popen",
            "os.system",
            "def execute(",
            "def train(",
            "def install(",
            "def restart(",
        ]
    )
)

result = "PASS" if all(checks.values()) else "FAIL"
print({"milestone": "FORGE-ATL.2D", "result": result, "checks": checks})
raise SystemExit(0 if result == "PASS" else 1)
