from __future__ import annotations

from typing import Any, Dict, List

from backend.sector_registry import SECTOR_ID_TO_LEGACY_DOMAIN, get_sector_entry


def _pick_name(names: List[str], idea: str) -> str:
    if not names:
        return "IdeasForgeAI Work Assistant"
    return names[abs(hash(idea)) % len(names)]


def create_sector_template(
    sector_result: Dict[str, Any],
    idea: str = "",
    reference_image: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    sector_id = sector_result.get("sector_id", "generic_saas")
    entry = get_sector_entry(sector_id)
    app_name = _pick_name(entry["app_name_options"], idea)
    return {
        "sector_id": entry["sector_id"],
        "sector_confidence": sector_result.get("confidence", 0),
        "sector_reasons": list(sector_result.get("reasons", [])),
        "sector_top_candidates": list(sector_result.get("top_candidates", [])),
        "clarification_needed": bool(sector_result.get("clarification_needed")),
        "clarification_prompt": sector_result.get("clarification_prompt", ""),
        "detected_domain": SECTOR_ID_TO_LEGACY_DOMAIN.get(entry["sector_id"], entry["legacy_domain"]),
        "theme_family": entry["theme_family"],
        "layout_family": entry["layout_family"],
        "visualThemeFamily": entry["theme_family"],
        "layoutVariant": entry["layout_family"],
        "app_name": app_name,
        "app_type": entry["app_type"],
        "target_users": list(entry["target_users"]),
        "core_features": list(entry["core_features"]),
        "screens": list(entry["screens"]),
        "sample_metrics": list(entry["sample_metrics"]),
        "sample_cards": list(entry["sample_cards"]),
        "cta_labels": cta_labels_for_sector(entry["sector_id"]),
        "clickable_aliases": dict(entry["clickable_aliases"]),
        "admin_dashboard_fields": list(entry["admin_dashboard_fields"]),
        "safety_rules": list(entry["safety_rules"]),
        "forbidden_outputs": list(entry["forbidden_outputs"]),
        "currency_default": entry["currency_default"],
        "preview_summary": _preview_summary(entry, app_name),
        "designInspirationNote": (
            f"Use {entry['theme_family']} with {entry['layout_family']} structure, "
            f"sector-specific screens, and clickable aliases from the registry."
        ),
        "image_guided_template": bool(reference_image),
    }


def _preview_summary(entry: Dict[str, Any], app_name: str) -> str:
    features = ", ".join(entry["core_features"][:5])
    return f"{app_name} is a {entry['app_type']} with {features}, and an admin-ready dashboard."


def cta_labels_for_sector(sector_id: str) -> List[str]:
    entry = get_sector_entry(sector_id)
    screens = entry["screens"]
    if entry["sector_id"] == "mutual_fund_advisor":
        return ["Compare Funds", "SIP Calculator", "Book Advisor"]
    if entry["sector_id"] == "insurance_broker":
        return ["Quote Builder", "Claim Tracker", "Renewals"]
    if entry["sector_id"] == "agriculture_farmer":
        return ["Crop Health", "Mandi Prices", "AI Chat"]
    return screens[1:4] if len(screens) > 3 else screens[:2]


def product_plan_from_sector(sector_result: Dict[str, Any], idea: str, reference_image: Dict[str, Any] | None = None) -> Dict[str, Any]:
    template = create_sector_template(sector_result, idea, reference_image)
    return {
        "idea": idea,
        "detected_domain": template["detected_domain"],
        "sector_id": template["sector_id"],
        "sector_confidence": template["sector_confidence"],
        "sector_reasons": template["sector_reasons"],
        "sector_top_candidates": template["sector_top_candidates"],
        "clarification_needed": template["clarification_needed"],
        "clarification_prompt": template["clarification_prompt"],
        "theme_family": template["theme_family"],
        "layout_family": template["layout_family"],
        "visualThemeFamily": template["visualThemeFamily"],
        "layoutVariant": template["layoutVariant"],
        "app_name": template["app_name"],
        "app_type": template["app_type"],
        "target_users": template["target_users"],
        "core_features": template["core_features"],
        "screens": template["screens"],
        "sample_metrics": template["sample_metrics"],
        "sample_cards": template["sample_cards"],
        "clickable_aliases": template["clickable_aliases"],
        "admin_dashboard_fields": template["admin_dashboard_fields"],
        "data_needs": template["admin_dashboard_fields"],
        "api_needs": ["backend proxy endpoint for approved submissions", "backend proxy endpoint for status sync"],
        "monetization": ["monthly subscription", "admin seat add-on", "workflow analytics add-on"],
        "preview_summary": template["preview_summary"],
        "safety_rules": template["safety_rules"],
        "forbidden_outputs": template["forbidden_outputs"],
        "next_action": "approve_generate",
    }

