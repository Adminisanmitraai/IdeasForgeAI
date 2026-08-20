from dataclasses import replace

from backend.durable_job_store import DurableJobStore
from backend.objective_supervision_store import ObjectiveSupervisionStore
from backend.platform.agent_job_coordination import create_assignment_job
from backend.platform.agent_orchestration import (
    AgentDescriptor,
    AgentTask,
    build_orchestration_plan,
)
from backend.platform.objective_execution_supervisor import supervise_objective


def _materialize(root):
    agent = AgentDescriptor("a1", "Agent", frozenset({"code"}), 2)
    tasks = (
        AgentTask("t1", "obj1", frozenset({"code"}), 1),
        AgentTask("t2", "obj1", frozenset({"code"}), 1, ("t1",)),
    )
    plan = build_orchestration_plan(
        objective_id="obj1", tasks=tasks, agents=(agent,), correlation_id="corr1"
    )
    jobs, links = {}, []
    job_store = DurableJobStore(root / "jobs")
    for assignment in plan.assignments:
        job, link = create_assignment_job(
            store=job_store, assignment=assignment, created_at="t0"
        )
        jobs[assignment.task_id] = job
        links.append(link)
    return plan, tuple(links), jobs

def test_supervision_round_trip_survives_restart(tmp_path):
    plan, links, jobs = _materialize(tmp_path)
    record = supervise_objective(plan=plan, links=links, jobs_by_task=jobs)
    store = ObjectiveSupervisionStore(tmp_path / "supervision")
    assert store.put(record) == record
    assert ObjectiveSupervisionStore(tmp_path / "supervision").get("obj1") == record


def test_failure_block_state_survives_restart(tmp_path):
    plan, links, jobs = _materialize(tmp_path)
    jobs["t1"] = replace(jobs["t1"], status="failed")
    record = supervise_objective(plan=plan, links=links, jobs_by_task=jobs)
    store = ObjectiveSupervisionStore(tmp_path / "supervision")
    store.put(record)
    restored = ObjectiveSupervisionStore(tmp_path / "supervision").get("obj1")
    assert restored.state == "failed"
    assert restored.blocked_task_ids == ("t2",)
    assert restored.correlation_id == "corr1"


def test_completed_dependency_unlock_state_survives_restart(tmp_path):
    plan, links, jobs = _materialize(tmp_path)
    jobs["t1"] = replace(jobs["t1"], status="completed")
    record = supervise_objective(plan=plan, links=links, jobs_by_task=jobs)
    store = ObjectiveSupervisionStore(tmp_path / "supervision")
    store.put(record)
    restored = ObjectiveSupervisionStore(tmp_path / "supervision").get("obj1")
    assert restored.ready_task_ids == ("t2",)
