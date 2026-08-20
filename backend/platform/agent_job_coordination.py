from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Mapping, Sequence

from backend.durable_job_store import DurableJobStore
from .agent_orchestration import (
    AgentAssignment,
    AgentDescriptor,
    AgentOrchestrationError,
    AgentTask,
    select_agent,
)
from .durable_job_runtime import append_audit_event
from .durable_jobs import DurableJob, acquire_lease

AGENT_JOB_COORDINATION_VERSION = "platform.agent-job-coordination.v1"


class AgentJobCoordinationError(RuntimeError):
    pass


@dataclass(frozen=True)
class AgentJobLink:
    assignment_id: str
    task_id: str
    agent_id: str
    job_id: str
    correlation_id: str
    dependency_task_ids: tuple[str, ...]


def _stable_id(prefix: str, *parts: str) -> str:
    digest = sha256("|".join(parts).encode("utf-8")).hexdigest()[:16]
    return f"{prefix}-{digest}"


def create_assignment_job(
    *,
    store: DurableJobStore,
    assignment: AgentAssignment,
    created_at: str,
) -> tuple[DurableJob, AgentJobLink]:
    payload = {
        "assignment_id": assignment.assignment_id,
        "task_id": assignment.task_id,
        "objective_id": assignment.objective_id,
        "agent_id": assignment.agent_id,
        "dependencies": assignment.dependency_task_ids,
    }
    job_id = _stable_id("agent-job", assignment.assignment_id)
    job = store.submit(
        job_id=job_id,
        idempotency_key=assignment.assignment_id,
        correlation_id=assignment.correlation_id,
        operation="agent_task",
        payload=payload,
        created_at=created_at,
    )
    if not job.audit_events:
        job = append_audit_event(
            job,
            event_type="agent_assignment_created",
            recorded_at=created_at,
        )
        job = store.replace(job)
    link = AgentJobLink(
        assignment_id=assignment.assignment_id,
        task_id=assignment.task_id,
        agent_id=assignment.agent_id,
        job_id=job.job_id,
        correlation_id=assignment.correlation_id,
        dependency_task_ids=assignment.dependency_task_ids,
    )
    return job, link


def dependency_state(
    link: AgentJobLink,
    jobs_by_task: Mapping[str, DurableJob],
) -> str:
    if not link.dependency_task_ids:
        return "ready"
    missing = [task_id for task_id in link.dependency_task_ids if task_id not in jobs_by_task]
    if missing:
        return "blocked_missing_dependency"
    states = [jobs_by_task[task_id].status for task_id in link.dependency_task_ids]
    if any(state in {"failed", "cancelled", "timed_out"} for state in states):
        return "blocked_failed_dependency"
    if all(state == "completed" for state in states):
        return "ready"
    return "waiting"


def route_job_to_worker(
    *,
    job: DurableJob,
    worker_id: str,
    acquired_at: str,
    expires_at: str,
) -> DurableJob:
    if job.status != "queued":
        raise AgentJobCoordinationError("only queued jobs may be routed")
    return acquire_lease(
        job,
        worker_id=worker_id,
        acquired_at=acquired_at,
        expires_at=expires_at,
    )


def reassign_agent(
    *,
    task: AgentTask,
    agents: Sequence[AgentDescriptor],
    previous_agent_ids: tuple[str, ...],
    reassignment_count: int,
    max_reassignments: int = 2,
) -> AgentDescriptor:
    if reassignment_count >= max_reassignments:
        raise AgentJobCoordinationError("agent reassignment limit reached")
    candidates = tuple(
        agent for agent in agents
        if agent.agent_id not in set(previous_agent_ids)
    )
    try:
        return select_agent(task, candidates)
    except AgentOrchestrationError as error:
        raise AgentJobCoordinationError("no alternate eligible agent") from error


def persist_routed_job(
    *,
    store: DurableJobStore,
    job: DurableJob,
    worker_id: str,
    acquired_at: str,
    expires_at: str,
) -> DurableJob:
    routed = route_job_to_worker(
        job=job,
        worker_id=worker_id,
        acquired_at=acquired_at,
        expires_at=expires_at,
    )
    routed = append_audit_event(
        routed,
        event_type=f"worker_routed:{worker_id}",
        recorded_at=acquired_at,
    )
    return store.replace(routed)


__all__ = [
    "AGENT_JOB_COORDINATION_VERSION",
    "AgentJobCoordinationError",
    "AgentJobLink",
    "create_assignment_job",
    "dependency_state",
    "persist_routed_job",
    "reassign_agent",
    "route_job_to_worker",
]
