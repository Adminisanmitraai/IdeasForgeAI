from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Iterable

from .task_orchestrator import DesktopTaskPlan, DesktopTaskState, DesktopTaskStep

FORGE_COMMANDER_INTENT_TASK_PLANNER_VERSION = "forge-commander.intent-task-planner.v1"

@dataclass(frozen=True, slots=True)
class PlannedAction:
    kind: str
    description: str
    target_id: str | None = None
    payload: str | None = None
    requires_approval: bool = False


def _step_id(goal: str, index: int, action: PlannedAction) -> str:
    raw = f"{goal}\n{index}\n{action.kind}\n{action.description}\n{action.target_id}\n{action.payload}"
    return "fc-step-" + sha256(raw.encode("utf-8")).hexdigest()[:16]
def build_plan(goal: str, actions: Iterable[PlannedAction], *, max_steps: int = 12,
               max_replans: int = 2) -> DesktopTaskPlan:
    items = tuple(actions)
    if not goal.strip():
        raise ValueError("goal is required")
    if not items:
        raise ValueError("at least one planned action is required")
    if len(items) > max_steps:
        raise ValueError("planned action count exceeds max_steps")
    steps = tuple(
        DesktopTaskStep(
            _step_id(goal, i, action), action.kind, action.description,
            action.target_id, action.payload, action.requires_approval,
        )
        for i, action in enumerate(items)
    )
    digest = sha256((goal + "\n" + "\n".join(s.step_id for s in steps)).encode("utf-8")).hexdigest()[:20]
    return DesktopTaskPlan(f"fc-plan-{digest}", goal.strip(), steps, max_replans=max_replans)


def replace_remaining_plan(state: DesktopTaskState, actions: Iterable[PlannedAction]) -> DesktopTaskState:
    replacement = build_plan(state.plan.goal, actions, max_replans=state.plan.max_replans)
    completed = state.plan.steps[:state.current_index]
    new_steps = completed + replacement.steps
    new_plan = DesktopTaskPlan(replacement.plan_id, state.plan.goal, new_steps, state.plan.max_replans)
    return DesktopTaskState(new_plan, state.current_index, state.replans_used, "ready", state.last_evidence)

def actions_from_instruction(instruction: str) -> tuple[PlannedAction, ...]:
    text = " ".join(instruction.strip().split())
    if not text:
        raise ValueError("instruction is required")
    lowered = text.lower()
    actions: list[PlannedAction] = []
    if any(word in lowered for word in ("open", "go to", "navigate")):
        actions.append(PlannedAction("click", f"navigate for: {text}", requires_approval=True))
    if any(word in lowered for word in ("change", "set", "enter", "type", "update")):
        actions.append(PlannedAction("type", f"apply requested value for: {text}", payload=text, requires_approval=True))
    actions.append(PlannedAction("verify", f"verify goal achieved: {text}"))
    if len(actions) > 4:
        raise ValueError("instruction expands beyond bounded planner limit")
    return tuple(actions)


__all__ = [
    "FORGE_COMMANDER_INTENT_TASK_PLANNER_VERSION", "PlannedAction",
    "build_plan", "replace_remaining_plan", "actions_from_instruction",
]
