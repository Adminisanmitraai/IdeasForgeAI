from pathlib import Path
from typing import Any
import json
import re


PROJECT_ROOT = Path("D:/APPS/IdeasForgeAI").resolve()

MAIN_PREVIEW_TARGET = (
    PROJECT_ROOT
    / "generated-apps"
    / "ideasforgeai-preview-v1"
).resolve()

PHASE20_SOURCE = (
    PROJECT_ROOT
    / "generated-apps"
    / "_phase20_final_apple_like_frontend_polish"
).resolve()

ROLLBACK_SNAPSHOT = (
    PROJECT_ROOT
    / "generated-apps"
    / "_phase21_rollback_snapshot_before_main_preview_replacement"
).resolve()

REQUIRED_FILES = [
    "index.html",
    "styles.css",
    "app.js",
    "manifest.json",
    "README.md",
    "phase20-polish-report.md",
    "phase20-validation-report.md",
    "phase21-replacement-manifest.json",
    "phase21-rollback-manifest.json",
    "phase21-replacement-report.md",
    "phase21-validation-report.md",
]


def _locked_flags() -> dict[str, Any]:
    return {
        "main_preview_output_validation_score_only": True,
        "validation_score_only": True,
        "file_write_allowed": False,
        "folder_creation_allowed": False,
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


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(_read_text(path))
        return value if isinstance(value, dict) else None
    except Exception:
        return None


def _score(ok: bool) -> int:
    return 100 if ok else 0


def _approved_local_scripts_only(html_text: str) -> bool:
    script_tags = re.findall(
        r"<script\b[^>]*>(?:.*?</script>)?",
        html_text,
        flags=re.IGNORECASE | re.DOTALL,
    )

    for tag in script_tags:
        normalized = re.sub(r"\s+", " ", tag.strip().lower())
        if 'src="app.js"' in normalized or "src='app.js'" in normalized:
            continue
        return False

    return True


def get_phase21g_main_preview_output_validation_score(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = payload or {}
    errors: list[str] = []
    warnings: list[str] = []

    if payload.get("project_name") not in (None, "IdeasForgeAI"):
        errors.append("project_name must equal IdeasForgeAI when provided")

    existing_files: list[str] = []
    missing_files: list[str] = REQUIRED_FILES[:]
    extra_files: list[str] = []

    if MAIN_PREVIEW_TARGET.exists():
        existing_files = sorted(item.name for item in MAIN_PREVIEW_TARGET.iterdir() if item.is_file())
        missing_files = [name for name in REQUIRED_FILES if name not in existing_files]
        extra_files = [name for name in existing_files if name not in REQUIRED_FILES]
    else:
        errors.append("main preview target folder is missing")

    index_html = _read_text(MAIN_PREVIEW_TARGET / "index.html") if (MAIN_PREVIEW_TARGET / "index.html").exists() else ""
    styles_css = _read_text(MAIN_PREVIEW_TARGET / "styles.css") if (MAIN_PREVIEW_TARGET / "styles.css").exists() else ""
    app_js = _read_text(MAIN_PREVIEW_TARGET / "app.js") if (MAIN_PREVIEW_TARGET / "app.js").exists() else ""

    manifest = _read_json(MAIN_PREVIEW_TARGET / "manifest.json") if (MAIN_PREVIEW_TARGET / "manifest.json").exists() else None
    replacement_manifest = _read_json(MAIN_PREVIEW_TARGET / "phase21-replacement-manifest.json") if (MAIN_PREVIEW_TARGET / "phase21-replacement-manifest.json").exists() else None
    rollback_manifest = _read_json(MAIN_PREVIEW_TARGET / "phase21-rollback-manifest.json") if (MAIN_PREVIEW_TARGET / "phase21-rollback-manifest.json").exists() else None

    phase20_polish_report = _read_text(MAIN_PREVIEW_TARGET / "phase20-polish-report.md").lower() if (MAIN_PREVIEW_TARGET / "phase20-polish-report.md").exists() else ""
    phase20_validation_report = _read_text(MAIN_PREVIEW_TARGET / "phase20-validation-report.md").lower() if (MAIN_PREVIEW_TARGET / "phase20-validation-report.md").exists() else ""
    phase21_replacement_report = _read_text(MAIN_PREVIEW_TARGET / "phase21-replacement-report.md").lower() if (MAIN_PREVIEW_TARGET / "phase21-replacement-report.md").exists() else ""
    phase21_validation_report = _read_text(MAIN_PREVIEW_TARGET / "phase21-validation-report.md").lower() if (MAIN_PREVIEW_TARGET / "phase21-validation-report.md").exists() else ""

    index_lower = index_html.lower()
    css_lower = styles_css.lower()
    app_lower = app_js.lower()

    html_blockers = [
        "<iframe",
        "http://",
        "https://",
        "fetch(",
        "xmlhttprequest",
        "supabase.createclient",
        "supabaseurl",
        "supabase_service_role",
        "service_role",
        "apikey=",
        "api_key=",
        "secret=",
        "token=",
        "access_token",
        "refresh_token",
        "deployment_allowed=true",
        "deployment_unlocked=true",
        "provider_calls_allowed=true",
        "database_writes_allowed=true",
        "render.yaml",
        "IdeasForgeAI",
    ]

    css_blockers = [
        "http://",
        "https://",
        "@import",
        "expression(",
        "javascript:",
        "IdeasForgeAI",
    ]

    app_blockers = [
        "fetch(",
        "xmlhttprequest",
        "import ",
        "import(",
        "http://",
        "https://",
        "localstorage",
        "sessionstorage",
        "supabase",
        "auth",
        "database",
        "apikey",
        "api_key",
        "secret=",
        "token=",
        "deploy(",
        "IdeasForgeAI",
    ]

    visual_keywords = [
        "turn rough ideas into polished product previews",
        "ai product builder for founders",
        "preview-first",
        "approval-gated",
        "rollback-ready",
        "product brain",
        "design system",
        "preview runner",
        "approval gates",
        "start with one rough idea",
    ]

    design_css_keywords = [
        "--brand",
        "--surface",
        "--shadow",
        "radial-gradient",
        "border-radius",
        "clamp(",
        "grid-template-columns",
        "backdrop-filter",
        "@media",
    ]

    score_categories = {
        "required_files_score": _score(MAIN_PREVIEW_TARGET.exists() and not missing_files and not extra_files),
        "approved_local_script_score": _score(_approved_local_scripts_only(index_html)),
        "html_runtime_safety_score": _score(not any(marker in index_lower for marker in html_blockers)),
        "css_safety_score": _score(not any(marker in css_lower for marker in css_blockers)),
        "app_js_safety_score": _score(not any(marker in app_lower for marker in app_blockers)),
        "apple_like_visual_content_score": _score(all(keyword in index_lower for keyword in visual_keywords)),
        "apple_like_css_system_score": _score(all(keyword in css_lower for keyword in design_css_keywords)),
        "responsive_css_score": _score("@media (max-width: 960px)" in css_lower and "@media (max-width: 560px)" in css_lower),
        "header_hero_score": _score("site-header" in index_lower and "hero-section" in index_lower),
        "sections_score": _score(
            "feature-grid" in index_lower
            and "workflow-section" in index_lower
            and "trust-section" in index_lower
            and "final-cta" in index_lower
            and "site-footer" in index_lower
        ),
        "phase20_manifest_score": _score(
            bool(manifest)
            and manifest.get("project_name") == "IdeasForgeAI"
            and manifest.get("phase") == "Phase 20E - Controlled Final Polish Sandbox Creation"
            and manifest.get("production_replacement_allowed") is False
            and manifest.get("deployment_allowed") is False
            and manifest.get("provider_calls_allowed") is False
            and manifest.get("database_writes_allowed") is False
            and manifest.get("supabase_allowed") is False
            and manifest.get("auth_allowed") is False
            and manifest.get("secrets_allowed") is False
            and manifest.get("ideasforgeai_preview_v1_touched") is False
            and manifest.get("IdeasForgeAI_production_touched") is False
        ),
        "phase21_replacement_manifest_score": _score(
            bool(replacement_manifest)
            and replacement_manifest.get("project_name") == "IdeasForgeAI"
            and replacement_manifest.get("phase") == "Phase 21F - Controlled Main Preview Replacement"
            and replacement_manifest.get("approved_by_human") is True
            and replacement_manifest.get("phase20h_frozen") is True
            and replacement_manifest.get("phase20g_validation_score") == 100
            and replacement_manifest.get("phase21c_approval_validated") is True
            and replacement_manifest.get("phase21d_dry_run_passed") is True
            and replacement_manifest.get("phase21e_rollback_snapshot_ready") is True
            and replacement_manifest.get("main_preview_replacement_performed") is True
            and replacement_manifest.get("production_replacement_allowed") is False
            and replacement_manifest.get("deployment_allowed") is False
            and replacement_manifest.get("provider_calls_allowed") is False
            and replacement_manifest.get("database_writes_allowed") is False
            and replacement_manifest.get("supabase_allowed") is False
            and replacement_manifest.get("auth_allowed") is False
            and replacement_manifest.get("secrets_allowed") is False
            and replacement_manifest.get("IdeasForgeAI_production_touched") is False
        ),
        "phase21_rollback_manifest_score": _score(
            bool(rollback_manifest)
            and rollback_manifest.get("project_name") == "IdeasForgeAI"
            and rollback_manifest.get("phase") == "Phase 21F - Controlled Main Preview Replacement"
            and rollback_manifest.get("rollback_available") is True
            and rollback_manifest.get("production_replacement_allowed") is False
            and rollback_manifest.get("deployment_allowed") is False
            and rollback_manifest.get("provider_calls_allowed") is False
            and rollback_manifest.get("database_writes_allowed") is False
            and rollback_manifest.get("supabase_allowed") is False
            and rollback_manifest.get("auth_allowed") is False
            and rollback_manifest.get("secrets_allowed") is False
        ),
        "phase20_reports_score": _score(
            "status: success" in phase20_polish_report
            and "final apple-like polished frontend sandbox created" in phase20_polish_report
            and "controlled final polish sandbox creation completed" in phase20_validation_report
        ),
        "phase21_reports_score": _score(
            "status: success" in phase21_replacement_report
            and "controlled main preview replacement was performed" in phase21_replacement_report
            and "replacement was limited to generated-apps/ideasforgeai-preview-v1/" in phase21_replacement_report
            and "controlled main preview replacement completed" in phase21_validation_report
            and "deployment unlocked: false" in phase21_validation_report
        ),
        "rollback_snapshot_exists_score": _score(
            ROLLBACK_SNAPSHOT.exists()
            and (ROLLBACK_SNAPSHOT / "phase21-rollback-manifest.json").exists()
            and (ROLLBACK_SNAPSHOT / "phase21-safety-manifest.json").exists()
            and (ROLLBACK_SNAPSHOT / "phase21-rollback-snapshot-report.md").exists()
        ),
        "phase20_source_protected_score": _score(PHASE20_SOURCE.exists()),
        "IdeasForgeAI_separation_score": _score("IdeasForgeAI" not in (index_lower + css_lower + app_lower)),
    }

    for name, value in score_categories.items():
        if value < 100:
            errors.append(f"{name} failed")

    overall_score = int(sum(score_categories.values()) / len(score_categories)) if score_categories else 0
    validation_passed = overall_score == 100 and not errors

    return {
        "status": "success" if validation_passed else "review_required",
        "phase": "Phase 21G - Main Preview Output Validation Score",
        "target_folder": str(MAIN_PREVIEW_TARGET),
        "phase20_source_folder": str(PHASE20_SOURCE),
        "rollback_snapshot_folder": str(ROLLBACK_SNAPSHOT),
        "existing_files": existing_files,
        "missing_files": missing_files,
        "extra_files": extra_files,
        "score_categories": score_categories,
        "overall_score": overall_score,
        "validation_passed": validation_passed,
        "validation_errors": errors,
        "validation_warnings": warnings,
        "next_required_phase": "Phase 21H - Main Preview Freeze Review",
        **_locked_flags(),
    }

