from pathlib import Path
from typing import Any


PROJECT_ROOT = Path("D:/APPS/IdeasForgeAI").resolve()

MAIN_PREVIEW_TARGET = (
    PROJECT_ROOT
    / "generated-apps"
    / "ideasforgeai-preview-v1"
).resolve()

REQUIRED_FILES = [
    "index.html",
    "styles.css",
    "app.js",
    "manifest.json",
    "README.md",
    "phase21-replacement-manifest.json",
    "phase21-validation-report.md",
]


def _locked_flags() -> dict[str, Any]:
    return {
        "desktop_visual_qa_checklist_only": True,
        "visual_qa_only": True,
        "file_write_allowed": False,
        "folder_creation_allowed": False,
        "files_copied": False,
        "files_replaced": False,
        "main_preview_files_modified_by_this_phase": False,
        "phase20_polish_folder_modified": False,
        "rollback_snapshot_modified": False,
        "production_deployment_performed": False,
        "production_replacement_allowed": False,
        "deployment_unlocked": False,
        "provider_calls_allowed": False,
        "database_writes_allowed": False,
        "supabase_allowed": False,
        "auth_allowed": False,
        "secrets_allowed": False,
        "backend_generation_unlocked": False,
        "generation_allowed": False,
        "IdeasForgeAI_production_touched": False,
    }


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="ignore")


def get_phase22c_desktop_visual_qa_checklist(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = payload or {}
    errors: list[str] = []
    warnings: list[str] = []

    if payload.get("project_name") not in (None, "IdeasForgeAI"):
        errors.append("project_name must equal IdeasForgeAI when provided")

    existing_files: list[str] = []
    missing_files: list[str] = REQUIRED_FILES[:]

    if MAIN_PREVIEW_TARGET.exists():
        existing_files = sorted(item.name for item in MAIN_PREVIEW_TARGET.iterdir() if item.is_file())
        missing_files = [name for name in REQUIRED_FILES if name not in existing_files]
    else:
        errors.append("main preview target folder is missing")

    index_html = _read_text(MAIN_PREVIEW_TARGET / "index.html") if (MAIN_PREVIEW_TARGET / "index.html").exists() else ""
    styles_css = _read_text(MAIN_PREVIEW_TARGET / "styles.css") if (MAIN_PREVIEW_TARGET / "styles.css").exists() else ""

    index_lower = index_html.lower()
    css_lower = styles_css.lower()

    desktop_checks = {
        "premium_header_present": "site-header" in index_lower,
        "ideasforgeai_brand_present": "ideasforgeai" in index_lower and "ai product builder" in index_lower,
        "nav_links_present": all(item in index_lower for item in ["product", "workflow", "trust", "preview"]),
        "preview_only_badge_present": "preview-only" in index_lower,
        "primary_cta_present": "start with an idea" in index_lower or "build a preview" in index_lower,
        "hero_section_present": "hero-section" in index_lower,
        "hero_headline_present": "turn rough ideas into polished product previews" in index_lower,
        "hero_visual_present": "hero-visual" in index_lower,
        "product_builder_console_present": "ideasforgeai.preview" in index_lower,
        "pipeline_cards_present": all(item in index_lower for item in ["product brain", "design system", "approval gate"]),
        "feature_grid_present": "feature-grid" in index_lower,
        "workflow_section_present": "workflow-section" in index_lower,
        "trust_section_present": "trust-section" in index_lower,
        "final_cta_present": "final-cta" in index_lower,
        "footer_present": "site-footer" in index_lower,
    }

    desktop_css_checks = {
        "desktop_max_width_present": "1240px" in css_lower or "1180px" in css_lower,
        "header_floating_style_present": "site-header" in css_lower and "sticky" in css_lower,
        "hero_two_column_grid_present": "hero-section" in css_lower and "grid-template-columns" in css_lower,
        "feature_grid_desktop_present": "feature-grid" in css_lower and "repeat(3, 1fr)" in css_lower,
        "rounded_cards_present": "border-radius" in css_lower,
        "soft_shadow_present": "--shadow" in css_lower or "box-shadow" in css_lower,
        "radial_gradient_present": "radial-gradient" in css_lower,
        "responsive_media_present": "@media" in css_lower,
    }

    blocked_visitor_terms = [
        "phase 17d sandbox patch",
        "copied html only",
        "raw approval reference",
        "backend/main.py",
        "render.yaml",
        "supabase.createclient",
        "service_role",
        "api_key",
        "secret=",
        "token=",
        "IdeasForgeAI",
    ]

    content_safety_checks = {
        f"blocked_term_absent_{term.replace(' ', '_').replace('=', '')}": term not in index_lower
        for term in blocked_visitor_terms
    }

    all_checks = {
        **desktop_checks,
        **desktop_css_checks,
        **content_safety_checks,
        "required_files_present": MAIN_PREVIEW_TARGET.exists() and not missing_files,
    }

    failed_checks = [name for name, passed in all_checks.items() if not passed]

    if failed_checks:
        errors.extend(f"{name} failed" for name in failed_checks)

    validation_passed = not errors

    return {
        "status": "success" if validation_passed else "review_required",
        "phase": "Phase 22C - Desktop Visual QA Checklist",
        "target_folder": str(MAIN_PREVIEW_TARGET),
        "existing_files": existing_files,
        "missing_files": missing_files,
        "desktop_checks": desktop_checks,
        "desktop_css_checks": desktop_css_checks,
        "content_safety_checks": content_safety_checks,
        "failed_checks": failed_checks,
        "validation_passed": validation_passed,
        "validation_errors": errors,
        "validation_warnings": warnings,
        "manual_browser_check_required": True,
        "manual_browser_check_items": [
            "Header visually appears premium and aligned",
            "Hero headline is large and readable",
            "Right product preview card is visible",
            "Above-the-fold spacing looks premium",
            "No visual overlap on desktop",
            "No debug/sandbox text appears above the fold",
            "CTA buttons are visible",
        ],
        "next_required_phase": "Phase 22D - Mobile Responsive QA Checklist",
        **_locked_flags(),
    }

