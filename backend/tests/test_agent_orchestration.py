import pytest

from backend.platform.agent_orchestration import (
    AgentDescriptor,
    AgentOrchestrationError,
    AgentTask,
    build_execution_waves,
    build_orchestration_plan,
    select_agent,
)


def _agents():
    return (
        AgentDescriptor(
            agent_id="agent-code",
            name="Code Agent",
            capabilities=frozenset({"code.read", "code.write"}),
            trust_tier=2,
            priority=10,
        ),
        AgentDescriptor(
            agent_id="agent-read",
            name="Read Agent",
            capabilities=frozenset({"code.read"}),
            trust_tier=1,
            priority=5,
        ),
    )


def test_selector_chooses_lowest_priority_eligible_agent():
    task = AgentTask(
        task_id="task-read",
        objective_id="obj-1",
        required_capabilities=frozenset({"code.read"}),
        required_trust_tier=1,
    )
    selected = select_agent(task, _agents())
    assert selected.agent_id == "agent-read"


def test_selector_rejects_capability_overreach():
    task = AgentTask(
        task_id="task-deploy",
        objective_id="obj-1",
        required_capabilities=frozenset({"deploy.write"}),
        required_trust_tier=3,
    )
    with pytest.raises(AgentOrchestrationError):
        select_agent(task, _agents())


def test_disabled_agent_is_not_eligible():
    disabled = AgentDescriptor(
        agent_id="agent-disabled",
        name="Disabled",
        capabilities=frozenset({"code.write"}),
        trust_tier=3,
        enabled=False,
    )
    task = AgentTask(
        task_id="task-write",
        objective_id="obj-1",
        required_capabilities=frozenset({"code.write"}),
        required_trust_tier=2,
    )
    with pytest.raises(AgentOrchestrationError):
        select_agent(task, (disabled,))


def test_parallel_ready_tasks_share_first_wave():
    tasks = (
        AgentTask("a", "obj", frozenset({"code.read"}), 1),
        AgentTask("b", "obj", frozenset({"code.read"}), 1),
        AgentTask("c", "obj", frozenset({"code.write"}), 2, ("a", "b")),
    )
    waves = build_execution_waves(tasks)
    assert waves[0].task_ids == ("a", "b")
    assert waves[1].task_ids == ("c",)


def test_unknown_dependency_is_rejected():
    tasks = (
        AgentTask("a", "obj", frozenset({"code.read"}), 1, ("missing",)),
    )
    with pytest.raises(AgentOrchestrationError):
        build_execution_waves(tasks)


def test_dependency_cycle_is_rejected():
    tasks = (
        AgentTask("a", "obj", frozenset({"code.read"}), 1, ("b",)),
        AgentTask("b", "obj", frozenset({"code.read"}), 1, ("a",)),
    )
    with pytest.raises(AgentOrchestrationError):
        build_execution_waves(tasks)


def test_plan_is_deterministic_and_preserves_correlation():
    tasks = (
        AgentTask("a", "obj", frozenset({"code.read"}), 1),
        AgentTask("b", "obj", frozenset({"code.write"}), 2, ("a",)),
    )
    first = build_orchestration_plan(
        objective_id="obj", tasks=tasks, agents=_agents(), correlation_id="corr-1"
    )
    second = build_orchestration_plan(
        objective_id="obj", tasks=tasks, agents=_agents(), correlation_id="corr-1"
    )
    assert first == second
    assert first.plan_id == second.plan_id
    assert all(item.correlation_id == "corr-1" for item in first.assignments)
