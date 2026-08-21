from __future__ import annotations

from dataclasses import dataclass

from backend.founder_brain.command_resolver import FounderCommandResolution
from backend.platform.cross_product_router import (
    CrossProductRouteDecision,
    CrossProductRouteRequest,
    decide_cross_product_route,
)

FOUNDER_COMMAND_ROUTER_VERSION = "founder-os.command-router.v1"


class FounderCommandRoutingError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class FounderCommandRouteRequest:
    resolution: FounderCommandResolution
    correlation_id: str
    requested_capability: str = ""
    requested_operation: str = ""
    approval_present: bool = False

def route_founder_command(request: FounderCommandRouteRequest) -> CrossProductRouteDecision:
    resolution = request.resolution
    if resolution.project is None:
        raise FounderCommandRoutingError("resolved command has no deterministic project")
    project = resolution.project
    return decide_cross_product_route(
        CrossProductRouteRequest(
            command=resolution.command.value,
            project_id=project.project_id or project.external_key or project.entity_id,
            project_name=project.name,
            correlation_id=request.correlation_id,
            requested_capability=request.requested_capability,
            requested_operation=request.requested_operation,
            approval_present=request.approval_present,
        )
    )


__all__ = [
    "FOUNDER_COMMAND_ROUTER_VERSION",
    "FounderCommandRoutingError",
    "FounderCommandRouteRequest",
    "route_founder_command",
]
