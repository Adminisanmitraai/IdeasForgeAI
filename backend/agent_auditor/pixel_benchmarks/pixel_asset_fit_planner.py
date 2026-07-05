from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, Any


ROOT = Path(__file__).resolve().parents[3]

SELECTED_ROOT = ROOT / "backend" / "agent_audit_reports" / "pixel_selected_assets"
OUT_DIR = ROOT / "backend" / "agent_audit_reports" / "pixel_asset_fit_plans"


TARGETS: Dict[str, Dict[str, Any]] = {
    "header_logo": {
        "frontend_asset_path": "frontend/assets/pixel-ui-approved/header-logo.png",
        "target_file": "frontend/pages/studio-v4.html",
        "target_selector": ".if-logo",
        "css_target_file": "frontend/pages/studio-v4.css",
        "expected_css": {
            "width": "42px",
            "height": "42px",
            "border-radius": "14px",
            "object-fit": "cover"
        },
        "risk": "medium",
        "reason": "Header logo affects brand/nav visual similarity."
    },
    "forge_studio": {
        "frontend_asset_path": "frontend/assets/pixel-ui-approved/forge-studio.png",
        "target_file": "frontend/pages/studio-v4.html",
        "target_selector": ".if-studio-icon",
        "css_target_file": "frontend/pages/studio-v4.css",
        "expected_css": {
            "width": "56px",
            "height": "56px",
            "border-radius": "18px",
            "object-fit": "cover"
        },
        "risk": "medium",
        "reason": "Card icon replacement can improve visual similarity but must not move card layout."
    },
    "forge_code": {
        "frontend_asset_path": "frontend/assets/pixel-ui-approved/forge-code.png",
        "target_file": "frontend/pages/studio-v4.html",
        "target_selector": ".if-code-icon",
        "css_target_file": "frontend/pages/studio-v4.css",
        "expected_css": {
            "width": "56px",
            "height": "56px",
            "border-radius": "18px",
            "object-fit": "cover"
        },
        "risk": "medium",
        "reason": "Card icon replacement can improve visual similarity but must not move card layout."
    },
    "forge_work": {
        "frontend_asset_path": "frontend/assets/pixel-ui-approved/forge-work.png",
        "target_file": "frontend/pages/studio-v4.html",
        "target_selector": ".if-work-icon",
        "css_target_file": "frontend/pages/studio-v4.css",
        "expected_css": {
            "width": "56px",
            "height": "56px",
            "border-radius": "18px",
            "object-fit": "cover"
        },
        "risk": "high",
        "reason": "ForgeWork crop has been unstable earlier. Must be verified before apply."
    }
}


def now_stamp() -> str:
    return time.strftime("%Y%m%d-%H%M%S")


def latest_selected_report() -> Path:
    reports = sorted(
        SELECTED_ROOT.glob("selected-icon-assets-*/selected-icon-assets-report.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not reports:
        raise FileNotFoundError("No selected icon asset report found. Run PIXEL-MAP-PERFECT-16G first.")
    return reports[0]


def main() -> int:
    stamp = now_stamp()
    selected_report_path = latest_selected_report()
    selected_report = json.loads(selected_report_path.read_text(encoding="utf-8-sig"))

    selected = selected_report.get("selected", {})

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    asset_fit_plan = []

    for icon_name, target in TARGETS.items():
        selected_asset = selected.get(icon_name)

        if not selected_asset:
            asset_fit_plan.append({
                "icon": icon_name,
                "ok": False,
                "status": "missing_selected_asset",
                "approval_required": True,
                "target": target
            })
            continue

        source_path = selected_asset.get("selected_path")
        score = selected_asset.get("score", 0)

        asset_fit_plan.append({
            "icon": icon_name,
            "ok": score >= 40,
            "status": "planned_not_applied",
            "source_asset_path": source_path,
            "selection_score": score,
            "frontend_asset_path": target["frontend_asset_path"],
            "target_file": target["target_file"],
            "target_selector": target["target_selector"],
            "css_target_file": target["css_target_file"],
            "expected_css": target["expected_css"],
            "risk": target["risk"],
            "reason": target["reason"],
            "frontend_write_status": "no_frontend_files_modified",
            "approval_required": True,
            "verification_after_apply": [
                "Run pixel_dom_geometry_auditor.py",
                "Run pixel_live_match_auditor.py",
                "Reject patch if DOM score drops below current stable baseline",
                "Reject patch if card/composer geometry shifts unexpectedly"
            ]
        })

    output = {
        "ok": True,
        "phase": "PIXEL-MAP-PERFECT-16H",
        "created_at": stamp,
        "selected_report": str(selected_report_path),
        "selected_assets_dir": selected_report.get("selected_dir"),
        "frontend_write_status": "no_frontend_files_modified",
        "asset_fit_plan": asset_fit_plan,
        "blocked_actions": [
            "copy_assets_to_frontend_without_approval",
            "replace_html_icons_without_fit_plan",
            "change_layout_spacing_during_asset_apply",
            "commit_generated_audit_reports",
            "commit_failed_asset_experiments"
        ],
        "next_step": "If approved, run PIXEL-MAP-PERFECT-16I to copy selected assets and patch HTML/CSS in one reversible step."
    }

    out_path = OUT_DIR / f"pixel-asset-fit-plan-{stamp}.json"
    out_path.write_text(json.dumps(output, indent=2), encoding="utf-8")

    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
