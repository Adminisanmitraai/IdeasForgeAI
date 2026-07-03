"""Phase 13C multi-file dry-run validator.

Validation metadata only.
No file writes.
No folder creation.
No generated app creation.
No HTML/CSS/JS generation.
No provider calls.
No deployment.
"""

from copy import deepcopy
from pathlib import PureWindowsPath
import re
from typing import Any, Dict, List, Optional, Tuple

from backend.frontend_generator.multi_file_generation_contract_schema import (
    ALLOWED_FUTURE_FILES,
    BLOCKED_FILES_AND_LOCATIONS,
    FILE_ENTRY_SCHEMA,
    SAFETY_FLAGS as CONTRACT_SAFETY_FLAGS,
    WRITE_ORDER,
)


IDEASFORGEAI_ROOT = PureWindowsPath("D:/APPS/IdeasForgeAI")
GENERATED_APPS_ROOT = IDEASFORGEAI_ROOT / "generated-apps"
GENERATION_ID_PATTERN = re.compile(r"^phase13c-[a-z0-9][a-z0-9-]{2,80}$")
DOCUMENTATION_PHASES = {"Phase 13C", "phase_13c", "documentation", "docs"}
PHASE_12_SANDBOX_NAMES = {
    "_phase12d_write_sandbox",
    "_phase12e_backup_sandbox",
    "_phase12g_controlled_html_css_generation",
}
DEPLOYMENT_CONFIG_FILES = {
    "render.yaml",
    "vercel.json",
    "netlify.toml",
    "firebase.json",
    "dockerfile",
    "docker-compose.yml",
    "railway.json",
    "fly.toml",
}
ROOT_PRODUCTION_FILES = {
    "README.md",
    "PROJECT_STATUS.md",
    "package.json",
    "requirements.txt",
    "pyproject.toml",
    "setup-ideasforge.ps1",
}
SECRET_FILE_NAMES = {
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",
    ".env.supabase",
    "secrets.json",
}
DATABASE_AUTH_SUPABASE_MARKERS = {
    "database",
    "databases",
    "db",
    "auth",
    "supabase",
    "migrations",
    "schema.sql",
}
BLOCKED_PAYLOAD_FIELDS = {
    "content",
    "file_content",
    "html_output",
    "css_output",
    "js_output",
    "react_output",
    "generated_files",
    "generated_app_path",
    "file_write_request",
    "deploy_request",
    "provider_prompt",
    "secret_value",
    "database_write",
    "supabase_config",
    "auth_config",
}

SAFETY_FLAGS = {
    **deepcopy(CONTRACT_SAFETY_FLAGS),
    "dry_run_only": True,
    "multi_file_validation_only": True,
    "backend_generation_unlocked": False,
    "deployment_unlocked": False,
}

DEFAULT_PLANNED_PAYLOAD = {
    "project_name": "IdeasForgeAI",
    "generation_id": "phase13c-safe-multi-file-dry-run",
    "target_folder": "D:/APPS/IdeasForgeAI/generated-apps/_phase13_controlled_multi_file_generation_v1",
    "source_phase": "Phase 13C",
    "allowed_files": list(ALLOWED_FUTURE_FILES),
    "blocked_files": list(BLOCKED_FILES_AND_LOCATIONS),
    "file_entries": [
        {
            **deepcopy(FILE_ENTRY_SCHEMA),
            "file_name": file_name,
            "relative_path": file_name,
            "file_type": "markdown" if file_name.endswith(".md") else file_name.rsplit(".", 1)[-1],
            "purpose": f"Future approved Phase 13 {file_name} output placeholder.",
            "write_status": "dry_run_only",
            "required": True,
            "dependency_order": WRITE_ORDER.index(file_name) + 1,
        }
        for file_name in WRITE_ORDER
    ],
    "write_order": list(WRITE_ORDER),
    "approval_required": True,
    "approved_by_human": True,
    "dry_run_validation_passed": False,
    "backup_required": True,
    "rollback_required": True,
    "deployment_allowed": False,
    "provider_calls_allowed": False,
    "database_writes_allowed": False,
    "secrets_allowed": False,
    "supabase_allowed": False,
    "auth_allowed": False,
}

DEFAULT_REJECTED_PAYLOAD = {
    **deepcopy(DEFAULT_PLANNED_PAYLOAD),
    "generation_id": "bad-id",
    "target_folder": "D:/APPS/IdeasForgeAI/generated-apps/ideasforgeai-preview-v1",
    "allowed_files": ["index.html", "styles.css", "deploy.yml"],
    "write_order": ["index.html", "manifest.json"],
    "deployment_allowed": True,
    "provider_calls_allowed": True,
}


def _as_windows_path(path_value: Any) -> Tuple[Optional[PureWindowsPath], str]:
    raw_path = str(path_value or "").strip().replace("\\", "/")
    if not raw_path:
        return None, ""
    path = PureWindowsPath(raw_path)
    if not path.is_absolute():
        path = IDEASFORGEAI_ROOT / raw_path
    return path, str(path).replace("\\", "/")


def _is_relative_to(path: PureWindowsPath, parent: PureWindowsPath) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def _contains_path_traversal(path_value: Any) -> bool:
    return ".." in PureWindowsPath(str(path_value or "").replace("\\", "/")).parts


def _normalized_relative(path_value: Any) -> str:
    return str(path_value or "").strip().replace("\\", "/").lstrip("/")


def _path_is_blocked(relative_path: str, source_phase: str) -> Optional[str]:
    normalized = _normalized_relative(relative_path)
    lower_path = normalized.lower()
    parts = [part.lower() for part in PureWindowsPath(normalized).parts]
    first_part = lower_path.split("/", 1)[0]
    file_name = lower_path.rsplit("/", 1)[-1]

    if _contains_path_traversal(normalized):
        return "Path traversal is blocked."
    if lower_path.startswith("backend/") or first_part == "backend":
        return "backend paths are blocked."
    if lower_path.startswith("frontend/pages/"):
        return "frontend/pages paths are blocked."
    if lower_path.startswith("frontend/shared/"):
        return "frontend/shared paths are blocked."
    if lower_path.startswith("docs/") and source_phase not in DOCUMENTATION_PHASES:
        return "docs writes are blocked unless this is a documentation phase."
    if normalized not in ALLOWED_FUTURE_FILES and (normalized in ROOT_PRODUCTION_FILES or first_part in ROOT_PRODUCTION_FILES):
        return "root production files are blocked."
    if file_name in DEPLOYMENT_CONFIG_FILES:
        return "deployment config files are blocked."
    if file_name in SECRET_FILE_NAMES or file_name.startswith(".env"):
        return "secrets/env files are blocked."
    if any(marker in parts or marker == file_name for marker in DATABASE_AUTH_SUPABASE_MARKERS):
        return "database/auth/Supabase files are blocked."
    if "IdeasForgeAI" in lower_path:
        return "IdeasForgeAI paths are blocked."
    return None


def _validate_project_and_generation(payload: Dict[str, Any], errors: List[str]) -> None:
    if payload.get("project_name") != "IdeasForgeAI":
        errors.append("project_name must equal IdeasForgeAI.")
    generation_id = str(payload.get("generation_id") or "").strip()
    if not GENERATION_ID_PATTERN.match(generation_id):
        errors.append("generation_id must match phase13c-[a-z0-9-] and be 12-90 characters.")


def _validate_target_folder(payload: Dict[str, Any], errors: List[str], warnings: List[str]) -> str:
    target_path, checked_target_folder = _as_windows_path(payload.get("target_folder"))
    raw_target = str(payload.get("target_folder") or "").strip()

    if not raw_target:
        errors.append("target_folder is required.")
        return ""
    if _contains_path_traversal(raw_target):
        errors.append("target_folder must not contain path traversal.")
    if target_path is None:
        errors.append("target_folder could not be normalized as a Windows path.")
        return checked_target_folder
    if not _is_relative_to(target_path, IDEASFORGEAI_ROOT):
        errors.append("target_folder must stay inside D:/APPS/IdeasForgeAI.")
    if not _is_relative_to(target_path, GENERATED_APPS_ROOT):
        errors.append("target_folder must be inside D:/APPS/IdeasForgeAI/generated-apps.")
    if target_path == GENERATED_APPS_ROOT:
        errors.append("target_folder must name a dedicated future Phase 13 sandbox folder, not generated-apps root.")

    lower_target = checked_target_folder.lower()
    if "ideasforgeai-preview-v1" in lower_target:
        errors.append("target_folder must not touch generated-apps/ideasforgeai-preview-v1.")
    if any(name.lower() in lower_target for name in PHASE_12_SANDBOX_NAMES):
        errors.append("target_folder must not use Phase 12 sandbox folders.")
    if "IdeasForgeAI" in lower_target:
        errors.append("target_folder must not contain IdeasForgeAI paths.")
    if "_phase13" not in target_path.name.lower():
        warnings.append("target_folder is inside generated-apps but does not use a Phase 13 sandbox-style name.")
    return checked_target_folder


def _validate_allowed_files(payload: Dict[str, Any], errors: List[str]) -> List[str]:
    allowed_files = payload.get("allowed_files")
    if not isinstance(allowed_files, list) or not allowed_files:
        errors.append("allowed_files must be a non-empty list.")
        return []

    checked_allowed = []
    for file_name in allowed_files:
        normalized = _normalized_relative(file_name)
        checked_allowed.append(normalized)
        if normalized not in ALLOWED_FUTURE_FILES:
            errors.append(f"allowed_files contains unapproved file: {normalized}")
        if "/" in normalized or _contains_path_traversal(normalized):
            errors.append(f"allowed_files must contain file names only: {normalized}")
    if checked_allowed != ALLOWED_FUTURE_FILES:
        errors.append("allowed_files must exactly match the Phase 13B approved file list.")
    return checked_allowed


def _validate_blocked_files(payload: Dict[str, Any], errors: List[str], warnings: List[str]) -> None:
    blocked_files = payload.get("blocked_files")
    if not isinstance(blocked_files, list) or not blocked_files:
        errors.append("blocked_files must be a non-empty list.")
        return
    blocked_text = "\n".join(str(item).lower() for item in blocked_files)
    for marker in BLOCKED_FILES_AND_LOCATIONS:
        if marker.lower() not in blocked_text:
            warnings.append(f"blocked_files should include: {marker}")


def _validate_write_order(payload: Dict[str, Any], errors: List[str]) -> List[str]:
    write_order = [_normalized_relative(item) for item in payload.get("write_order", [])]
    if write_order != WRITE_ORDER:
        errors.append("write_order must match: manifest.json, index.html, styles.css, app.js, README.md, validation-report.md.")
    return write_order


def _validate_file_entries(payload: Dict[str, Any], checked_allowed_files: List[str], errors: List[str]) -> List[Dict[str, Any]]:
    file_entries = payload.get("file_entries")
    checked_entries: List[Dict[str, Any]] = []
    source_phase = str(payload.get("source_phase") or "").strip()
    required_fields = list(FILE_ENTRY_SCHEMA.keys())

    if not isinstance(file_entries, list) or not file_entries:
        errors.append("file_entries must be a non-empty list.")
        return checked_entries
    if len(file_entries) != len(ALLOWED_FUTURE_FILES):
        errors.append("file_entries must include exactly one entry for each allowed file.")

    seen_files = []
    for index, entry in enumerate(file_entries):
        if not isinstance(entry, dict):
            errors.append(f"file_entries[{index}] must be an object.")
            continue
        missing_fields = [field for field in required_fields if field not in entry]
        if missing_fields:
            errors.append(f"file_entries[{index}] is missing fields: {', '.join(missing_fields)}")

        file_name = _normalized_relative(entry.get("file_name"))
        relative_path = _normalized_relative(entry.get("relative_path"))
        seen_files.append(file_name)
        checked_entries.append(
            {
                "file_name": file_name,
                "relative_path": relative_path,
                "write_status": entry.get("write_status"),
                "dependency_order": entry.get("dependency_order"),
                "required": entry.get("required"),
                "approval_required": entry.get("approval_required"),
                "validation_required": entry.get("validation_required"),
                "backup_required": entry.get("backup_required"),
                "rollback_required": entry.get("rollback_required"),
                "allowed_to_overwrite": entry.get("allowed_to_overwrite"),
            }
        )

        if file_name not in ALLOWED_FUTURE_FILES:
            errors.append(f"file_entries[{index}].file_name is not allowed: {file_name}")
        if file_name not in checked_allowed_files:
            errors.append(f"file_entries[{index}].file_name is missing from allowed_files: {file_name}")
        if relative_path != file_name:
            errors.append(f"file_entries[{index}].relative_path must equal approved file name: {file_name}")
        blocked_reason = _path_is_blocked(relative_path, source_phase)
        if blocked_reason:
            errors.append(f"file_entries[{index}].relative_path blocked: {blocked_reason}")
        if entry.get("required") is not True:
            errors.append(f"file_entries[{index}].required must be true.")
        if entry.get("approval_required") is not True:
            errors.append(f"file_entries[{index}].approval_required must be true.")
        if entry.get("validation_required") is not True:
            errors.append(f"file_entries[{index}].validation_required must be true.")
        if entry.get("backup_required") is not True:
            errors.append(f"file_entries[{index}].backup_required must be true.")
        if entry.get("rollback_required") is not True:
            errors.append(f"file_entries[{index}].rollback_required must be true.")
        if entry.get("allowed_to_overwrite") is not False:
            errors.append(f"file_entries[{index}].allowed_to_overwrite must be false.")
        if entry.get("write_status") not in {"planned", "dry_run_only", "blocked", "approved_later"}:
            errors.append(f"file_entries[{index}].write_status is invalid.")
        expected_dependency_order = WRITE_ORDER.index(file_name) + 1 if file_name in WRITE_ORDER else None
        if expected_dependency_order is not None and entry.get("dependency_order") != expected_dependency_order:
            errors.append(f"file_entries[{index}].dependency_order does not match required write order.")
        for blocked_field in BLOCKED_PAYLOAD_FIELDS:
            if blocked_field in entry:
                errors.append(f"file_entries[{index}] contains blocked field: {blocked_field}")

    if seen_files != WRITE_ORDER:
        errors.append("file_entries must follow the required write order from the Phase 13B contract.")
    return checked_entries


def _validate_flags(payload: Dict[str, Any], errors: List[str], warnings: List[str]) -> None:
    required_true = ["approval_required", "approved_by_human", "backup_required", "rollback_required"]
    required_false = [
        "deployment_allowed",
        "provider_calls_allowed",
        "database_writes_allowed",
        "secrets_allowed",
        "supabase_allowed",
        "auth_allowed",
    ]
    for field in required_true:
        if payload.get(field) is not True:
            errors.append(f"{field} must be true.")
    for field in required_false:
        if payload.get(field) is not False:
            errors.append(f"{field} must be false.")
    if payload.get("dry_run_validation_passed") is True:
        warnings.append("dry_run_validation_passed is already true in a dry-run request; no write unlock is granted.")
    elif payload.get("dry_run_validation_passed") is not False:
        errors.append("dry_run_validation_passed must be false for the pre-write dry-run request.")


def build_phase13c_multi_file_dry_run_validator_response(payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Validate a planned Phase 13 multi-file generation request without side effects."""

    payload = deepcopy(payload) if payload else deepcopy(DEFAULT_PLANNED_PAYLOAD)
    validation_errors: List[str] = []
    validation_warnings: List[str] = []

    for blocked_field in sorted(BLOCKED_PAYLOAD_FIELDS):
        if blocked_field in payload:
            validation_errors.append(f"Payload contains blocked field: {blocked_field}")

    _validate_project_and_generation(payload, validation_errors)
    checked_target_folder = _validate_target_folder(payload, validation_errors, validation_warnings)
    checked_allowed_files = _validate_allowed_files(payload, validation_errors)
    _validate_blocked_files(payload, validation_errors, validation_warnings)
    checked_write_order = _validate_write_order(payload, validation_errors)
    checked_file_entries = _validate_file_entries(payload, checked_allowed_files, validation_errors)
    _validate_flags(payload, validation_errors, validation_warnings)

    validation_passed = not validation_errors

    return {
        "status": "success" if validation_passed else "blocked",
        "phase": "Phase 13C - Multi-File Dry-Run Validator",
        "dry_run_only": True,
        "multi_file_validation_only": True,
        "file_write_allowed": False,
        "folder_creation_allowed": False,
        "generation_allowed": False,
        "backend_generation_unlocked": False,
        "deployment_unlocked": False,
        "provider_calls_allowed": False,
        "database_writes_allowed": False,
        "secrets_allowed": False,
        "validation_passed": validation_passed,
        "validation_errors": validation_errors,
        "validation_warnings": validation_warnings,
        "checked_target_folder": checked_target_folder,
        "checked_allowed_files": checked_allowed_files,
        "checked_file_entries": checked_file_entries,
        "checked_write_order": checked_write_order,
        "safety_flags": deepcopy(SAFETY_FLAGS),
        "next_required_approval": "Phase 13D approval is required before any folder creation or file write.",
        "next_required_phase": "Phase 13D - Controlled Multi-File Sandbox Writer",
        "side_effects": {
            "files_written": False,
            "folders_created": False,
            "generated_app_created": False,
            "html_css_js_generated": False,
            "providers_called": False,
            "deployment_started": False,
            "database_writes_made": False,
            "secrets_used": False,
        },
    }
