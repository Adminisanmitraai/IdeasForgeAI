from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]

UI_GATE = ROOT / "backend" / "agent_auditor" / "pixel_benchmarks" / "pixel_ui_patch_gate.py"
DOM_MAPPER = ROOT / "backend" / "agent_auditor" / "pixel_benchmarks" / "pixel_dom_mapper.py"

PATCH_PLAN_DIR = ROOT / "backend" / "agent_audit_reports" / "pixel_patch_plans"
DOM_MAP_DIR = ROOT / "backend" / "agent_audit_reports" / "pixel_dom_maps"
OUTPUT_DIR = ROOT / "backend" / "agent_audit_reports" / "pixel_safe_css_plans"


def latest_file(directory: Path, pattern: str):
    if not directory.exists():
        return None
    files = sorted(directory.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def run_gate(script: Path, name: str):
    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"{name} failed. Safe CSS planning is blocked.\n"
            f"STDOUT:\n{result.stdout[-3000:]}\n"
            f"STDERR:\n{result.stderr[-3000:]}"
        )


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main() -> int:
    run_gate(UI_GATE, "Pixel UI Patch Gate")
    run_gate(DOM_MAPPER, "Pixel DOM Mapper")

    patch_plan_path = latest_file(PATCH_PLAN_DIR, "pixel-ui-patch-plan-*.json")
    dom_map_path = latest_file(DOM_MAP_DIR, "pixel-dom-map-*.json")

    if not patch_plan_path:
        raise SystemExit("Missing pixel UI patch plan.")
    if not dom_map_path:
        raise SystemExit("Missing pixel DOM map.")

    patch_plan = load_json(patch_plan_path)
    dom_map = load_json(dom_map_path)

    validation = patch_plan.get("validation", {})
    dom_mapping = dom_map.get("dom_mapping", {})
    regions = dom_mapping.get("regions", {})

    blockers = []

    if not patch_plan.get("ok_to_patch_ui"):
        blockers.append("pixel_ui_patch_gate_failed")

    if not validation.get("browser_chrome_check", {}).get("ok"):
        blockers.append("browser_chrome_check_failed")

    if validation.get("confidence_score", 0) < 80:
        blockers.append("pixel_confidence_below_80")

    if not dom_map.get("ok"):
        blockers.append("dom_mapping_gate_failed")

    changes = []

    for region in ["composer", "cards", "header", "hero"]:
        item = regions.get(region, {})
        best = item.get("best_candidate")

        if not best:
            continue

        changes.append({
            "region": region,
            "target_file": best.get("file"),
            "target_selector_or_symbol": best.get("selector_or_symbol"),
            "mapping_score": best.get("score"),
            "patch_status": "plan_only_not_applied",
            "approval_required": True
        })

    required = {"composer", "cards"}
    planned = {change["region"] for change in changes}

    missing = sorted(required - planned)
    if missing:
        blockers.append("missing_required_regions:" + ",".join(missing))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    stamp = time.strftime("%Y%m%d-%H%M%S")
    output_path = OUTPUT_DIR / f"pixel-safe-css-plan-{stamp}.json"

    plan = {
        "ok": len(blockers) == 0,
        "phase": "PIXEL-AGENT-09",
        "created_at": stamp,
        "approval_required": True,
        "frontend_write_status": "no_frontend_files_modified",
        "blockers": blockers,
        "source_reports": {
            "pixel_ui_patch_plan": str(patch_plan_path),
            "pixel_dom_map": str(dom_map_path)
        },
        "changes": changes,
        "rollback_plan": [
            "No rollback needed because this planner does not modify frontend files.",
            "Any future approved CSS patch must list exact file, selector, before/after intent, and rollback."
        ],
        "blocked_actions": [
            "apply_css_without_safe_css_patch_plan",
            "apply_css_without_human_approval",
            "patch_unmapped_selector",
            "blind_css_override"
        ],
        "output_path": str(output_path)
    }

    output_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    print(json.dumps(plan, indent=2))

    return 0 if plan["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
