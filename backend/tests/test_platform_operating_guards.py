from __future__ import annotations

import pytest

from backend.platform.contracts import ActionRecord, AgentAssignment
from backend.platform.operating_guards import (
    CapabilityBoundaryError,
    IdempotencyGuard,
    InvalidStateTransitionError,
    ReplayConflictError,
    assert_agent_action_allowed,
    assert_state_transition,
    build_trace_event,
)


def _action(**overrides):
    values = {
        "action_id": "action-1",
        "task_id": "task-1",
        "agent_id": "agent-1",
        "operation": "modify-source",
        "idempotency_key": "task-1:action-1:v1",
        "capability": "code.change",
        "correlation_id": "corr-1",
    }
    values.update(overrides)
    return ActionRecord(**values)


def test_state_transition_guards_reject_invalid_moves():
    assert_state_transition("objective", "proposed", "approved")
    assert_state_transition("action", "authorized", "running")

    with pytest.raises(InvalidStateTransitionError):
        assert_state_transition("objective", "proposed", "completed")


def test_founder_brain_direct_write_is_prohibited():
    assignment = AgentAssignment(
        agent_id="agent-1",
        task_id="task-1",
        capability="code.change",
        trust_tier="privileged",
        role="founder_brain",
    )

    with pytest.raises(CapabilityBoundaryError):
        assert_agent_action_allowed(assignment, _action())


def test_agent_capability_overreach_is_prohibited():
    assignment = AgentAssignment(
        agent_id="agent-1",
        task_id="task-1",
        capability="repository.read",
        trust_tier="controlled_write",
    )

    with pytest.raises(CapabilityBoundaryError):
        assert_agent_action_allowed(assignment, _action())


def test_duplicate_action_replay_is_suppressed():
    guard = IdempotencyGuard()
    action = _action()

    first = guard.register(action)
    second = guard.register(action)

    assert first.accepted is True
    assert second.accepted is False
    assert second.duplicate is True
    assert second.original_action_id == action.action_id


def test_idempotency_key_collision_is_rejected():
    guard = IdempotencyGuard()
    guard.register(_action())

    with pytest.raises(ReplayConflictError):
        guard.register(_action(action_id="action-2"))


def test_correlation_trace_is_required_and_preserved():
    event = build_trace_event(
        event_id="evt-1",
        event_type="action.status.changed",
        entity_type="action",
        entity_id="action-1",
        previous_state="authorized",
        new_state="running",
        correlation_id="corr-1",
        causation_id="plan-1",
    )

    assert event.correlation_id == "corr-1"
    assert event.causation_id == "plan-1"

    with pytest.raises(Exception):
        build_trace_event(
            event_id="evt-2",
            event_type="action.status.changed",
            entity_type="action",
            entity_id="action-1",
            previous_state="running",
            new_state="succeeded",
            correlation_id="",
        )
