from pathlib import Path
from typing import Any


PROJECT_ROOT = Path("D:/APPS/IdeasForgeAI").resolve()

APPROVED_PHASE19_SOURCE = (
    PROJECT_ROOT
    / "generated-apps"
    / "_phase19_main_preview_candidate"
).resolve()

FUTURE_PHASE20_POLISH_SANDBOX = (
    PROJECT_ROOT
    / "generated-apps"
    / "_phase20_final_apple_like_frontend_polish"
).resolve()


def _locked_flags() -> dict[str, Any]:
    return {
        "design_system_rules_only": True,
        "frontend_files_modified": False,
        "candidate_files_modified": False,
        "polish_sandbox_created": False,
        "file_write_allowed": False,
        "folder_creation_allowed": False,
        "production_replacement_allowed": False,
        "real_generated_app_modified": False,
        "phase19_candidate_folder_modified": False,
        "ideasforgeai_preview_v1_touched": False,
        "generation_allowed": False,
        "backend_generation_unlocked": False,
        "deployment_unlocked": False,
        "provider_calls_allowed": False,
        "database_writes_allowed": False,
        "secrets_allowed": False,
        "supabase_allowed": False,
        "auth_allowed": False,
        "IdeasForgeAI_production_touched": False,
    }


def get_phase20b_final_apple_like_design_system_rules() -> dict[str, Any]:
    return {
        "status": "success",
        "phase": "Phase 20B - Final Apple-Like Design System Rules",
        "approved_source": str(APPROVED_PHASE19_SOURCE),
        "future_polish_sandbox": str(FUTURE_PHASE20_POLISH_SANDBOX),
        "visual_principles": [
            "calm premium interface",
            "generous whitespace",
            "soft off-white background",
            "subtle green-tinted radial gradients",
            "strong visual hierarchy",
            "large refined hero typography",
            "minimal premium navigation",
            "rounded cards with subtle shadows",
            "glass-like panels without heavy blur",
            "clear CTAs with strong contrast",
            "mobile-first responsive structure",
            "no generic template look",
        ],
        "approved_palette": {
            "page_background": "#f7fbf8",
            "surface": "#ffffff",
            "soft_green_surface": "#ecfdf5",
            "brand_green": "#0f8f5b",
            "deep_text": "#102318",
            "muted_text": "#607268",
            "soft_border": "rgba(15, 143, 91, 0.16)",
            "soft_shadow": "rgba(16, 35, 24, 0.08)",
            "premium_gold_accent": "#d6a84f",
        },
        "typography": {
            "font_stack": "-apple-system, BlinkMacSystemFont, Segoe UI, Inter, Arial, sans-serif",
            "hero_title_desktop": "64px to 76px",
            "hero_title_mobile": "38px to 46px",
            "section_title": "34px to 44px",
            "body": "16px to 18px",
            "hero_line_height": "1.05 to 1.15",
            "body_line_height": "1.55 to 1.7",
        },
        "layout_rules": {
            "desktop_max_width": "1180px to 1240px",
            "desktop_section_padding": "72px to 110px",
            "mobile_section_padding": "44px to 64px",
            "card_padding": "24px to 36px",
            "border_radius": "22px to 32px",
            "grid_gap": "18px to 28px",
        },
        "required_sections": [
            "Premium Header",
            "Hero Section",
            "Product Builder Preview",
            "Feature Grid",
            "Workflow Section",
            "Trust / Safety Section",
            "Founder CTA Section",
            "Footer",
        ],
        "content_rules": {
            "speak_to": "founders and product builders",
            "main_promise": "Turn rough ideas into polished product previews.",
            "avoid": [
                "internal phase names in main hero",
                "debug wording",
                "raw sandbox wording",
                "too many safety disclaimers above the fold",
                "technical backend wording for visitors",
            ],
        },
        "next_required_phase": "Phase 20C - Final Header + Hero Polish Plan",
        **_locked_flags(),
    }

