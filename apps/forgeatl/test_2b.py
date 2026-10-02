from __future__ import annotations

import inspect
import json
from pathlib import Path

import runpod_provider
from runpod_provider import (
    credential_state,
    dry_run_match,
    fetch_account_pods,
    normalize_gpu_catalog,
    zero_activation,
)


ROOT = Path(__file__).resolve().parent


def load(name: str):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


fabric_contracts = load("compute_contracts.json")
capabilities = load("capability_registry.json")
provider_contract = load("cloud_provider_contract.json")

sample_observation = {
    "provider": "runpod",
    "observed_at": "2026-10-02T17:00:00+00:00",
    "provider_health": "healthy",
    "credential_required": False,
    "gpu_types": [
        {
            "id": "NVIDIA H100 80GB HBM3",
            "displayName": "H100 SXM",
            "memoryInGb": 80,
            "secureCloud": True,
            "communityCloud": True,
            "lowestPrice": {
                "stockStatus": "Low",
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
                "stockStatus": None,
                "uninterruptablePrice": None,
                "minimumBidPrice": None,
                "availableGpuCounts": None,
            },
        },
        {
            "id": "AMD Instinct MI350 OAM",
            "displayName": "MI350X",
            "memoryInGb": 294,
            "secureCloud": True,
            "communityCloud": False,
            "lowestPrice": {
                "stockStatus": "Low",
                "uninterruptablePrice": 0.5,
                "minimumBidPrice": 0.5,
                "availableGpuCounts": None,
            },
        },
    ],
}

normalized = normalize_gpu_catalog(sample_observation)
nodes = normalized["nodes"]
by_label = {node["hardware_label"]: node for node in nodes}

requirement = {
    "request_id": "req-2b-dry-run",
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

checks = {}

secret = "do-not-leak-this-runpod-key"
state = credential_state({"RUNPOD_API_KEY": secret})
checks["credential_boundary"] = (
    state["present"] is True
    and state["value_exposed"] is False
    and secret not in json.dumps(state)
)

missing = fetch_account_pods({})
checks["missing_credential_fail_closed"] = (
    missing["status"] == "skipped_no_credential"
    and missing["pods"] == []
    and missing["credential"]["present"] is False
)

checks["provider_contract_zero_activation"] = all(
    value is False for value in provider_contract["activation"].values()
)

checks["live_shape_normalization"] = (
    normalized["fixture_mode"] is False
    and normalized["provider"] == "runpod"
    and normalized["provider_health"]["status"] == "healthy"
    and len(nodes) == 3
)

h100 = by_label["NVIDIA H100 80GB HBM3"]
rtx4090 = by_label["NVIDIA GeForce RTX 4090"]\nmi350 = by_label["AMD Instinct MI350 OAM"]
checks["vram_and_availability"] = (
    h100["memory_gb"] == 80
    and h100["availability"] == "available"
    and rtx4090["memory_gb"] == 24
    and rtx4090["availability"] == "unknown"
)

checks["compute_capability_routing"] = (
    "cuda_compute" in h100["capabilities"]
    and "rocm_compute" not in h100["capabilities"]
    and "rocm_compute" in mi350["capabilities"]
    and "cuda_compute" not in mi350["capabilities"]
)

checks["health_truthfulness"] = (
    h100["health"] == "unknown"
    and h100["telemetry"]["source"] == "runpod_live_catalog"
    and h100["telemetry"]["observed_at"] == sample_observation["observed_at"]
    and h100["telemetry"]["load_percent"] is None
    and h100["telemetry"]["temperature_c"] is None
)

checks["cost_metadata"] = (
    h100["cost"]["currency"] == "USD"
    and h100["cost"]["unit"] == "gpu_hour"
    and h100["cost"]["estimated_per_hour"] == 2.69
    and h100["cost"]["source"] == "runpod_live_catalog"
)

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
    and matches[0]["provisioning_authority"] is False
    and matches[0]["execution_authority"] is False
)

checks["zero_node_execution"] = zero_activation(normalized)

checks["public_query_is_read_only"] = (
    "query ForgeATLGpuCatalog" in runpod_provider.GPU_CATALOG_QUERY
    and "mutation" not in runpod_provider.GPU_CATALOG_QUERY.lower()
)

source = inspect.getsource(runpod_provider)
checks["no_mutation_surface"] = not any(
    token in source
    for token in [
        'method="DELETE"',
        'method="PUT"',
        'method="PATCH"',
        "def provision(",
        "def create_pod(",
        "def start_pod(",
        "def stop_pod(",
        "def terminate_pod(",
        "def execute(",
        "def train(",
    ]
)

contract_text = json.dumps(provider_contract)
checks["no_secret_persistence"] = (
    secret not in contract_text
    and "RUNPOD_API_KEY" in contract_text
    and provider_contract["credential_boundary"]["persist_in_repository"] is False
)

checks["phase2a_compatibility"] = all(
    node["provider_type"] == "gpu"
    and node["location_type"] == "cloud"
    and node["telemetry"]["memory_total_gb"] == node["memory_gb"]
    for node in nodes
)

result = "PASS" if all(checks.values()) else "FAIL"
print({"milestone": "FORGE-ATL.2B", "result": result, "checks": checks})
raise SystemExit(0 if result == "PASS" else 1)
