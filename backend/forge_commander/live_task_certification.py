from __future__ import annotations

from dataclasses import dataclass

from .contracts import AuthorityLevel
from .gui_policy import GuiActionRequest
from .task_orchestrator import DesktopTaskState, DesktopTaskPlan, DesktopTaskStep
from .task_step_runner import TaskStepRunResult, run_current_gui_step
from .visual_verification import VisualRegion

FORGE_COMMANDER_LIVE_CERT_VERSION = "forge-commander.live-cert.v1"

@dataclass(frozen=True, slots=True)
class LiveCertificationResult:
    switched: TaskStepRunResult
    restored: TaskStepRunResult | None
    certified: bool
    reason: str


def build_alt_tab_state() -> DesktopTaskState:
    steps = (
        DesktopTaskStep("fc-live-switch", "hotkey", "switch foreground window", payload="alt+tab", requires_approval=True),
        DesktopTaskStep("fc-live-restore", "hotkey", "restore foreground window", payload="alt+tab", requires_approval=True),
    )
    return DesktopTaskState(DesktopTaskPlan("fc-live-alt-tab", "reversible live desktop certification", steps, 0), state="ready")


def _request(step: DesktopTaskStep, device_id: str) -> GuiActionRequest:
    return GuiActionRequest(
        action_id=step.step_id, device_id=device_id,
        action_type="hotkey", target_window_id=None,
        text=step.payload, required_authority="operational",
    )


def certify_alt_tab_roundtrip(
    *, device_id: str, region: VisualRegion, capture_dir: str,
    granted_authority: AuthorityLevel = "operational", approved: bool = True,
) -> LiveCertificationResult:
    state = build_alt_tab_state()
    first = run_current_gui_step(
        state, request=_request(state.current_step, device_id), region=region,
        capture_dir=capture_dir, granted_authority=granted_authority, approved=approved,
        verifier=_settled_verifier,
    )
    if not first.verification or not first.verification.verified:
        return LiveCertificationResult(first, None, False, first.reason)
    second_step = first.state.current_step
    if second_step is None:
        return LiveCertificationResult(first, None, False, "restore_step_missing")
    second = run_current_gui_step(
        first.state, request=_request(second_step, device_id), region=region,
        capture_dir=capture_dir, granted_authority=granted_authority, approved=approved,
        verifier=_settled_verifier,
    )
    certified = second.state.state == "succeeded" and bool(second.verification and second.verification.verified)
    return LiveCertificationResult(first, second, certified, "certified" if certified else second.reason)


def _settled_verifier(*, request, region, capture_dir, granted_authority,
                      approved=False, dry_run=False, settle_seconds=0.6):
    import time
    from pathlib import Path
    from .gui_executor import execute_gui_action
    from .visual_action_verifier import VisualActionVerification
    from .visual_verification import compare_region
    from .windows_capture import capture_primary_screen

    root = Path(capture_dir).resolve()
    root.mkdir(parents=True, exist_ok=True)
    before = capture_primary_screen(str(root / f"{request.action_id}-before.png"))
    execution = execute_gui_action(
        request, granted_authority=granted_authority,
        approved=approved, dry_run=dry_run,
    )
    time.sleep(settle_seconds)
    after = capture_primary_screen(str(root / f"{request.action_id}-after.png"))
    comparison = compare_region(
        before_path=before.path, after_path=after.path,
        region=region, ratio_threshold=0.002,
    )
    verified = execution.executed and comparison.changed
    reason = "verified_visual_change" if verified else (
        execution.reason if not execution.executed else "expected_visual_change_not_detected"
    )
    return VisualActionVerification(
        request.action_id, execution.executed, verified,
        before, after, execution, comparison, reason,
    )
