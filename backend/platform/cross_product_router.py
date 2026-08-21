from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256

CROSS_PRODUCT_ROUTER_VERSION = "platform.cross-product-router.v1"


class RouteState(str, Enum):
    READY = "ready"
    PLANNING_ONLY = "planning_only"
    APPROVAL_REQUIRED = "approval_required"
    BLOCKED = "blocked"


@dataclass(frozen=True, slots=True)
class CrossProductRouteRequest:
    command: str
    project_id: str
    project_name: str
    correlation_id: str
    requested_capability: str = ""
    requested_operation: str = ""
    approval_present: bool = False

@dataclass(frozen=True, slots=True)
class CrossProductRouteDecision:
    route_id: str
    product_id: str
    capability: str
    target: str
    state: RouteState
    requires_approval: bool
    mutates_state: bool
    reason: str
    correlation_id: str
    contract_version: str = CROSS_PRODUCT_ROUTER_VERSION


_WRITE_OPERATIONS = {
    "modify-source", "write-file", "create", "update", "delete",
    "deploy", "rollback", "send", "permission-change", "billing-change",
}

_READ_COMMANDS = {"status", "blockers", "audit"}

_PRODUCT_TARGETS = {
    "forgevoice": ("forgevoice", "voice.orchestration"),
    "forgecall": ("forgecall", "agent.orchestration"),
    "forgehr": ("forgehr", "agent.orchestration"),
    "forgesocial": ("forgesocial", "agent.orchestration"),
    "forgestudio": ("forgestudio", "agent.orchestration"),
    "storiya": ("storiya", "agent.orchestration"),
}

def _normalize(value: str) -> str:
    return "".join(character for character in value.strip().lower() if character.isalnum())


def _product_target(project_id: str, project_name: str) -> tuple[str, str]:
    for candidate in (_normalize(project_id), _normalize(project_name)):
        for key, value in _PRODUCT_TARGETS.items():
            if key in candidate:
                return value
    return (project_id.strip().lower() or "unknown", "agent.orchestration")


def _capability(request: CrossProductRouteRequest, target: str) -> str:
    if request.requested_capability.strip():
        return request.requested_capability.strip()
    command = request.command.strip().lower()
    if command in _READ_COMMANDS:
        return "project.read"
    if target == "voice.orchestration":
        return "voice.orchestrate"
    return "project.plan_next"


def _route_id(request: CrossProductRouteRequest, capability: str, target: str) -> str:
    signature = "|".join((request.command, request.project_id, capability, target, request.correlation_id))
    return f"xroute-{sha256(signature.encode('utf-8')).hexdigest()[:16]}"

def decide_cross_product_route(request: CrossProductRouteRequest) -> CrossProductRouteDecision:
    if not request.correlation_id.strip():
        raise ValueError("correlation_id is required")
    if not request.project_id.strip() and not request.project_name.strip():
        raise ValueError("project identity is required")
    product_id, target = _product_target(request.project_id, request.project_name)
    capability = _capability(request, target)
    operation = request.requested_operation.strip().lower()
    mutates = operation in _WRITE_OPERATIONS
    requires_approval = mutates
    if mutates and not request.approval_present:
        state = RouteState.APPROVAL_REQUIRED
        reason = "state-changing operation requires existing approval gate"
    elif request.command.strip().lower() in {"continue", "start_next"}:
        state = RouteState.PLANNING_ONLY
        reason = "command resolved to planning route; execution remains separately authorized"
    else:
        state = RouteState.READY
        reason = "read-safe capability route selected"
    return CrossProductRouteDecision(
        route_id=_route_id(request, capability, target),
        product_id=product_id,
        capability=capability,
        target=target,
        state=state,
        requires_approval=requires_approval,
        mutates_state=mutates,
        reason=reason,
        correlation_id=request.correlation_id.strip(),
    )


__all__ = [
    "CROSS_PRODUCT_ROUTER_VERSION", "RouteState", "CrossProductRouteRequest",
    "CrossProductRouteDecision", "decide_cross_product_route",
]
