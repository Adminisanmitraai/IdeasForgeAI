"""Phase 13G generated output validation score.

Read-only scoring for the existing Phase 13E sandbox output.
No file writes.
No folder creation.
No HTML/CSS/JS generation.
No provider calls.
No deployment.
No Supabase/auth/database/secrets.
"""

from copy import deepcopy
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


TARGET_FOLDER_TEXT = "D:/APPS/IdeasForgeAI/generated-apps/_phase13e_controlled_html_css_js_generation"
LOCAL_TARGET_FOLDER = Path("D:/APPS/IdeasForgeAI/generated-apps/_phase13e_controlled_html_css_js_generation")
REQUIRED_FILES = [
    "manifest.json",
    "index.html",
    "styles.css",
    "app.js",
    "README.md",
    "validation-report.md",
]

LOCKED_FLAGS = {
    "file_write_allowed": False,
    "folder_creation_allowed": False,
    "generation_allowed": False,
    "backend_generation_unlocked": False,
    "deployment_unlocked": False,
    "provider_calls_allowed": False,
    "database_writes_allowed": False,
    "secrets_allowed": False,
}

DEFAULT_APPROVED_PAYLOAD = {
    "project_name": "IdeasForgeAI",
    "human_approval_id": "phase13g-human-approved-validation-score",
    "approved_by_human": True,
    "source_phase": "Phase 13G",
}


def _read_text(file_name: str) -> Tuple[str, Optional[str]]:
    path = LOCAL_TARGET_FOLDER / file_name
    try:
        return path.read_text(encoding="utf-8"), None
    except FileNotFoundError:
        return "", f"{file_name} is missing."
    except UnicodeDecodeError:
        return "", f"{file_name} is not valid UTF-8 text."


def _score_from_checks(checks: Dict[str, bool]) -> int:
    if not checks:
        return 0
    passed = sum(1 for value in checks.values() if value)
    return round((passed / len(checks)) * 100)


def _validate_payload(payload: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    if payload and payload.get("project_name") != "IdeasForgeAI":
        errors.append("project_name must equal IdeasForgeAI.")
    if payload and not str(payload.get("human_approval_id") or "").strip():
        errors.append("human_approval_id is required when payload is supplied.")
    if payload and payload.get("approved_by_human") is not True:
        errors.append("approved_by_human must be true when payload is supplied.")
    if payload and payload.get("source_phase") != "Phase 13G":
        errors.append("source_phase must equal Phase 13G when payload is supplied.")
    return errors


def _scan_files() -> Tuple[List[str], List[str], List[str]]:
    if not LOCAL_TARGET_FOLDER.exists():
        return [], REQUIRED_FILES[:], []

    actual_file_names = sorted(path.name for path in LOCAL_TARGET_FOLDER.iterdir() if path.is_file())
    folder_names = sorted(f"{path.name}/" for path in LOCAL_TARGET_FOLDER.iterdir() if path.is_dir())
    missing_files = [file_name for file_name in REQUIRED_FILES if file_name not in actual_file_names]
    extra_files = [file_name for file_name in actual_file_names if file_name not in REQUIRED_FILES] + folder_names
    files_checked = [file_name for file_name in REQUIRED_FILES if file_name in actual_file_names] + extra_files
    return files_checked, missing_files, extra_files


def _build_score(payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    payload = deepcopy(payload) if payload else {}
    validation_errors = _validate_payload(payload)
    validation_warnings: List[str] = []

    files_checked, missing_files, extra_files = _scan_files()
    if missing_files:
        validation_errors.append(f"Missing required files: {', '.join(missing_files)}")
    if extra_files:
        validation_errors.append(f"Extra files found: {', '.join(extra_files)}")

    index_html, html_error = _read_text("index.html")
    styles_css, css_error = _read_text("styles.css")
    app_js, js_error = _read_text("app.js")
    manifest_text, manifest_error = _read_text("manifest.json")
    validation_report, validation_report_error = _read_text("validation-report.md")
    readme_text, readme_error = _read_text("README.md")
    for error in [html_error, css_error, js_error, manifest_error, validation_report_error, readme_error]:
        if error:
            validation_errors.append(error)

    lower_html = index_html.lower()
    lower_css = styles_css.lower()
    lower_js = app_js.lower()

    html_checks = {
        "no_external_script": not bool(re.search(r"<script[^>]+src=[\"'](?:https?:)?//", index_html, re.IGNORECASE)),
        "no_iframe": "<iframe" not in lower_html,
        "no_external_url": "http://" not in lower_html and "https://" not in lower_html,
        "no_kisanmitra_reference": "kisanmitra" not in lower_html,
    }
    css_checks = {
        "no_http": "http" not in lower_css,
        "no_https": "https" not in lower_css,
        "no_import": "@import" not in lower_css,
    }
    js_checks = {
        "no_fetch": "fetch" not in lower_js,
        "no_xmlhttprequest": "xmlhttprequest" not in lower_js,
        "no_import": "import" not in lower_js,
        "no_http": "http" not in lower_js,
        "no_https": "https" not in lower_js,
        "no_localstorage": "localstorage" not in lower_js,
        "no_sessionstorage": "sessionstorage" not in lower_js,
        "no_provider_reference": "provider" not in lower_js,
        "no_supabase_reference": "supabase" not in lower_js,
        "no_auth_reference": "auth" not in lower_js,
        "no_database_reference": "database" not in lower_js,
        "no_api_key_marker": "api key" not in lower_js and "api_key" not in lower_js,
        "no_deployment_marker": "deploy" not in lower_js,
    }

    manifest_json = None
    manifest_valid = False
    if manifest_text:
        try:
            manifest_json = json.loads(manifest_text)
            manifest_valid = True
        except json.JSONDecodeError as exc:
            validation_errors.append(f"manifest.json is invalid JSON: {exc.msg}")

    manifest_checks = {
        "valid_json": manifest_valid,
        "project_name_is_ideasforgeai": bool(manifest_json and manifest_json.get("project_name") == "IdeasForgeAI"),
        "target_folder_is_phase13e": bool(manifest_json and manifest_json.get("target_folder") == TARGET_FOLDER_TEXT),
        "write_order_matches_required": bool(manifest_json and manifest_json.get("write_order") == REQUIRED_FILES),
        "next_phase_is_phase13f_or_later": bool(manifest_json and str(manifest_json.get("next_required_phase", "")).startswith("Phase 13")),
    }
    validation_report_checks = {
        "exists": "validation-report.md" in files_checked,
        "non_empty": bool(validation_report.strip()),
    }
    readme_checks = {
        "exists": "README.md" in files_checked,
        "non_empty": bool(readme_text.strip()),
    }
    required_file_checks = {
        "all_required_files_exist": not missing_files,
        "no_extra_files": not extra_files,
        "exact_file_count": len(files_checked) == len(REQUIRED_FILES),
    }

    no_external_dependency_checks = {
        "html_no_external_url": html_checks["no_external_url"],
        "html_no_external_script": html_checks["no_external_script"],
        "css_no_external_dependency": css_checks["no_http"] and css_checks["no_https"] and css_checks["no_import"],
        "js_no_external_dependency": js_checks["no_http"] and js_checks["no_https"] and js_checks["no_import"],
    }
    no_provider_call_checks = {
        "js_no_fetch": js_checks["no_fetch"],
        "js_no_xmlhttprequest": js_checks["no_xmlhttprequest"],
        "js_no_provider_reference": js_checks["no_provider_reference"],
        "manifest_provider_calls_false": bool(manifest_json and manifest_json.get("safety_flags", {}).get("provider_calls_allowed") is False),
    }
    no_database_auth_secret_checks = {
        "js_no_supabase_reference": js_checks["no_supabase_reference"],
        "js_no_auth_reference": js_checks["no_auth_reference"],
        "js_no_database_reference": js_checks["no_database_reference"],
        "js_no_storage": js_checks["no_localstorage"] and js_checks["no_sessionstorage"],
        "js_no_api_key_marker": js_checks["no_api_key_marker"],
        "manifest_database_false": bool(manifest_json and manifest_json.get("safety_flags", {}).get("database_writes_allowed") is False),
        "manifest_secrets_false": bool(manifest_json and manifest_json.get("safety_flags", {}).get("secrets_allowed") is False),
    }
    kisanmitra_checks = {
        "no_kisanmitra_visible_or_runtime_reference": "kisanmitra" not in "\n".join([index_html, styles_css, app_js]).lower(),
        "manifest_connection_locked": bool(manifest_json and manifest_json.get("safety_flags", {}).get("kisanmitra_connection_allowed") is False),
        "target_folder_is_ideasforgeai_only": "kisanmitra" not in TARGET_FOLDER_TEXT.lower(),
    }
    preview_runner_checks = {
        "entry_file_exists": "index.html" in files_checked,
        "required_files_exact": not missing_files and not extra_files,
        "local_assets_exist": "styles.css" in files_checked and "app.js" in files_checked,
    }

    all_named_checks = {
        **{f"html_{key}": value for key, value in html_checks.items()},
        **{f"css_{key}": value for key, value in css_checks.items()},
        **{f"js_{key}": value for key, value in js_checks.items()},
        **{f"manifest_{key}": value for key, value in manifest_checks.items()},
        **{f"validation_report_{key}": value for key, value in validation_report_checks.items()},
        **{f"readme_{key}": value for key, value in readme_checks.items()},
        **{f"required_files_{key}": value for key, value in required_file_checks.items()},
    }
    failed_checks = [name for name, passed in all_named_checks.items() if not passed]
    if failed_checks:
        validation_errors.extend(f"Failed check: {name}" for name in failed_checks)

    score_categories = {
        "required_files_score": _score_from_checks(required_file_checks),
        "html_safety_score": _score_from_checks(html_checks),
        "css_safety_score": _score_from_checks(css_checks),
        "js_safety_score": _score_from_checks(js_checks),
        "manifest_score": _score_from_checks(manifest_checks),
        "validation_report_score": _score_from_checks(validation_report_checks),
        "readme_score": _score_from_checks(readme_checks),
        "no_external_dependency_score": _score_from_checks(no_external_dependency_checks),
        "no_provider_call_score": _score_from_checks(no_provider_call_checks),
        "no_database_auth_secret_score": _score_from_checks(no_database_auth_secret_checks),
        "kisanmitra_separation_score": _score_from_checks(kisanmitra_checks),
        "preview_runner_compatibility_score": _score_from_checks(preview_runner_checks),
    }
    overall_score = round(sum(score_categories.values()) / len(score_categories)) if score_categories else 0
    score_categories["overall_score"] = overall_score
    validation_passed = not validation_errors and overall_score == 100

    if overall_score < 100 and not validation_errors:
        validation_warnings.append("Overall score is below 100 even though no hard validation errors were collected.")

    return {
        "status": "success" if validation_passed else "blocked",
        "phase": "Phase 13G - Generated Output Validation Score",
        "validation_score_only": True,
        "target_folder": TARGET_FOLDER_TEXT,
        "files_checked": files_checked,
        "extra_files_found": extra_files,
        "missing_files_found": missing_files,
        "score_categories": score_categories,
        "overall_score": overall_score,
        "validation_passed": validation_passed,
        "validation_errors": validation_errors,
        "validation_warnings": validation_warnings,
        **deepcopy(LOCKED_FLAGS),
        "next_required_phase": "Phase 13H",
        "side_effects": {
            "files_written": False,
            "folders_created": False,
            "files_modified": False,
            "files_deleted": False,
            "html_css_js_generated": False,
            "providers_called": False,
            "deployment_started": False,
            "database_writes_made": False,
            "secrets_used": False,
        },
    }


def build_phase13g_generated_output_validation_score_response(payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Return read-only validation scores for the existing Phase 13E sandbox output."""

    return _build_score(payload)