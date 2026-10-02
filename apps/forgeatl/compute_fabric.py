from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Iterable


class ComputeContractError(ValueError):
    pass


def load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _capability_map(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    entries = registry.get("capabilities", [])
    mapped = {item["capability_id"]: item for item in entries}
    if len(mapped) != len(entries):
        raise ComputeContractError("duplicate capability_id")
    return mapped


def validate_requirement(
    requirement: dict[str, Any],
    contracts: dict[str, Any],
    capability_registry: dict[str, Any],
) -> dict[str, Any]:
    spec = contracts["requirement_contract"]
    missing = [key for key in spec["required"] if key not in requirement]
    if missing:
        raise ComputeContractError(f"missing requirement fields: {missing}")

    forbidden = [key for key in spec["forbidden_hardware_fields"] if key in requirement]
    if forbidden:
        raise ComputeContractError(f"hardware binding forbidden: {forbidden}")

    if requirement["locality"] not in spec["locality_values"]:
        raise ComputeContractError("invalid locality")
    if requirement["priority"] not in spec["priority_values"]:
        raise ComputeContractError("invalid priority")
    if not isinstance(requirement["capabilities"], list) or not requirement["capabilities"]:
        raise ComputeContractError("capabilities must be a non-empty list")

    known = _capability_map(capability_registry)
    unknown = sorted(set(requirement["capabilities"]) - set(known))
    if unknown:
        raise ComputeContractError(f"unknown capabilities: {unknown}")

    for field in ("memory_gb_min", "max_cost_inr", "estimated_duration_minutes"):
        if requirement[field] is None or requirement[field] < 0:
            raise ComputeContractError(f"{field} must be >= 0")

    return copy.deepcopy(requirement)


def validate_nodes(nodes_doc: dict[str, Any], contracts: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    required = contracts["node_contract"]["required"]
    provider_types = set(contracts["provider_types"])
    locations = set(contracts["location_types"])
    availability = set(contracts["node_contract"]["availability_values"])
    health_values = set(contracts["telemetry_contract"]["health_values"])
    telemetry_required = contracts["telemetry_contract"]["required"]

    seen: set[str] = set()
    validated: list[dict[str, Any]] = []
    for node in nodes_doc.get("nodes", []):
        missing = [key for key in required if key not in node]
        if missing:
            raise ComputeContractError(f"node missing fields: {missing}")
        if node["node_id"] in seen:
            raise ComputeContractError("duplicate node_id")
        seen.add(node["node_id"])
        if node["provider_type"] not in provider_types:
            raise ComputeContractError("invalid provider_type")
        if node["location_type"] not in locations:
            raise ComputeContractError("invalid location_type")
        if node["availability"] not in availability:
            raise ComputeContractError("invalid availability")
        if node["health"] not in health_values:
            raise ComputeContractError("invalid health")
        if node["memory_gb"] < 0:
            raise ComputeContractError("memory_gb must be >= 0")
        missing_telemetry = [key for key in telemetry_required if key not in node["telemetry"]]
        if missing_telemetry:
            raise ComputeContractError(f"telemetry missing fields: {missing_telemetry}")
        if node["telemetry"]["memory_total_gb"] != node["memory_gb"]:
            raise ComputeContractError("telemetry memory_total_gb mismatch")
        validated.append(copy.deepcopy(node))
    return tuple(validated)


class ComputeFabricRegistry:
    """Read-only Phase-2A registry. It discovers candidates; it cannot execute them."""

    def __init__(
        self,
        contracts: dict[str, Any],
        capability_registry: dict[str, Any],
        nodes_doc: dict[str, Any],
    ) -> None:
        self._contracts = copy.deepcopy(contracts)
        self._capabilities = copy.deepcopy(capability_registry)
        self._nodes = validate_nodes(nodes_doc, contracts)
        _capability_map(self._capabilities)

    def providers(self) -> dict[str, int]:
        counts = {provider: 0 for provider in self._contracts["provider_types"]}
        for node in self._nodes:
            counts[node["provider_type"]] += 1
        return counts

    def nodes(self) -> tuple[dict[str, Any], ...]:
        return tuple(copy.deepcopy(node) for node in self._nodes)

    def discover(self, requirement: dict[str, Any]) -> tuple[dict[str, Any], ...]:
        request = validate_requirement(requirement, self._contracts, self._capabilities)
        requested = set(request["capabilities"])
        candidates: list[dict[str, Any]] = []

        for node in self._nodes:
            if request["locality"] != "any" and node["location_type"] != request["locality"]:
                continue
            if node["memory_gb"] < request["memory_gb_min"]:
                continue
            if not requested.issubset(set(node["capabilities"])):
                continue

            runnable = bool(
                node["execution_enabled"]
                and node["availability"] == "available"
                and node["health"] == "healthy"
            )
            candidates.append(
                {
                    "node_id": node["node_id"],
                    "provider_type": node["provider_type"],
                    "location_type": node["location_type"],
                    "availability": node["availability"],
                    "health": node["health"],
                    "memory_gb": node["memory_gb"],
                    "execution_enabled": node["execution_enabled"],
                    "runnable": runnable,
                    "candidate_only": True,
                }
            )

        return tuple(candidates)

    def health_snapshot(self) -> dict[str, Any]:
        by_health: dict[str, int] = {}
        by_availability: dict[str, int] = {}
        telemetry = []
        for node in self._nodes:
            by_health[node["health"]] = by_health.get(node["health"], 0) + 1
            by_availability[node["availability"]] = by_availability.get(node["availability"], 0) + 1
            telemetry.append(
                {
                    "node_id": node["node_id"],
                    "health": node["health"],
                    "availability": node["availability"],
                    "observed_at": node["telemetry"]["observed_at"],
                    "telemetry_state": (
                        "observed" if node["telemetry"]["observed_at"] else "not_observed"
                    ),
                }
            )
        return {
            "node_count": len(self._nodes),
            "by_health": by_health,
            "by_availability": by_availability,
            "telemetry": telemetry,
            "execution_authority": False,
        }


def phase2a_activation_disabled(contracts: dict[str, Any], nodes: Iterable[dict[str, Any]]) -> bool:
    return (
        all(value is False for value in contracts["activation"].values())
        and all(node["execution_enabled"] is False for node in nodes)
    )
