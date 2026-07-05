from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
SCREENSHOT_DIR = ROOT / "backend" / "agent_auditor" / "pixel_benchmarks" / "screenshots"
EXPECTED_FILE = ROOT / "backend" / "agent_auditor" / "pixel_benchmarks" / "pixel_expected.json"

sys.path.insert(0, str(ROOT))


def box_iou(a: Dict[str, int], b: Dict[str, int]) -> float:
    ax1, ay1, ax2, ay2 = a["x1"], a["y1"], a["x2"], a["y2"]
    bx1, by1, bx2, by2 = b["x1"], b["y1"], b["x2"], b["y2"]

    ix1 = max(ax1, bx1)
    iy1 = max(ay1, by1)
    ix2 = min(ax2, bx2)
    iy2 = min(ay2, by2)

    if ix2 <= ix1 or iy2 <= iy1:
        return 0.0

    inter = (ix2 - ix1) * (iy2 - iy1)
    area_a = max(1, (ax2 - ax1) * (ay2 - ay1))
    area_b = max(1, (bx2 - bx1) * (by2 - by1))

    return inter / float(area_a + area_b - inter)


def center_distance_score(detected: Dict[str, int], expected: Dict[str, int], height: int) -> float:
    detected_center = (detected["y1"] + detected["y2"]) / 2
    expected_center = (expected["y1"] + expected["y2"]) / 2
    distance = abs(detected_center - expected_center)

    return max(0.0, 1.0 - (distance / max(1, height * 0.12)))


def load_expected() -> Dict[str, Any]:
    if not EXPECTED_FILE.exists():
        raise FileNotFoundError(f"Missing expected file: {EXPECTED_FILE}")

    return json.loads(EXPECTED_FILE.read_text(encoding="utf-8-sig"))


def make_agent():
    from backend.agents.pixel_matched_page_converter_agent import PixelMatchedPageConverterAgent

    try:
        return PixelMatchedPageConverterAgent()
    except TypeError:
        return PixelMatchedPageConverterAgent(project_root=str(ROOT))


def audit_case(agent, case: Dict[str, Any]) -> Dict[str, Any]:
    image_path = SCREENSHOT_DIR / case["image"]

    if not image_path.exists():
        return {
            "name": case["name"],
            "ok": False,
            "score": 0,
            "error": f"Missing screenshot: {image_path}",
        }

    img = Image.open(image_path).convert("RGB")
    width, height = img.size

    light_regions = agent._detect_light_regions(img)
    composer = agent._estimate_composer_region(img, light_regions)
    cards = agent._estimate_card_regions(img, light_regions, composer=composer)

    expected = case["expected"]
    expected_composer = expected["composer"]
    bad_region = expected.get("browser_bad_region")
    cards_min, cards_max = expected.get("cards_count_range", [2, 4])

    checks = {}
    score = 0

    checks["composer_detected"] = composer is not None
    if composer:
        score += 15

        iou = box_iou(composer, expected_composer)
        checks["composer_iou"] = round(iou, 4)

        if iou >= 0.85:
            score += 35
        elif iou >= 0.70:
            score += 28
        elif iou >= 0.55:
            score += 18
        elif iou >= 0.40:
            score += 8

        center_score = center_distance_score(composer, expected_composer, height)
        checks["composer_center_score"] = round(center_score, 4)
        score += round(center_score * 15, 2)

        browser_cutoff = min(int(height * 0.925), max(0, height - 105))
        checks["composer_above_browser_chrome"] = composer["y2"] <= browser_cutoff
        if checks["composer_above_browser_chrome"]:
            score += 15

        checks["composer_tray_like_height"] = 34 <= composer["height"] <= 210
        if checks["composer_tray_like_height"]:
            score += 10

        if bad_region:
            bad_iou = box_iou(composer, bad_region)
            checks["bad_browser_region_iou"] = round(bad_iou, 4)
            checks["not_browser_region"] = bad_iou < 0.25
            if checks["not_browser_region"]:
                score += 10
    else:
        checks["composer_iou"] = 0
        checks["composer_center_score"] = 0
        checks["composer_above_browser_chrome"] = False
        checks["composer_tray_like_height"] = False
        checks["not_browser_region"] = False

    checks["cards_detected"] = len(cards)
    checks["cards_count_ok"] = cards_min <= len(cards) <= cards_max

    if checks["cards_count_ok"]:
        score += 15

    score = round(min(100, score), 2)

    return {
        "name": case["name"],
        "ok": score >= 80,
        "score": score,
        "image_size": {
            "width": width,
            "height": height,
        },
        "detected": {
            "composer": composer,
            "cards_count": len(cards),
            "cards": cards,
            "light_regions_count": len(light_regions),
        },
        "expected": expected,
        "checks": checks,
    }


def main() -> int:
    expected = load_expected()
    cases = expected.get("cases", [])

    if not cases:
        raise SystemExit("No pixel benchmark cases found.")

    agent = make_agent()
    results: List[Dict[str, Any]] = []

    for case in cases:
        results.append(audit_case(agent, case))

    avg_score = round(sum(item["score"] for item in results) / max(1, len(results)), 2)

    report = {
        "ok": avg_score >= 80 and all(item["ok"] for item in results),
        "overall_score": avg_score,
        "accuracy_score": avg_score,
        "benchmark": "pixel_real_iou_v1",
        "cases": results,
    }

    print(json.dumps(report, indent=2))

    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
