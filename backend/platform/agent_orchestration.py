from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from typing import FrozenSet, Literal, Mapping, Sequence

AGENT_ORCHESTRATION_VERSION = "platform.agent-orchestration.v1"
TrustTier = Literal[0, 1, 2, 3]


class AgentOrchestrationError(RuntimeError):
    pass


@dataclass(frozen=True)
class AgentDescriptor:
    agent_id: str
    name: str
    capabilities: FrozenSet[str]
    trust_tier: TrustTier
    enabled: bool = True
    priority: int = 100
    metadata: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class AgentTask:
    task_id: str
    objective_id: str
    required_capabilities: FrozenSet[str]
    required_trust_tier: TrustTier
    dependency_task_ids: tuple[str, ...] = ()
    priority: int = 100


@dataclass(frozen=True)
class AgentAssignment:
    assignment_id: str
    task_id: str
    objective_id: str
    agent_id: str
    selected_capabilities: FrozenSet[str]
    trust_tier: TrustTier
    dependency_task_ids: tuple[str, ...]
    correlation_id: str


@dataclass(frozen=True)
class OrchestrationWave:
    wave_index: int
    task_ids: tuple[str, ...]


@dataclass(frozen=True)
class OrchestrationPlan:
    plan_id: str
    objective_id: str
    assignments: tuple[AgentAssignment, ...]
    waves: tuple[OrchestrationWave, ...]
    blocked_task_ids: tuple[str, ...] = ()
    contract_version: str = AGENT_ORCHESTRATION_VERSION


def _validate_unique_agents(agents: Sequence[AgentDescriptor]) -> None:
    ids = [agent.agent_id for agent in agents]
    if len(ids) != len(set(ids)):
        raise AgentOrchestrationError("duplicate agent_id")


def select_agent(
    task: AgentTask,
    agents: Sequence[AgentDescriptor],
) -> AgentDescriptor:
    _validate_unique_agents(agents)
    eligible = [
        agent for agent in agents
        if agent.enabled
        and agent.trust_tier >= task.required_trust_tier
        and task.required_capabilities <= agent.capabilities
    ]
    if not eligible:
        raise AgentOrchestrationError(f"no eligible agent for task {task.task_id}")
    eligible.sort(
        key=lambda agent: (
            agent.priority,
            agent.trust_tier,
            agent.agent_id,
        )
    )
    return eligible[0]


def build_execution_waves(tasks: Sequence[AgentTask]) -> tuple[OrchestrationWave, ...]:
    task_map = {task.task_id: task for task in tasks}
    if len(task_map) != len(tasks):
        raise AgentOrchestrationError("duplicate task_id")
    unknown = {
        dependency
        for task in tasks
        for dependency in task.dependency_task_ids
        if dependency not in task_map
    }
    if unknown:
        raise AgentOrchestrationError(
            f"unknown task dependencies: {tuple(sorted(unknown))}"
        )
    remaining = set(task_map)
    completed: set[str] = set()
    waves: list[OrchestrationWave] = []
    while remaining:
        ready = sorted(
            task_id for task_id in remaining
            if set(task_map[task_id].dependency_task_ids) <= completed
        )
        if not ready:
            raise AgentOrchestrationError("task dependency cycle detected")
        waves.append(OrchestrationWave(len(waves) + 1, tuple(ready)))
        completed.update(ready)
        remaining.difference_update(ready)
    return tuple(waves)


def build_orchestration_plan(
    *,
    objective_id: str,
    tasks: Sequence[AgentTask],
    agents: Sequence[AgentDescriptor],
    correlation_id: str,
) -> OrchestrationPlan:
    waves = build_execution_waves(tasks)
    assignments: list[AgentAssignment] = []
    for task in sorted(tasks, key=lambda item: (item.priority, item.task_id)):
        agent = select_agent(task, agents)
        assignments.append(
            AgentAssignment(
                assignment_id=f"assign-{objective_id}-{task.task_id}-{agent.agent_id}",
                task_id=task.task_id,
                objective_id=objective_id,
                agent_id=agent.agent_id,
                selected_capabilities=task.required_capabilities,
                trust_tier=agent.trust_tier,
                dependency_task_ids=task.dependency_task_ids,
                correlation_id=correlation_id,
            )
        )
    signature = "|".join(item.assignment_id for item in assignments)
    return OrchestrationPlan(
        plan_id=f"agent-plan-{sha256(signature.encode('utf-8')).hexdigest()[:16]}",
        objective_id=objective_id,
        assignments=tuple(assignments),
        waves=waves,
    )
