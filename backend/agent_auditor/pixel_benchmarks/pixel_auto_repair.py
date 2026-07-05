from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional


ROOT = Path(__file__).resolve().parents[3]

VISUAL_REGRESSION = ROOT / "backend" / "agent_auditor" / "pixel_benchmarks" / "pixel_visual_regression.py"
EXPECTED_FILE = ROOT / "backend" / "agent_auditor" / "pixel_benchmarks" / "pixel_expected.json"

VISUAL_REGRESSION_DIR = ROOT / "backend" / "agent_audit_reports" / "pixel_visual_regression"
SAFE_CSS_PLAN_DIR = ROOT / "backend" / "agent_audit_reports" / "pixel_safe_css_plans"
DOM_MAP_DIR = ROOT / "backend" / "agent_audit_reports" / "pixel_dom_maps"
REPAIR_DIR = ROOT / "backend" / "agent_audit_reports" / "pixel_auto_repairs"


def now_stamp() -> str:
    return time.strftime("%Y%m%d-%H%M%S")


def latest_file(directory: Path, pattern: str) -> Optional[Path]:
    if not directory.exists():
        return None

    files = sorted(
        directory.glob(pattern),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )

    return files[0] if files else None


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def run_visual_regression_if_needed() -> Path:
    existing = latest_file(VISUAL_REGRESSION_DIR, "pixel-visual-regression-*.json")

    if existing:
        return existing

    result = subprocess.run(
        [sys.executable, str(VISUAL_REGRESSION)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )

    if result.returncode not in (0, 1):
        raise RuntimeError(
            "Visual regression tool failed before auto-repair planning.\n"
            f"STDOUT:\n{result.stdout[-3000:]}\n"
            f"STDERR:\n{result.stderr[-3000:]}"
        )

    created = latest_file(VISUAL_REGRESSION_DIR, "pixel-visual-regression-*.json")

    if not created:
        raise RuntimeError("Visual regression ran but no report was created.")

    return created


def load_expected_composer() -> Dict[str, int]:
    data = load_json(EXPECTED_FILE)
    return data["cases"][0]["expected"]["composer"]


def center_y(box: Dict[str, Any]) -> float:
    return (float(box["y1"]) + float(box["y2"])) / 2


def add_action(
    actions: List[Dict[str, Any]],
    issue: str,
    recommendation: str,
    region: str,
    severity: str = "medium",
    suggested_delta_px: Optional[int] = None,
    target_property: Optional[str] = None,
) -> None:
    actions.append({
        "issue": issue,
        "region": region,
        "severity": severity,
        "recommendation": recommendation,
        "suggested_delta_px": suggested_delta_px,
        "target_property": target_property,
        "approval_required": True,
        "patch_status": "suggestion_only_not_applied",
    })


def build_repair_actions(report: Dict[str, Any]) -> List[Dict[str, Any]]:
    actions: List[Dict[str, Any]] = []

    expected_composer = load_expected_composer()

    comparison = report.get("comparison", {})
    blockers = comparison.get("blockers", [])

    after = report.get("after") or report.get("before") or {}
    before = report.get("before") or {}

    checks = after.get("checks", {})
    detected = after.get("detected", {})
    composer = detected.get("composer")

    before_score = comparison.get("before_score", before.get("score", 0))
    after_score = comparison.get("after_score", after.get("score", before_score))

    if "before_baseline_failed" in blockers:
        add_action(
            actions,
            "before_baseline_failed",
            "Do not patch UI. Rebuild baseline screenshot and recalibrate expected boxes first.",
            "benchmark",
            "high",
        )

    if "after_screenshot_failed" in blockers:
        add_action(
            actions,
            "after_screenshot_failed",
            "Reject the UI patch. The after screenshot failed baseline pixel checks.",
            "full_screen",
            "high",
        )

    if "overall_pixel_score_regressed" in blockers:
        add_action(
            actions,
            "overall_pixel_score_regressed",
            f"Reject or rollback the patch. Pixel score moved from {before_score} to {after_score}.",
            "full_screen",
            "high",
        )

    if not composer:
        add_action(
            actions,
            "composer_missing",
            "Composer was not detected. Check composer selector, bottom tray visibility, and screenshot quality.",
            "composer",
            "high",
        )
    else:
        expected_center = center_y(expected_composer)
        detected_center = center_y(composer)
        delta = round(detected_center - expected_center)

        if checks.get("composer_iou", 0) < 0.70:
            if delta > 0:
                recommendation = f"Move composer upward by about {delta}px or reduce bottom offset."
                target_property = "bottom / transform translateY / margin-bottom"
                suggested_delta = -abs(delta)
            elif delta < 0:
                recommendation = f"Move composer downward by about {abs(delta)}px."
                target_property = "bottom / transform translateY / margin-bottom"
                suggested_delta = abs(delta)
            else:
                recommendation = "Composer size/width mismatch. Align tray width and height with expected composer box."
                target_property = "width / height / padding"
                suggested_delta = None

            add_action(
                actions,
                "composer_iou_below_target",
                recommendation,
                "composer",
                "high",
                suggested_delta,
                target_property,
            )

        if not checks.get("composer_above_browser_chrome", True):
            add_action(
                actions,
                "composer_enters_browser_chrome",
                "Move composer tray upward so y2 stays above browser cutoff. Do not use browser chrome as composer.",
                "composer",
                "critical",
                -32,
                "bottom / margin-bottom / safe-area-inset-bottom",
            )

        if not checks.get("not_browser_region", True):
            add_action(
                actions,
                "composer_overlaps_browser_region",
                "Reject the patch. Composer overlaps browser chrome. Increase bottom safe area and re-run Pixel UI Patch Gate.",
                "composer",
                "critical",
                -48,
                "bottom / padding-bottom / safe-area-inset-bottom",
            )

        if not checks.get("composer_tray_like_height", True):
            add_action(
                actions,
                "composer_height_not_tray_like",
                "Adjust composer tray height to a tray-like range. Avoid selecting full browser bottom area.",
                "composer",
                "medium",
                None,
                "height / padding / min-height",
            )

    if not checks.get("cards_count_ok", True):
        cards_detected = checks.get("cards_detected", 0)

        if cards_detected == 0:
            recommendation = "Cards disappeared or are not detectable. Check card selectors, card background contrast, and vertical spacing."
        else:
            recommendation = f"Cards count is {cards_detected}. Keep expected card count in range and preserve card spacing."

        add_action(
            actions,
            "cards_count_invalid",
            recommendation,
            "cards",
            "high",
            None,
            "card display / gap / opacity / background",
        )

    if "composer_iou_regressed" in blockers:
        add_action(
            actions,
            "composer_iou_regressed",
            "Rollback composer-related CSS from the patch, then apply a smaller controlled movement.",
            "composer",
            "high",
        )

    if "browser_region_overlap_regressed" in blockers:
        add_action(
            actions,
            "browser_region_overlap_regressed",
            "Increase distance from browser chrome. Composer must remain above browser cutoff.",
            "composer",
            "critical",
            -40,
            "bottom / safe-area-inset-bottom",
        )

    if not actions and report.get("ok"):
        add_action(
            actions,
            "no_repair_needed",
            "Visual regression passed. No repair is needed.",
            "system",
            "low",
        )

    return actions


def attach_latest_context() -> Dict[str, Optional[str]]:
    safe_plan = latest_file(SAFE_CSS_PLAN_DIR, "pixel-safe-css-plan-*.json")
    dom_map = latest_file(DOM_MAP_DIR, "pixel-dom-map-*.json")

    return {
        "latest_safe_css_plan": str(safe_plan) if safe_plan else None,
        "latest_dom_map": str(dom_map) if dom_map else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Pixel Agent auto-repair suggestions.")
    parser.add_argument("--report", help="Specific visual regression JSON report.")
    parser.add_argument("--fail-if-critical", action="store_true")
    args = parser.parse_args()

    if args.report:
        report_path = (ROOT / args.report).resolve()
    else:
        report_path = run_visual_regression_if_needed()

    report = load_json(report_path)
    actions = build_repair_actions(report)

    critical_count = len([a for a in actions if a.get("severity") == "critical"])
    high_count = len([a for a in actions if a.get("severity") == "high"])

    repair_required = not (
        len(actions) == 1 and actions[0].get("issue") == "no_repair_needed"
    )

    output = {
        "ok": critical_count == 0,
        "phase": "PIXEL-AGENT-11",
        "created_at": now_stamp(),
        "source_visual_regression_report": str(report_path),
        "repair_required": repair_required,
        "approval_required": True,
        "frontend_write_status": "no_frontend_files_modified",
        "critical_count": critical_count,
        "high_count": high_count,
        "actions": actions,
        "context": attach_latest_context(),
        "rule": "Auto-repair loop may suggest changes only. It must not apply frontend patches without approval.",
        "blocked_actions": [
            "auto_apply_css_repair_without_approval",
            "repair_unmapped_selector",
            "ignore_visual_regression_failure",
            "use_screenshot_as_background",
            "blind_css_override",
        ],
    }

    REPAIR_DIR.mkdir(parents=True, exist_ok=True)
    output_path = REPAIR_DIR / f"pixel-auto-repair-{now_stamp()}.json"
    output["output_path"] = str(output_path)
    output_path.write_text(json.dumps(output, indent=2), encoding="utf-8")

    print(json.dumps(output, indent=2))

    if args.fail_if_critical and critical_count > 0:
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
