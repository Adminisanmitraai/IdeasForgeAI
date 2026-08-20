from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Any, Mapping

from .contracts.operating import ActionRecord, AgentAssignment


class OperatingGuardError(RuntimeError):
    pass


class InvalidStateTransitionError(OperatingGuardError):
    pass


class CapabilityBoundaryError(OperatingGuardError):
    pass


class ReplayConflictError(OperatingGuardError):
    pass


OBJECTIVE_TRANSITIONS = {
    "proposed": {"approved", "cancelled"},
    "approved": {"planning", "cancelled"},
    "planning": {"executing", "failed", "cancelled"},
    "executing": {"verifying", "failed", "cancelled"},
    "verifying": {"completed", "failed"},
    "completed": set(),
    "failed": set(),
    "cancelled": set(),
}

ACTION_TRANSITIONS = {
    "proposed": {"authorized", "rejected", "cancelled"},
    "authorized": {"running", "cancelled"},
    "running": {"succeeded", "failed", "cancelled"},
    "succeeded": set(),
    "failed": set(),
    "rejected": set(),
    "cancelled": set(),
}


def assert_state_transition(entity_type: str, current: str, target: str) -> None:
    tables = {
        "objective": OBJECTIVE_TRANSITIONS,
        "action": ACTION_TRANSITIONS,
    }
    table = tables.get(entity_type)
    if table is None:
        raise InvalidStateTransitionError(f"Unsupported entity type: {entity_type}")
    if target not in table.get(current, set()):
        raise InvalidStateTransitionError(
            f"Invalid {entity_type} transition: {current} -> {target}"
        )

WRITE_OPERATIONS = {
    "modify-source", "write-file", "create", "update", "delete",
    "deploy", "rollback", "send", "permission-change", "billing-change",
}
PRIVILEGED_OPERATIONS = {
    "delete", "deploy", "rollback", "send", "permission-change", "billing-change",
}


def assert_agent_action_allowed(
    assignment: AgentAssignment,
    action: ActionRecord,
) -> None:
    if assignment.agent_id != action.agent_id or assignment.task_id != action.task_id:
        raise CapabilityBoundaryError("Action is outside the assigned agent/task boundary.")
    if action.capability and action.capability != assignment.capability:
        raise CapabilityBoundaryError("Agent does not hold the requested capability.")
    is_write = action.operation in WRITE_OPERATIONS
    if assignment.role == "founder_brain" and is_write:
        raise CapabilityBoundaryError("Founder Brain may not execute direct writes.")
    if assignment.trust_tier == "read_only" and is_write:
        raise CapabilityBoundaryError("Read-only agent may not execute writes.")
    if action.operation in PRIVILEGED_OPERATIONS:
        if assignment.trust_tier != "privileged":
            raise CapabilityBoundaryError("Privileged operation requires privileged trust tier.")
        if not action.requires_approval:
            raise CapabilityBoundaryError("Privileged operation must require approval.")


@dataclass(frozen=True)
class ReplayDecision:
    accepted: bool
    action_id: str
    original_action_id: str = ""
    duplicate: bool = False


class IdempotencyGuard:
    """Process-local replay guard; durable storage is delegated to later phases."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._seen: dict[str, str] = {}

    def register(self, action: ActionRecord) -> ReplayDecision:
        if not action.idempotency_key:
            raise ReplayConflictError("Write actions require an idempotency key.")
        with self._lock:
            original = self._seen.get(action.idempotency_key)
            if original is None:
                self._seen[action.idempotency_key] = action.action_id
                return ReplayDecision(accepted=True, action_id=action.action_id)
            if original == action.action_id:
                return ReplayDecision(
                    accepted=False,
                    action_id=action.action_id,
                    original_action_id=original,
                    duplicate=True,
                )
            raise ReplayConflictError(
                "Idempotency key is already owned by another action."
            )


@dataclass(frozen=True)
class OperatingTraceEvent:
    event_id: str
    event_type: str
    entity_type: str
    entity_id: str
    previous_state: str
    new_state: str
    correlation_id: str
    causation_id: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)


def build_trace_event(
    *,
    event_id: str,
    event_type: str,
    entity_type: str,
    entity_id: str,
    previous_state: str,
    new_state: str,
    correlation_id: str,
    causation_id: str = "",
    metadata: Mapping[str, Any] | None = None,
) -> OperatingTraceEvent:
    if not correlation_id:
        raise OperatingGuardError("Audit trace requires a correlation_id.")
    return OperatingTraceEvent(
        event_id=event_id,
        event_type=event_type,
        entity_type=entity_type,
        entity_id=entity_id,
        previous_state=previous_state,
        new_state=new_state,
        correlation_id=correlation_id,
        causation_id=causation_id,
        metadata={} if metadata is None else metadata,
    )
