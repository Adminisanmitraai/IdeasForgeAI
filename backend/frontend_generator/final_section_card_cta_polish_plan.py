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
        "section_card_cta_polish_plan_only": True,
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


def get_phase20d_final_section_card_cta_polish_plan() -> dict[str, Any]:
    return {
        "status": "success",
        "phase": "Phase 20D - Final Section/Card/CTA Polish Plan",
        "approved_source": str(APPROVED_PHASE19_SOURCE),
        "future_polish_sandbox": str(FUTURE_PHASE20_POLISH_SANDBOX),
        "product_builder_preview_plan": {
            "headline": "From idea to approval-ready preview.",
            "layout": "premium rounded container with explanation and product-builder console mockup",
            "steps": [
                "Founder Idea",
                "Product Brain",
                "Design System",
                "Preview + Approval Gate",
            ],
            "avoid": [
                "raw phase wording",
                "sandbox debug wording",
                "backend implementation language",
            ],
        },
        "feature_grid_plan": {
            "required_cards": [
                "Product Brain",
                "Design System Engine",
                "Pixel-Matched Converter",
                "Preview Runner",
                "Section Editor",
                "Approval Gates",
                "Rollback Safety",
                "Main Preview Candidate",
            ],
            "card_style": [
                "short title",
                "one-sentence benefit",
                "soft border",
                "rounded corners",
                "subtle shadow",
                "premium spacing",
            ],
        },
        "workflow_plan": {
            "steps": [
                "Write your rough product idea",
                "Review the product plan",
                "Generate a safe preview",
                "Edit selected sections",
                "Approve a main preview candidate",
            ],
            "desktop_style": "horizontal steps with soft connector lines",
            "mobile_style": "vertical timeline with numbered pills",
        },
        "trust_safety_plan": {
            "cards": [
                "Preview-first workflow",
                "Human approval gates",
                "No deployment without approval",
                "No provider calls without approval",
                "No database writes without approval",
                "Secrets stay locked",
                "Rollback-ready previews",
                "IdeasForgeAI separation preserved",
            ],
            "tone": "short, confident, founder-friendly",
        },
        "final_cta_plan": {
            "headline": "Start with one rough idea.",
            "body": (
                "IdeasForgeAI will help shape it into a product strategy, visual direction, "
                "and preview-ready frontend before anything goes live."
            ),
            "primary_cta": "Build a preview",
            "secondary_cta": "Review workflow",
            "style": "large rounded panel with soft green radial glow",
        },
        "footer_plan": {
            "wordmark": "IdeasForgeAI",
            "description": "AI Product Builder for turning rough ideas into polished product previews.",
            "links": ["Product", "Workflow", "Trust", "Preview"],
            "note": "Preview-only. Deployment remains approval-gated.",
        },
        "content_cleanup_rules": [
            "Remove raw Phase 17D Sandbox Patch wording from visitor-facing hero",
            "Remove copied HTML only wording from above the fold",
            "Remove raw approval references from the hero",
            "Avoid internal sandbox paths",
            "Avoid backend implementation details",
            "Keep validation and safety language below the main product story",
        ],
        "next_required_phase": "Phase 20E - Controlled Final Polish Sandbox Creation",
        **_locked_flags(),
    }

