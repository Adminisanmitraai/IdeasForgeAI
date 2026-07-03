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
        "style_direction": "Premium blue and purple education dashboard with bright, trustable tutor energy",
        "color_story": "education blue, premium indigo, clean white, slate text, soft cyan highlights",
        "surface_style": "layered mobile tutor dashboard cards with polished education analytics",
        "layout_targets": [
            "mobile-first tutor dashboard hero with student, class, and attendance snapshot cards",
            "class schedule strip above homework, fees pending, and parent message sections",
            "student progress and test performance cards inside a compact premium analytics row",
            "quick actions for attendance, homework, fees, and parent communication in the first fold",
        ],
        "required_visible_content": [
            "students",
            "classes",
            "attendance",
            "homework",
            "fees pending",
            "parent messages",
            "class schedule",
            "progress",
            "tests",
        ],
        "prompt_phrases": [
            "Private Tutor App",
            "premium tutor dashboard",
            "students",
            "classes",
            "attendance",
            "homework",
            "fees pending",
            "parent messages",
            "class schedule",
            "progress",
            "tests",
            "premium blue purple education style",
            "mobile-first dashboard composition",
        ],
    },
    "wedding_event_lawn": {
        "style_direction": "Plum, gold, and champagne luxury venue dashboard with premium event planning polish",
        "color_story": "deep plum, champagne ivory, brushed gold, warm rose neutrals",
        "surface_style": "premium venue booking cards with rich package and event management framing",
        "layout_targets": [
            "event calendar hero with booking urgency and premium venue summary",
            "package showcase cards paired with decor theme gallery in the first fold",
            "vendor task ribbon and site visit schedule panel beside payment progress",
            "lead pipeline stack with enquiry movement and booking milestone overview",
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
            "plum gold champagne premium theme",
        ],
    },
    "agriculture_farmer": {
        "style_direction": "Green agri intelligence dashboard with practical field-ready advisory layout",
        "color_story": "leaf green, earthy neutrals, weather-safe contrast, muted gold accents",
        "surface_style": "field intelligence cards with dense mobile-first advisory composition",
        "layout_targets": [
            "mobile farm dashboard hero with crop health and weather intelligence cards",
            "mandi price and buyer connect cards near top actions for quick decisions",
            "farm tasks and advisory blocks grouped in the mid fold for daily execution",
            "green agri dashboard framing with grounded operational cards instead of generic SaaS sections",
        ],
        "required_visible_content": [
            "crop health",
            "weather",
            "mandi price",
            "farm tasks",
            "buyer connect",
        ],
        "prompt_phrases": [
            "premium agriculture dashboard",
            "crop health",
            "weather",
            "mandi price",
            "farm tasks",
            "buyer connect",
            "green agri dashboard",
        ],
    },
    "mutual_fund_advisor": {
        "style_direction": "Compliance-safe wealth dashboard with premium trust blue financial framing",
        "color_story": "deep trust blue, restrained green, soft white, low-noise compliance surfaces",
        "surface_style": "clean advisory cards with disciplined typography and trust-forward spacing",
        "layout_targets": [
            "advisor dashboard hero with AUM and SIP book metrics in the first fold",
            "goal progress and portfolio review cards above risk profile summaries",
            "compliance note panel kept visible without any guaranteed-return language",
            "client follow-up, meeting, and review blocks arranged as a mobile-first advisory cockpit",
        ],
        "required_visible_content": [
            "AUM",
            "SIP book",
            "risk profile",
            "goal progress",
            "portfolio review",
            "compliance note",
        ],
        "prompt_phrases": [
            "premium mutual fund advisor dashboard",
            "AUM",
            "SIP book",
            "risk profile",
            "goal progress",
            "portfolio review",
            "compliance note",
            "without return promises",
        ],
    },
    "generic_saas": {
        "style_direction": "Polished workflow SaaS dashboard with premium operational clarity",
        "color_story": "graphite, clean white, crisp accent blue, subtle premium gradients",
        "surface_style": "balanced metric and workflow cards with modular approvals",
        "layout_targets": [
            "hero dashboard with primary workflow metrics",
            "feature grid paired with action queue",
            "records and approval states in modular cards",
            "clean desktop and mobile hierarchy without false sector claims",
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


def build_image_first_mockup(plan: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(plan, dict):
        return {
            "ok": False,
            "phase": "34H",
            "status": "invalid_plan",
            "mockup_type": "premium_ui_image_first",
            "error": "invalid_plan",
        }

    sector_id = _clean_text(plan.get("sector_id"), "generic_saas")
    app_name = _clean_text(plan.get("app_name") or plan.get("product_name"), "IdeasForgeAI Product")
    preview_summary = _clean_text(plan.get("preview_summary"))
    target_users = _clean_list(plan.get("target_users"))
    features = _clean_list(plan.get("core_features"))
    screens = _clean_list(plan.get("screens"))
    preset = _preset_for_sector(sector_id)

    required_visible_content = list(
        dict.fromkeys(preset["required_visible_content"] + features[:5] + screens[:4])
    )[:10]
    layout_targets = list(
        dict.fromkeys(preset["layout_targets"] + [f"highlight {screen.lower()} view" for screen in screens[:2]])
    )[:6]

    prompt_segments = [
        f"{app_name} premium app UI mockup target",
        *preset["prompt_phrases"],
    ]
    if target_users:
        prompt_segments.append(f"target users: {', '.join(target_users[:3])}")
    if preview_summary:
        prompt_segments.append(f"product intent: {preview_summary}")

    visual_prompt = ". ".join(segment for segment in prompt_segments if segment)
    mobile_visual_prompt = (
        f"{visual_prompt}. Mobile-first, approval-ready, high-end product mockup, "
        "dense but polished dashboard composition, sticky actions, premium hierarchy."
    )
    desktop_visual_prompt = (
        f"{visual_prompt}. Desktop companion dashboard with wider analytics rail, "
        "premium card composition, and approval-ready product design framing."
    )

    return {
        "ok": True,
        "phase": "34H",
        "status": "ready_for_approval",
        "mockup_type": "premium_ui_image_first",
        "app_name": app_name,
        "sector_id": sector_id,
        "visual_prompt": visual_prompt,
        "mobile_visual_prompt": mobile_visual_prompt,
        "desktop_visual_prompt": desktop_visual_prompt,
        "style_direction": preset["style_direction"],
        "layout_targets": layout_targets,
        "required_visible_content": required_visible_content,
        "approval_actions": [
            "approve_visual_mockup",
            "make_more_premium",
            "regenerate_mockup",
            "change_color_style",
            "continue_to_frontend_preview",
        ],
        "rendering_profile": {
            "color_story": preset["color_story"],
            "surface_style": preset["surface_style"],
            "theme_family": _clean_text(plan.get("theme_family") or plan.get("visualThemeFamily"), "generic-modern-saas"),
            "layout_family": _clean_text(plan.get("layout_family") or plan.get("layoutVariant"), "card-first-dashboard"),
        },
        "visual_prompt_summary": " | ".join(prompt_segments[:5]),
        "provider_state": "placeholder_ready_no_external_provider_configured",
    }

