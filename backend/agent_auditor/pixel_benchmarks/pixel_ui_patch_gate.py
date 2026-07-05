from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional


ROOT = Path(__file__).resolve().parents[3]
PIXEL_DEBUG_SCRIPT = ROOT / "backend" / "agent_auditor" / "pixel_benchmarks" / "pixel_debug_report.py"
PIXEL_DEBUG_DIR = ROOT / "backend" / "agent_audit_reports" / "pixel_debug"
PATCH_PLAN_DIR = ROOT / "backend" / "agent_audit_reports" / "pixel_patch_plans"

DEFAULT_MIN_CONFIDENCE = 80


def latest_report() -> Optional[Path]:
    if not PIXEL_DEBUG_DIR.exists():
        return None

    reports = sorted(
        PIXEL_DEBUG_DIR.glob("pixel-debug-report-*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    return reports[0] if reports else None


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def run_pixel_debug_report() -> Dict[str, Any]:
    result = subprocess.run(
        [sys.executable, str(PIXEL_DEBUG_SCRIPT)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "Pixel debug report failed. UI patch is blocked.\n"
            f"STDOUT:\n{result.stdout[-3000:]}\n"
            f"STDERR:\n{result.stderr[-3000:]}"
        )

    report_path = latest_report()

    if not report_path:
        raise RuntimeError("Pixel debug report passed but no report file was found.")

    return load_json(report_path)


def build_css_variables(report: Dict[str, Any]) -> Dict[str, Any]:
    detected = report.get("detected", {})
    size = report.get("image_size", {})

    width = int(size.get("width", 0))
    height = int(size.get("height", 0))

    composer = detected.get("composer")
    cards = detected.get("cards", [])
    header = detected.get("header")
    hero = detected.get("hero")

    css = {}

    if header:
        css["--pixel-header-y"] = f'{header["y1"]}px'
        css["--pixel-header-height"] = f'{header["y2"] - header["y1"]}px'

    if hero:
        css["--pixel-hero-y"] = f'{hero["y1"]}px'
        css["--pixel-hero-height"] = f'{hero["y2"] - hero["y1"]}px'

    if composer:
        css["--pixel-composer-x"] = f'{composer["x1"]}px'
        css["--pixel-composer-y"] = f'{composer["y1"]}px'
        css["--pixel-composer-width"] = f'{composer["x2"] - composer["x1"]}px'
        css["--pixel-composer-height"] = f'{composer["y2"] - composer["y1"]}px'

        if height:
            bottom_gap = height - composer["y2"]
            css["--pixel-composer-bottom-gap"] = f"{bottom_gap}px"

    if cards:
        first = cards[0]
        css["--pixel-card-x"] = f'{first["x1"]}px'
        css["--pixel-card-width"] = f'{first["x2"] - first["x1"]}px'
        css["--pixel-card-count"] = str(len(cards))

    return {
        "viewport": {
            "width": width,
            "height": height,
        },
        "css_variables": css,
    }


def validate_report(report: Dict[str, Any], min_confidence: float) -> Dict[str, Any]:
    confidence = float(report.get("confidence_score", 0))
    chrome = report.get("browser_chrome_check", {})
    detected = report.get("detected", {})

    composer = detected.get("composer")
    cards_count = int(detected.get("cards_count", 0))

    blockers = []

    if confidence < min_confidence:
        blockers.append(f"confidence_below_{min_confidence}")

    if not chrome.get("ok"):
        blockers.append("browser_chrome_check_failed")

    if not composer:
        blockers.append("composer_missing")

    if not (2 <= cards_count <= 4):
        blockers.append("cards_count_not_in_expected_range")

    return {
        "ok": len(blockers) == 0,
        "blockers": blockers,
        "confidence_score": confidence,
        "browser_chrome_check": chrome,
        "composer": composer,
        "cards_count": cards_count,
    }


def write_patch_plan(report: Dict[str, Any], validation: Dict[str, Any]) -> Path:
    PATCH_PLAN_DIR.mkdir(parents=True, exist_ok=True)

    stamp = time.strftime("%Y%m%d-%H%M%S")
    path = PATCH_PLAN_DIR / f"pixel-ui-patch-plan-{stamp}.json"

    plan = {
        "ok_to_patch_ui": validation["ok"],
        "created_at": stamp,
        "rule": "UI patch allowed only when Pixel Debug Report passes.",
        "validation": validation,
        "pixel_report_path": report.get("outputs", {}).get("report_path"),
        "pixel_overlay_path": report.get("outputs", {}).get("overlay_path"),
        "detected": report.get("detected", {}),
        "css_suggestions": build_css_variables(report),
        "blocked_actions": [
            "blind_css_patch",
            "use_screenshot_as_background",
            "patch_ui_when_browser_chrome_check_fails",
            "patch_ui_when_confidence_below_threshold",
        ],
    }

    path.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Gate UI patches using Pixel Debug Report.")
    parser.add_argument("--use-latest", action="store_true")
    parser.add_argument("--min-confidence", type=float, default=DEFAULT_MIN_CONFIDENCE)
    args = parser.parse_args()

    if args.use_latest:
        report_path = latest_report()

        if not report_path:
            raise SystemExit("No latest Pixel Debug Report found. Run without --use-latest first.")

        report = load_json(report_path)
    else:
        report = run_pixel_debug_report()

    validation = validate_report(report, min_confidence=args.min_confidence)
    plan_path = write_patch_plan(report, validation)

    output = {
        "ok": validation["ok"],
        "message": "UI patch gate passed." if validation["ok"] else "UI patch is blocked.",
        "patch_plan_path": str(plan_path),
        "validation": validation,
    }

    print(json.dumps(output, indent=2))

    return 0 if validation["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

