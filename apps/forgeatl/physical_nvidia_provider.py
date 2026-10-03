from __future__ import annotations

import copy
import os
import platform
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any, Callable

from compute_fabric import ComputeFabricRegistry


NVIDIA_SMI_CANDIDATES = (
    r"C:\Windows\System32\nvidia-smi.exe",
    r"C:\Program Files\NVIDIA Corporation\NVSMI\nvidia-smi.exe",
)

GPU_QUERY_FIELDS = (
    "index",
    "name",
    "uuid",
    "memory.total",
    "memory.used",
    "utilization.gpu",
    "temperature.gpu",
    "driver_version",
    "pstate",
)


class PhysicalNvidiaError(RuntimeError):
    pass


def find_nvidia_smi() -> str | None:
    discovered = shutil.which("nvidia-smi") or shutil.which("nvidia-smi.exe")
    if discovered:
        return discovered
    for candidate in NVIDIA_SMI_CANDIDATES:
        if Path(candidate).exists():
            return candidate
    return None


def _run_fixed(
    argv: list[str],
    *,
    timeout_seconds: int = 10,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> subprocess.CompletedProcess[str]:
    return runner(
        argv,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout_seconds,
        check=False,
        shell=False,
    )


def _parse_float(value: str) -> float | None:
    stripped = value.strip()
    if stripped in {"", "N/A", "[Not Supported]", "Not Supported"}:
        return None
    try:
        return float(stripped)
    except ValueError:
        return None


def _mib_to_gib(value: str) -> float | None:
    mib = _parse_float(value)
    return None if mib is None else round(mib / 1024.0, 3)


def _cuda_version(header_text: str) -> str | None:
    match = re.search(r"CUDA Version:\s*([0-9.]+)", header_text)
    return None if not match else match.group(1)


def discover_physical_nvidia(
    *,
    executable: str | None = None,
    timeout_seconds: int = 10,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
    hostname: str | None = None,
) -> dict[str, Any]:
    nvidia_smi = executable or find_nvidia_smi()
    if not nvidia_smi:
        return {
            "provider": "physical_nvidia",
            "status": "no_nvidia_smi",
            "observed_at": None,
            "hostname": hostname or platform.node(),
            "cuda_version": None,
            "gpus": [],
        }

    header = _run_fixed(
        [nvidia_smi],
        timeout_seconds=timeout_seconds,
        runner=runner,
    )
    if header.returncode != 0:
        raise PhysicalNvidiaError("nvidia-smi header query failed")

    query = _run_fixed(
        [
            nvidia_smi,
            "--query-gpu=" + ",".join(GPU_QUERY_FIELDS),
            "--format=csv,noheader,nounits",
        ],
        timeout_seconds=timeout_seconds,
        runner=runner,
    )
    if query.returncode != 0:
        raise PhysicalNvidiaError("nvidia-smi GPU query failed")

    rows: list[dict[str, Any]] = []
    for raw_line in query.stdout.splitlines():
        if not raw_line.strip():
            continue
        parts = [part.strip() for part in raw_line.split(",")]
        if len(parts) != len(GPU_QUERY_FIELDS):
            raise PhysicalNvidiaError("unexpected nvidia-smi CSV shape")
        index, name, uuid, total_mib, used_mib, util, temp, driver, pstate = parts
        rows.append(
            {
                "index": int(index),
                "name": name,
                "uuid": uuid,
                "memory_total_gb": _mib_to_gib(total_mib),
                "memory_used_gb": _mib_to_gib(used_mib),
                "utilization_gpu_percent": _parse_float(util),
                "temperature_c": _parse_float(temp),
                "driver_version": driver or None,
                "performance_state": pstate or None,
            }
        )

    return {
        "provider": "physical_nvidia",
        "status": "observed",
        "observed_at": None,
        "hostname": hostname or platform.node(),
        "cuda_version": _cuda_version(header.stdout),
        "gpus": rows,
    }


def _availability(load_percent: float | None, used_gb: float | None, total_gb: float | None) -> str:
    memory_percent = None
    if used_gb is not None and total_gb not in {None, 0}:
        memory_percent = (used_gb / total_gb) * 100.0
    if load_percent is not None and load_percent >= 85:
        return "busy"
    if memory_percent is not None and memory_percent >= 90:
        return "busy"
    return "available"


def _capabilities(memory_gb: float | None) -> list[str]:
    values = [
        "general_compute",
        "tensor_fp32",
        "parallel_training",
        "cuda_compute",
    ]
    if memory_gb is not None and memory_gb >= 48:
        values.append("large_memory_compute")
    return values


def normalize_physical_nvidia(observation: dict[str, Any]) -> dict[str, Any]:
    if observation.get("provider") != "physical_nvidia":
        raise PhysicalNvidiaError("unexpected provider")

    if observation.get("status") == "no_nvidia_smi":
        return {
            "schema_version": "forgeatl.compute-nodes.v1",
            "fixture_mode": False,
            "provider": "physical_nvidia",
            "discovery_status": "no_nvidia_node_discovered",
            "nodes": [],
        }

    if observation.get("status") != "observed":
        raise PhysicalNvidiaError("unexpected discovery status")

    hostname = str(observation.get("hostname") or "unknown-host")
    cuda_version = observation.get("cuda_version")
    nodes: list[dict[str, Any]] = []

    for gpu in observation.get("gpus", []):
        total_gb = gpu.get("memory_total_gb")
        if not gpu.get("uuid") or not gpu.get("name") or total_gb is None:
            continue
        used_gb = gpu.get("memory_used_gb")
        load = gpu.get("utilization_gpu_percent")

        nodes.append(
            {
                "node_id": f"physical-nvidia::{hostname}::{gpu['uuid']}",
                "provider_type": "gpu",
                "location_type": "physical",
                "display_name": f"{hostname} / {gpu['name']}",
                "hardware_label": gpu["name"],
                "capabilities": _capabilities(total_gb),
                "memory_gb": total_gb,
                "availability": _availability(load, used_gb, total_gb),
                "execution_enabled": False,
                "health": "unknown",
                "telemetry": {
                    "observed_at": observation.get("observed_at"),
                    "source": "nvidia_smi",
                    "load_percent": load,
                    "memory_used_gb": used_gb,
                    "memory_total_gb": total_gb,
                    "temperature_c": gpu.get("temperature_c"),
                },
                "cost": {
                    "currency": "INR",
                    "estimated_per_hour": None,
                    "source": "physical_not_metered",
                },
                "provider_metadata": {
                    "provider": "physical_nvidia",
                    "hostname": hostname,
                    "gpu_index": gpu.get("index"),
                    "gpu_uuid": gpu["uuid"],
                    "driver_version": gpu.get("driver_version"),
                    "cuda_version": cuda_version,
                    "performance_state": gpu.get("performance_state"),
                    "discovery_tool": "nvidia-smi",
                },
            }
        )

    return {
        "schema_version": "forgeatl.compute-nodes.v1",
        "fixture_mode": False,
        "provider": "physical_nvidia",
        "discovery_status": "observed",
        "nodes": nodes,
    }


def dry_run_match(
    requirement: dict[str, Any],
    *,
    fabric_contracts: dict[str, Any],
    capability_registry: dict[str, Any],
    normalized_nodes: dict[str, Any],
) -> tuple[dict[str, Any], ...]:
    registry = ComputeFabricRegistry(fabric_contracts, capability_registry, normalized_nodes)
    discovered = registry.discover(requirement)
    by_id = {node["node_id"]: node for node in normalized_nodes.get("nodes", [])}
    result: list[dict[str, Any]] = []
    for candidate in discovered:
        node = by_id[candidate["node_id"]]
        result.append(
            {
                **candidate,
                "display_name": node["display_name"],
                "hardware_label": node["hardware_label"],
                "telemetry": copy.deepcopy(node["telemetry"]),
                "provider_metadata": copy.deepcopy(node["provider_metadata"]),
                "dry_run_only": True,
                "assignment_authority": False,
                "execution_authority": False,
            }
        )
    return tuple(result)


def zero_activation(normalized_nodes: dict[str, Any]) -> bool:
    return all(node.get("execution_enabled") is False for node in normalized_nodes.get("nodes", []))
