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
        "header_hero_polish_plan_only": True,
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
        "kisanmitra_production_touched": False,
    }


def get_phase20c_final_header_hero_polish_plan() -> dict[str, Any]:
    return {
        "status": "success",
        "phase": "Phase 20C - Final Header + Hero Polish Plan",
        "approved_source": str(APPROVED_PHASE19_SOURCE),
        "future_polish_sandbox": str(FUTURE_PHASE20_POLISH_SANDBOX),
        "header_plan": {
            "style": "floating Apple-like SaaS header",
            "layout": "centered max-width rounded glass surface",
            "logo": "IdeasForgeAI",
            "tagline": "AI Product Builder",
            "navigation": ["Product", "Workflow", "Trust", "Preview"],
            "cta": "Start with an idea",
            "badge": "Preview-only",
            "avoid": [
                "debug text",
                "internal phase text above the fold",
                "heavy green header",
                "visual clutter",
            ],
        },
        "hero_plan": {
            "eyebrow": "AI PRODUCT BUILDER FOR FOUNDERS",
            "headline": "Turn rough ideas into polished product previews.",
            "subheadline": (
                "IdeasForgeAI helps founders shape an idea into strategy, structure, "
                "design direction, preview screens, and approval-ready product output "
                "before anything goes live."
            ),
            "primary_cta": "Build a preview",
            "secondary_cta": "See workflow",
            "trust_badges": [
                "Preview-first",
                "Approval-gated",
                "Rollback-ready",
                "No deployment without approval",
            ],
        },
        "hero_visual_plan": {
            "visual_type": "premium mini product-builder console",
            "cards": [
                "Idea input",
                "Product Brain",
                "Design System",
                "Preview",
                "Approval Gate",
            ],
            "style": "soft white cards, rounded corners, subtle green accents",
            "avoid": [
                "raw debug wording",
                "sandbox patch wording in top hero",
                "backend implementation language",
            ],
        },
        "content_cleanup_rules": [
            "Move Phase 17D Sandbox Patch text below the fold or remove from visitor hero",
            "Move copied HTML only badges out of the hero",
            "Hide raw approval reference from top hero",
            "Keep safety language concise and founder-friendly",
        ],
        "next_required_phase": "Phase 20D - Final Section/Card/CTA Polish Plan",
        **_locked_flags(),
    }
