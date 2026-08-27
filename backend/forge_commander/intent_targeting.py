from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .desktop_state import WindowState
from .element_refinement import RankedElement

FORGE_COMMANDER_INTENT_TARGETING_VERSION = "forge-commander.intent-targeting.v1"

TargetIntent = Literal["page_content", "browser_chrome", "form_input", "navigation", "generic"]

@dataclass(frozen=True, slots=True)
class IntentRankedElement:
    ranked: RankedElement
    intent_score: float
    chrome_suppressed: bool

def _role_boost(role: str, intent: TargetIntent) -> float:
    if intent == "form_input":
        return {"input": 1.35, "button": 1.20}.get(role, 0.85)
    if intent == "navigation":
        return {"menu": 1.30, "button": 1.15}.get(role, 0.90)
    if intent == "browser_chrome":
        return 1.15 if role in {"icon", "input", "button"} else 0.90
    if intent == "page_content":
        return 1.15 if role in {"button", "input", "menu", "card"} else 0.82
    return 1.0

def rank_for_intent(
    ranked: tuple[RankedElement, ...], *, window: WindowState,
    intent: TargetIntent = "page_content", chrome_height: int = 88,
    max_results: int = 12,
) -> tuple[IntentRankedElement, ...]:
    items: list[IntentRankedElement] = []
    chrome_bottom = window.y + max(0, chrome_height)
    for item in ranked:
        e = item.element
        _, cy = e.center
        in_chrome = cy < chrome_bottom
        score = item.score * _role_boost(e.role, intent)
        suppressed = False
        if intent != "browser_chrome" and in_chrome:
            score *= 0.28
            suppressed = True
        if intent == "page_content" and e.role == "icon":
            score *= 0.72
        score = max(0.0, min(0.99, score))
        items.append(IntentRankedElement(item, score, suppressed))
    items.sort(key=lambda i: (i.intent_score, i.ranked.score), reverse=True)
    return tuple(items[:max_results])

__all__ = [
    "FORGE_COMMANDER_INTENT_TARGETING_VERSION", "TargetIntent",
    "IntentRankedElement", "rank_for_intent",
]
