from __future__ import annotations

import copy
from typing import Any
from urllib.parse import urlencode

from compute_fabric import ComputeFabricRegistry
from runpod_provider import (
    RUNPOD_PODS_URL,
    _credential_value,
    _request_json,
    _utc_now,
    credential_state,
)


_STATUS = {
    "RUNNING": ("busy", "healthy"),
    "STARTING": ("busy", "unknown"),
    "PROVISIONING": ("busy", "unknown"),
    "EXITED": ("declared", "unknown"),
    "ERROR": ("offline", "degraded"),
    "TERMINATED": ("offline", "offline"),
}


class RunPodAccountInventoryError(RuntimeError):
    pass


def _mean(values: list[Any]) -> float | None:
    numbers = [float(value) for value in values if isinstance(value, (int, float))]
    return None if not numbers else sum(numbers) / len(numbers)


def fetch_all_account_pods(
    env: dict[str, str] | None = None,
    *,
    timeout_seconds: int = 15,
    max_pages: int = 20,
) -> dict[str, Any]:
    state = credential_state(env)
    if not state["present"]:
        return {
            "provider": "runpod",
            "status": "skipped_no_credential",
            "credential": state,
            "observed_at": None,
            "pages": 0,
            "pods": [],
        }

    api_key = _credential_value(env)
    observed_at = _utc_now()
    cursor: str | None = None
    pods: list[dict[str, Any]] = []
    pages = 0

    while True:
        query = {"includeClusterPods": "false", "limit": "100"}
        if cursor:
            query["cursor"] = cursor
        url = f"{RUNPOD_PODS_URL}?{urlencode(query)}"
        payload = _request_json(
            url=url,
            method="GET",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout_seconds=timeout_seconds,
        )
        if not isinstance(payload, dict) or not isinstance(payload.get("pods"), list):
            raise RunPodAccountInventoryError("RunPod /v2/pods response shape is invalid")

        pods.extend(copy.deepcopy(payload["pods"]))
        pages += 1
        pagination = payload.get("pagination") or {}
        has_next = bool(pagination.get("hasNextPage"))
        cursor = pagination.get("nextCursor")
        if not has_next:
            break
        if not cursor:
            raise RunPodAccountInventoryError("pagination says next page but nextCursor is missing")
        if pages >= max_pages:
            raise RunPodAccountInventoryError("account inventory exceeded max_pages")

    return {
        "provider": "runpod",
        "status": "read_only_inventory",
        "credential": state,
        "observed_at": observed_at,
        "pages": pages,
        "pods": pods,
    }


def _catalog_index(normalized_catalog: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        node["hardware_label"]: node
        for node in normalized_catalog.get("nodes", [])
        if node.get("provider_type") == "gpu"
    }


def _fallback_capabilities(gpu_id: str) -> list[str]:
    result = ["general_compute", "parallel_training"]
    upper = gpu_id.upper()
    if upper.startswith("NVIDIA "):
        result.append("cuda_compute")
    elif upper.startswith("AMD "):
        result.append("rocm_compute")
    return result


def normalize_account_inventory(
    inventory: dict[str, Any],
    normalized_catalog: dict[str, Any],
) -> dict[str, Any]:
    if inventory.get("status") == "skipped_no_credential":
        return {
            "schema_version": "forgeatl.compute-nodes.v1",
            "fixture_mode": False,
            "provider": "runpod",
            "inventory_scope": "account",
            "inventory_status": "skipped_no_credential",
            "observed_at": None,
            "nodes": [],
        }
    if inventory.get("provider") != "runpod" or inventory.get("status") != "read_only_inventory":
        raise RunPodAccountInventoryError("unexpected account inventory state")

    observed_at = inventory.get("observed_at") or _utc_now()
    catalog = _catalog_index(normalized_catalog)
    nodes: list[dict[str, Any]] = []

    for pod in inventory.get("pods", []):
        gpu = pod.get("gpu")
        if not isinstance(gpu, dict):
            continue
        pod_id = pod.get("id")
        gpu_id = gpu.get("id")
        if not pod_id or not gpu_id:
            continue

        gpu_count = gpu.get("count", 1)
        if not isinstance(gpu_count, int) or gpu_count < 1:
            gpu_count = 1

        catalog_node = catalog.get(gpu_id)
        per_gpu_vram = int(catalog_node["memory_gb"]) if catalog_node else 0
        capabilities = (
            list(catalog_node["capabilities"])
            if catalog_node
            else _fallback_capabilities(gpu_id)
        )

        status = str(pod.get("status") or "UNKNOWN").upper()
        availability, health = _STATUS.get(status, ("unknown", "unknown"))
        runtime = pod.get("runtime") if isinstance(pod.get("runtime"), dict) else {}
        runtime_gpus = runtime.get("gpus") if isinstance(runtime.get("gpus"), list) else []
        load_percent = _mean([item.get("util") for item in runtime_gpus if isinstance(item, dict)])
        memory_util_percent = _mean(
            [item.get("memoryUtil") for item in runtime_gpus if isinstance(item, dict)]
        )

        cost = pod.get("cost")
        hourly_cost = float(cost) if isinstance(cost, (int, float)) else None
        name = pod.get("name") or pod_id

        nodes.append(
            {
                "node_id": f"runpod-pod::{pod_id}",
                "provider_type": "gpu",
                "location_type": "cloud",
                "display_name": f"RunPod Pod {name}",
                "hardware_label": gpu_id,
                "capabilities": capabilities,
                "memory_gb": per_gpu_vram,
                "availability": availability,
                "execution_enabled": False,
                "health": health,
                "telemetry": {
                    "observed_at": observed_at,
                    "source": "runpod_account_pod",
                    "load_percent": load_percent,
                    "memory_used_gb": None,
                    "memory_total_gb": per_gpu_vram,
                    "temperature_c": None,
                },
                "cost": {
                    "currency": "USD",
                    "unit": "pod_hour",
                    "estimated_per_hour": hourly_cost,
                    "source": "runpod_account_pod",
                },
                "provider_metadata": {
                    "provider": "runpod",
                    "resource_scope": "account",
                    "pod_id": pod_id,
                    "pod_status": status,
                    "gpu_count": gpu_count,
                    "vram_gb_per_gpu": per_gpu_vram,
                    "aggregate_vram_gb": per_gpu_vram * gpu_count,
                    "cloud": pod.get("cloud"),
                    "data_center_id": pod.get("dataCenterId"),
                    "cuda_version": pod.get("cudaVersion"),
                    "runtime_gpu_memory_util_percent": memory_util_percent,
                    "uptime_seconds": runtime.get("uptime"),
                    "created_at": pod.get("createdAt"),
                    "started_at": pod.get("startedAt"),
                    "actions_reported_by_provider": copy.deepcopy(pod.get("actions") or []),
                },
            }
        )

    return {
        "schema_version": "forgeatl.compute-nodes.v1",
        "fixture_mode": False,
        "provider": "runpod",
        "inventory_scope": "account",
        "inventory_status": "read_only_inventory",
        "observed_at": observed_at,
        "nodes": nodes,
    }


def merge_compute_fabric(
    normalized_catalog: dict[str, Any],
    normalized_account: dict[str, Any],
) -> dict[str, Any]:
    catalog_nodes = copy.deepcopy(normalized_catalog.get("nodes", []))
    account_nodes = copy.deepcopy(normalized_account.get("nodes", []))
    all_nodes = catalog_nodes + account_nodes
    ids = [node["node_id"] for node in all_nodes]
    if len(ids) != len(set(ids)):
        raise RunPodAccountInventoryError("duplicate node_id during compute fabric merge")
    return {
        "schema_version": "forgeatl.compute-nodes.v1",
        "fixture_mode": False,
        "provider": "runpod",
        "sources": ["live_catalog", "account_inventory"],
        "account_inventory_status": normalized_account.get("inventory_status"),
        "nodes": all_nodes,
    }


def dry_run_existing_pod_match(
    requirement: dict[str, Any],
    *,
    fabric_contracts: dict[str, Any],
    capability_registry: dict[str, Any],
    normalized_account: dict[str, Any],
) -> tuple[dict[str, Any], ...]:
    registry = ComputeFabricRegistry(
        fabric_contracts,
        capability_registry,
        normalized_account,
    )
    discovered = registry.discover(requirement)
    by_id = {node["node_id"]: node for node in normalized_account.get("nodes", [])}
    result: list[dict[str, Any]] = []
    for candidate in discovered:
        node = by_id[candidate["node_id"]]
        result.append(
            {
                **candidate,
                "display_name": node["display_name"],
                "hardware_label": node["hardware_label"],
                "cost": copy.deepcopy(node["cost"]),
                "provider_metadata": copy.deepcopy(node["provider_metadata"]),
                "dry_run_only": True,
                "existing_account_resource": True,
                "assignment_authority": False,
                "execution_authority": False,
            }
        )
    return tuple(result)


def account_health_snapshot(normalized_account: dict[str, Any]) -> dict[str, Any]:
    nodes = normalized_account.get("nodes", [])
    status_counts: dict[str, int] = {}
    observed_gpu_load_nodes = 0
    for node in nodes:
        status = node["provider_metadata"]["pod_status"]
        status_counts[status] = status_counts.get(status, 0) + 1
        if node["telemetry"]["load_percent"] is not None:
            observed_gpu_load_nodes += 1
    return {
        "inventory_status": normalized_account.get("inventory_status"),
        "pod_nodes": len(nodes),
        "status_counts": status_counts,
        "observed_gpu_load_nodes": observed_gpu_load_nodes,
        "temperature_observed_nodes": sum(
            1 for node in nodes if node["telemetry"]["temperature_c"] is not None
        ),
        "execution_authority": False,
    }


def zero_activation(normalized_account: dict[str, Any]) -> bool:
    return all(node.get("execution_enabled") is False for node in normalized_account.get("nodes", []))
