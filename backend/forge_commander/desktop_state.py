from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Literal

FORGE_COMMANDER_DESKTOP_STATE_VERSION = "forge-commander.desktop-state.v1"
GuiActionType = Literal["move", "click", "double_click", "type", "scroll", "hotkey"]


@dataclass(frozen=True, slots=True)
class MonitorState:
    monitor_id: str
    x: int
    y: int
    width: int
    height: int
    primary: bool = False


@dataclass(frozen=True, slots=True)
class WindowState:
    window_id: str
    title: str
    process_name: str
    x: int
    y: int
    width: int
    height: int
    active: bool = False

@dataclass(frozen=True, slots=True)
class DesktopSnapshot:
    snapshot_id: str
    monitors: tuple[MonitorState, ...]
    windows: tuple[WindowState, ...]
    active_window_id: str | None
    screenshot_path: str | None = None
    contract_version: str = FORGE_COMMANDER_DESKTOP_STATE_VERSION


def build_snapshot_id(*, monitors: tuple[MonitorState, ...], windows: tuple[WindowState, ...]) -> str:
    payload = [
        *(f"m:{m.monitor_id}:{m.x}:{m.y}:{m.width}:{m.height}:{m.primary}" for m in monitors),
        *(f"w:{w.window_id}:{w.title}:{w.process_name}:{w.x}:{w.y}:{w.width}:{w.height}:{w.active}" for w in windows),
    ]
    return "fc-screen-" + sha256("\n".join(payload).encode("utf-8")).hexdigest()[:20]


__all__ = [
    "FORGE_COMMANDER_DESKTOP_STATE_VERSION", "GuiActionType",
    "MonitorState", "WindowState", "DesktopSnapshot", "build_snapshot_id",
]
