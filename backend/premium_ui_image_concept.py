from __future__ import annotations

from typing import Any, Dict, List


def _clean_text(value: Any, fallback: str = "") -> str:
    if isinstance(value, str):
        cleaned = " ".join(value.split())
        return cleaned or fallback
    return fallback


def _clean_list(value: Any) -> List[str]:
    if isinstance(value, list):
        return [_clean_text(item) for item in value if _clean_text(item)]
    if isinstance(value, str):
        cleaned = _clean_text(value)
        return [cleaned] if cleaned else []
    return []


SECTOR_IMAGE_FIRST_PRESETS: Dict[str, Dict[str, Any]] = {
    "school_teacher_parent": {
        "style_label": "Education blue clarity",
        "color_story": "education-blue, paper-white, slate text, soft cyan accents",
        "surface_style": "layered cards with clean tutor dashboard sections",
        "layout_targets": [
            "mobile tutor dashboard hero with student and class snapshot cards",
            "class schedule strip above homework and attendance cards",
            "fee reminders and parent message queue in the first fold",
            "student progress and test result cards in a compact analytics row",
        ],
        "required_visible_content": [
            "students",
            "class schedule",
            "homework",
            "attendance",
            "fee reminders",
            "parent messages",
            "progress tracking",
        ],
        "prompt_phrases": [
            "premium tutor dashboard",
            "students",
            "class schedule",
            "homework",
            "attendance",
            "fee reminders",
            "parent messages",
            "progress tracking",
            "clean education-blue theme",
        ],
    },
    "wedding_event_lawn": {
        "style_label": "Plum champagne luxury",
        "color_story": "plum, champagne, warm ivory, brushed gold accents",
        "surface_style": "premium event cards with elegant booking and showcase sections",
        "layout_targets": [
            "venue dashboard hero with booking calendar and lead pipeline",
            "package showcase cards paired with decor theme gallery",
            "vendor task ribbon and site visit schedule panel",
            "payment progress card stack with premium event overview",
        ],
        "required_visible_content": [
            "event calendar",
            "package showcase",
            "decor themes",
            "vendor tasks",
            "payment progress",
            "lead pipeline",
            "site visit schedule",
        ],
        "prompt_phrases": [
            "premium wedding venue dashboard",
            "event calendar",
            "package showcase",
            "decor themes",
            "vendor tasks",
            "payment progress",
            "lead pipeline",
            "site visit schedule",
            "plum champagne gold theme",
        ],
    },
    "agriculture_farmer": {
        "style_label": "Advisory green field intelligence",
        "color_story": "green agri theme with earthy neutrals and weather-safe contrast",
        "surface_style": "field-ready advisory dashboard cards with mobile-first density",
        "layout_targets": [
            "mobile farm dashboard hero with crop and weather cards",
            "mandi price and buyer connect cards near top actions",
            "farm task list and advisory panel in the mid fold",
            "crop health and weather intelligence sections with grounded agri visuals",
        ],
        "required_visible_content": [
            "crop health",
            "weather",
            "mandi price",
            "farm tasks",
            "buyer connect",
            "advisory style",
        ],
        "prompt_phrases": [
            "premium farmer advisory dashboard",
            "crop health",
            "weather",
            "mandi price",
            "farm tasks",
            "buyer connect",
            "advisory style",
            "green agri theme",
        ],
    },
    "mutual_fund_advisor": {
        "style_label": "Compliance-safe wealth trust",
        "color_story": "deep blue, restrained green, mist white, finance trust contrast",
        "surface_style": "clean wealth advisory cards with trust-forward metrics",
        "layout_targets": [
            "advisor dashboard hero with AUM and SIP book metrics",
            "portfolio review and risk profile cards above action queue",
            "compliance-safe investor guidance panel without return promises",
            "meeting and follow-up blocks next to client review summaries",
        ],
        "required_visible_content": [
            "AUM",
            "SIP book",
            "portfolio review",
            "risk profile",
            "compliance-safe messaging",
        ],
        "prompt_phrases": [
            "premium mutual fund advisor dashboard",
            "AUM",
            "SIP book",
            "portfolio review",
            "risk profile",
            "compliance-safe messaging",
            "avoid return promises",
        ],
    },
    "generic_saas": {
        "style_label": "Polished workflow SaaS",
        "color_story": "neutral graphite, cloud white, crisp accent blue",
        "surface_style": "balanced metric cards with premium workflow hierarchy",
        "layout_targets": [
            "hero dashboard with primary workflow metrics",
            "feature grid paired with action queue",
            "records and approval states in modular cards",
            "clean desktop and mobile balance without false sector claims",
        ],
        "required_visible_content": [
            "dashboard metrics",
            "workflow actions",
            "approval states",
            "records",
        ],
        "prompt_phrases": [
            "polished SaaS dashboard",
            "workflow metrics",
            "approval states",
            "records",
            "clean premium SaaS hierarchy",
        ],
    },
}


def _preset_for_sector(sector_id: str) -> Dict[str, Any]:
    return SECTOR_IMAGE_FIRST_PRESETS.get(sector_id, SECTOR_IMAGE_FIRST_PRESETS["generic_saas"])


def build_premium_ui_image_concept(plan: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(plan, dict):
        return {
            "ok": False,
            "phase": "34G",
            "concept_type": "premium_ui_image_first",
            "error": "invalid_plan",
        }

    sector_id = _clean_text(plan.get("sector_id"), "generic_saas")
    app_name = _clean_text(plan.get("app_name") or plan.get("product_name"), "IdeasForgeAI Product")
    preview_summary = _clean_text(plan.get("preview_summary"))
    target_users = _clean_list(plan.get("target_users"))
    features = _clean_list(plan.get("core_features"))
    screens = _clean_list(plan.get("screens"))
    preset = _preset_for_sector(sector_id)

    visible_content = list(dict.fromkeys(preset["required_visible_content"] + features[:4] + screens[:3]))
    layout_targets = list(dict.fromkeys(preset["layout_targets"] + [f"highlight {screen.lower()} view" for screen in screens[:2]]))
    prompt_segments = [
        f"{app_name} premium app UI concept",
        *preset["prompt_phrases"],
    ]
    if target_users:
        prompt_segments.append(f"target users: {', '.join(target_users[:3])}")
    if preview_summary:
        prompt_segments.append(f"product intent: {preview_summary}")

    visual_prompt = ". ".join(segment for segment in prompt_segments if segment)
    mobile_prompt = (
        f"{visual_prompt}. Mobile-first, iPhone-sized, dense but premium, sticky primary actions, "
        "clear hierarchy, and app-like dashboard framing."
    )
    desktop_prompt = (
        f"{visual_prompt}. Desktop companion layout with wider analytics rail, premium card composition, "
        "and approval-ready hero/dashboard framing."
    )

    return {
        "ok": True,
        "phase": "34G",
        "concept_type": "premium_ui_image_first",
        "sector_id": sector_id,
        "app_name": app_name,
        "visual_prompt": visual_prompt,
        "mobile_prompt": mobile_prompt,
        "desktop_prompt": desktop_prompt,
        "style_tokens": {
            "style_label": preset["style_label"],
            "color_story": preset["color_story"],
            "surface_style": preset["surface_style"],
            "theme_family": _clean_text(plan.get("theme_family") or plan.get("visualThemeFamily"), "generic-modern-saas"),
            "layout_family": _clean_text(plan.get("layout_family") or plan.get("layoutVariant"), "card-first-dashboard"),
        },
        "layout_targets": layout_targets[:6],
        "required_visible_content": visible_content[:8],
        "approval_options": [
            "approve_visual_direction",
            "make_more_premium",
            "regenerate_concept",
            "continue_to_frontend_preview",
        ],
        "prompt_summary": " | ".join(prompt_segments[:5]),
    }
