from pathlib import Path
import re


PROJECT_ROOT = Path("D:/APPS/IdeasForgeAI").resolve()

APPROVED_REFERENCE_TARGET = (
    PROJECT_ROOT
    / "generated-apps"
    / "_phase13e_controlled_html_css_js_generation"
).resolve()

ALLOWED_SECTION_TYPES = {
    "navbar",
    "hero",
    "features",
    "product_card",
    "pricing",
    "cta",
    "footer",
    "form",
    "dashboard_panel",
    "sidebar",
    "preview_card",
    "trust_section",
    "approval_section",
}

ALLOWED_SOURCE_FILES = {
    "index.html",
}

BLOCKED_TARGET_MARKERS = [
    "generated-apps/ideasforgeai-preview-v1",
    "backend/",
    "frontend/pages/",
    "frontend/shared/",
    "docs/",
    ".env",
    "secret",
    "token",
    "key",
    "pem",
    "deploy",
    "deployment",
    "supabase",
    "auth",
    "database",
    "IdeasForgeAI",
    "IdeasForgeAI",
]


def _locked_flags() -> dict:
    return {
        "dry_run_only": True,
        "section_patch_allowed": False,
        "section_regeneration_allowed": False,
        "file_write_allowed": False,
        "folder_creation_allowed": False,
        "generation_allowed": False,
        "backend_generation_unlocked": False,
        "deployment_unlocked": False,
        "provider_calls_allowed": False,
        "database_writes_allowed": False,
        "secrets_allowed": False,
        "supabase_allowed": False,
        "auth_allowed": False,
    }


def _is_valid_generation_id(value: str) -> bool:
    return bool(re.fullmatch(r"IF-SECTION-DRYRUN-[A-Za-z0-9-]{4,64}", value or ""))


def validate_phase16e_section_regeneration_dry_run(payload: dict | None = None) -> dict:
    payload = payload or {}
    errors = []
    warnings = []

    project_name = payload.get("project_name")
    generation_id = payload.get("generation_id")
    selected_section_id = payload.get("selected_section_id")
    selected_section_type = payload.get("selected_section_type")
    source_file = payload.get("source_file")
    start_marker = payload.get("start_marker")
    end_marker = payload.get("end_marker")
    current_section_html = payload.get("current_section_html")
    user_requested_change = payload.get("user_requested_change")
    human_approval_id = payload.get("human_approval_id")

    if project_name != "IdeasForgeAI":
        errors.append("project_name must equal IdeasForgeAI")

    if not _is_valid_generation_id(generation_id):
        errors.append("generation_id must match IF-SECTION-DRYRUN-* format")

    if not selected_section_id:
        errors.append("selected_section_id is required")

    if selected_section_type not in ALLOWED_SECTION_TYPES:
        errors.append("selected_section_type is not allowed")

    if source_file not in ALLOWED_SOURCE_FILES:
        errors.append("source_file must be index.html only for this dry-run phase")

    if not start_marker or "IF_SECTION_START" not in start_marker:
        errors.append("valid start_marker is required")

    if not end_marker or "IF_SECTION_END" not in end_marker:
        errors.append("valid end_marker is required")

    if selected_section_id and start_marker and selected_section_id not in start_marker:
        errors.append("selected_section_id must appear in start_marker")

    if selected_section_id and end_marker and selected_section_id not in end_marker:
        errors.append("selected_section_id must appear in end_marker")

    if not current_section_html:
        errors.append("current_section_html is required")

    if not user_requested_change:
        errors.append("user_requested_change is required")

    if not human_approval_id:
        errors.append("human_approval_id is required")

    if payload.get("approved_by_human") is not True:
        errors.append("approved_by_human must be true")

    if payload.get("validation_required") is not True:
        errors.append("validation_required must be true")

    if payload.get("approval_required") is not True:
        errors.append("approval_required must be true")

    if payload.get("rollback_required") is not True:
        errors.append("rollback_required must be true")

    locked_false_fields = [
        "deployment_allowed",
        "provider_calls_allowed",
        "database_writes_allowed",
        "secrets_allowed",
        "supabase_allowed",
        "auth_allowed",
    ]

    for field in locked_false_fields:
        if payload.get(field) is not False:
            errors.append(f"{field} must be false")

    target_folder = str(payload.get("target_folder", APPROVED_REFERENCE_TARGET)).replace("\\", "/")
    approved_target = str(APPROVED_REFERENCE_TARGET).replace("\\", "/")

    if target_folder != approved_target:
        errors.append("target_folder must equal the approved Phase 13E sandbox reference target")

    lower_combined = " ".join(str(v) for v in payload.values()).replace("\\", "/").lower()
    for marker in BLOCKED_TARGET_MARKERS:
        if marker.lower() in lower_combined:
            if marker.lower() not in approved_target.lower():
                errors.append(f"blocked target marker found: {marker}")

    if "<script" in str(current_section_html).lower():
        warnings.append("current_section_html contains script tag; future patch must not add scripts")

    validation_passed = not errors

    return {
        "status": "success" if validation_passed else "blocked",
        "phase": "Phase 16E - Section Regeneration Dry-Run Validator",
        "validation_passed": validation_passed,
        "validation_errors": errors,
        "validation_warnings": warnings,
        "checked_section_id": selected_section_id,
        "checked_section_type": selected_section_type,
        "checked_source_file": source_file,
        "checked_target_folder": str(APPROVED_REFERENCE_TARGET),
        "allowed_section_types": sorted(ALLOWED_SECTION_TYPES),
        "allowed_source_files": sorted(ALLOWED_SOURCE_FILES),
        "next_required_phase": "Phase 16F - Controlled Section Patch Sandbox",
        **_locked_flags(),
    }

