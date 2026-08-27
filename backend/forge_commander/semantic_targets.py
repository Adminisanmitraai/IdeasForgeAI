from __future__ import annotations

from dataclasses import dataclass, replace
from hashlib import sha256

from .desktop_state import WindowState
from .visual_elements import VisualElement

FORGE_COMMANDER_SEMANTIC_TARGETS_VERSION = "forge-commander.semantic-targets.v1"

INTERACTIVE_ROLES = {"button", "input", "menu", "icon"}

@dataclass(frozen=True, slots=True)
class SafeClickTarget:
    target_id: str
    element_id: str
    parent_window_id: str
    role: str
    x: int
    y: int
    confidence: float
    executable: bool = False


def bind_elements_to_window(
    elements: tuple[VisualElement, ...], window: WindowState,
) -> tuple[VisualElement, ...]:
    bound: list[VisualElement] = []
    for element in elements:
        cx, cy = element.center
        inside = (
            window.x <= cx < window.x + window.width and
            window.y <= cy < window.y + window.height
        )
        if inside:
            bound.append(replace(element, parent_window_id=window.window_id))
    return tuple(bound)


def build_safe_click_targets(
    elements: tuple[VisualElement, ...], *, min_confidence: float = 0.55,
) -> tuple[SafeClickTarget, ...]:
    targets: list[SafeClickTarget] = []
    for element in elements:
        if element.role not in INTERACTIVE_ROLES:
            continue
        if element.parent_window_id is None or element.confidence < min_confidence:
            continue
        x, y = element.center
        digest = sha256(
            f"{element.element_id}\n{element.parent_window_id}\n{x},{y}".encode()
        ).hexdigest()[:20]
        targets.append(SafeClickTarget(
            target_id=f"fc-click-{digest}", element_id=element.element_id,
            parent_window_id=element.parent_window_id, role=element.role,
            x=x, y=y, confidence=element.confidence, executable=False,
        ))
    return tuple(targets)

__all__ = [
    "FORGE_COMMANDER_SEMANTIC_TARGETS_VERSION", "INTERACTIVE_ROLES",
    "SafeClickTarget", "bind_elements_to_window", "build_safe_click_targets",
]
