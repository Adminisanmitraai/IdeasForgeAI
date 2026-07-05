from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SCREENSHOT = ROOT / "backend" / "agent_auditor" / "pixel_benchmarks" / "screenshots" / "chat-mobile-current.png"
REPORT_DIR = ROOT / "backend" / "agent_audit_reports" / "pixel_debug"

sys.path.insert(0, str(ROOT))


def now_stamp() -> str:
    return time.strftime("%Y%m%d-%H%M%S")


def safe_box(region: Optional[Dict[str, Any]]) -> Optional[Dict[str, int]]:
    if not region:
        return None

    required = ["x1", "y1", "x2", "y2"]
    if not all(key in region for key in required):
        return None

    return {
        "x1": int(region["x1"]),
        "y1": int(region["y1"]),
        "x2": int(region["x2"]),
        "y2": int(region["y2"]),
    }


def draw_box(draw: ImageDraw.ImageDraw, box: Dict[str, int], label: str, width: int = 4) -> None:
    x1, y1, x2, y2 = box["x1"], box["y1"], box["x2"], box["y2"]

    draw.rectangle([x1, y1, x2, y2], outline="red", width=width)

    label_bg = [x1, max(0, y1 - 28), min(x2, x1 + 260), y1]
    draw.rectangle(label_bg, fill="red")
    draw.text((x1 + 8, max(0, y1 - 24)), label, fill="white")


def make_agent():
    from backend.agents.pixel_matched_page_converter_agent import PixelMatchedPageConverterAgent

    try:
        return PixelMatchedPageConverterAgent()
    except TypeError:
        return PixelMatchedPageConverterAgent(project_root=str(ROOT))


def detect_header_region(light_regions: List[Dict[str, Any]], width: int, height: int) -> Optional[Dict[str, int]]:
    candidates = []

    for region in light_regions:
        x1 = int(region.get("x1", 0))
        y1 = int(region.get("y1", 0))
        x2 = int(region.get("x2", 0))
        y2 = int(region.get("y2", 0))

        rw = x2 - x1
        rh = y2 - y1

        if y1 > height * 0.20:
            continue

        if rw < width * 0.50:
            continue

        if rh < 35 or rh > height * 0.20:
            continue

        candidates.append({
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2,
            "width": rw,
            "height": rh,
        })

    if not candidates:
        return None

    candidates.sort(key=lambda item: (item["y1"], -item["width"]))
    return safe_box(candidates[0])


def detect_hero_region(light_regions: List[Dict[str, Any]], width: int, height: int, header: Optional[Dict[str, int]]) -> Optional[Dict[str, int]]:
    header_bottom = header["y2"] if header else int(height * 0.10)
    candidates = []

    for region in light_regions:
        x1 = int(region.get("x1", 0))
        y1 = int(region.get("y1", 0))
        x2 = int(region.get("x2", 0))
        y2 = int(region.get("y2", 0))

        rw = x2 - x1
        rh = y2 - y1

        if y1 < header_bottom:
            continue

        if y1 > height * 0.55:
            continue

        if rw < width * 0.45:
            continue

        if rh < 80 or rh > height * 0.45:
            continue

        candidates.append({
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2,
            "width": rw,
            "height": rh,
            "area": rw * rh,
        })

    if not candidates:
        return None

    candidates.sort(key=lambda item: item["area"], reverse=True)
    return safe_box(candidates[0])


def browser_chrome_check(composer: Optional[Dict[str, int]], width: int, height: int) -> Dict[str, Any]:
    if not composer:
        return {
            "ok": False,
            "reason": "composer_missing",
        }

    browser_cutoff = min(int(height * 0.925), max(0, height - 105))

    old_bad_shape = (
        composer["x1"] <= 2
        and composer["x2"] >= width - 2
        and composer["y1"] >= int(height * 0.90)
        and composer["y2"] >= height - 5
    )

    return {
        "ok": composer["y2"] <= browser_cutoff and not old_bad_shape,
        "browser_cutoff_y": browser_cutoff,
        "old_bad_shape": old_bad_shape,
        "composer_above_browser_chrome": composer["y2"] <= browser_cutoff,
    }


def build_report(image_path: Path, create_overlay: bool = True) -> Dict[str, Any]:
    if not image_path.exists():
        raise FileNotFoundError(f"Missing screenshot: {image_path}")

    image = Image.open(image_path).convert("RGB")
    width, height = image.size

    agent = make_agent()

    light_regions = agent._detect_light_regions(image)
    composer = safe_box(agent._estimate_composer_region(image, light_regions))
    cards = [safe_box(card) for card in agent._estimate_card_regions(image, light_regions, composer=composer)]
    cards = [card for card in cards if card]

    header = detect_header_region(light_regions, width, height)
    hero = detect_hero_region(light_regions, width, height, header)

    chrome = browser_chrome_check(composer, width, height)

    confidence = 0

    if composer:
        confidence += 35

    if chrome["ok"]:
        confidence += 25

    if 2 <= len(cards) <= 4:
        confidence += 20

    if header:
        confidence += 10

    if hero:
        confidence += 10

    confidence = min(100, confidence)

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = now_stamp()

    report_path = REPORT_DIR / f"pixel-debug-report-{stamp}.json"
    overlay_path = REPORT_DIR / f"pixel-debug-overlay-{stamp}.png"

    report = {
        "ok": confidence >= 80 and chrome["ok"],
        "created_at": stamp,
        "image": str(image_path),
        "image_size": {
            "width": width,
            "height": height,
        },
        "confidence_score": confidence,
        "browser_chrome_check": chrome,
        "detected": {
            "header": header,
            "hero": hero,
            "cards": cards,
            "cards_count": len(cards),
            "composer": composer,
            "light_regions_count": len(light_regions),
        },
        "outputs": {
            "report_path": str(report_path),
            "overlay_path": str(overlay_path) if create_overlay else None,
        },
    }

    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if create_overlay:
        overlay = image.copy()
        draw = ImageDraw.Draw(overlay)

        if header:
            draw_box(draw, header, "HEADER")

        if hero:
            draw_box(draw, hero, "HERO")

        for index, card in enumerate(cards, start=1):
            draw_box(draw, card, f"CARD {index}", width=3)

        if composer:
            draw_box(draw, composer, "COMPOSER", width=5)

        if chrome.get("browser_cutoff_y"):
            y = int(chrome["browser_cutoff_y"])
            draw.line([(0, y), (width, y)], fill="blue", width=3)
            draw.rectangle([0, max(0, y - 28), 280, y], fill="blue")
            draw.text((8, max(0, y - 24)), "BROWSER CUTOFF", fill="white")

        overlay.save(overlay_path)

    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Pixel Agent debug report and overlay.")
    parser.add_argument("--image", default=str(DEFAULT_SCREENSHOT))
    parser.add_argument("--no-overlay", action="store_true")
    parser.add_argument("--fail-under", type=float, default=80)
    args = parser.parse_args()

    report = build_report(Path(args.image), create_overlay=not args.no_overlay)

    print(json.dumps(report, indent=2))

    if report["confidence_score"] < args.fail_under or not report["browser_chrome_check"]["ok"]:
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
