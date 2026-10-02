from __future__ import annotations

import copy
import json
import os
from datetime import datetime, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from compute_fabric import ComputeFabricRegistry


RUNPOD_GRAPHQL_URL = "https://api.runpod.io/graphql"
RUNPOD_PODS_URL = "https://api.runpod.io/v2/pods"
RUNPOD_API_KEY_ENV = "RUNPOD_API_KEY"

GPU_CATALOG_QUERY = """
query ForgeATLGpuCatalog {
  gpuTypes {
    id
    displayName
    memoryInGb
    secureCloud
    communityCloud
    lowestPrice(input: {gpuCount: 1}) {
      stockStatus
      uninterruptablePrice
      minimumBidPrice
      availableGpuCounts
    }
  }
}
""".strip()


class RunPodProviderError(RuntimeError):
    pass


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def credential_state(env: dict[str, str] | None = None) -> dict[str, Any]:
    source = os.environ if env is None else env
    present = bool(source.get(RUNPOD_API_KEY_ENV))
    return {
        "environment_variable": RUNPOD_API_KEY_ENV,
        "present": present,
        "value_exposed": False,
        "persistence": "environment_only",
    }


def _credential_value(env: dict[str, str] | None = None) -> str:
    source = os.environ if env is None else env
    value = source.get(RUNPOD_API_KEY_ENV)
    if not value:
        raise RunPodProviderError("RUNPOD_API_KEY is not configured")
    return value


def _request_json(
    *,
    url: str,
    method: str,
    body: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    timeout_seconds: int = 15,
) -> Any:
    encoded = None if body is None else json.dumps(body).encode("utf-8")
    request_headers = {"Accept": "application/json"}
    if body is not None:
        request_headers["Content-Type"] = "application/json"
    if headers:
        request_headers.update(headers)

    request = Request(
        url,
        data=encoded,
        headers=request_headers,
        method=method,
    )
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            payload = response.read().decode("utf-8")
    except HTTPError as exc:
        raise RunPodProviderError(f"RunPod HTTP {exc.code}") from exc
    except URLError as exc:
        raise RunPodProviderError("RunPod network request failed") from exc
    except TimeoutError as exc:
        raise RunPodProviderError("RunPod request timed out") from exc

    try:
        return json.loads(payload)
    except json.JSONDecodeError as exc:
        raise RunPodProviderError("RunPod returned invalid JSON") from exc


def fetch_public_gpu_catalog(timeout_seconds: int = 15) -> dict[str, Any]:
    observed_at = _utc_now()
    payload = _request_json(
        url=RUNPOD_GRAPHQL_URL,
        method="POST",
        body={"query": GPU_CATALOG_QUERY},
        timeout_seconds=timeout_seconds,
    )
    if payload.get("errors"):
        raise RunPodProviderError("RunPod GraphQL returned query errors")
    gpu_types = payload.get("data", {}).get("gpuTypes")
    if not isinstance(gpu_types, list):
        raise RunPodProviderError("RunPod GPU catalog shape is invalid")
    return {
        "provider": "runpod",
        "observed_at": observed_at,
        "provider_health": "healthy",
        "credential_required": False,
        "gpu_types": gpu_types,
    }


def fetch_account_pods(
    env: dict[str, str] | None = None,
    timeout_seconds: int = 15,
) -> dict[str, Any]:
    state = credential_state(env)
    if not state["present"]:
        return {
            "provider": "runpod",
            "status": "skipped_no_credential",
            "credential": state,
            "pods": [],
        }

    api_key = _credential_value(env)
    payload = _request_json(
        url=RUNPOD_PODS_URL,
        method="GET",
        headers={"Authorization": f"Bearer {api_key}"},
        timeout_seconds=timeout_seconds,
    )
    pods = payload.get("data", payload) if isinstance(payload, dict) else payload
    if not isinstance(pods, list):
        pods = [pods] if isinstance(pods, dict) else []
    return {
        "provider": "runpod",
        "status": "read_only_inventory",
        "credential": state,
        "pods": copy.deepcopy(pods),
    }


def _availability(stock_status: Any) -> str:
    if stock_status is None:
        return "unknown"
    normalized = str(stock_status).strip().lower()
    if normalized in {"high", "medium", "low"}:
        return "available"
    return "unknown"


def _capabilities(memory_gb: int) -> list[str]:
    values = [
        "general_compute",
        "tensor_fp32",
        "tensor_fp16",
        "parallel_training",
    ]
    if memory_gb >= 48:
        values.append("large_memory_compute")
    return values


def normalize_gpu_catalog(observation: dict[str, Any]) -> dict[str, Any]:
    if observation.get("provider") != "runpod":
        raise RunPodProviderError("unexpected provider")
    gpu_types = observation.get("gpu_types")
    if not isinstance(gpu_types, list):
        raise RunPodProviderError("gpu_types must be a list")

    observed_at = observation.get("observed_at") or _utc_now()
    nodes: list[dict[str, Any]] = []

    for gpu in gpu_types:
        provider_id = gpu.get("id")
        display_name = gpu.get("displayName")
        memory_gb = gpu.get("memoryInGb")
        if not provider_id or not display_name or not isinstance(memory_gb, int) or memory_gb < 0:
            continue

        price = gpu.get("lowestPrice") or {}
        stock_status = price.get("stockStatus")
        on_demand = price.get("uninterruptablePrice")
        bid_floor = price.get("minimumBidPrice")

        nodes.append(
            {
                "node_id": f"runpod-catalog::{provider_id}",
                "provider_type": "gpu",
                "location_type": "cloud",
                "display_name": f"RunPod {display_name}",
                "hardware_label": provider_id,
                "capabilities": _capabilities(memory_gb),
                "memory_gb": memory_gb,
                "availability": _availability(stock_status),
                "execution_enabled": False,
                "health": "unknown",
                "telemetry": {
                    "observed_at": observed_at,
                    "source": "runpod_live_catalog",
                    "load_percent": None,
                    "memory_used_gb": None,
                    "memory_total_gb": memory_gb,
                    "temperature_c": None,
                },
                "cost": {
                    "currency": "USD",
                    "unit": "gpu_hour",
                    "estimated_per_hour": on_demand,
                    "bid_floor_per_hour": bid_floor,
                    "source": "runpod_live_catalog",
                },
                "provider_metadata": {
                    "provider": "runpod",
                    "provider_gpu_id": provider_id,
                    "stock_status": stock_status,
                    "secure_cloud": bool(gpu.get("secureCloud")),
                    "community_cloud": bool(gpu.get("communityCloud")),
                    "available_gpu_counts": price.get("availableGpuCounts"),
                },
            }
        )

    return {
        "schema_version": "forgeatl.compute-nodes.v1",
        "fixture_mode": False,
        "provider": "runpod",
        "provider_health": {
            "status": observation.get("provider_health", "unknown"),
            "observed_at": observed_at,
            "source": "runpod_catalog_request",
        },
        "nodes": nodes,
    }


def dry_run_match(
    requirement: dict[str, Any],
    *,
    fabric_contracts: dict[str, Any],
    capability_registry: dict[str, Any],
    normalized_nodes: dict[str, Any],
) -> tuple[dict[str, Any], ...]:
    registry = ComputeFabricRegistry(
        fabric_contracts,
        capability_registry,
        normalized_nodes,
    )
    discovered = registry.discover(requirement)
    by_id = {node["node_id"]: node for node in normalized_nodes["nodes"]}
    available: list[dict[str, Any]] = []

    for candidate in discovered:
        node = by_id[candidate["node_id"]]
        if node["availability"] != "available":
            continue
        available.append(
            {
                **candidate,
                "display_name": node["display_name"],
                "hardware_label": node["hardware_label"],
                "cost": copy.deepcopy(node["cost"]),
                "provider_metadata": copy.deepcopy(node["provider_metadata"]),
                "dry_run_only": True,
                "assignment_authority": False,
                "provisioning_authority": False,
                "execution_authority": False,
            }
        )

    return tuple(available)


def zero_activation(normalized_nodes: dict[str, Any]) -> bool:
    return all(node["execution_enabled"] is False for node in normalized_nodes.get("nodes", []))
