from pathlib import Path
from typing import Any
import json
import re


PROJECT_ROOT = Path("D:/APPS/IdeasForgeAI").resolve()

CANDIDATE_TARGET = (
    PROJECT_ROOT
    / "generated-apps"
    / "_phase19_main_preview_candidate"
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
    "candidate-manifest.json",
    "phase19-candidate-report.md",
    "phase19-validation-report.md",
]


def _locked_flags() -> dict[str, Any]:
    return {
        "candidate_output_validation_score_only": True,
        "validation_score_only": True,
        "file_write_allowed": False,
        "folder_creation_allowed": False,
        "candidate_creation_performed_by_this_phase": False,
        "production_replacement_allowed": False,
        "real_generated_app_modified": False,
        "phase13e_sandbox_modified": False,
        "phase16f_sandbox_modified": False,
        "phase17_sandbox_modified": False,
        "phase18_promoted_folder_modified": False,
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


def get_phase19g_candidate_output_validation_score(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = payload or {}

    errors: list[str] = []
    warnings: list[str] = []

    if payload.get("project_name") not in (None, "IdeasForgeAI"):
        errors.append("project_name must equal IdeasForgeAI when provided")

    existing_files: list[str] = []
    missing_files: list[str] = REQUIRED_FILES[:]
    extra_files: list[str] = []

    if CANDIDATE_TARGET.exists():
        existing_files = sorted(item.name for item in CANDIDATE_TARGET.iterdir() if item.is_file())
        missing_files = [name for name in REQUIRED_FILES if name not in existing_files]
        extra_files = [name for name in existing_files if name not in REQUIRED_FILES]
    else:
        errors.append("Phase 19 candidate target folder is missing")

    index_html = _read_text(CANDIDATE_TARGET / "index.html") if (CANDIDATE_TARGET / "index.html").exists() else ""
    styles_css = _read_text(CANDIDATE_TARGET / "styles.css") if (CANDIDATE_TARGET / "styles.css").exists() else ""
    app_js = _read_text(CANDIDATE_TARGET / "app.js") if (CANDIDATE_TARGET / "app.js").exists() else ""

    index_lower = index_html.lower()
    css_lower = styles_css.lower()
    app_lower = app_js.lower()

    candidate_manifest = _read_json(CANDIDATE_TARGET / "candidate-manifest.json") if (CANDIDATE_TARGET / "candidate-manifest.json").exists() else None
    promotion_manifest = _read_json(CANDIDATE_TARGET / "promotion-manifest.json") if (CANDIDATE_TARGET / "promotion-manifest.json").exists() else None
    rollback_manifest = _read_json(CANDIDATE_TARGET / "rollback-manifest.json") if (CANDIDATE_TARGET / "rollback-manifest.json").exists() else None

    phase19_candidate_report = _read_text(CANDIDATE_TARGET / "phase19-candidate-report.md").lower() if (CANDIDATE_TARGET / "phase19-candidate-report.md").exists() else ""
    phase19_validation_report = _read_text(CANDIDATE_TARGET / "phase19-validation-report.md").lower() if (CANDIDATE_TARGET / "phase19-validation-report.md").exists() else ""

    runtime_blockers = [
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
        "kisanmitra",
    ]

    css_blockers = [
        "http://",
        "https://",
        "@import",
        "expression(",
        "javascript:",
        "kisanmitra",
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
        "secret",
        "token",
        "deploy",
        "kisanmitra",
    ]

    score_categories = {
        "required_files_score": _score(CANDIDATE_TARGET.exists() and not missing_files and not extra_files),
        "candidate_html_patch_marker_score": _score("ifai-phase17d-selected-section-patch" in index_lower),
        "approved_local_script_score": _score(_approved_local_scripts_only(index_html)),
        "html_runtime_safety_score": _score(not any(marker in index_lower for marker in runtime_blockers)),
        "css_safety_score": _score(not any(marker in css_lower for marker in css_blockers)),
        "app_js_safety_score": _score(not any(marker in app_lower for marker in app_blockers)),
        "candidate_manifest_score": _score(
            bool(candidate_manifest)
            and candidate_manifest.get("project_name") == "IdeasForgeAI"
            and candidate_manifest.get("phase") == "Phase 19E - Controlled Candidate Folder Creation"
            and candidate_manifest.get("production_replacement_allowed") is False
            and candidate_manifest.get("deployment_allowed") is False
            and candidate_manifest.get("provider_calls_allowed") is False
            and candidate_manifest.get("database_writes_allowed") is False
            and candidate_manifest.get("secrets_allowed") is False
            and candidate_manifest.get("real_generated_app_modified") is False
            and candidate_manifest.get("ideasforgeai_preview_v1_touched") is False
            and candidate_manifest.get("kisanmitra_production_touched") is False
        ),
        "promotion_manifest_score": _score(
            bool(promotion_manifest)
            and promotion_manifest.get("project_name") == "IdeasForgeAI"
            and promotion_manifest.get("deployment_allowed") is False
            and promotion_manifest.get("provider_calls_allowed") is False
            and promotion_manifest.get("database_writes_allowed") is False
            and promotion_manifest.get("secrets_allowed") is False
            and promotion_manifest.get("real_generated_app_modified") is False
            and promotion_manifest.get("ideasforgeai_preview_v1_touched") is False
        ),
        "rollback_manifest_score": _score(
            bool(rollback_manifest)
            and rollback_manifest.get("real_generated_app_modified") is False
            and rollback_manifest.get("ideasforgeai_preview_v1_touched") is False
            and rollback_manifest.get("deployment_unlocked") is False
            and rollback_manifest.get("provider_calls_allowed") is False
            and rollback_manifest.get("database_writes_allowed") is False
            and rollback_manifest.get("secrets_allowed") is False
        ),
        "phase19_candidate_report_score": _score(
            "status: success" in phase19_candidate_report
            and "candidate creation performed: true" in phase19_candidate_report
            and "production replacement allowed: false" in phase19_candidate_report
            and "generated-apps/ideasforgeai-preview-v1 touched: false" in phase19_candidate_report
        ),
        "phase19_validation_report_score": _score(
            "status: success" in phase19_validation_report
            and "controlled candidate folder creation completed" in phase19_validation_report
            and "no production replacement was performed" in phase19_validation_report
            and "no deployment was performed" in phase19_validation_report
        ),
        "kisanmitra_separation_score": _score("kisanmitra" not in (index_lower + css_lower + app_lower)),
    }

    for name, value in score_categories.items():
        if value < 100:
            errors.append(f"{name} failed")

    overall_score = int(sum(score_categories.values()) / len(score_categories)) if score_categories else 0
    validation_passed = overall_score == 100 and not errors

    return {
        "status": "success" if validation_passed else "review_required",
        "phase": "Phase 19G - Candidate Output Validation Score",
        "target_folder": str(CANDIDATE_TARGET),
        "existing_files": existing_files,
        "missing_files": missing_files,
        "extra_files": extra_files,
        "score_categories": score_categories,
        "overall_score": overall_score,
        "validation_passed": validation_passed,
        "validation_errors": errors,
        "validation_warnings": warnings,
        "next_required_phase": "Phase 19H - Phase 19 Freeze Review",
        **_locked_flags(),
    }
