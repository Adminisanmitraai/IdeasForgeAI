from dataclasses import replace

import pytest

from backend.durable_job_store import DurableJobStore
from backend.platform.agent_job_coordination import create_assignment_job
from backend.platform.agent_orchestration import AgentDescriptor, AgentTask, build_orchestration_plan
from backend.platform.objective_execution_supervisor import (
    ObjectiveExecutionSupervisorError,
    supervise_objective,
)


def _agents():
    return (AgentDescriptor("a1", "Agent", frozenset({"code"}), 2),)


def _plan():
    tasks = (
        AgentTask("t1", "obj1", frozenset({"code"}), 1),
        AgentTask("t2", "obj1", frozenset({"code"}), 1, ("t1",)),
        AgentTask("t3", "obj1", frozenset({"code"}), 1, ("t1",)),
    )
    return build_orchestration_plan(
        objective_id="obj1", tasks=tasks, agents=_agents(), correlation_id="corr1"
    )


def _materialize(tmp_path):
    store = DurableJobStore(tmp_path)
    plan = _plan()
    links = []
    jobs = {}
    for assignment in plan.assignments:
        job, link = create_assignment_job(store=store, assignment=assignment, created_at="t0")
        links.append(link)
        jobs[assignment.task_id] = job
    return plan, tuple(links), jobs


def test_initial_state_exposes_only_first_wave(tmp_path):
    plan, links, jobs = _materialize(tmp_path)
    result = supervise_objective(plan=plan, links=links, jobs_by_task=jobs)
    assert result.state == "pending"
    assert result.ready_task_ids == ("t1",)
    states = {item.task_id: item.state for item in result.tasks}
    assert states == {"t1": "ready", "t2": "waiting", "t3": "waiting"}


def test_completion_unlocks_parallel_dependents(tmp_path):
    plan, links, jobs = _materialize(tmp_path)
    jobs["t1"] = replace(jobs["t1"], status="completed")
    result = supervise_objective(plan=plan, links=links, jobs_by_task=jobs)
    assert result.state == "running"
    assert result.ready_task_ids == ("t2", "t3")


def test_failed_dependency_blocks_downstream(tmp_path):
    plan, links, jobs = _materialize(tmp_path)
    jobs["t1"] = replace(jobs["t1"], status="failed")
    result = supervise_objective(plan=plan, links=links, jobs_by_task=jobs)
    assert result.state == "failed"
    assert result.blocked_task_ids == ("t2", "t3")
    states = {item.task_id: item.state for item in result.tasks}
    assert states["t1"] == "failed"
    assert states["t2"] == "blocked"
    assert states["t3"] == "blocked"


def test_all_completed_marks_objective_completed(tmp_path):
    plan, links, jobs = _materialize(tmp_path)
    jobs = {task_id: replace(job, status="completed") for task_id, job in jobs.items()}
    result = supervise_objective(plan=plan, links=links, jobs_by_task=jobs)
    assert result.state == "completed"
    assert set(result.terminal_task_ids) == {"t1", "t2", "t3"}


def test_lineage_mismatch_is_rejected(tmp_path):
    plan, links, jobs = _materialize(tmp_path)
    jobs["t1"] = replace(jobs["t1"], correlation_id="other")
    with pytest.raises(ObjectiveExecutionSupervisorError):
        supervise_objective(plan=plan, links=links, jobs_by_task=jobs)
