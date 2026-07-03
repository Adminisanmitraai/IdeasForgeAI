"""Phase 12C real generation dry-run validator.

Validation metadata only.
No folder creation.
No file writes.
No generated app creation.
No HTML/CSS/JS generation.
No provider calls.
No deployment.
"""

from copy import deepcopy
from pathlib import PureWindowsPath
import re
from typing import Any, Dict, List, Optional, Tuple

from backend.frontend_generator.generation_file_contract_schema import (
    ALLOWED_FUTURE_FILES,
    BLOCKED_FILES_AND_LOCATIONS,
    FILE_ENTRY_SCHEMA,
)


IDEASFORGEAI_ROOT = PureWindowsPath("D:/APPS/IdeasForgeAI")
GENERATED_APPS_ROOT = IDEASFORGEAI_ROOT / "generated-apps"
GENERATION_ID_PATTERN = re.compile(r"^phase12c-[a-z0-9][a-z0-9-]{2,80}$")
PROJECT_NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 ._-]{1,80}$")
DOCUMENTATION_PHASES = {"Phase 12C", "phase_12c", "documentation", "docs"}

ALLOWED_FILES = list(ALLOWED_FUTURE_FILES)
REQUIRED_FILE_ENTRY_FIELDS = list(FILE_ENTRY_SCHEMA.keys())
REQUIRED_BLOCKED_MARKERS = [
    "backend/",
    "frontend/pages/",
    "frontend/shared/",
    "docs/ except documentation phases",
    "root production files",
    "deployment config",
    "secrets/env files",
    "IdeasForgeAI folders",
    "any folder outside D:/APPS/IdeasForgeAI",
]
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
BLOCKED_PAYLOAD_FIELDS = {
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
    "real_generation_dry_run_validator_created": True,
    "dry_run_only": True,
    "file_write_allowed": False,
    "folder_creation_allowed": False,
    "generation_allowed": False,
    "generated_app_write_allowed": False,
    "html_generation_allowed": False,
    "css_generation_allowed": False,
    "js_generation_allowed": False,
    "backend_generation_allowed": False,
    "deployment_allowed": False,
    "provider_calls_allowed": False,
    "database_writes_allowed": False,
    "supabase_allowed": False,
    "auth_allowed": False,
    "secrets_allowed": False,
    "approval_required": True,
    "backup_required": True,
    "rollback_required": True,
}

DEFAULT_PLANNED_PAYLOAD = {
    "project_name": "IdeasForgeAI",
    "generation_id": "phase12c-dry-run-safe-sample",
    "target_folder": "D:/APPS/IdeasForgeAI/generated-apps/ideasforgeai-controlled-generation-v1",
    "source_phase": "Phase 12C",
    "allowed_files": ALLOWED_FILES,
    "blocked_files": BLOCKED_FILES_AND_LOCATIONS,
    "file_entries": [
        {
            **deepcopy(FILE_ENTRY_SCHEMA),
            "file_name": file_name,
            "relative_path": file_name,
            "file_type": file_name.rsplit(".", 1)[-1],
            "purpose": f"Future approved {file_name} output placeholder.",
            "write_status": "dry_run_only",
        }
        for file_name in ALLOWED_FILES
    ],
    "approval_required": True,
    "backup_required": True,
    "rollback_required": True,
    "deployment_allowed": False,
    "provider_calls_allowed": False,
    "database_writes_allowed": False,
    "secrets_allowed": False,
}


def _as_windows_path(path_value: Any) -> Tuple[Optional[PureWindowsPath], str]:
    raw_path = str(path_value or "").strip().replace("\\", "/")
    if not raw_path:
        return None, ""
    if raw_path.startswith("/mnt/"):
        return None, raw_path
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


def _validate_project_name(payload: Dict[str, Any], errors: List[str]) -> None:
    project_name = str(payload.get("project_name") or "").strip()
    if not project_name:
        errors.append("project_name is required.")
        return
    if "IdeasForgeAI" in project_name.lower():
        errors.append("project_name must not target IdeasForgeAI or IdeasForgeAI production.")
    if not PROJECT_NAME_PATTERN.match(project_name):
        errors.append("project_name has an invalid format.")


def _validate_generation_id(payload: Dict[str, Any], errors: List[str]) -> None:
    generation_id = str(payload.get("generation_id") or "").strip()
    if not GENERATION_ID_PATTERN.match(generation_id):
        errors.append("generation_id must match phase12c-[a-z0-9-] and be 12-90 characters.")


def _validate_target_folder(payload: Dict[str, Any], errors: List[str], warnings: List[str]) -> str:
    target_path, checked_target_folder = _as_windows_path(payload.get("target_folder"))
    raw_target = str(payload.get("target_folder") or "").strip()

    if not raw_target:
        errors.append("target_folder is required.")
        return ""
    if _contains_path_traversal(raw_target):
        errors.append("target_folder must not contain path traversal.")
    if "IdeasForgeAI" in raw_target.lower():
        errors.append("target_folder must not contain IdeasForgeAI paths.")
    if target_path is None:
        errors.append("target_folder could not be normalized as a Windows path.")
        return checked_target_folder
    if not _is_relative_to(target_path, IDEASFORGEAI_ROOT):
        errors.append("target_folder must stay inside D:/APPS/IdeasForgeAI.")
    if not _is_relative_to(target_path, GENERATED_APPS_ROOT):
        errors.append("target_folder must be inside D:/APPS/IdeasForgeAI/generated-apps.")
    if target_path == GENERATED_APPS_ROOT:
        errors.append("target_folder must name a dedicated generated app sandbox folder, not generated-apps root.")
    normalized_lower = checked_target_folder.lower()
    if normalized_lower.endswith("/ideasforgeai-preview-v1") or "/ideasforgeai-preview-v1/" in normalized_lower:
        errors.append("target_folder must not reuse generated-apps/ideasforgeai-preview-v1.")
    if "controlled-generation" not in target_path.name.lower():
        warnings.append("target_folder is inside generated-apps but does not use a controlled-generation name.")
    return checked_target_folder


def _path_is_blocked(relative_path: str, source_phase: str) -> Optional[str]:
    lower_path = relative_path.lower()
    first_part = lower_path.split("/", 1)[0]
    file_name = lower_path.rsplit("/", 1)[-1]

    if lower_path.startswith("backend/") or first_part == "backend":
        return "backend paths are blocked."
    if lower_path.startswith("frontend/pages/"):
        return "frontend/pages paths are blocked."
    if lower_path.startswith("frontend/shared/"):
        return "frontend/shared paths are blocked."
    if lower_path.startswith("docs/") and source_phase not in DOCUMENTATION_PHASES:
        return "docs writes are blocked unless this is a documentation phase."
    if first_part in {".", ".git", ".venv", "__pycache__"}:
        return "repository metadata, virtualenv, and cache paths are blocked."
    if relative_path not in ALLOWED_FILES and (relative_path in ROOT_PRODUCTION_FILES or first_part in ROOT_PRODUCTION_FILES):
        return "root production files are blocked."
    if file_name in DEPLOYMENT_CONFIG_FILES:
        return "deployment config files are blocked."
    if file_name in SECRET_FILE_NAMES or file_name.startswith(".env"):
        return "secrets/env files are blocked."
    if "IdeasForgeAI" in lower_path:
        return "IdeasForgeAI paths are blocked."
    return None


def _validate_allowed_files(payload: Dict[str, Any], errors: List[str]) -> List[str]:
    allowed_files = payload.get("allowed_files")
    if not isinstance(allowed_files, list) or not allowed_files:
        errors.append("allowed_files must be a non-empty list.")
        return []

    normalized_allowed = []
    for file_name in allowed_files:
        normalized = _normalized_relative(file_name)
        normalized_allowed.append(normalized)
        if normalized not in ALLOWED_FILES:
            errors.append(f"allowed_files contains unapproved file: {normalized}")
        if "/" in normalized or _contains_path_traversal(normalized):
            errors.append(f"allowed_files must contain file names only: {normalized}")
    return normalized_allowed


def _validate_blocked_files(payload: Dict[str, Any], errors: List[str], warnings: List[str]) -> None:
    blocked_files = payload.get("blocked_files")
    if not isinstance(blocked_files, list) or not blocked_files:
        errors.append("blocked_files must be a non-empty list.")
        return
    blocked_text = "\n".join(str(item) for item in blocked_files).lower()
    for marker in REQUIRED_BLOCKED_MARKERS:
        if marker.lower() not in blocked_text:
            warnings.append(f"blocked_files should include: {marker}")


def _validate_file_entries(payload: Dict[str, Any], allowed_files: List[str], errors: List[str]) -> List[Dict[str, Any]]:
    file_entries = payload.get("file_entries")
    checked_entries: List[Dict[str, Any]] = []
    source_phase = str(payload.get("source_phase") or "").strip()

    if not isinstance(file_entries, list) or not file_entries:
        errors.append("file_entries must be a non-empty list.")
        return checked_entries

    for index, entry in enumerate(file_entries):
        if not isinstance(entry, dict):
            errors.append(f"file_entries[{index}] must be an object.")
            continue

        missing_fields = [field for field in REQUIRED_FILE_ENTRY_FIELDS if field not in entry]
        if missing_fields:
            errors.append(f"file_entries[{index}] is missing fields: {', '.join(missing_fields)}")

        file_name = _normalized_relative(entry.get("file_name"))
        relative_path = _normalized_relative(entry.get("relative_path"))
        checked_entries.append(
            {
                "file_name": file_name,
                "relative_path": relative_path,
                "write_status": entry.get("write_status"),
                "approval_required": entry.get("approval_required"),
                "validation_required": entry.get("validation_required"),
                "rollback_required": entry.get("rollback_required"),
                "allowed_to_overwrite": entry.get("allowed_to_overwrite"),
            }
        )

        if file_name not in ALLOWED_FILES:
            errors.append(f"file_entries[{index}].file_name is not allowed: {file_name}")
        if file_name not in allowed_files:
            errors.append(f"file_entries[{index}].file_name is missing from allowed_files: {file_name}")
        if relative_path != file_name:
            errors.append(f"file_entries[{index}].relative_path must equal approved file name: {file_name}")
        if _contains_path_traversal(relative_path):
            errors.append(f"file_entries[{index}].relative_path must not contain path traversal.")
        blocked_reason = _path_is_blocked(relative_path, source_phase)
        if blocked_reason:
            errors.append(f"file_entries[{index}].relative_path blocked: {blocked_reason}")
        if entry.get("approval_required") is not True:
            errors.append(f"file_entries[{index}].approval_required must be true.")
        if entry.get("validation_required") is not True:
            errors.append(f"file_entries[{index}].validation_required must be true.")
        if entry.get("rollback_required") is not True:
            errors.append(f"file_entries[{index}].rollback_required must be true.")
        if entry.get("allowed_to_overwrite") is not False:
            errors.append(f"file_entries[{index}].allowed_to_overwrite must be false.")
        if entry.get("write_status") not in {"planned", "dry_run_only", "blocked", "approved_later"}:
            errors.append(f"file_entries[{index}].write_status is invalid.")
        for blocked_field in BLOCKED_PAYLOAD_FIELDS:
            if blocked_field in entry:
                errors.append(f"file_entries[{index}] contains blocked field: {blocked_field}")

    return checked_entries


def _validate_required_flags(payload: Dict[str, Any], errors: List[str]) -> None:
    required_true = ["approval_required", "backup_required", "rollback_required"]
    required_false = ["deployment_allowed", "provider_calls_allowed", "database_writes_allowed", "secrets_allowed"]

    for field in required_true:
        if payload.get(field) is not True:
            errors.append(f"{field} must be true.")
    for field in required_false:
        if payload.get(field) is not False:
            errors.append(f"{field} must be false.")

    nested_flags = payload.get("safety_flags")
    if isinstance(nested_flags, dict):
        for field in required_true:
            if field in nested_flags and nested_flags.get(field) is not True:
                errors.append(f"safety_flags.{field} must be true.")
        for field in required_false:
            if field in nested_flags and nested_flags.get(field) is not False:
                errors.append(f"safety_flags.{field} must be false.")
        for field in ["file_write_allowed", "folder_creation_allowed", "generation_allowed"]:
            if field in nested_flags and nested_flags.get(field) is not False:
                errors.append(f"safety_flags.{field} must be false.")


def build_real_generation_dry_run_validator_response(payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Validate a planned future generation request without side effects."""

    payload = deepcopy(payload) if payload else deepcopy(DEFAULT_PLANNED_PAYLOAD)
    validation_errors: List[str] = []
    validation_warnings: List[str] = []

    for blocked_field in sorted(BLOCKED_PAYLOAD_FIELDS):
        if blocked_field in payload:
            validation_errors.append(f"Payload contains blocked field: {blocked_field}")

    _validate_project_name(payload, validation_errors)
    _validate_generation_id(payload, validation_errors)
    checked_target_folder = _validate_target_folder(payload, validation_errors, validation_warnings)
    allowed_files = _validate_allowed_files(payload, validation_errors)
    _validate_blocked_files(payload, validation_errors, validation_warnings)
    checked_file_entries = _validate_file_entries(payload, allowed_files, validation_errors)
    _validate_required_flags(payload, validation_errors)

    validation_passed = not validation_errors

    return {
        "status": "success" if validation_passed else "blocked",
        "phase": "Phase 12C - Real Generation Dry-Run Validator",
        "mode": "dry_run_validation_only",
        "dry_run_only": True,
        "file_write_allowed": False,
        "folder_creation_allowed": False,
        "generation_allowed": False,
        "validation_passed": validation_passed,
        "validation_errors": validation_errors,
        "validation_warnings": validation_warnings,
        "checked_target_folder": checked_target_folder,
        "checked_file_entries": checked_file_entries,
        "safety_flags": deepcopy(SAFETY_FLAGS),
        "next_required_approval": "Phase 12D approval is required before any sandbox file write or folder creation.",
        "allowed_files_checked": ALLOWED_FILES,
        "blocked_files_checked": BLOCKED_FILES_AND_LOCATIONS,
        "side_effects": {
            "files_written": False,
            "folders_created": False,
            "html_css_js_generated": False,
            "provider_calls_made": False,
            "deployment_started": False,
            "database_writes_made": False,
            "secrets_used": False,
        },
        "next_phase_handoff": {
            "current_phase": "Phase 12C - Real Generation Dry-Run Validator",
            "next_phase": "Phase 12D - Single-File Write Sandbox",
            "phase_12d_implemented": False,
            "handoff_status": "approval_gated",
            "generated_app_writes_remain_locked": True,
            "backend_generation_remains_locked": True,
            "deployment_remains_locked": True,
        },
    }


