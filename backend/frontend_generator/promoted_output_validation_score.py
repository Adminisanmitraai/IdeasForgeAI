from pathlib import Path
from typing import Any
import json
import re


PROJECT_ROOT = Path("D:/APPS/IdeasForgeAI").resolve()

PROMOTED_TARGET = (
    PROJECT_ROOT
    / "generated-apps"
    / "_phase18_promoted_section_patch_preview"
).resolve()

REQUIRED_FILES = [
    "index.html",
    "styles.css",
    "app.js",
    "manifest.json",
    "README.md",
    "validation-report.md",
    "rollback-manifest.json",
    "phase17-validation-report.md",
    "section-patch-application-report.md",
    "promotion-manifest.json",
    "phase18-promotion-report.md",
    "phase18-validation-report.md",
]

APP_VISIBLE_FILES = [
    "index.html",
    "styles.css",
    "app.js",
    "manifest.json",
]


def _locked_flags() -> dict[str, Any]:
    return {
        "promoted_output_validation_score_only": True,
        "validation_score_only": True,
        "file_write_allowed": False,
        "folder_creation_allowed": False,
        "promotion_performed_by_this_phase": False,
        "real_generated_app_modified": False,
        "phase13e_sandbox_modified": False,
        "phase16f_sandbox_modified": False,
        "phase17_sandbox_modified": False,
        "phase18_promoted_folder_modified": False,
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


def _score(ok: bool) -> int:
    return 100 if ok else 0


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="ignore")


def _read_json(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        data = json.loads(_read_text(path))
        if isinstance(data, dict):
            return data, []
        return None, [f"{path.name} must be a JSON object"]
    except Exception as exc:
        return None, [f"{path.name} invalid JSON: {exc}"]


def _approved_local_scripts_only(html_text: str) -> tuple[bool, list[str]]:
    errors: list[str] = []
    script_tags = re.findall(
        r"<script\b[^>]*>(?:.*?</script>)?",
        html_text,
        flags=re.IGNORECASE | re.DOTALL,
    )

    for tag in script_tags:
        normalized = re.sub(r"\s+", " ", tag.strip().lower())
        if 'src="app.js"' in normalized or "src='app.js'" in normalized:
            continue
        errors.append("non-approved script tag found")

    return len(errors) == 0, errors


def get_phase18g_promoted_output_validation_score(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = payload or {}

    errors: list[str] = []
    warnings: list[str] = []
    score_categories: dict[str, int] = {}

    if payload.get("project_name") not in (None, "IdeasForgeAI"):
        errors.append("project_name must equal IdeasForgeAI when provided")

    existing_files: list[str] = []
    missing_files: list[str] = []
    extra_files: list[str] = []

    if not PROMOTED_TARGET.exists():
        errors.append("Phase 18 promoted target folder is missing")
        missing_files = REQUIRED_FILES[:]
    else:
        existing_files = sorted(item.name for item in PROMOTED_TARGET.iterdir() if item.is_file())
        missing_files = [name for name in REQUIRED_FILES if name not in existing_files]
        extra_files = [name for name in existing_files if name not in REQUIRED_FILES]

    required_files_ok = PROMOTED_TARGET.exists() and not missing_files and not extra_files
    score_categories["required_files_score"] = _score(required_files_ok)

    index_html = ""
    styles_css = ""
    app_js = ""
    promotion_manifest = None
    rollback_manifest = None

    if PROMOTED_TARGET.exists():
        if (PROMOTED_TARGET / "index.html").exists():
            index_html = _read_text(PROMOTED_TARGET / "index.html")
        if (PROMOTED_TARGET / "styles.css").exists():
            styles_css = _read_text(PROMOTED_TARGET / "styles.css")
        if (PROMOTED_TARGET / "app.js").exists():
            app_js = _read_text(PROMOTED_TARGET / "app.js")

        if (PROMOTED_TARGET / "promotion-manifest.json").exists():
            promotion_manifest, manifest_errors = _read_json(PROMOTED_TARGET / "promotion-manifest.json")
            errors.extend(manifest_errors)

        if (PROMOTED_TARGET / "rollback-manifest.json").exists():
            rollback_manifest, rollback_errors = _read_json(PROMOTED_TARGET / "rollback-manifest.json")
            errors.extend(rollback_errors)

    index_lower = index_html.lower()
    css_lower = styles_css.lower()
    app_js_lower = app_js.lower()

    promoted_html_patch_marker_ok = (
        "ifai-phase17d-selected-section-patch" in index_lower
        and "phase 17d sandbox patch" in index_lower
        and "copied html only" in index_lower
    )
    score_categories["promoted_html_patch_marker_score"] = _score(promoted_html_patch_marker_ok)

    approved_script_ok, script_errors = _approved_local_scripts_only(index_html)
    errors.extend(script_errors)
    score_categories["approved_local_script_score"] = _score(approved_script_ok)

    html_runtime_blockers = [
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
        "deploy.yml",
        "render.yaml",
        "kisanmitra",
    ]

    html_runtime_safety_ok = not any(marker in index_lower for marker in html_runtime_blockers)
    score_categories["html_runtime_safety_score"] = _score(html_runtime_safety_ok)

    css_blockers = [
        "http://",
        "https://",
        "@import",
        "expression(",
        "javascript:",
        "kisanmitra",
    ]

    css_safety_ok = not any(marker in css_lower for marker in css_blockers)
    score_categories["css_safety_score"] = _score(css_safety_ok)

    app_js_blockers = [
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
        "secret",
        "token",
        "deploy",
        "kisanmitra",
    ]

    app_js_safety_ok = not any(marker in app_js_lower for marker in app_js_blockers)
    score_categories["app_js_safety_score"] = _score(app_js_safety_ok)

    promotion_manifest_ok = bool(
        promotion_manifest
        and promotion_manifest.get("project_name") == "IdeasForgeAI"
        and promotion_manifest.get("phase") == "Phase 18E - Controlled Promotion to Approved Preview Folder"
        and promotion_manifest.get("approved_by_human") is True
        and promotion_manifest.get("source_validation_score") == 100
        and promotion_manifest.get("phase17f_validation_passed") is True
        and promotion_manifest.get("phase18c_approval_validated") is True
        and promotion_manifest.get("phase18d_dry_run_validation_passed") is True
        and promotion_manifest.get("rollback_available") is True
        and promotion_manifest.get("promoted_output_validation_required") is True
        and promotion_manifest.get("deployment_allowed") is False
        and promotion_manifest.get("provider_calls_allowed") is False
        and promotion_manifest.get("database_writes_allowed") is False
        and promotion_manifest.get("secrets_allowed") is False
        and promotion_manifest.get("supabase_allowed") is False
        and promotion_manifest.get("auth_allowed") is False
        and promotion_manifest.get("real_generated_app_modified") is False
        and promotion_manifest.get("ideasforgeai_preview_v1_touched") is False
        and promotion_manifest.get("kisanmitra_production_touched") is False
    )
    score_categories["promotion_manifest_score"] = _score(promotion_manifest_ok)

    promotion_report = ""
    if (PROMOTED_TARGET / "phase18-promotion-report.md").exists():
        promotion_report = _read_text(PROMOTED_TARGET / "phase18-promotion-report.md").lower()

    phase18_promotion_report_ok = (
        "status: success" in promotion_report
        and "promotion performed: true" in promotion_report
        and "generated-apps/ideasforgeai-preview-v1 touched: false" in promotion_report
        and "deployment unlocked: false" in promotion_report
        and "provider calls allowed: false" in promotion_report
        and "database writes allowed: false" in promotion_report
        and "secrets allowed: false" in promotion_report
    )
    score_categories["phase18_promotion_report_score"] = _score(phase18_promotion_report_ok)

    phase18_validation_report = ""
    if (PROMOTED_TARGET / "phase18-validation-report.md").exists():
        phase18_validation_report = _read_text(PROMOTED_TARGET / "phase18-validation-report.md").lower()

    phase18_validation_report_ok = (
        "status: success" in phase18_validation_report
        and "controlled promotion completed" in phase18_validation_report
        and "no deployment was performed" in phase18_validation_report
        and "no provider calls were made" in phase18_validation_report
        and "no database writes were made" in phase18_validation_report
        and "no secrets were used" in phase18_validation_report
    )
    score_categories["phase18_validation_report_score"] = _score(phase18_validation_report_ok)

    rollback_manifest_ok = bool(
        rollback_manifest
        and rollback_manifest.get("patch_applied_to_copy_only") is True
        and rollback_manifest.get("real_generated_app_modified") is False
        and rollback_manifest.get("ideasforgeai_preview_v1_touched") is False
        and rollback_manifest.get("phase13e_sandbox_modified") is False
        and rollback_manifest.get("phase16f_sandbox_modified") is False
        and rollback_manifest.get("deployment_unlocked") is False
        and rollback_manifest.get("provider_calls_allowed") is False
        and rollback_manifest.get("database_writes_allowed") is False
        and rollback_manifest.get("secrets_allowed") is False
        and rollback_manifest.get("rollback_available") is True
    )
    score_categories["rollback_manifest_score"] = _score(rollback_manifest_ok)

    no_real_app_modification_ok = bool(
        promotion_manifest
        and promotion_manifest.get("real_generated_app_modified") is False
        and promotion_manifest.get("ideasforgeai_preview_v1_touched") is False
        and promotion_manifest.get("kisanmitra_production_touched") is False
    )
    score_categories["no_real_app_modification_score"] = _score(no_real_app_modification_ok)

    app_visible_combined = "\n".join(
        _read_text(PROMOTED_TARGET / name)
        for name in APP_VISIBLE_FILES
        if (PROMOTED_TARGET / name).exists()
    ).lower()

    kisanmitra_separation_ok = "kisanmitra" not in app_visible_combined
    score_categories["kisanmitra_separation_score"] = _score(kisanmitra_separation_ok)

    for name, value in score_categories.items():
        if value < 100:
            errors.append(f"{name} failed")

    overall_score = int(sum(score_categories.values()) / len(score_categories)) if score_categories else 0
    validation_passed = overall_score == 100 and not errors

    return {
        "status": "success" if validation_passed else "review_required",
        "phase": "Phase 18G - Promoted Output Validation Score",
        "target_folder": str(PROMOTED_TARGET),
        "existing_files": existing_files,
        "missing_files": missing_files,
        "extra_files": extra_files,
        "score_categories": score_categories,
        "overall_score": overall_score,
        "validation_passed": validation_passed,
        "validation_errors": errors,
        "validation_warnings": warnings,
        "next_required_phase": "Phase 18H - Phase 18 Freeze Review",
        **_locked_flags(),
    }
