from __future__ import annotations

from typing import Any, Dict

from backend.image_first_mockup_engine import build_image_first_mockup


def build_premium_ui_image_concept(plan: Dict[str, Any]) -> Dict[str, Any]:
    mockup = build_image_first_mockup(plan)
    if not mockup.get("ok"):
        return {
            "ok": False,
            "phase": "34H",
            "concept_type": "premium_ui_image_first",
            "error": mockup.get("error", "invalid_plan"),
        }

    rendering_profile = mockup.get("rendering_profile") if isinstance(mockup.get("rendering_profile"), dict) else {}
    return {
        "ok": True,
        "phase": "34H",
        "status": mockup.get("status", "ready_for_approval"),
        "concept_type": "premium_ui_image_first",
        "sector_id": mockup.get("sector_id"),
        "app_name": mockup.get("app_name"),
        "visual_prompt": mockup.get("visual_prompt"),
        "mobile_prompt": mockup.get("mobile_visual_prompt"),
        "desktop_prompt": mockup.get("desktop_visual_prompt"),
        "style_tokens": {
            "style_label": mockup.get("style_direction"),
            "color_story": rendering_profile.get("color_story", ""),
            "surface_style": rendering_profile.get("surface_style", ""),
            "theme_family": rendering_profile.get("theme_family", "generic-modern-saas"),
            "layout_family": rendering_profile.get("layout_family", "card-first-dashboard"),
        },
        "layout_targets": mockup.get("layout_targets", []),
        "required_visible_content": mockup.get("required_visible_content", []),
        "approval_options": mockup.get("approval_actions", []),
        "prompt_summary": mockup.get("visual_prompt_summary", ""),
    }

