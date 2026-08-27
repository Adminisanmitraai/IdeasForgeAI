from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from .contracts import AuthorityLevel, ForgeCommanderTask
from .desktop_state import GuiActionType
from .policy import AuthorityDecision, authorize_task

FORGE_COMMANDER_GUI_POLICY_VERSION = "forge-commander.gui-policy.v1"


@dataclass(frozen=True, slots=True)
class GuiActionRequest:
    action_id: str
    device_id: str
    action_type: GuiActionType
    target_window_id: str | None
    x: int | None = None
    y: int | None = None
    text: str | None = None
    required_authority: AuthorityLevel = "safe_execute"


@dataclass(frozen=True, slots=True)
class GuiActionDecision:
    allowed: bool
    approval_required: bool
    reason: str
    decision_id: str

def authorize_gui_action(
    request: GuiActionRequest, *, granted_authority: AuthorityLevel,
    approved: bool = False,
) -> GuiActionDecision:
    task = ForgeCommanderTask(
        task_id=request.action_id,
        device_id=request.device_id,
        action="gui_action",
        command=request.action_type,
        working_directory="desktop",
        required_authority=request.required_authority,
        visible_terminal=False,
        allow_retry=False,
    )
    base: AuthorityDecision = authorize_task(
        task, granted_authority=granted_authority, approved=approved
    )
    digest = sha256(
        f"{base.decision_id}\n{request.action_type}\n{request.target_window_id}".encode("utf-8")
    ).hexdigest()[:20]
    return GuiActionDecision(
        allowed=base.allowed,
        approval_required=base.approval_required,
        reason=base.reason,
        decision_id=f"fc-gui-{digest}",
    )


__all__ = [
    "FORGE_COMMANDER_GUI_POLICY_VERSION", "GuiActionRequest",
    "GuiActionDecision", "authorize_gui_action",
]
