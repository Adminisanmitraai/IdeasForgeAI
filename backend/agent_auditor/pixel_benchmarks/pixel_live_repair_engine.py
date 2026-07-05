from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, Any, List


ROOT = Path(__file__).resolve().parents[3]

MATCH_DIR = ROOT / "backend" / "agent_audit_reports" / "pixel_live_match"
REPAIR_DIR = ROOT / "backend" / "agent_audit_reports" / "pixel_live_repairs"


def now_stamp() -> str:
    return time.strftime("%Y%m%d-%H%M%S")


def latest_match_report() -> Path:
    files = sorted(MATCH_DIR.glob("pixel-live-match-*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        raise FileNotFoundError(f"No live match reports found in {MATCH_DIR}")
    return files[0]


def classify(score: float) -> str:
    if score >= 86:
        return "stable"
    if score >= 75:
        return "minor_repair"
    if score >= 60:
        return "major_repair"
    return "critical_repair"


def build_region_repair(region: str, score: float) -> Dict[str, Any]:
    status = classify(score)

    repair: Dict[str, Any] = {
        "region": region,
        "score": score,
        "status": status,
        "priority": "low",
        "touch_files": ["frontend/pages/studio-v4.css"],
        "safe_to_auto_patch": False,
        "instructions": [],
    }

    if region == "hero":
        repair["priority"] = "high"
        repair["instructions"] = [
            "Tune .if-hero vertical padding, .if-hero h1 max-width, font-size, line-height, and letter-spacing.",
            "Target: heading should remain two lines and align closer to reference block.",
            "Do not make hero taller if it pushes cards into composer.",
            "Use small changes only: font-size ±1px, padding ±4px, max-width ±10px."
        ]

    elif region == "cards":
        repair["priority"] = "high"
        repair["instructions"] = [
            "Tune .if-card-list gap and .if-card min-height/padding.",
            "Target: all three cards visible above composer with same rhythm as reference.",
            "Do not increase card height if third card enters composer zone.",
            "Improve title/description alignment before changing global scale."
        ]

    elif region == "top_nav":
        repair["priority"] = "medium"
        repair["instructions"] = [
            "Tune .if-header height, logo size, menu spacing, brand text size, and action button size.",
            "Header should match reference without consuming extra vertical height.",
            "Do not change page flow until hero/cards are stable."
        ]

    elif region == "composer":
        repair["priority"] = "low" if score >= 80 else "medium"
        repair["instructions"] = [
            "Composer is close. Avoid major changes.",
            "Only tune bottom offset ±4px and height ±2px if needed after cards are stable."
        ]

    elif region == "browser_safe_area":
        repair["priority"] = "medium"
        repair["instructions"] = [
            "Bottom safe area still differs.",
            "Keep browser bar below composer and prevent overlap with third card.",
            "Only tune .if-browserbar bottom after composer/card layout is stable."
        ]

    else:
        repair["priority"] = "low"
        repair["instructions"] = [
            "Region is not a primary blocker."
        ]

    return repair


def build_css_patch_plan(report: Dict[str, Any]) -> List[Dict[str, Any]]:
    scores = report.get("region_scores", {})

    plan: List[Dict[str, Any]] = []

    hero_score = scores.get("hero", {}).get("score", 0)
    cards_score = scores.get("cards", {}).get("score", 0)
    composer_score = scores.get("composer", {}).get("score", 0)

    if hero_score < 55:
        plan.append({
            "target": ".if-hero h1",
            "intent": "Improve hero region match without changing card flow.",
            "suggested_change": {
                "font-size": "increase_or_decrease_by_1px_after_visual_check",
                "max-width": "adjust_by_8_to_12px",
                "line-height": "keep_between_1.14_and_1.18"
            },
            "approval_required": True
        })

    if cards_score < 65:
        plan.append({
            "target": ".if-card / .if-card-copy",
            "intent": "Improve card rhythm and content alignment.",
            "suggested_change": {
                "min-height": "keep_between_112px_and_122px",
                "title_font_size": "keep_between_22px_and_24px",
                "description_font_size": "keep_between_15.5px_and_16.5px",
                "gap": "keep_between_13px_and_15px"
            },
            "approval_required": True
        })

    if composer_score >= 80:
        plan.append({
            "target": ".if-composer",
            "intent": "Composer is acceptable. Freeze major composer changes.",
            "suggested_change": {
                "allowed_change": "bottom_offset_only_plus_minus_4px"
            },
            "approval_required": True
        })

    return plan


def main() -> int:
    report_path = latest_match_report()
    report = json.loads(report_path.read_text(encoding="utf-8-sig"))

    REPAIR_DIR.mkdir(parents=True, exist_ok=True)

    region_scores = report.get("region_scores", {})
    repairs = [
        build_region_repair(region, data.get("score", 0))
        for region, data in region_scores.items()
    ]

    priority_order = {"high": 0, "medium": 1, "low": 2}
    repairs.sort(key=lambda x: priority_order.get(x["priority"], 3))

    output = {
        "ok": False,
        "phase": "PIXEL-MAP-PERFECT-10",
        "created_at": now_stamp(),
        "source_match_report": str(report_path),
        "overall_ui_match_score": report.get("overall_ui_match_score"),
        "verdict": report.get("verdict"),
        "repair_strategy": "Do not guess large CSS changes. Repair highest-impact regions first and preserve already-good composer.",
        "repairs": repairs,
        "css_patch_plan": build_css_patch_plan(report),
        "blocked_actions": [
            "commit_ui_when_live_match_score_is_below_threshold",
            "make_large_css_changes_without_new_live_capture",
            "keep_appending_css_overrides_without_cleanup",
            "change_composer_majorly_when_composer_score_is_already_good"
        ],
        "next_step": "Apply a small hero/cards-only patch, capture again, and verify score improvement."
    }

    out_path = REPAIR_DIR / f"pixel-live-repair-{output['created_at']}.json"
    out_path.write_text(json.dumps(output, indent=2), encoding="utf-8")

    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
