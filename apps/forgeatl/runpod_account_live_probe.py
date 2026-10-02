from __future__ import annotations

import json
from pathlib import Path

from runpod_account_inventory import (
    account_health_snapshot,
    dry_run_existing_pod_match,
    fetch_all_account_pods,
    merge_compute_fabric,
    normalize_account_inventory,
)
from runpod_provider import (
    credential_state,
    fetch_public_gpu_catalog,
    normalize_gpu_catalog,
)


ROOT = Path(__file__).resolve().parent


def load(name: str):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


credential = credential_state()
catalog_observation = fetch_public_gpu_catalog()
catalog = normalize_gpu_catalog(catalog_observation)
inventory = fetch_all_account_pods()
account = normalize_account_inventory(inventory, catalog)
merged = merge_compute_fabric(catalog, account)
health = account_health_snapshot(account)

requirement = {
    "request_id": "live-probe-2c-existing-pod",
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

matches = ()
if account["inventory_status"] == "read_only_inventory":
    matches = dry_run_existing_pod_match(
        requirement,
        fabric_contracts=load("compute_contracts.json"),
        capability_registry=load("capability_registry.json"),
        normalized_account=account,
    )

summary = {
    "milestone": "FORGE-ATL.2C-LIVE-ACCOUNT-PROBE",
    "provider": "runpod",
    "credential": credential,
    "inventory_status": account["inventory_status"],
    "account_pod_nodes": len(account["nodes"]),
    "inventory_pages": inventory.get("pages", 0),
    "health": health,
    "compute_fabric_merged_nodes": len(merged["nodes"]),
    "existing_pod_dry_run_match_count": len(matches),
    "existing_pod_dry_run_matches": [
        {
            "node_id": item["node_id"],
            "gpu": item["hardware_label"],
            "vram_gb_per_gpu": item["provider_metadata"]["vram_gb_per_gpu"],
            "gpu_count": item["provider_metadata"]["gpu_count"],
            "pod_status": item["provider_metadata"]["pod_status"],
            "gpu_load_percent": next(
                node["telemetry"]["load_percent"]
                for node in account["nodes"]
                if node["node_id"] == item["node_id"]
            ),
            "usd_per_pod_hour": item["cost"]["estimated_per_hour"],
            "runnable": item["runnable"],
            "dry_run_only": item["dry_run_only"],
        }
        for item in matches
    ],
    "create_enabled": False,
    "start_enabled": False,
    "stop_enabled": False,
    "delete_enabled": False,
    "job_execution_enabled": False,
    "training_enabled": False,
    "teacher_enabled": False,
}
print(json.dumps(summary, indent=2))
