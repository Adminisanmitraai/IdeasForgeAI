from dataclasses import replace

import pytest

from backend.durable_job_store import DurableJobStore
from backend.platform.agent_job_coordination import (
    AgentJobCoordinationError,
    create_assignment_job,
    dependency_state,
    persist_routed_job,
    reassign_agent,
)
from backend.platform.agent_orchestration import (
    AgentDescriptor,
    AgentTask,
    build_orchestration_plan,
)
from backend.platform.durable_jobs import DurableJob


def _agents():
    return (
        AgentDescriptor("a1", "Primary", frozenset({"code"}), 2, priority=10),
        AgentDescriptor("a2", "Backup", frozenset({"code"}), 2, priority=20),
    )


def _task(task_id="t1", deps=()):
    return AgentTask(task_id, "obj1", frozenset({"code"}), 1, deps)


def _plan(tasks=None):
    tasks = tuple(tasks or (_task(),))
    return build_orchestration_plan(
        objective_id="obj1", tasks=tasks, agents=_agents(), correlation_id="corr1"
    )


def test_assignment_creates_idempotent_durable_job(tmp_path):
    store = DurableJobStore(tmp_path)
    assignment = _plan().assignments[0]
    first, link = create_assignment_job(store=store, assignment=assignment, created_at="t0")
    second, link2 = create_assignment_job(store=store, assignment=assignment, created_at="t1")
    assert first.job_id == second.job_id
    assert link == link2
    assert first.correlation_id == assignment.correlation_id
    assert first.audit_events[0].event_type == "agent_assignment_created"


def test_dependency_state_wait_ready_and_failed(tmp_path):
    plan = _plan((_task("t1"), _task("t2", ("t1",))))
    _, link = create_assignment_job(
        store=DurableJobStore(tmp_path), assignment=plan.assignments[1], created_at="t0"
    )
    base = DurableJob("j1", "i1", "c1", "agent_task", "d", "t0")
    assert dependency_state(link, {"t1": base}) == "waiting"
    assert dependency_state(link, {"t1": replace(base, status="completed")}) == "ready"
    assert dependency_state(link, {"t1": replace(base, status="failed")}) == "blocked_failed_dependency"
    assert dependency_state(link, {}) == "blocked_missing_dependency"


def test_routing_persists_lease_and_audit(tmp_path):
    store = DurableJobStore(tmp_path)
    job, _ = create_assignment_job(
        store=store, assignment=_plan().assignments[0], created_at="t0"
    )
    routed = persist_routed_job(
        store=store, job=job, worker_id="worker-1", acquired_at="t1", expires_at="t2"
    )
    restored = DurableJobStore(tmp_path).get(job.job_id)
    assert routed.status == "leased"
    assert routed.lease.worker_id == "worker-1"
    assert restored == routed
    assert restored.audit_events[-1].event_type == "worker_routed:worker-1"


def test_reassignment_is_deterministic_and_bounded():
    selected = reassign_agent(
        task=_task(), agents=_agents(), previous_agent_ids=("a1",), reassignment_count=0
    )
    assert selected.agent_id == "a2"
    with pytest.raises(AgentJobCoordinationError):
        reassign_agent(
            task=_task(), agents=_agents(), previous_agent_ids=("a1",),
            reassignment_count=2, max_reassignments=2,
        )
