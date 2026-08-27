from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .contracts import AuthorityLevel
from .gui_policy import GuiActionRequest
from .task_orchestrator import DesktopTaskState, advance_task, replan_task
from .visual_action_verifier import VisualActionVerification, verify_gui_action
from .visual_verification import VisualRegion

FORGE_COMMANDER_TASK_STEP_RUNNER_VERSION = "forge-commander.task-step-runner.v1"

@dataclass(frozen=True, slots=True)
class TaskStepRunResult:
    state: DesktopTaskState
    verification: VisualActionVerification | None
    replanned: bool
    reason: str

def run_current_gui_step(
    state: DesktopTaskState, *, request: GuiActionRequest,
    region: VisualRegion, capture_dir: str,
    granted_authority: AuthorityLevel, approved: bool = False,
    verifier: Callable[..., VisualActionVerification] = verify_gui_action,
) -> TaskStepRunResult:
    step = state.current_step
    if step is None:
        return TaskStepRunResult(state, None, False, "task_already_complete")
    if step.kind not in {"click", "type", "hotkey"}:
        return TaskStepRunResult(state, None, False, "current_step_not_gui_action")
    if request.action_id != step.step_id:
        raise ValueError("request action_id must match current step_id")
    verification = verifier(
        request=request, region=region, capture_dir=capture_dir,
        granted_authority=granted_authority, approved=approved,
    )
    if verification.verified:
        next_state = advance_task(
            state, verified=True, evidence=verification.reason,
        )
        return TaskStepRunResult(next_state, verification, False, verification.reason)
    replanned = replan_task(state, evidence=verification.reason)
    return TaskStepRunResult(
        replanned, verification,
        replanned.replans_used > state.replans_used,
        verification.reason,
    )

__all__ = [
    "FORGE_COMMANDER_TASK_STEP_RUNNER_VERSION", "TaskStepRunResult",
    "run_current_gui_step",
]
