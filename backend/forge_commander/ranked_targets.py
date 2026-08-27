from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from .element_refinement import RankedElement

FORGE_COMMANDER_RANKED_TARGETS_VERSION = "forge-commander.ranked-targets.v1"
INTERACTIVE_ROLES = {"button", "input", "menu", "icon"}

@dataclass(frozen=True, slots=True)
class RankedClickTarget:
    target_id: str
    element_id: str
    parent_window_id: str
    role: str
    x: int
    y: int
    score: float
    rank: int
    executable: bool = False
def build_ranked_click_targets(
    ranked: tuple[RankedElement, ...], *, max_targets: int = 8,
    min_score: float = 0.50,
) -> tuple[RankedClickTarget, ...]:
    targets: list[RankedClickTarget] = []
    for item in ranked:
        e = item.element
        if e.role not in INTERACTIVE_ROLES:
            continue
        if e.parent_window_id is None or item.score < min_score:
            continue
        x, y = e.center
        digest = sha256(
            f"{e.element_id}\n{e.parent_window_id}\n{x},{y}\n{item.rank}".encode()
        ).hexdigest()[:20]
        targets.append(RankedClickTarget(
            target_id=f"fc-ranked-click-{digest}", element_id=e.element_id,
            parent_window_id=e.parent_window_id, role=e.role,
            x=x, y=y, score=item.score, rank=item.rank,
        ))
        if len(targets) >= max_targets:
            break
    return tuple(targets)

__all__ = [
    "FORGE_COMMANDER_RANKED_TARGETS_VERSION", "RankedClickTarget",
    "build_ranked_click_targets",
]
