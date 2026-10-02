from __future__ import annotations

import inspect
import json
from pathlib import Path

import runpod_account_inventory as account
from runpod_account_inventory import (
    account_health_snapshot,
    dry_run_existing_pod_match,
    fetch_all_account_pods,
    merge_compute_fabric,
    normalize_account_inventory,
    zero_activation,
)
from runpod_provider import normalize_gpu_catalog


ROOT = Path(__file__).resolve().parent


def load(name: str):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


fabric_contracts = load("compute_contracts.json")
capabilities = load("capability_registry.json")
account_contract = load("cloud_account_contract.json")

catalog_observation = {
    "provider": "runpod",
    "observed_at": "2026-10-02T18:00:00+00:00",
    "provider_health": "healthy",
    "gpu_types": [
        {
            "id": "NVIDIA H100 80GB HBM3",
            "displayName": "H100 SXM",
            "memoryInGb": 80,
            "secureCloud": True,
            "communityCloud": True,
            "lowestPrice": {
                "stockStatus": "Medium",
                "uninterruptablePrice": 2.69,
                "minimumBidPrice": 2.69,
                "availableGpuCounts": [1],
            },
        },
        {
            "id": "NVIDIA GeForce RTX 4090",
            "displayName": "RTX 4090",
            "memoryInGb": 24,
            "secureCloud": True,
            "communityCloud": True,
            "lowestPrice": {
                "stockStatus": "Low",
                "uninterruptablePrice": 0.34,
                "minimumBidPrice": 0.34,
                "availableGpuCounts": [1],
            },
        },
    ],
}
catalog = normalize_gpu_catalog(catalog_observation)

pod_h100 = {
    "id": "pod_h100",
    "name": "research-h100",
    "status": "RUNNING",
    "actions": ["STOP", "RESET"],
    "gpu": {"id": "NVIDIA H100 80GB HBM3", "count": 1, "vcpuCount": 16, "memory": 188},
    "cloud": "SECURE",
    "dataCenterId": "US-TX-3",
    "cudaVersion": "12.8",
    "cost": 2.69,
    "runtime": {
        "uptime": 3600,
        "gpus": [{"util": 72, "memoryUtil": 64}],
        "cpu": {"util": 31},
        "memory": {"util": 41},
        "ports": [],
    },
    "createdAt": "2026-10-02T16:00:00Z",
    "startedAt": "2026-10-02T17:00:00Z",
}
pod_4090 = {
    "id": "pod_4090",
    "name": "stopped-4090",
    "status": "EXITED",
    "actions": ["START", "TERMINATE"],
    "gpu": {"id": "NVIDIA GeForce RTX 4090", "count": 1, "vcpuCount": 8, "memory": 62},
    "cloud": "COMMUNITY",
    "dataCenterId": "EU-RO-1",
    "cudaVersion": "12.6",
    "cost": 0.0,
    "runtime": None,
    "createdAt": "2026-09-30T16:00:00Z",
    "startedAt": None,
}
cpu_pod = {
    "id": "cpu_only",
    "name": "cpu-only",
    "status": "RUNNING",
    "cpu": {"id": "cpu", "count": 1},
    "cloud": "SECURE",
    "cost": 0.2,
    "runtime": {"uptime": 50},
}

sample_inventory = {
    "provider": "runpod",
    "status": "read_only_inventory",
    "credential": {
        "environment_variable": "RUNPOD_API_KEY",
        "present": True,
        "value_exposed": False,
        "persistence": "environment_only",
    },
    "observed_at": "2026-10-02T18:01:00+00:00",
    "pages": 1,
    "pods": [pod_h100, pod_4090, cpu_pod],
}

checks = {}

checks["contract_zero_activation"] = all(
    value is False for value in account_contract["activation"].values()
)

missing = fetch_all_account_pods({})
checks["missing_credential_fail_closed"] = (
    missing["status"] == "skipped_no_credential"
    and missing["pods"] == []
    and missing["pages"] == 0
)

secret = "private-runpod-key-for-test"
calls = []
pages = [
    {
        "pods": [pod_h100],
        "pagination": {"hasNextPage": True, "nextCursor": "cursor-2"},
    },
    {
        "pods": [pod_4090],
        "pagination": {"hasNextPage": False, "nextCursor": None},
    },
]
original_request = account._request_json


def fake_request_json(**kwargs):
    calls.append(kwargs)
    return pages[len(calls) - 1]


account._request_json = fake_request_json
try:
    paged = fetch_all_account_pods({"RUNPOD_API_KEY": secret})
finally:
    account._request_json = original_request

checks["pagination_and_secret_boundary"] = (
    paged["status"] == "read_only_inventory"
    and paged["pages"] == 2
    and len(paged["pods"]) == 2
    and paged["credential"]["value_exposed"] is False
    and secret not in json.dumps(paged)
    and len(calls) == 2
    and calls[0]["method"] == "GET"
    and "cursor-2" in calls[1]["url"]
    and calls[0]["headers"]["Authorization"] == f"Bearer {secret}"
)

normalized = normalize_account_inventory(sample_inventory, catalog)
nodes = normalized["nodes"]
by_id = {node["node_id"]: node for node in nodes}
h100 = by_id["runpod-pod::pod_h100"]
rtx4090 = by_id["runpod-pod::pod_4090"]

checks["gpu_only_account_normalization"] = (
    normalized["inventory_status"] == "read_only_inventory"
    and len(nodes) == 2
    and "runpod-pod::cpu_only" not in by_id
)

checks["per_gpu_vram_semantics"] = (
    h100["memory_gb"] == 80
    and h100["provider_metadata"]["vram_gb_per_gpu"] == 80
    and h100["provider_metadata"]["aggregate_vram_gb"] == 80
    and rtx4090["memory_gb"] == 24
)

checks["runtime_health_projection"] = (
    h100["availability"] == "busy"
    and h100["health"] == "healthy"
    and h100["telemetry"]["load_percent"] == 72.0
    and h100["provider_metadata"]["runtime_gpu_memory_util_percent"] == 64.0
    and h100["provider_metadata"]["uptime_seconds"] == 3600
    and h100["telemetry"]["memory_used_gb"] is None
    and h100["telemetry"]["temperature_c"] is None
    and rtx4090["availability"] == "declared"
    and rtx4090["health"] == "unknown"
    and rtx4090["telemetry"]["load_percent"] is None
)

checks["account_cost_binding"] = (
    h100["cost"]["currency"] == "USD"
    and h100["cost"]["unit"] == "pod_hour"
    and h100["cost"]["estimated_per_hour"] == 2.69
    and rtx4090["cost"]["estimated_per_hour"] == 0.0
)

checks["execution_disabled"] = zero_activation(normalized) and all(
    node["execution_enabled"] is False for node in nodes
)

merged = merge_compute_fabric(catalog, normalized)
checks["compute_fabric_merge"] = (
    merged["sources"] == ["live_catalog", "account_inventory"]
    and len(merged["nodes"]) == len(catalog["nodes"]) + len(nodes)
    and len({node["node_id"] for node in merged["nodes"]}) == len(merged["nodes"])
)

requirement = {
    "request_id": "req-2c-existing-pod",
    "requester_id": "science",
    "workload_type": "research_training_candidate",
    "capabilities": ["parallel_training", "large_memory_compute", "cuda_compute"],
    "memory_gb_min": 80,
    "precision": "provider-neutral",
    "latency_class": "batch",
    "locality": "cloud",
    "max_cost_inr": 5000,
    "estimated_duration_minutes": 60,
    "priority": "normal",
}
matches = dry_run_existing_pod_match(
    requirement,
    fabric_contracts=fabric_contracts,
    capability_registry=capabilities,
    normalized_account=normalized,
)
checks["dry_run_existing_resource_match"] = (
    len(matches) == 1
    and matches[0]["node_id"] == "runpod-pod::pod_h100"
    and matches[0]["existing_account_resource"] is True
    and matches[0]["dry_run_only"] is True
    and matches[0]["runnable"] is False
    and matches[0]["assignment_authority"] is False
    and matches[0]["execution_authority"] is False
)

health = account_health_snapshot(normalized)
checks["health_summary"] = (
    health["pod_nodes"] == 2
    and health["status_counts"] == {"RUNNING": 1, "EXITED": 1}
    and health["observed_gpu_load_nodes"] == 1
    and health["temperature_observed_nodes"] == 0
    and health["execution_authority"] is False
)

source = inspect.getsource(account)
checks["read_only_surface"] = (
    'method="GET"' in source
    and not any(
        token in source
        for token in [
            'method="POST"',
            'method="PUT"',
            'method="PATCH"',
            'method="DELETE"',
            "def create(",
            "def start(",
            "def stop(",
            "def restart(",
            "def delete(",
            "def execute(",
            "def train(",
        ]
    )
)

contract_text = json.dumps(account_contract)
checks["no_secret_persistence"] = (
    secret not in contract_text
    and account_contract["credential_boundary"]["persist_in_repository"] is False
    and account_contract["credential_boundary"]["emit_value"] is False
)

result = "PASS" if all(checks.values()) else "FAIL"
print({"milestone": "FORGE-ATL.2C", "result": result, "checks": checks})
raise SystemExit(0 if result == "PASS" else 1)
