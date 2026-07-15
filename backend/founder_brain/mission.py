from __future__ import annotations

from collections.abc import Mapping, Sequence

from .models import (
    FounderBrainDecisionNode,
    FounderBrainMilestoneNode,
    FounderBrainMissionGraph,
    FounderBrainMissionNode,
    FounderBrainProjectNode,
    FounderBrainTaskNode,
)

DEFAULT_MISSION_TITLE = "Build IdeasForgeAI"
DEFAULT_PROJECT_TITLE = "IdeasForgeAI"
DEFAULT_ACTIVE_MILESTONE_ID = "FOS-1B.3"
DEFAULT_ACTIVE_TASK_TITLE = "Mission, Milestone, Task & Timeline Model"
DEFAULT_NEXT_ACTION = "Continue FOS-1B.3 validation"


class MissionGraphValidationError(ValueError):
    """Raised when mission bootstrap nodes do not form a safe graph."""


_HISTORY: tuple[tuple[str, str, str, str], ...] = (
    ("FOS-1A.1", "Route Registration", "completed", "2026-07-07T09:00:00Z"),
    (
        "FOS-1A.2",
        "Workspace & Capability Catalogue",
        "completed",
        "2026-07-08T09:00:00Z",
    ),
    ("FOS-1A.3", "Desktop Integration", "completed", "2026-07-09T09:00:00Z"),
    (
        "FOS-1B.1",
        "Founder Brain Operating State",
        "completed",
        "2026-07-10T09:00:00Z",
    ),
    ("FOS-1B.2", "Capability Graph", "completed", "2026-07-12T09:00:00Z"),
    (
        "FOS-1B.3",
        DEFAULT_ACTIVE_TASK_TITLE,
        "active",
        "2026-07-13T09:00:00Z",
    ),
)


def build_bootstrap_mission_graph(
    *,
    generated_at: str,
    context: Mapping[str, object] | None = None,
) -> FounderBrainMissionGraph:
    safe_context = context if isinstance(context, Mapping) else {}
    mission_title = _safe_text(safe_context.get("mission")) or DEFAULT_MISSION_TITLE
    project_title = _safe_text(safe_context.get("project")) or DEFAULT_PROJECT_TITLE

    tasks = tuple(
        FounderBrainTaskNode(
            task_id=_task_id(milestone_id),
            milestone_id=milestone_id,
            title=title,
            description=f"Deliver {title} as a read-only Founder OS milestone.",
            status=status,
            sequence=sequence,
            risk_level="medium" if status == "active" else "low",
            capability_ids=_capability_ids(milestone_id),
            dependency_ids=(
                (_task_id(_HISTORY[sequence - 2][0]),) if sequence > 1 else ()
            ),
            approval_required=False,
            validation_state="pending" if status == "active" else "passed",
            result_reference=(
                None if status == "active" else f"milestone:{milestone_id}"
            ),
            metadata={"bootstrap": True},
        )
        for sequence, (milestone_id, title, status, _timestamp) in enumerate(
            _HISTORY, start=1
        )
    )
    milestones = tuple(
        FounderBrainMilestoneNode(
            milestone_id=milestone_id,
            project_id="ideasforgeai",
            title=title,
            description=f"Founder OS milestone {milestone_id}: {title}.",
            status=status,
            sequence=sequence,
            task_ids=(_task_id(milestone_id),),
            completed_task_count=1 if status == "completed" else 0,
            total_task_count=1,
            started_at=timestamp,
            completed_at=timestamp if status == "completed" else None,
            next_action=DEFAULT_NEXT_ACTION if status == "active" else None,
            metadata={"bootstrap": True},
        )
        for sequence, (milestone_id, title, status, timestamp) in enumerate(
            _HISTORY, start=1
        )
    )
    projects = (
        FounderBrainProjectNode(
            project_id="ideasforgeai",
            title=project_title,
            description="Founder OS platform and product development.",
            status="active",
            active_milestone_id=DEFAULT_ACTIVE_MILESTONE_ID,
            workspace_id="founder-os",
            repository_reference=None,
            metadata={"bootstrap": True},
        ),
    )
    mission = FounderBrainMissionNode(
        mission_id="ideasforgeai-mission",
        title=mission_title,
        description="Build the IdeasForgeAI Founder OS through safe milestones.",
        status="active",
        priority="high",
        project_ids=("ideasforgeai",),
        active_project_id="ideasforgeai",
        created_at="2026-07-07T09:00:00Z",
        updated_at=generated_at,
        metadata={"bootstrap": True, "durable_memory": False},
    )
    decisions = (
        FounderBrainDecisionNode(
            decision_id="decision.read-only-foundation",
            title="Keep Founder Brain read-only",
            summary="Describe executive state without activating platform work.",
            status="completed",
            scope="founder-brain",
            related_project_id="ideasforgeai",
            related_milestone_id="FOS-1B.1",
            related_task_id=_task_id("FOS-1B.1"),
            created_at="2026-07-10T08:30:00Z",
            supersedes=(),
            metadata={"bootstrap": True},
        ),
    )

    ordered = validate_mission_graph_nodes(
        mission=mission,
        projects=projects,
        milestones=milestones,
        tasks=tasks,
        decisions=decisions,
    )
    return FounderBrainMissionGraph(
        generated_at=generated_at,
        mission=mission,
        projects=ordered[0],
        milestones=ordered[1],
        tasks=ordered[2],
        decisions=ordered[3],
        active_project_id="ideasforgeai",
        active_milestone_id=DEFAULT_ACTIVE_MILESTONE_ID,
        active_task_id=_task_id(DEFAULT_ACTIVE_MILESTONE_ID),
        recommended_next_action=DEFAULT_NEXT_ACTION,
    )


def validate_mission_graph_nodes(
    *,
    mission: FounderBrainMissionNode,
    projects: Sequence[FounderBrainProjectNode],
    milestones: Sequence[FounderBrainMilestoneNode],
    tasks: Sequence[FounderBrainTaskNode],
    decisions: Sequence[FounderBrainDecisionNode],
) -> tuple[
    tuple[FounderBrainProjectNode, ...],
    tuple[FounderBrainMilestoneNode, ...],
    tuple[FounderBrainTaskNode, ...],
    tuple[FounderBrainDecisionNode, ...],
]:
    ordered_projects = tuple(sorted(projects, key=lambda item: item.project_id))
    ordered_milestones = tuple(
        sorted(milestones, key=lambda item: (item.sequence, item.milestone_id))
    )
    ordered_tasks = tuple(
        sorted(tasks, key=lambda item: (item.sequence, item.task_id))
    )
    ordered_decisions = tuple(
        sorted(decisions, key=lambda item: (item.created_at, item.decision_id))
    )

    project_ids = _unique_ids(ordered_projects, "project_id")
    milestone_ids = _unique_ids(ordered_milestones, "milestone_id")
    task_ids = _unique_ids(ordered_tasks, "task_id")
    decision_ids = _unique_ids(ordered_decisions, "decision_id")

    if set(mission.project_ids) - project_ids:
        raise MissionGraphValidationError("mission references an unknown project")
    if mission.active_project_id and mission.active_project_id not in project_ids:
        raise MissionGraphValidationError("mission active project is unknown")

    for project in ordered_projects:
        if (
            project.active_milestone_id
            and project.active_milestone_id not in milestone_ids
        ):
            raise MissionGraphValidationError("project active milestone is unknown")

    for milestone in ordered_milestones:
        if milestone.project_id not in project_ids:
            raise MissionGraphValidationError("milestone project is unknown")
        if set(milestone.task_ids) - task_ids:
            raise MissionGraphValidationError("milestone task reference is unknown")
        if (
            milestone.completed_task_count < 0
            or milestone.total_task_count != len(milestone.task_ids)
            or milestone.completed_task_count > milestone.total_task_count
        ):
            raise MissionGraphValidationError("milestone task counts are invalid")

    by_task_id = {item.task_id: item for item in ordered_tasks}
    for task in ordered_tasks:
        if task.milestone_id not in milestone_ids:
            raise MissionGraphValidationError("task milestone is unknown")
        if set(task.dependency_ids) - task_ids:
            raise MissionGraphValidationError("task dependency is unknown")

    for decision in ordered_decisions:
        if decision.related_project_id and decision.related_project_id not in project_ids:
            raise MissionGraphValidationError("decision project is unknown")
        if (
            decision.related_milestone_id
            and decision.related_milestone_id not in milestone_ids
        ):
            raise MissionGraphValidationError("decision milestone is unknown")
        if decision.related_task_id and decision.related_task_id not in task_ids:
            raise MissionGraphValidationError("decision task is unknown")
        if set(decision.supersedes) - decision_ids:
            raise MissionGraphValidationError("decision supersedes an unknown decision")

    _validate_task_cycles(by_task_id)
    return ordered_projects, ordered_milestones, ordered_tasks, ordered_decisions


def safe_empty_mission_graph(generated_at: str) -> FounderBrainMissionGraph:
    mission = FounderBrainMissionNode(
        mission_id="ideasforgeai-mission",
        title=DEFAULT_MISSION_TITLE,
        description="Static mission context is temporarily unavailable.",
        status="blocked",
        priority="high",
        project_ids=(),
        active_project_id=None,
        created_at=generated_at,
        updated_at=generated_at,
        metadata={"bootstrap": True, "durable_memory": False},
    )
    return FounderBrainMissionGraph(
        generated_at=generated_at,
        mission=mission,
        active_project_id=None,
        active_milestone_id=None,
        active_task_id=None,
        recommended_next_action=DEFAULT_NEXT_ACTION,
    )


def _unique_ids(items: Sequence[object], field: str) -> set[str]:
    identifiers: set[str] = set()
    for item in items:
        value = getattr(item, field, None)
        if not isinstance(value, str) or not value or value in identifiers:
            raise MissionGraphValidationError(f"invalid or duplicate {field}")
        identifiers.add(value)
    return identifiers


def _validate_task_cycles(tasks: Mapping[str, FounderBrainTaskNode]) -> None:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(task_id: str) -> None:
        if task_id in visiting:
            raise MissionGraphValidationError("cyclic task dependency")
        if task_id in visited:
            return
        visiting.add(task_id)
        for dependency_id in tasks[task_id].dependency_ids:
            visit(dependency_id)
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in sorted(tasks):
        visit(task_id)


def _task_id(milestone_id: str) -> str:
    return f"task.{milestone_id.lower()}"


def _capability_ids(milestone_id: str) -> tuple[str, ...]:
    if milestone_id == "FOS-1B.2":
        return ("system.registry.inspect",)
    if milestone_id == "FOS-1B.3":
        return ("system.health",)
    return ()


def _safe_text(value: object, *, limit: int = 512) -> str:
    return value.strip()[:limit] if isinstance(value, str) else ""


__all__ = [
    "DEFAULT_ACTIVE_MILESTONE_ID",
    "DEFAULT_ACTIVE_TASK_TITLE",
    "DEFAULT_MISSION_TITLE",
    "DEFAULT_NEXT_ACTION",
    "DEFAULT_PROJECT_TITLE",
    "MissionGraphValidationError",
    "build_bootstrap_mission_graph",
    "safe_empty_mission_graph",
    "validate_mission_graph_nodes",
]
