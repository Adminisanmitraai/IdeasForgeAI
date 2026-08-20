from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Literal, Mapping, Sequence

from .agent_job_coordination import AgentJobLink, dependency_state
from .agent_orchestration import OrchestrationPlan
from .durable_jobs import DurableJob

OBJECTIVE_SUPERVISOR_VERSION = "platform.objective-supervisor.v1"
TaskExecutionState = Literal[
    "ready", "waiting", "running", "completed", "failed", "blocked"
]
ObjectiveExecutionState = Literal[
    "pending", "running", "completed", "failed", "blocked"
]


class ObjectiveExecutionSupervisorError(RuntimeError):
    pass


@dataclass(frozen=True)
class TaskSupervision:
    task_id: str
    assignment_id: str
    job_id: str
    state: TaskExecutionState
    dependency_state: str
    wave_index: int


@dataclass(frozen=True)
class ObjectiveSupervision:
    supervision_id: str
    objective_id: str
    correlation_id: str
    state: ObjectiveExecutionState
    tasks: tuple[TaskSupervision, ...]
    ready_task_ids: tuple[str, ...]
    blocked_task_ids: tuple[str, ...]
    terminal_task_ids: tuple[str, ...]
    contract_version: str = OBJECTIVE_SUPERVISOR_VERSION


def _wave_index(plan: OrchestrationPlan, task_id: str) -> int:
    for wave in plan.waves:
        if task_id in wave.task_ids:
            return wave.wave_index
    raise ObjectiveExecutionSupervisorError(f"task {task_id} missing from execution waves")


def _task_state(job: DurableJob, dep_state: str) -> TaskExecutionState:
    if dep_state.startswith("blocked_"):
        return "blocked"
    if dep_state == "waiting":
        return "waiting"
    if job.status == "completed":
        return "completed"
    if job.status in {"failed", "cancelled", "timed_out"}:
        return "failed"
    if job.status in {"leased", "running", "paused"}:
        return "running"
    return "ready"


def supervise_objective(
    *,
    plan: OrchestrationPlan,
    links: Sequence[AgentJobLink],
    jobs_by_task: Mapping[str, DurableJob],
) -> ObjectiveSupervision:
    link_map = {link.task_id: link for link in links}
    if len(link_map) != len(links):
        raise ObjectiveExecutionSupervisorError("duplicate task links")
    expected_tasks = {item.task_id for item in plan.assignments}
    if set(link_map) != expected_tasks or set(jobs_by_task) != expected_tasks:
        raise ObjectiveExecutionSupervisorError("plan, links and jobs must cover identical tasks")

    correlations = {item.correlation_id for item in plan.assignments}
    if len(correlations) != 1:
        raise ObjectiveExecutionSupervisorError("plan assignments must share one correlation_id")
    correlation_id = next(iter(correlations), "")

    task_states: list[TaskSupervision] = []
    for assignment in plan.assignments:
        link = link_map[assignment.task_id]
        job = jobs_by_task[assignment.task_id]
        if link.assignment_id != assignment.assignment_id or link.job_id != job.job_id:
            raise ObjectiveExecutionSupervisorError("assignment/job lineage mismatch")
        if job.correlation_id != correlation_id or link.correlation_id != correlation_id:
            raise ObjectiveExecutionSupervisorError("correlation lineage mismatch")
        dep_state = dependency_state(link, jobs_by_task)
        task_states.append(
            TaskSupervision(
                task_id=assignment.task_id,
                assignment_id=assignment.assignment_id,
                job_id=job.job_id,
                state=_task_state(job, dep_state),
                dependency_state=dep_state,
                wave_index=_wave_index(plan, assignment.task_id),
            )
        )

    ready = tuple(sorted(item.task_id for item in task_states if item.state == "ready"))
    blocked = tuple(sorted(item.task_id for item in task_states if item.state == "blocked"))
    terminal = tuple(
        sorted(item.task_id for item in task_states if item.state in {"completed", "failed", "blocked"})
    )

    if task_states and all(item.state == "completed" for item in task_states):
        state: ObjectiveExecutionState = "completed"
    elif any(item.state == "failed" for item in task_states):
        state = "failed"
    elif blocked:
        state = "blocked"
    elif any(item.state in {"running", "completed"} for item in task_states):
        state = "running"
    else:
        state = "pending"

    signature = "|".join(
        f"{item.task_id}:{item.state}:{item.job_id}" for item in sorted(task_states, key=lambda x: x.task_id)
    )
    supervision_id = "objective-supervision-" + sha256(
        f"{plan.plan_id}|{correlation_id}|{signature}".encode("utf-8")
    ).hexdigest()[:16]
    return ObjectiveSupervision(
        supervision_id=supervision_id,
        objective_id=plan.objective_id,
        correlation_id=correlation_id,
        state=state,
        tasks=tuple(sorted(task_states, key=lambda item: (item.wave_index, item.task_id))),
        ready_task_ids=ready,
        blocked_task_ids=blocked,
        terminal_task_ids=terminal,
    )


__all__ = [
    "OBJECTIVE_SUPERVISOR_VERSION", "ObjectiveExecutionState",
    "ObjectiveExecutionSupervisorError", "ObjectiveSupervision",
    "TaskExecutionState", "TaskSupervision", "supervise_objective",
]
