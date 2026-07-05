from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from PIL import Image


ROOT = Path(__file__).resolve().parents[3]
SCREENSHOT_DIR = ROOT / "backend" / "agent_auditor" / "pixel_benchmarks" / "screenshots"
EXPECTED_FILE = ROOT / "backend" / "agent_auditor" / "pixel_benchmarks" / "pixel_expected.json"
REPORT_DIR = ROOT / "backend" / "agent_audit_reports" / "pixel_visual_regression"

DEFAULT_BEFORE = SCREENSHOT_DIR / "chat-mobile-current.png"

sys.path.insert(0, str(ROOT))


def now_stamp() -> str:
    return time.strftime("%Y%m%d-%H%M%S")


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
    return json.loads(EXPECTED_FILE.read_text(encoding="utf-8-sig"))


def make_agent():
    from backend.agents.pixel_matched_page_converter_agent import PixelMatchedPageConverterAgent

    try:
        return PixelMatchedPageConverterAgent()
    except TypeError:
        return PixelMatchedPageConverterAgent(project_root=str(ROOT))


def score_image(image_path: Path, expected: Dict[str, Any]) -> Dict[str, Any]:
    if not image_path.exists():
        return {
            "ok": False,
            "score": 0,
            "error": f"Missing screenshot: {image_path}",
        }

    agent = make_agent()

    image = Image.open(image_path).convert("RGB")
    width, height = image.size

    light_regions = agent._detect_light_regions(image)
    composer = agent._estimate_composer_region(image, light_regions)
    cards = agent._estimate_card_regions(image, light_regions, composer=composer)

    expected_composer = expected["composer"]
    bad_region = expected.get("browser_bad_region")
    cards_min, cards_max = expected.get("cards_count_range", [2, 4])

    checks: Dict[str, Any] = {}
    score = 0

    checks["composer_detected"] = composer is not None

    if composer:
        score += 15

        composer_iou = box_iou(composer, expected_composer)
        checks["composer_iou"] = round(composer_iou, 4)

        if composer_iou >= 0.85:
            score += 35
        elif composer_iou >= 0.70:
            score += 28
        elif composer_iou >= 0.55:
            score += 18
        elif composer_iou >= 0.40:
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
            checks["bad_browser_region_iou"] = None
            checks["not_browser_region"] = True
    else:
        checks["composer_iou"] = 0
        checks["composer_center_score"] = 0
        checks["composer_above_browser_chrome"] = False
        checks["composer_tray_like_height"] = False
        checks["bad_browser_region_iou"] = None
        checks["not_browser_region"] = False

    checks["cards_detected"] = len(cards)
    checks["cards_count_ok"] = cards_min <= len(cards) <= cards_max

    if checks["cards_count_ok"]:
        score += 15

    score = round(min(100, score), 2)

    return {
        "ok": score >= 80,
        "image": str(image_path),
        "image_size": {
            "width": width,
            "height": height,
        },
        "score": score,
        "detected": {
            "composer": composer,
            "cards_count": len(cards),
            "cards": cards,
            "light_regions_count": len(light_regions),
        },
        "checks": checks,
    }


def compare_scores(before: Dict[str, Any], after: Dict[str, Any], tolerance: float) -> Dict[str, Any]:
    blockers: List[str] = []

    if not before.get("ok"):
        blockers.append("before_baseline_failed")

    if not after.get("ok"):
        blockers.append("after_screenshot_failed")

    before_score = float(before.get("score", 0))
    after_score = float(after.get("score", 0))

    if after_score + tolerance < before_score:
        blockers.append("overall_pixel_score_regressed")

    before_checks = before.get("checks", {})
    after_checks = after.get("checks", {})

    if not after_checks.get("not_browser_region"):
        blockers.append("after_composer_matches_browser_region")

    if not after_checks.get("composer_above_browser_chrome"):
        blockers.append("after_composer_includes_browser_chrome")

    if not after_checks.get("cards_count_ok"):
        blockers.append("after_cards_count_invalid")

    if after_checks.get("composer_iou", 0) + 0.05 < before_checks.get("composer_iou", 0):
        blockers.append("composer_iou_regressed")

    if after_checks.get("bad_browser_region_iou", 0) > max(
        0.25,
        before_checks.get("bad_browser_region_iou", 0) + 0.08,
    ):
        blockers.append("browser_region_overlap_regressed")

    return {
        "ok": len(blockers) == 0,
        "blockers": blockers,
        "before_score": before_score,
        "after_score": after_score,
        "score_delta": round(after_score - before_score, 2),
        "before_checks": before_checks,
        "after_checks": after_checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Pixel Agent visual regression test.")
    parser.add_argument("--before", default=str(DEFAULT_BEFORE))
    parser.add_argument("--after", help="After-patch screenshot. If omitted, baseline-only mode is used.")
    parser.add_argument("--tolerance", type=float, default=2.0)
    parser.add_argument("--fail-if-regressed", action="store_true")
    args = parser.parse_args()

    expected_data = load_expected()
    case = expected_data["cases"][0]
    expected = case["expected"]

    before = score_image((ROOT / args.before).resolve() if not Path(args.before).is_absolute() else Path(args.before), expected)

    if args.after:
        after_path = (ROOT / args.after).resolve() if not Path(args.after).is_absolute() else Path(args.after)
        after = score_image(after_path, expected)
        comparison = compare_scores(before, after, args.tolerance)
        mode = "before_after_regression"
    else:
        after = None
        comparison = {
            "ok": before.get("ok", False),
            "blockers": [] if before.get("ok", False) else ["baseline_failed"],
            "before_score": before.get("score", 0),
            "after_score": None,
            "score_delta": None,
            "note": "Baseline-only mode. Provide --after after an approved UI patch.",
        }
        mode = "baseline_only"

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = now_stamp()
    report_path = REPORT_DIR / f"pixel-visual-regression-{stamp}.json"

    report = {
        "ok": comparison["ok"],
        "phase": "PIXEL-AGENT-10",
        "mode": mode,
        "created_at": stamp,
        "rule": "After any approved UI patch, after screenshot must not regress composer/card/browser-chrome detection.",
        "before": before,
        "after": after,
        "comparison": comparison,
        "approval_status": "visual_regression_required_before_accepting_ui_patch",
        "frontend_write_status": "no_frontend_files_modified",
        "output_path": str(report_path),
    }

    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(json.dumps(report, indent=2))

    if args.fail_if_regressed and not report["ok"]:
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
