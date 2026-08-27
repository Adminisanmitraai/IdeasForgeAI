from __future__ import annotations

from dataclasses import dataclass
import ctypes

from .contracts import AuthorityLevel
from .gui_policy import GuiActionRequest, authorize_gui_action
from .windows_capture import enumerate_monitors
from .windows_desktop import enumerate_visible_windows

FORGE_COMMANDER_GUI_EXECUTOR_VERSION = "forge-commander.gui-executor.v2"

@dataclass(frozen=True, slots=True)
class GuiExecutionResult:
    action_id: str
    executed: bool
    dry_run: bool
    approval_required: bool
    reason: str
    cursor_position: tuple[int, int] | None = None

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

def _cursor_position(user32) -> tuple[int, int]:
    point = POINT()
    if not user32.GetCursorPos(ctypes.byref(point)):
        raise RuntimeError("unable to read cursor position")
    return int(point.x), int(point.y)

def _coordinates_valid(x: int, y: int) -> bool:
    return any(
        m.x <= x < m.x + m.width and m.y <= y < m.y + m.height
        for m in enumerate_monitors()
    )

def _target_is_foreground(target_window_id: str | None) -> bool:
    if target_window_id is None:
        return True
    return any(
        w.window_id == target_window_id and w.active
        for w in enumerate_visible_windows()
    )

def execute_gui_action(
    request: GuiActionRequest, *, granted_authority: AuthorityLevel,
    approved: bool = False, dry_run: bool = True,
) -> GuiExecutionResult:
    decision = authorize_gui_action(
        request, granted_authority=granted_authority, approved=approved,
    )
    if not decision.allowed:
        return GuiExecutionResult(
            request.action_id, False, dry_run,
            decision.approval_required, decision.reason,
        )
    if not _target_is_foreground(request.target_window_id):
        return GuiExecutionResult(
            request.action_id, False, dry_run, False,
            "target_window_not_foreground",
        )
    if request.action_type in ("move", "click", "double_click"):
        if request.x is None or request.y is None:
            raise ValueError("x and y are required")
        if not _coordinates_valid(int(request.x), int(request.y)):
            raise ValueError("coordinates outside monitor bounds")
    if dry_run:
        return GuiExecutionResult(
            request.action_id, False, True, False,
            "authorized_dry_run",
        )

    user32 = ctypes.windll.user32
    if request.action_type == "move":
        user32.SetCursorPos(int(request.x), int(request.y))
    elif request.action_type in ("click", "double_click"):
        user32.SetCursorPos(int(request.x), int(request.y))
        count = 2 if request.action_type == "double_click" else 1
        for _ in range(count):
            user32.mouse_event(0x0002, 0, 0, 0, 0)
            user32.mouse_event(0x0004, 0, 0, 0, 0)
    elif request.action_type == "type":
        if not request.text:
            raise ValueError("text is required for type")
        for ch in request.text:
            vk = user32.VkKeyScanW(ord(ch))
            if vk == -1:
                raise ValueError(f"unsupported character: {ch!r}")
            code = vk & 0xFF
            shift = (vk >> 8) & 0xFF
            if shift & 1:
                user32.keybd_event(0x10, 0, 0, 0)
            user32.keybd_event(code, 0, 0, 0)
            user32.keybd_event(code, 0, 0x0002, 0)
            if shift & 1:
                user32.keybd_event(0x10, 0, 0x0002, 0)
    elif request.action_type == "hotkey":
        if not request.text:
            raise ValueError("text is required for hotkey")
        keys = [k.strip().lower() for k in request.text.split("+") if k.strip()]
        keymap = {
            "ctrl": 0x11, "shift": 0x10, "alt": 0x12,
            "enter": 0x0D, "esc": 0x1B, "tab": 0x09,
        }
        codes = [keymap.get(k, ord(k.upper()) if len(k) == 1 else None) for k in keys]
        if any(code is None for code in codes):
            raise ValueError("unsupported hotkey")
        for code in codes:
            user32.keybd_event(code, 0, 0, 0)
        for code in reversed(codes):
            user32.keybd_event(code, 0, 0x0002, 0)
    else:
        raise NotImplementedError(
            f"GUI action not implemented: {request.action_type}"
        )

    cursor = (
        _cursor_position(user32)
        if request.action_type in ("move", "click", "double_click")
        else None
    )
    return GuiExecutionResult(
        request.action_id, True, False, False, "executed", cursor,
    )

__all__ = [
    "FORGE_COMMANDER_GUI_EXECUTOR_VERSION", "GuiExecutionResult",
    "execute_gui_action",
]
