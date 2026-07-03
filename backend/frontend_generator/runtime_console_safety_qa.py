from pathlib import Path
from typing import Any
import re


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
        "runtime_console_safety_qa_only": True,
        "runtime_safety_qa_only": True,
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


def get_phase22e_runtime_console_safety_qa(payload: dict[str, Any] | None = None) -> dict[str, Any]:
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
    app_js = _read_text(MAIN_PREVIEW_TARGET / "app.js") if (MAIN_PREVIEW_TARGET / "app.js").exists() else ""

    combined = (index_html + "\n" + styles_css + "\n" + app_js).lower()
    index_lower = index_html.lower()
    css_lower = styles_css.lower()
    app_lower = app_js.lower()

    runtime_checks = {
        "required_files_present": MAIN_PREVIEW_TARGET.exists() and not missing_files,
        "approved_local_script_only": _approved_local_scripts_only(index_html),
        "local_stylesheet_present": 'href="styles.css"' in index_lower or "href='styles.css'" in index_lower,
        "local_app_js_present": 'src="app.js"' in index_lower or "src='app.js'" in index_lower,
        "no_iframe": "<iframe" not in index_lower,
        "no_fetch_calls": "fetch(" not in combined,
        "no_xmlhttprequest": "xmlhttprequest" not in combined,
        "no_external_http": "http://" not in combined and "https://" not in combined,
        "no_external_import": "@import" not in css_lower and "import " not in app_lower and "import(" not in app_lower,
        "no_localstorage": "localstorage" not in app_lower,
        "no_sessionstorage": "sessionstorage" not in app_lower,
        "no_supabase": "supabase" not in combined,
        "no_auth_logic": "auth" not in app_lower,
        "no_database_logic": "database" not in app_lower,
        "no_secret_markers": all(marker not in combined for marker in ["secret=", "token=", "api_key", "apikey", "service_role"]),
        "no_deployment_logic": all(marker not in combined for marker in ["deploy(", "deployment_unlocked=true", "render.yaml"]),
        "no_IdeasForgeAI_reference": "IdeasForgeAI" not in combined,
    }

    safe_runtime_markers = {
        "DOMContentLoaded listener allowed": "domcontentloaded" in app_lower,
        "preview dataset allowed": "phase20-polished" in app_lower,
    }

    failed_checks = [name for name, passed in runtime_checks.items() if not passed]

    if failed_checks:
        errors.extend(f"{name} failed" for name in failed_checks)

    validation_passed = not errors

    return {
        "status": "success" if validation_passed else "review_required",
        "phase": "Phase 22E - Runtime Console + Safety QA",
        "target_folder": str(MAIN_PREVIEW_TARGET),
        "browser_route": "/api/frontend-generator/phase22b-main-preview/index.html",
        "existing_files": existing_files,
        "missing_files": missing_files,
        "runtime_checks": runtime_checks,
        "safe_runtime_markers": safe_runtime_markers,
        "failed_checks": failed_checks,
        "validation_passed": validation_passed,
        "validation_errors": errors,
        "validation_warnings": warnings,
        "manual_console_check_required": True,
        "manual_console_check_items": [
            "Open Phase 22B browser route",
            "Open DevTools Console",
            "Hard refresh",
            "Confirm no uncaught red runtime errors",
            "Confirm no failed app network calls",
            "Ignore browser extension noise if any",
            "Confirm page layout still loads",
        ],
        "next_required_phase": "Phase 22F - Final Product QA Score",
        **_locked_flags(),
    }

