from __future__ import annotations

import inspect
import json
from pathlib import Path

from compute_fabric import (
    ComputeContractError,
    ComputeFabricRegistry,
    phase2a_activation_disabled,
    validate_requirement,
)


ROOT = Path(__file__).resolve().parent


def load(name: str):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


contracts = load("compute_contracts.json")
capabilities = load("capability_registry.json")
nodes_doc = load("compute_nodes.json")
registry = ComputeFabricRegistry(contracts, capabilities, nodes_doc)

base_request = {
    "request_id": "req-fixture-001",
    "requester_id": "cad",
    "workload_type": "training_candidate",
    "capabilities": ["tensor_bf16", "parallel_training"],
    "memory_gb_min": 48,
    "precision": "bf16",
    "latency_class": "batch",
    "locality": "any",
    "max_cost_inr": 500,
    "estimated_duration_minutes": 60,
    "priority": "normal",
}

checks = {}

validated = validate_requirement(base_request, contracts, capabilities)
checks["compute_independent_requirement"] = validated == base_request and not any(
    key in validated for key in contracts["requirement_contract"]["forbidden_hardware_fields"]
)

checks["provider_types"] = contracts["provider_types"] == ["cpu", "gpu", "npu", "qpu"]

cap_map = {item["capability_id"]: item for item in capabilities["capabilities"]}
checks["capability_registry"] = (
    len(cap_map) == len(capabilities["capabilities"])
    and cap_map["parallel_training"]["provider_types"] == ["gpu"]
    and cap_map["quantum_circuit_execution"]["status"] == "future_reserved"
)

nodes = registry.nodes()
physical_gpu = [n for n in nodes if n["provider_type"] == "gpu" and n["location_type"] == "physical"]
cloud_gpu = [n for n in nodes if n["provider_type"] == "gpu" and n["location_type"] == "cloud"]
checks["physical_cloud_gpu_registry"] = len(physical_gpu) >= 1 and len(cloud_gpu) >= 1

providers = registry.providers()
checks["provider_coverage"] = set(providers) == {"cpu", "gpu", "npu", "qpu"} and all(
    providers[key] >= 1 for key in providers
)

candidates = registry.discover(base_request)
checks["resource_discovery"] = (
    len(candidates) == 1
    and candidates[0]["node_id"] == "fixture-cloud-gpu-01"
    and candidates[0]["candidate_only"] is True
    and candidates[0]["runnable"] is False
)

physical_request = dict(base_request, request_id="req-fixture-002", locality="physical", memory_gb_min=16)
physical_candidates = registry.discover(physical_request)
checks["locality_and_memory_filter"] = (
    len(physical_candidates) == 1
    and physical_candidates[0]["node_id"] == "fixture-physical-gpu-01"
)

forbidden_rejected = False
try:
    validate_requirement(dict(base_request, gpu_model="RTX"), contracts, capabilities)
except ComputeContractError:
    forbidden_rejected = True
checks["hardware_binding_fail_closed"] = forbidden_rejected

unknown_rejected = False
try:
    validate_requirement(dict(base_request, capabilities=["not_registered"]), contracts, capabilities)
except ComputeContractError:
    unknown_rejected = True
checks["unknown_capability_fail_closed"] = unknown_rejected

qpu_request = dict(
    base_request,
    request_id="req-fixture-qpu",
    capabilities=["quantum_circuit_execution"],
    memory_gb_min=0,
    precision="quantum",
)
qpu_candidates = registry.discover(qpu_request)
checks["future_qpu_reserved"] = (
    len(qpu_candidates) == 1
    and qpu_candidates[0]["provider_type"] == "qpu"
    and qpu_candidates[0]["availability"] == "future"
    and qpu_candidates[0]["runnable"] is False
)

health = registry.health_snapshot()
checks["health_telemetry_contract"] = (
    health["node_count"] == len(nodes)
    and health["execution_authority"] is False
    and len(health["telemetry"]) == len(nodes)
    and all(item["telemetry_state"] == "not_observed" for item in health["telemetry"])
)

joined = json.dumps(nodes_doc).lower()
checks["no_credentials_or_live_endpoints"] = not any(
    token in joined for token in ["api_key", "credential", "secret", "token", "http://", "https://"]
)

source = inspect.getsource(__import__("compute_fabric"))
checks["read_only_surface"] = not any(
    token in source
    for token in [
        "def execute(",
        "def provision(",
        "def train(",
        "subprocess",
        "requests.",
        "httpx",
        "socket.",
        "urllib.",
    ]
)

checks["zero_activation"] = phase2a_activation_disabled(contracts, nodes)

result = "PASS" if all(checks.values()) else "FAIL"
print({"milestone": "FORGE-ATL.2A", "result": result, "checks": checks})
raise SystemExit(0 if result == "PASS" else 1)
