from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional

from backend.sector_blueprints import build_generation_hints, get_sector_blueprint


def _as_list(value: Any) -> List[Any]:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]


def _dedupe(values: List[Any]) -> List[Any]:
    seen = set()
    out: List[Any] = []
    for value in values:
        key = str(value).strip().lower()
        if key and key not in seen:
            seen.add(key)
            out.append(value)
    return out


def _detect_sector_key(plan: Dict[str, Any]) -> str:
    for key in [
        "sector_id",
        "detected_domain",
        "sector_key",
        "app_type",
        "category",
    ]:
        value = plan.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "generic_saas"


def _screen_record(screen_key: str) -> Dict[str, Any]:
    label = screen_key.replace("_", " ").title()
    return {
        "id": screen_key,
        "key": screen_key,
        "name": label,
        "title": label,
        "label": label,
    }


def apply_blueprint_to_generated_plan(
    plan: Dict[str, Any],
    user_text: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Phase 33B adapter.

    Adds sector blueprint UI guidance to generated app plans without changing
    the existing plan contract aggressively.

    Safe behavior:
    - Keeps existing fields.
    - Adds blueprint_ui and generation_hints.
    - Completes missing screens/actions/aliases using the sector blueprint.
    - Keeps generic_saas generic only when detection says generic_saas.
    """
    if not isinstance(plan, dict):
        return plan

    enriched = deepcopy(plan)
    sector_key = _detect_sector_key(enriched)
    blueprint = get_sector_blueprint(sector_key)
    hints = build_generation_hints(blueprint["sector_key"])

    enriched["sector_id"] = blueprint["sector_key"]
    enriched["detected_domain"] = blueprint["sector_key"]
    enriched.setdefault("theme_family", blueprint["theme_intent"])
    enriched.setdefault("theme_intent", blueprint["theme_intent"])
    enriched["generation_hints"] = hints

    existing_screens = _as_list(enriched.get("screens"))
    screen_values: List[Any] = existing_screens[:]

    existing_screen_keys = set()
    for screen in existing_screens:
        if isinstance(screen, dict):
            raw = screen.get("id") or screen.get("key") or screen.get("name") or screen.get("title")
        else:
            raw = screen
        if raw:
            existing_screen_keys.add(str(raw).strip().lower().replace(" ", "_"))

    for screen_key in blueprint["must_have_screens"]:
        normalized = screen_key.strip().lower()
        if normalized not in existing_screen_keys:
            screen_values.append(_screen_record(screen_key))
            existing_screen_keys.add(normalized)

    enriched["screens"] = screen_values

    enriched["dashboard_cards"] = _dedupe(
        _as_list(enriched.get("dashboard_cards")) + blueprint["dashboard_cards"]
    )

    enriched["primary_actions"] = _dedupe(
        _as_list(enriched.get("primary_actions")) + blueprint["primary_actions"]
    )

    enriched["clickable_aliases"] = _dedupe(
        _as_list(enriched.get("clickable_aliases")) + blueprint["clickable_aliases"]
    )

    enriched["domain_terms"] = _dedupe(
        _as_list(enriched.get("domain_terms")) + blueprint["domain_terms"]
    )

    enriched["sample_records"] = _dedupe(
        _as_list(enriched.get("sample_records")) + blueprint["sample_records"]
    )

    enriched["trust_and_safety_notes"] = _dedupe(
        _as_list(enriched.get("trust_and_safety_notes")) + blueprint["trust_and_safety_notes"]
    )

    enriched["blueprint_ui"] = {
        "sector_key": blueprint["sector_key"],
        "app_name_style": blueprint["app_name_style"],
        "theme_intent": blueprint["theme_intent"],
        "primary_users": blueprint["primary_users"],
        "must_have_screens": blueprint["must_have_screens"],
        "suggested_screens": blueprint["suggested_screens"],
        "dashboard_cards": blueprint["dashboard_cards"],
        "primary_actions": blueprint["primary_actions"],
        "clickable_aliases": blueprint["clickable_aliases"],
        "domain_terms": blueprint["domain_terms"],
        "sample_records": blueprint["sample_records"],
        "empty_state_guidance": blueprint["empty_state_guidance"],
        "trust_and_safety_notes": blueprint["trust_and_safety_notes"],
        "compliance_notes": blueprint.get("compliance_notes", []),
    }

    if user_text:
        enriched["blueprint_ui"]["source_prompt_hint"] = user_text[:240]

    return enriched
