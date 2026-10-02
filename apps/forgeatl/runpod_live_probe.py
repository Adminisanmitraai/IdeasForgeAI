from __future__ import annotations

import json
from pathlib import Path

from runpod_provider import (
    credential_state,
    dry_run_match,
    fetch_account_pods,
    fetch_public_gpu_catalog,
    normalize_gpu_catalog,
)


ROOT = Path(__file__).resolve().parent


def load(name: str):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


observation = fetch_public_gpu_catalog()
normalized = normalize_gpu_catalog(observation)
nodes = normalized["nodes"]

requirement = {
    "request_id": "live-probe-2b",
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

matches = dry_run_match(
    requirement,
    fabric_contracts=load("compute_contracts.json"),
    capability_registry=load("capability_registry.json"),
    normalized_nodes=normalized,
)

large_available = [
    node
    for node in nodes
    if node["memory_gb"] >= 80 and node["availability"] == "available"
]
large_available.sort(
    key=lambda node: (
        node["cost"]["estimated_per_hour"] is None,
        node["cost"]["estimated_per_hour"] or 10**9,
        node["memory_gb"],
    )
)

account = fetch_account_pods()
summary = {
    "milestone": "FORGE-ATL.2B-LIVE-PROBE",
    "provider": "runpod",
    "observed_at": observation["observed_at"],
    "provider_health": normalized["provider_health"]["status"],
    "gpu_types_observed": len(nodes),
    "available_gpu_types": sum(1 for node in nodes if node["availability"] == "available"),
    "available_80gb_plus": len(large_available),
    "sample_80gb_plus": [
        {
            "gpu": node["hardware_label"],
            "vram_gb": node["memory_gb"],
            "stock_status": node["provider_metadata"]["stock_status"],
            "usd_per_gpu_hour": node["cost"]["estimated_per_hour"],
        }
        for node in large_available[:8]
    ],
    "dry_run_match_count": len(matches),
    "dry_run_matches": [
        {
            "gpu": item["hardware_label"],
            "vram_gb": item["memory_gb"],
            "availability": item["availability"],
            "usd_per_gpu_hour": item["cost"]["estimated_per_hour"],
            "runnable": item["runnable"],
            "dry_run_only": item["dry_run_only"],
        }
        for item in matches[:12]
    ],
    "credential": credential_state(),
    "account_inventory_status": account["status"],
    "account_pod_count": len(account["pods"]),
    "instance_provisioning": False,
    "job_execution": False,
    "training": False,
    "teacher_activation": False,
}
print(json.dumps(summary, indent=2))
