from __future__ import annotations

from typing import Any, Dict, List

from backend.sector_registry import get_sector_entry


DEVELOPER_ONLY_LABELS = ["Data Model", "API Ready", "Monetization"]


def quality_aliases_for_sector(sector_id: str) -> Dict[str, str]:
    return get_sector_entry(sector_id).get("clickable_aliases", {})


def quality_notes_for_generated_app(plan: Dict[str, Any]) -> Dict[str, Any]:
    sector_id = plan.get("sector_id") or plan.get("detected_domain") or "generic_saas"
    entry = get_sector_entry(str(sector_id))
    aliases = dict(entry.get("clickable_aliases", {}))
    return {
        "sector_id": entry["sector_id"],
        "clickable_aliases": aliases,
        "required_screen_targets": sorted(set(aliases.values())),
        "forbidden_visible_labels": list(DEVELOPER_ONLY_LABELS),
        "raw_api_urls_visible": False,
        "frontend_secrets_allowed": False,
        "quality_rules": [
            "Every visible button, card, tab, and screen section must route to a registry-backed screen target.",
            "Do not show raw /api/runtime URLs in the generated UI.",
            "Do not show developer-only Data Model, API Ready, or Monetization sections in the preview UI.",
        ],
    }

