from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .contracts import AuthorityLevel
from .gui_executor import GuiExecutionResult, execute_gui_action
from .gui_policy import GuiActionRequest
from .visual_verification import VisualComparison, VisualRegion, compare_region
from .windows_capture import ScreenshotCapture, capture_primary_screen

FORGE_COMMANDER_VISUAL_ACTION_VERIFY_VERSION = "forge-commander.visual-action-verify.v1"

@dataclass(frozen=True, slots=True)
class VisualActionVerification:
    action_id: str
    executed: bool
    verified: bool
    before_capture: ScreenshotCapture
    after_capture: ScreenshotCapture
    execution: GuiExecutionResult
    comparison: VisualComparison
    reason: str
def verify_gui_action(
    *, request: GuiActionRequest, region: VisualRegion,
    capture_dir: str, granted_authority: AuthorityLevel,
    approved: bool = False, dry_run: bool = False,
    capture: Callable[[str], ScreenshotCapture] = capture_primary_screen,
    executor: Callable[..., GuiExecutionResult] = execute_gui_action,
    ratio_threshold: float = 0.01,
) -> VisualActionVerification:
    root = Path(capture_dir).resolve()
    root.mkdir(parents=True, exist_ok=True)
    before = capture(str(root / f"{request.action_id}-before.png"))
    execution = executor(
        request, granted_authority=granted_authority,
        approved=approved, dry_run=dry_run,
    )
    after = capture(str(root / f"{request.action_id}-after.png"))
    comparison = compare_region(
        before_path=before.path, after_path=after.path,
        region=region, ratio_threshold=ratio_threshold,
    )
    verified = execution.executed and comparison.changed
    reason = "verified_visual_change" if verified else (
        execution.reason if not execution.executed
        else "expected_visual_change_not_detected"
    )
    return VisualActionVerification(
        action_id=request.action_id, executed=execution.executed,
        verified=verified, before_capture=before, after_capture=after,
        execution=execution, comparison=comparison, reason=reason,
    )

__all__ = [
    "FORGE_COMMANDER_VISUAL_ACTION_VERIFY_VERSION",
    "VisualActionVerification", "verify_gui_action",
]
