from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional


ROOT = Path(__file__).resolve().parents[3]

PIXEL_UI_PATCH_GATE = ROOT / "backend" / "agent_auditor" / "pixel_benchmarks" / "pixel_ui_patch_gate.py"
PIXEL_DOM_MAPPER = ROOT / "backend" / "agent_auditor" / "pixel_benchmarks" / "pixel_dom_mapper.py"

PIXEL_PATCH_PLAN_DIR = ROOT / "backend" / "agent_audit_reports" / "pixel_patch_plans"
PIXEL_DOM_MAP_DIR = ROOT / "backend" / "agent_audit_reports" / "pixel_dom_maps"
SAFE_CSS_PLAN_DIR = ROOT / "backend" / "agent_audit_reports" / "pixel_safe_css_plans"


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


def run_command(command: List[str], label: str) -> None:
    result = subprocess.run(
        command,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"{label} failed. Safe CSS patch planning is blocked.\n"
            f"STDOUT:\n{result.stdout[-4000:]}\n"
            f"STDERR:\n{result.stderr[-4000:]}"
        )


def ensure_gates() -> Dict[str, Path]:
    run_command(
        [sys.executable, str(PIXEL_UI_PATCH_GATE)],
        "Pixel UI Patch Gate",
    )

    run_command(
        [sys.executable, str(PIXEL_DOM_MAPPER)],
        "Pixel DOM Mapper",
    )

    patch_plan = latest_file(PIXEL_PATCH_PLAN_DIR, "pixel-ui-patch-plan-*.json")
    dom_map = latest_file(PIXEL_DOM_MAP_DIR, "pixel-dom-map-*.json")

    if not patch_plan:
        raise RuntimeError("No Pixel UI patch plan found after gate execution.")

    if not dom_map:
        raise RuntimeError("No Pixel DOM map found after DOM mapper execution.")

    return {
        "patch_plan": patch_plan,
        "dom_map": dom_map,
    }


def best_mapping(dom_map: Dict[str, Any], region: str) -> Optional[Dict[str, Any]]:
    regions = dom_map.get("dom_mapping", {}).get("regions", {})
    item = regions.get(region, {})

    return item.get("best_candidate")


def css_variables_for_region(patch_plan: Dict[str, Any], region: str) -> Dict[str, str]:
    suggestions = patch_plan.get("css_suggestions", {})
    variables = suggestions.get("css_variables", {})

    if region == "composer":
        keys = [
            "--pixel-composer-x",
            "--pixel-composer-y",
            "--pixel-composer-width",
            "--pixel-composer-height",
            "--pixel-composer-bottom-gap",
        ]
    elif region == "cards":
        keys = [
            "--pixel-card-x",
            "--pixel-card-width",
            "--pixel-card-count",
        ]
    elif region == "header":
        keys = [
            "--pixel-header-y",
            "--pixel-header-height",
        ]
    elif region == "hero":
        keys = [
            "--pixel-hero-y",
            "--pixel-hero-height",
        ]
    else:
        keys = []

    return {
        key: variables[key]
        for key in keys
        if key in variables
    }


def build_change(region: str, patch_plan: Dict[str, Any], dom_map: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    mapping = best_mapping(dom_map, region)

    if not mapping:
        return None

    variables = css_variables_for_region(patch_plan, region)

    if not variables:
        return None

    return {
        "region": region,
        "target_file": mapping.get("file"),
        "target_selector_or_symbol": mapping.get("selector_or_symbol"),
        "mapping_score": mapping.get("score"),
        "keyword_hits": mapping.get("keyword_hits", []),
        "change_type": "css_variable_or_selector_review",
        "suggested_css_variables": variables,
        "patch_status": "plan_only_not_applied",
        "approval_required": True,
        "reason": (
            f"Pixel Agent detected {region} region and mapped it to a real frontend selector/file. "
            "This is a reviewable patch suggestion only."
        ),
    }


def build_safe_css_plan(patch_plan: Dict[str, Any], dom_map: Dict[str, Any]) -> Dict[str, Any]:
    validation = patch_plan.get("validation", {})
    dom_mapping = dom_map.get("dom_mapping", {})

    blockers: List[str] = []

    if not patch_plan.get("ok_to_patch_ui"):
        blockers.append("pixel_ui_patch_gate_not_passed")

    if not validation.get("browser_chrome_check", {}).get("ok"):
        blockers.append("browser_chrome_check_failed")

    if validation.get("confidence_score", 0) < 80:
        blockers.append("pixel_confidence_below_80")

    if not dom_map.get("ok"):
        blockers.append("dom_mapping_gate_not_passed")

    if dom_mapping.get("confidence_score", 0) < 60:
        blockers.append("dom_mapping_confidence_below_60")

    changes = []

    for region in ["composer", "cards", "header", "hero"]:
        change = build_change(region, patch_plan, dom_map)

        if change:
            changes.append(change)

    required_regions = {"composer", "cards"}
    planned_regions = {change["region"] for change in changes}

    missing_required = sorted(required_regions - planned_regions)

    if missing_required:
        blockers.append("missing_required_patch_regions:" + ",".join(missing_required))

    ok = len(blockers) == 0

    return {
        "ok": ok,
        "approval_required": True,
        "created_at": now_stamp(),
        "phase": "PIXEL-AGENT-09",
        "summary": "Safe CSS patch plan generated from Pixel Debug Report + UI Patch Gate + DOM Mapping Gate.",
        "blockers": blockers,
        "source_reports": {
            "pixel_ui_patch_plan": patch_plan.get("pixel_report_path"),
            "pixel_overlay": patch_plan.get("pixel_overlay_path"),
            "dom_map": dom_map.get("output_path"),
        },
        "gate_scores": {
            "pixel_confidence_score": validation.get("confidence_score"),
            "dom_mapping_confidence_score": dom_mapping.get("confidence_score"),
        },
        "changes": changes,
        "frontend_write_status": "no_frontend_files_modified",
        "rollback_plan": [
            "No rollback needed because this planner does not apply changes.",
            "If a future approved patch is applied, revert only the listed target file/selector changes.",
            "Run Pixel Debug Report again after any approved UI patch.",
        ],
        "blocked_actions": [
            "apply_css_without_approval",
            "patch_unmapped_selector",
            "patch_when_pixel_gate_fails",
            "patch_when_dom_mapping_fails",
            "use_screenshot_as_background",
            "blind_css_override",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a safe CSS patch plan from Pixel Agent outputs.")
    parser.add_argument("--use-latest", action="store_true", help="Use latest existing gate reports instead of regenerating.")
    parser.add_argument("--fail-if-blocked", action="store_true", help="Exit 1 if the plan has blockers.")
    args = parser.parse_args()

    if args.use_latest:
        patch_plan_path = latest_file(PIXEL_PATCH_PLAN_DIR, "pixel-ui-patch-plan-*.json")
        dom_map_path = latest_file(PIXEL_DOM_MAP_DIR, "pixel-dom-map-*.json")

        if not patch_plan_path or not dom_map_path:
            raise SystemExit("Latest patch plan or DOM map missing. Run without --use-latest first.")
    else:
        paths = ensure_gates()
        patch_plan_path = paths["patch_plan"]
        dom_map_path = paths["dom_map"]

    patch_plan = load_json(patch_plan_path)
    dom_map = load_json(dom_map_path)

    safe_plan = build_safe_css_plan(patch_plan, dom_map)

    SAFE_CSS_PLAN_DIR.mkdir(parents=True, exist_ok=True)
    output_path = SAFE_CSS_PLAN_DIR / f"pixel-safe-css-plan-{now_stamp()}.json"

    safe_plan["output_path"] = str(output_path)
    output_path.write_text(json.dumps(safe_plan, indent=2), encoding="utf-8")

    print(json.dumps(safe_plan, indent=2))

    if args.fail_if_blocked and not safe_plan["ok"]:
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
