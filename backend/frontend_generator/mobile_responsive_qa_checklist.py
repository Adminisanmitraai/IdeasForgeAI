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
    "phase21-replacement-manifest.json",
    "phase21-validation-report.md",
]


def _locked_flags() -> dict[str, Any]:
    return {
        "mobile_responsive_qa_checklist_only": True,
        "responsive_qa_only": True,
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


def get_phase22d_mobile_responsive_qa_checklist(payload: dict[str, Any] | None = None) -> dict[str, Any]:
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

    mobile_css_checks = {
        "viewport_meta_present": 'name="viewport"' in index_lower,
        "media_960_present": "@media (max-width: 960px)" in css_lower,
        "media_560_present": "@media (max-width: 560px)" in css_lower,
        "mobile_header_stacks": ".site-header" in css_lower and "flex-direction: column" in css_lower,
        "mobile_hero_single_column": "hero-section" in css_lower and "grid-template-columns: 1fr" in css_lower,
        "mobile_trust_single_column": "trust-section" in css_lower and "grid-template-columns: 1fr" in css_lower,
        "mobile_footer_single_column": "site-footer" in css_lower and "grid-template-columns: 1fr" in css_lower,
        "mobile_feature_grid_single_column": "feature-grid" in css_lower and "grid-template-columns: 1fr" in css_lower,
        "mobile_workflow_single_column": "workflow-steps" in css_lower and "grid-template-columns: 1fr" in css_lower,
        "mobile_buttons_full_width": ".button" in css_lower and "width: 100%" in css_lower,
        "mobile_shell_width_safe": "100% - 22px" in css_lower or "calc(100% - 22px)" in css_lower,
        "mobile_border_radius_adjusted": "border-radius: 26px" in css_lower or "border-radius: 28px" in css_lower,
    }

    mobile_content_checks = {
        "logo_present": "ideasforgeai" in index_lower,
        "hero_headline_present": "turn rough ideas into polished product previews" in index_lower,
        "hero_visual_present": "hero-visual" in index_lower,
        "preview_only_present": "preview-only" in index_lower,
        "cta_present": "start with an idea" in index_lower or "build a preview" in index_lower,
        "feature_grid_present": "feature-grid" in index_lower,
        "workflow_section_present": "workflow-section" in index_lower,
        "trust_section_present": "trust-section" in index_lower,
        "final_cta_present": "final-cta" in index_lower,
        "footer_present": "site-footer" in index_lower,
    }

    blocked_terms = [
        "phase 17d sandbox patch",
        "copied html only",
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
        for term in blocked_terms
    }

    all_checks = {
        **mobile_css_checks,
        **mobile_content_checks,
        **content_safety_checks,
        "required_files_present": MAIN_PREVIEW_TARGET.exists() and not missing_files,
    }

    failed_checks = [name for name, passed in all_checks.items() if not passed]

    if failed_checks:
        errors.extend(f"{name} failed" for name in failed_checks)

    validation_passed = not errors

    return {
        "status": "success" if validation_passed else "review_required",
        "phase": "Phase 22D - Mobile Responsive QA Checklist",
        "target_folder": str(MAIN_PREVIEW_TARGET),
        "existing_files": existing_files,
        "missing_files": missing_files,
        "mobile_css_checks": mobile_css_checks,
        "mobile_content_checks": mobile_content_checks,
        "content_safety_checks": content_safety_checks,
        "failed_checks": failed_checks,
        "validation_passed": validation_passed,
        "validation_errors": errors,
        "validation_warnings": warnings,
        "manual_mobile_browser_check_required": True,
        "manual_mobile_browser_check_items": [
            "Open browser devtools mobile size around 390px width",
            "Header stacks cleanly",
            "Hero becomes single-column",
            "Headline remains readable",
            "Preview visual stacks below copy",
            "Feature cards become single-column",
            "Workflow cards become single-column",
            "No horizontal scrolling",
            "CTA buttons are not clipped",
            "Footer stacks cleanly",
        ],
        "next_required_phase": "Phase 22E - Runtime Console + Safety QA",
        **_locked_flags(),
    }

