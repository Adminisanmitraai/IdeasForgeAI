from __future__ import annotations

import json
from pathlib import Path

from physical_nvidia_provider import (
    discover_physical_nvidia,
    dry_run_match,
    normalize_physical_nvidia,
)


ROOT = Path(__file__).resolve().parent


def load(name: str):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


observation = discover_physical_nvidia()
normalized = normalize_physical_nvidia(observation)

requirement = {
    "request_id": "live-probe-2d",
    "requester_id": "ai",
    "workload_type": "training_candidate",
    "capabilities": ["parallel_training", "cuda_compute"],
    "memory_gb_min": 16,
    "precision": "provider-neutral",
    "latency_class": "batch",
    "locality": "physical",
    "max_cost_inr": 5000,
    "estimated_duration_minutes": 60,
    "priority": "normal",
}

matches = ()
if normalized["nodes"]:
    matches = dry_run_match(
        requirement,
        fabric_contracts=load("compute_contracts.json"),
        capability_registry=load("capability_registry.json"),
        normalized_nodes=normalized,
    )

summary = {
    "milestone": "FORGE-ATL.2D-LIVE-PHYSICAL-PROBE",
    "provider": "physical_nvidia",
    "discovery_status": normalized["discovery_status"],
    "physical_nvidia_nodes": len(normalized["nodes"]),
    "nodes": [
        {
            "node_id": node["node_id"],
            "gpu": node["hardware_label"],
            "vram_gb": node["memory_gb"],
            "availability": node["availability"],
            "health": node["health"],
            "gpu_load_percent": node["telemetry"]["load_percent"],
            "vram_used_gb": node["telemetry"]["memory_used_gb"],
            "temperature_c": node["telemetry"]["temperature_c"],
            "driver_version": node["provider_metadata"]["driver_version"],
            "cuda_version": node["provider_metadata"]["cuda_version"],
            "performance_state": node["provider_metadata"]["performance_state"],
            "execution_enabled": node["execution_enabled"],
        }
        for node in normalized["nodes"]
    ],
    "dry_run_match_count": len(matches),
    "dry_run_matches": [
        {
            "gpu": item["hardware_label"],
            "vram_gb": item["memory_gb"],
            "availability": item["availability"],
            "runnable": item["runnable"],
            "dry_run_only": item["dry_run_only"],
        }
        for item in matches
    ],
    "training_enabled": False,
    "job_execution_enabled": False,
    "teacher_enabled": False,
}
print(json.dumps(summary, indent=2))
