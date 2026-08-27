from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from .desktop_state import WindowState
from .visual_verification import VisualRegion

FORGE_COMMANDER_VISUAL_TARGET_VERSION = "forge-commander.visual-target.v1"

@dataclass(frozen=True, slots=True)
class WindowVisualTarget:
    target_id: str
    window_id: str
    title: str
    region: VisualRegion


def target_from_window(window: WindowState, *, inset: int = 0) -> WindowVisualTarget:
    pad = max(0, int(inset))
    width = max(1, window.width - pad * 2)
    height = max(1, window.height - pad * 2)
    region = VisualRegion(
        region_id=f"region-{window.window_id}", x=window.x + pad, y=window.y + pad,
        width=width, height=height, label=window.title,
    )
    digest = sha256(
        f"{window.window_id}\n{region.x},{region.y},{region.width},{region.height}".encode()
    ).hexdigest()[:20]
    return WindowVisualTarget(
        target_id=f"fc-vtarget-{digest}", window_id=window.window_id,
        title=window.title, region=region,
    )


__all__ = [
    "FORGE_COMMANDER_VISUAL_TARGET_VERSION", "WindowVisualTarget",
    "target_from_window",
]
