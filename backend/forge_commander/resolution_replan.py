from __future__ import annotations

from dataclasses import dataclass

from .step_target_resolver import StepTargetResolution
from .task_orchestrator import DesktopTaskState, replan_task

FORGE_COMMANDER_RESOLUTION_REPLAN_VERSION = "forge-commander.resolution-replan.v1"

@dataclass(frozen=True, slots=True)
class ResolutionReplanResult:
    state: DesktopTaskState
    replanned: bool
    reason: str


def handle_resolution_result(
    state: DesktopTaskState, resolution: StepTargetResolution,
) -> ResolutionReplanResult:
    if resolution.resolved:
        return ResolutionReplanResult(state, False, "target_resolved")
    next_state = replan_task(state, evidence=resolution.reason)
    return ResolutionReplanResult(
        next_state,
        next_state.replans_used > state.replans_used,
        resolution.reason,
    )
