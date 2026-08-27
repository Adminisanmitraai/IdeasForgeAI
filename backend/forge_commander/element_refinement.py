from __future__ import annotations

from dataclasses import dataclass, replace

from .visual_elements import VisualElement

FORGE_COMMANDER_ELEMENT_REFINEMENT_VERSION = "forge-commander.element-refinement.v1"

ROLE_WEIGHT = {
    "button": 1.00,
    "input": 0.95,
    "menu": 0.90,
    "icon": 0.72,
    "card": 0.45,
    "text_region": 0.35,
    "unknown": 0.20,
}

@dataclass(frozen=True, slots=True)
class RankedElement:
    element: VisualElement
    score: float
    rank: int
def _iou(a: VisualElement, b: VisualElement) -> float:
    left = max(a.x, b.x); top = max(a.y, b.y)
    right = min(a.x + a.width, b.x + b.width)
    bottom = min(a.y + a.height, b.y + b.height)
    inter = max(0, right-left) * max(0, bottom-top)
    if inter <= 0:
        return 0.0
    area_a = a.width * a.height
    area_b = b.width * b.height
    return inter / max(1, area_a + area_b - inter)

def _calibrated_confidence(element: VisualElement) -> float:
    score = element.confidence * ROLE_WEIGHT.get(element.role, 0.2)
    area = element.width * element.height
    if element.role == "icon" and area < 196:
        score *= 0.55
    if element.role in {"button", "input"} and element.width < 40:
        score *= 0.7
    return max(0.0, min(0.99, score))
def refine_elements(
    elements: tuple[VisualElement, ...], *, max_results: int = 16,
    overlap_threshold: float = 0.70,
) -> tuple[RankedElement, ...]:
    candidates: list[VisualElement] = []
    for element in elements:
        if element.width < 10 or element.height < 10:
            continue
        calibrated = replace(element, confidence=_calibrated_confidence(element))
        if calibrated.confidence < 0.30:
            continue
        if any(_iou(calibrated, kept) >= overlap_threshold for kept in candidates):
            continue
        candidates.append(calibrated)

    candidates.sort(
        key=lambda e: (e.confidence, ROLE_WEIGHT.get(e.role, 0.2), e.width*e.height),
        reverse=True,
    )
    return tuple(
        RankedElement(element=e, score=e.confidence, rank=i+1)
        for i, e in enumerate(candidates[:max_results])
    )
