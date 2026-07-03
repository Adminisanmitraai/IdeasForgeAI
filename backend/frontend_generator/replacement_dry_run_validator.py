from pathlib import Path
from typing import Any
import json
import re


PROJECT_ROOT = Path("D:/APPS/IdeasForgeAI").resolve()

APPROVED_REPLACEMENT_SOURCE = (
    PROJECT_ROOT
    / "generated-apps"
    / "_phase20_final_apple_like_frontend_polish"
).resolve()

PROTECTED_REPLACEMENT_TARGET = (
    PROJECT_ROOT
    / "generated-apps"
    / "ideasforgeai-preview-v1"
).resolve()

REQUIRED_SOURCE_FILES = [
    "index.html",
    "styles.css",
    "app.js",
    "manifest.json",
    "README.md",
    "phase20-polish-report.md",
    "phase20-validation-report.md",
]

FUTURE_REPLACEMENT_FILES = REQUIRED_SOURCE_FILES + [
    "phase21-replacement-manifest.json",
    "phase21-rollback-manifest.json",
    "phase21-replacement-report.md",
    "phase21-validation-report.md",
]

BLOCKED_TARGET_MARKERS = [
    "backend/",
    "frontend/pages/",
    "frontend/shared/",
    "deployment",
    "render.yaml",
    ".env",
    "secret",
    "token",
    "api_key",
    "apikey",
    "supabase",
    "auth",
    "database",
    "IdeasForgeAI",
]


def _locked_flags() -> dict[str, Any]:
    return {
        "replacement_dry_run_only": True,
        "replacement_dry_run_passed": False,
        "next_phase_allowed": False,
        "file_write_allowed": False,
        "folder_creation_allowed": False,
        "files_copied": False,
        "files_replaced": False,
        "main_preview_target_touched": False,
        "phase20_polish_folder_modified": False,
        "production_replacement_performed": False,
        "production_replacement_allowed": False,
        "real_generated_app_modified": False,
        "ideasforgeai_preview_v1_touched": False,
        "generation_allowed": False,
        "backend_generation_unlocked": False,
        "deployment_unlocked": False,
        "provider_calls_allowed": False,
        "database_writes_allowed": False,
        "supabase_allowed": False,
        "auth_allowed": False,
        "secrets_allowed": False,
        "IdeasForgeAI_production_touched": False,
    }


def _approval_id_valid(value: str) -> bool:
    return bool(re.fullmatch(r"HUMAN-REPLACEMENT-APPROVED-21C-[A-Za-z0-9-]{4,64}", value or ""))


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="ignore")


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(_read_text(path))
        return value if isinstance(value, dict) else None
    except Exception:
        return None


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


def _validate_source_safety(errors: list[str]) -> None:
    index_html = _read_text(APPROVED_REPLACEMENT_SOURCE / "index.html")
    styles_css = _read_text(APPROVED_REPLACEMENT_SOURCE / "styles.css")
    app_js = _read_text(APPROVED_REPLACEMENT_SOURCE / "app.js")
    manifest = _read_json(APPROVED_REPLACEMENT_SOURCE / "manifest.json")

    index_lower = index_html.lower()
    css_lower = styles_css.lower()
    app_lower = app_js.lower()

    if not _approved_local_scripts_only(index_html):
        errors.append("source index.html contains non-approved script tag")

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

    for marker in html_blockers:
        if marker in index_lower:
            errors.append(f"blocked marker found in source index.html: {marker}")

    for marker in css_blockers:
        if marker in css_lower:
            errors.append(f"blocked marker found in source styles.css: {marker}")

    for marker in app_blockers:
        if marker in app_lower:
            errors.append(f"blocked marker found in source app.js: {marker}")

    manifest_ok = bool(
        manifest
        and manifest.get("project_name") == "IdeasForgeAI"
        and manifest.get("phase") == "Phase 20E - Controlled Final Polish Sandbox Creation"
        and manifest.get("production_replacement_allowed") is False
        and manifest.get("deployment_allowed") is False
        and manifest.get("provider_calls_allowed") is False
        and manifest.get("database_writes_allowed") is False
        and manifest.get("supabase_allowed") is False
        and manifest.get("auth_allowed") is False
        and manifest.get("secrets_allowed") is False
        and manifest.get("real_generated_app_modified") is False
        and manifest.get("ideasforgeai_preview_v1_touched") is False
        and manifest.get("IdeasForgeAI_production_touched") is False
    )

    if not manifest_ok:
        errors.append("source Phase 20 manifest is invalid or unsafe")


def validate_phase21d_replacement_dry_run(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = payload or {}

    errors: list[str] = []
    warnings: list[str] = []

    if payload.get("project_name") != "IdeasForgeAI":
        errors.append("project_name must equal IdeasForgeAI")

    if payload.get("source_phase") != "Phase 21D":
        errors.append("source_phase must equal Phase 21D")

    human_approval_id = str(payload.get("human_approval_id", ""))
    if not _approval_id_valid(human_approval_id):
        errors.append("human_approval_id must match HUMAN-REPLACEMENT-APPROVED-21C-* format")

    if payload.get("approved_by_human") is not True:
        errors.append("approved_by_human must be true")

    required_true_fields = [
        "phase20h_frozen",
        "phase20f_preview_route_working",
        "phase21a_frozen",
        "phase21b_frozen",
        "phase21c_frozen",
        "phase21c_approval_validated",
        "rollback_required",
        "rollback_snapshot_required",
        "replacement_manifest_required",
    ]

    for field in required_true_fields:
        if payload.get(field) is not True:
            errors.append(f"{field} must be true")

    if int(payload.get("phase20g_validation_score", 0)) != 100:
        errors.append("phase20g_validation_score must be 100")

    source_folder = str(payload.get("source_folder", "")).replace("\\", "/")
    approved_source = str(APPROVED_REPLACEMENT_SOURCE).replace("\\", "/")
    if source_folder != approved_source:
        errors.append("source_folder must equal approved Phase 20 polished source folder")

    target_folder = str(payload.get("target_folder", "")).replace("\\", "/")
    protected_target = str(PROTECTED_REPLACEMENT_TARGET).replace("\\", "/")
    if target_folder != protected_target:
        errors.append("target_folder must equal protected main preview target folder")

    for field in [
        "production_replacement_allowed",
        "deployment_allowed",
        "provider_calls_allowed",
        "database_writes_allowed",
        "supabase_allowed",
        "auth_allowed",
        "secrets_allowed",
    ]:
        if payload.get(field) is not False:
            errors.append(f"{field} must be false")

    combined_target = " ".join(str(v) for v in payload.values()).replace("\\", "/").lower()
    protected_target_lower = protected_target.lower()
    approved_source_lower = approved_source.lower()

    for marker in BLOCKED_TARGET_MARKERS:
        marker_lower = marker.lower()
        if marker_lower in combined_target:
            if marker_lower not in protected_target_lower and marker_lower not in approved_source_lower:
                errors.append(f"blocked marker found in dry-run payload: {marker}")

    existing_source_files: list[str] = []
    existing_target_files: list[str] = []

    if not APPROVED_REPLACEMENT_SOURCE.exists():
        errors.append("approved Phase 20 polished source folder does not exist")
    else:
        existing_source_files = sorted(
            item.name for item in APPROVED_REPLACEMENT_SOURCE.iterdir() if item.is_file()
        )
        missing_source_files = [
            name for name in REQUIRED_SOURCE_FILES if name not in existing_source_files
        ]
        if missing_source_files:
            errors.append("missing required source files: " + ", ".join(missing_source_files))
        else:
            _validate_source_safety(errors)

    if not PROTECTED_REPLACEMENT_TARGET.exists():
        errors.append("protected main preview target folder does not exist")
    else:
        existing_target_files = sorted(
            item.name for item in PROTECTED_REPLACEMENT_TARGET.iterdir() if item.is_file()
        )
        if not existing_target_files:
            warnings.append("protected main preview target exists but has no files")

    validation_passed = not errors

    locked = _locked_flags()
    locked["replacement_dry_run_passed"] = validation_passed
    locked["next_phase_allowed"] = validation_passed

    return {
        "status": "success" if validation_passed else "blocked",
        "phase": "Phase 21D - Replacement Dry-Run Validator",
        "validation_passed": validation_passed,
        "validation_errors": errors,
        "validation_warnings": warnings,
        "approved_replacement_source": str(APPROVED_REPLACEMENT_SOURCE),
        "protected_replacement_target": str(PROTECTED_REPLACEMENT_TARGET),
        "existing_source_files": existing_source_files,
        "existing_target_files": existing_target_files,
        "required_source_files": REQUIRED_SOURCE_FILES,
        "future_replacement_files": FUTURE_REPLACEMENT_FILES,
        "next_required_phase": "Phase 21E - Rollback Snapshot + Safety Manifest",
        **locked,
    }

