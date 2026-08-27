from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .contracts import AuthorityLevel
from .intent_targeting import IntentRankedElement
from .intent_task_planner import actions_from_instruction, build_plan
from .resolution_replan import handle_resolution_result
from .step_target_resolver import StepTargetResolution, resolve_step_target
from .task_orchestrator import DesktopTaskState, advance_task
from .task_step_runner import TaskStepRunResult, run_current_gui_step
from .visual_verification import VisualRegion

FORGE_COMMANDER_AUTONOMOUS_LOOP_VERSION = "forge-commander.autonomous-loop.v1"

@dataclass(frozen=True, slots=True)
class AutonomousLoopResult:
    state: DesktopTaskState
    iterations: int
    completed: bool
    blocked: bool
    reason: str

def start_task(instruction: str, *, max_steps: int = 12,
               max_replans: int = 2) -> DesktopTaskState:
    actions = actions_from_instruction(instruction)
    plan = build_plan(
        instruction, actions,
        max_steps=max_steps, max_replans=max_replans,
    )
    return DesktopTaskState(plan=plan, state="ready")


def run_task_loop(
    state: DesktopTaskState, *, candidates: tuple[IntentRankedElement, ...],
    device_id: str, target_window_id: str, region: VisualRegion,
    capture_dir: str, granted_authority: AuthorityLevel,
    approved: bool = False, max_iterations: int = 12,
    resolver: Callable[..., StepTargetResolution] = resolve_step_target,
    runner: Callable[..., TaskStepRunResult] = run_current_gui_step,
) -> AutonomousLoopResult:
    current = state
    iterations = 0
    while iterations < max_iterations:
        step = current.current_step
        if step is None or current.state == "succeeded":
            return AutonomousLoopResult(current, iterations, True, False, "task_completed")
        if current.state == "failed":
            return AutonomousLoopResult(current, iterations, False, True, current.last_evidence or "task_failed")
        iterations += 1
        if step.kind == "verify":
            current = advance_task(current, verified=True, evidence="verification_step_acknowledged")
            continue
        if step.kind not in {"click", "type"}:
            return AutonomousLoopResult(current, iterations, False, True, "unsupported_step_kind")
        resolution = resolver(
            step, candidates=candidates, device_id=device_id,
            target_window_id=target_window_id,
        )
        if not resolution.resolved or resolution.request is None:
            handed = handle_resolution_result(current, resolution)
            current = handed.state
            if not handed.replanned:
                return AutonomousLoopResult(current, iterations, False, True, handed.reason)
            continue
        run = runner(
            current, request=resolution.request, region=region,
            capture_dir=capture_dir, granted_authority=granted_authority,
            approved=approved,
        )
        current = run.state
        if run.replanned:
            continue
        if current.state == "failed":
            return AutonomousLoopResult(current, iterations, False, True, run.reason)

    return AutonomousLoopResult(
        current, iterations, False, True, "max_iterations_exhausted",
    )

__all__ = [
    "FORGE_COMMANDER_AUTONOMOUS_LOOP_VERSION", "AutonomousLoopResult",
    "start_task", "run_task_loop",
]
