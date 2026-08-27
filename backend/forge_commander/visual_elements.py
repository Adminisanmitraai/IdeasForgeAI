from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Literal

FORGE_COMMANDER_VISUAL_ELEMENTS_VERSION = "forge-commander.visual-elements.v2"

ElementRole = Literal["button", "input", "menu", "card", "icon", "text_region", "unknown"]

@dataclass(frozen=True, slots=True)
class VisualElement:
    element_id: str
    x: int
    y: int
    width: int
    height: int
    confidence: float
    role: ElementRole = "unknown"
    parent_window_id: str | None = None
    source: str = "edge_component"

    @property
    def center(self) -> tuple[int, int]:
        return self.x + self.width // 2, self.y + self.height // 2

def _element_id(path: str, box: tuple[int, int, int, int]) -> str:
    digest = sha256(f"{Path(path).name}\n{box}".encode()).hexdigest()[:20]
    return f"fc-element-{digest}"


def _classify(width: int, height: int, image_w: int, image_h: int) -> ElementRole:
    area = width * height
    total = max(1, image_w * image_h)
    ratio = area / total
    aspect = width / max(1, height)
    if width <= 48 and height <= 48:
        return "icon"
    if aspect <= 0.8 and height >= 96:
        return "menu"
    if aspect >= 5.0 and width >= 160 and 20 <= height <= 64:
        return "input"
    if 1.8 <= aspect <= 5.0 and 18 <= height <= 72:
        return "button"
    if ratio >= 0.08 and 0.7 <= aspect <= 4.0:
        return "card"
    if aspect >= 4.0 and height <= 40:
        return "text_region"
    return "unknown"

def discover_visual_elements(
    image_path: str, *, threshold: int = 48,
    min_width: int = 8, min_height: int = 8,
    max_elements: int = 64,
) -> tuple[VisualElement, ...]:
    from PIL import Image, ImageFilter

    image = Image.open(image_path).convert("L")
    edges = image.filter(ImageFilter.FIND_EDGES)
    mask = edges.point(lambda p: 255 if p >= threshold else 0)
    px = mask.load()
    seen: set[tuple[int, int]] = set()
    boxes: list[tuple[int, int, int, int, int]] = []

    for y in range(mask.height):
        for x in range(mask.width):
            if not px[x, y] or (x, y) in seen:
                continue
            stack = [(x, y)]
            seen.add((x, y))
            xs: list[int] = []
            ys: list[int] = []
            while stack:
                cx, cy = stack.pop()
                xs.append(cx); ys.append(cy)
                for nx, ny in ((cx-1,cy),(cx+1,cy),(cx,cy-1),(cx,cy+1)):
                    if 0 <= nx < mask.width and 0 <= ny < mask.height:
                        if px[nx, ny] and (nx, ny) not in seen:
                            seen.add((nx, ny)); stack.append((nx, ny))
            left, right = min(xs), max(xs) + 1
            top, bottom = min(ys), max(ys) + 1
            width, height = right - left, bottom - top
            if width >= min_width and height >= min_height:
                boxes.append((left, top, right, bottom, len(xs)))

    boxes.sort(key=lambda b: b[4], reverse=True)
    result: list[VisualElement] = []
    for left, top, right, bottom, edge_pixels in boxes[:max_elements]:
        width, height = right-left, bottom-top
        density = edge_pixels / max(1, width * height)
        confidence = max(0.15, min(0.99, 0.45 + density * 0.9))
        box = (left, top, right, bottom)
        result.append(VisualElement(
            element_id=_element_id(image_path, box), x=left, y=top,
            width=width, height=height, confidence=confidence,
            role=_classify(width, height, image.width, image.height),
        ))
    return tuple(result)

__all__ = [
    "FORGE_COMMANDER_VISUAL_ELEMENTS_VERSION", "ElementRole",
    "VisualElement", "discover_visual_elements",
]
