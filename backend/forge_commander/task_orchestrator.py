from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

FORGE_COMMANDER_TASK_ORCHESTRATOR_VERSION = "forge-commander.task-orchestrator.v1"

TaskStepKind = Literal["observe", "click", "type", "hotkey", "verify"]
TaskStepState = Literal["pending", "ready", "blocked", "succeeded", "failed"]

@dataclass(frozen=True, slots=True)
class DesktopTaskStep:
    step_id: str
    kind: TaskStepKind
    description: str
    target_id: str | None = None
    payload: str | None = None
    requires_approval: bool = False

@dataclass(frozen=True, slots=True)
class DesktopTaskPlan:
    plan_id: str
    goal: str
    steps: tuple[DesktopTaskStep, ...]
    max_replans: int = 2

@dataclass(frozen=True, slots=True)
class DesktopTaskState:
    plan: DesktopTaskPlan
    current_index: int = 0
    replans_used: int = 0
    state: TaskStepState = "pending"
    last_evidence: str | None = None

    @property
    def current_step(self) -> DesktopTaskStep | None:
        if self.current_index >= len(self.plan.steps):
            return None
        return self.plan.steps[self.current_index]


def advance_task(state: DesktopTaskState, *, verified: bool, evidence: str = "") -> DesktopTaskState:
    if not verified:
        return DesktopTaskState(
            plan=state.plan, current_index=state.current_index,
            replans_used=state.replans_used, state="failed",
            last_evidence=evidence or "verification_failed",
        )
    next_index = state.current_index + 1
    next_state: TaskStepState = "succeeded" if next_index >= len(state.plan.steps) else "ready"
    return DesktopTaskState(
        plan=state.plan, current_index=next_index,
        replans_used=state.replans_used, state=next_state,
        last_evidence=evidence or "verified",
    )


def replan_task(state: DesktopTaskState, *, evidence: str = "") -> DesktopTaskState:
    if state.replans_used >= state.plan.max_replans:
        return DesktopTaskState(
            plan=state.plan, current_index=state.current_index,
            replans_used=state.replans_used, state="failed",
            last_evidence=evidence or "replan_limit_exhausted",
        )
    return DesktopTaskState(
        plan=state.plan, current_index=state.current_index,
        replans_used=state.replans_used + 1, state="ready",
        last_evidence=evidence or "replan_requested",
    )


__all__ = [
    "FORGE_COMMANDER_TASK_ORCHESTRATOR_VERSION", "TaskStepKind",
    "TaskStepState", "DesktopTaskStep", "DesktopTaskPlan",
    "DesktopTaskState", "advance_task", "replan_task",
]
