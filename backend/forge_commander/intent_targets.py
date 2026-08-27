from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from .intent_targeting import IntentRankedElement

FORGE_COMMANDER_INTENT_TARGETS_VERSION = "forge-commander.intent-targets.v1"
INTERACTIVE_ROLES = {"button", "input", "menu", "icon"}

@dataclass(frozen=True, slots=True)
class IntentClickTarget:
    target_id: str
    element_id: str
    parent_window_id: str
    role: str
    x: int
    y: int
    score: float
    chrome_suppressed: bool
    executable: bool = False

def build_intent_click_targets(
    items: tuple[IntentRankedElement, ...], *, max_targets: int = 6,
    min_score: float = 0.50,
) -> tuple[IntentClickTarget, ...]:
    targets: list[IntentClickTarget] = []
    for item in items:
        e = item.ranked.element
        if e.role not in INTERACTIVE_ROLES:
            continue
        if e.parent_window_id is None or item.intent_score < min_score:
            continue
        x, y = e.center
        digest = sha256(
            f"{e.element_id}\n{e.parent_window_id}\n{x},{y}\n{item.intent_score:.6f}".encode()
        ).hexdigest()[:20]
        targets.append(IntentClickTarget(
            target_id=f"fc-intent-click-{digest}", element_id=e.element_id,
            parent_window_id=e.parent_window_id, role=e.role,
            x=x, y=y, score=item.intent_score,
            chrome_suppressed=item.chrome_suppressed,
        ))
        if len(targets) >= max_targets:
            break
    return tuple(targets)

__all__ = [
    "FORGE_COMMANDER_INTENT_TARGETS_VERSION", "IntentClickTarget",
    "build_intent_click_targets",
]
