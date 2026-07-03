"""Phase 13F local preview runner integration.

Metadata-only preview runner for the existing Phase 13E sandbox output.
No file writes.
No folder creation.
No HTML/CSS/JS generation.
No provider calls.
No deployment.
No Supabase/auth/database/secrets.
"""

from copy import deepcopy
from pathlib import Path, PureWindowsPath
from typing import Any, Dict, List, Optional, Tuple


IDEASFORGEAI_ROOT = PureWindowsPath("D:/APPS/IdeasForgeAI")
GENERATED_APPS_ROOT = IDEASFORGEAI_ROOT / "generated-apps"
PREVIEW_TARGET_FOLDER = GENERATED_APPS_ROOT / "_phase13e_controlled_html_css_js_generation"
LOCAL_PREVIEW_TARGET_FOLDER = Path("D:/APPS/IdeasForgeAI/generated-apps/_phase13e_controlled_html_css_js_generation")
PREVIEW_TARGET_FOLDER_TEXT = "D:/APPS/IdeasForgeAI/generated-apps/_phase13e_controlled_html_css_js_generation"
PREVIEW_ENTRY_FILE = "index.html"
PREVIEW_ENTRY_PATH_TEXT = f"{PREVIEW_TARGET_FOLDER_TEXT}/{PREVIEW_ENTRY_FILE}"
ALLOWED_FILES = [
    "manifest.json",
    "index.html",
    "styles.css",
    "app.js",
    "README.md",
    "validation-report.md",
]

BLOCKED_FOLDERS_AND_FILES = {
    "backend",
    "frontend",
    "docs",
    "ideasforgeai-preview-v1",
    "_phase12d_write_sandbox",
    "_phase12e_backup_sandbox",
    "_phase12g_controlled_html_css_generation",
    "_phase13d_multi_file_write_sandbox",
    ".env",
    "render.yaml",
    "vercel.json",
    "netlify.toml",
    "dockerfile",
    "docker-compose.yml",
    "database",
    "auth",
    "supabase",
    "IdeasForgeAI",
}

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
    "human_approval_id": "phase13f-human-approved-local-preview-runner",
    "approved_by_human": True,
    "source_phase": "Phase 13F",
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


def _validate_payload(payload: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    if payload.get("project_name") != "IdeasForgeAI":
        errors.append("project_name must equal IdeasForgeAI.")
    if not str(payload.get("human_approval_id") or "").strip():
        errors.append("human_approval_id is required.")
    if payload.get("approved_by_human") is not True:
        errors.append("approved_by_human must be true.")
    if payload.get("source_phase") != "Phase 13F":
        errors.append("source_phase must equal Phase 13F.")

    requested_target = payload.get("preview_target_folder") or payload.get("target_folder")
    if requested_target:
        target_path, checked_target = _as_windows_path(requested_target)
        if _contains_path_traversal(requested_target):
            errors.append("preview target must not contain path traversal.")
        if target_path is None or checked_target != PREVIEW_TARGET_FOLDER_TEXT:
            errors.append("preview target must exactly match the Phase 13E sandbox folder.")
        elif not _is_relative_to(target_path, PREVIEW_TARGET_FOLDER):
            errors.append("preview target must stay inside the Phase 13E sandbox folder.")

    requested_entry = str(payload.get("preview_entry_file") or PREVIEW_ENTRY_FILE).strip().replace("\\", "/")
    if requested_entry != PREVIEW_ENTRY_FILE:
        errors.append("preview_entry_file must equal index.html.")
    if _contains_path_traversal(requested_entry):
        errors.append("preview_entry_file must not contain path traversal.")

    return errors


def _scan_preview_folder() -> Tuple[List[str], List[str], List[str]]:
    allowed_files_found: List[str] = []
    blocked_files_found: List[str] = []
    warnings: List[str] = []

    if not LOCAL_PREVIEW_TARGET_FOLDER.exists():
        warnings.append("Phase 13E preview target folder is missing.")
        return allowed_files_found, blocked_files_found, warnings

    for path in sorted(LOCAL_PREVIEW_TARGET_FOLDER.iterdir(), key=lambda item: item.name.lower()):
        name = path.name
        lower_name = name.lower()
        if path.is_dir():
            blocked_files_found.append(f"{name}/")
            continue
        if name in ALLOWED_FILES:
            allowed_files_found.append(name)
        else:
            blocked_files_found.append(name)
        if any(marker in lower_name for marker in BLOCKED_FOLDERS_AND_FILES):
            blocked_files_found.append(name)

    missing = [file_name for file_name in ALLOWED_FILES if file_name not in allowed_files_found]
    if missing:
        warnings.append(f"Missing expected Phase 13E files: {', '.join(missing)}")
    if PREVIEW_ENTRY_FILE not in allowed_files_found:
        warnings.append("Preview entry file index.html is missing.")

    return allowed_files_found, sorted(set(blocked_files_found)), warnings


def _build_response(payload: Optional[Dict[str, Any]] = None, require_approval: bool = True) -> Dict[str, Any]:
    payload = deepcopy(payload) if payload else deepcopy(DEFAULT_APPROVED_PAYLOAD)
    validation_errors = _validate_payload(payload) if require_approval else []
    allowed_files_found, blocked_files_found, validation_warnings = _scan_preview_folder()

    if blocked_files_found:
        validation_errors.append("Preview target contains blocked files or folders.")

    status = "success" if not validation_errors else "blocked"
    return {
        "status": status,
        "phase": "Phase 13F - Local Preview Runner Integration",
        "preview_runner_only": True,
        "preview_target_folder": PREVIEW_TARGET_FOLDER_TEXT,
        "preview_entry_file": PREVIEW_ENTRY_FILE,
        "preview_url_or_path": PREVIEW_ENTRY_PATH_TEXT,
        "allowed_files_found": allowed_files_found,
        "blocked_files_found": blocked_files_found,
        "validation_errors": validation_errors,
        "validation_warnings": validation_warnings,
        **deepcopy(LOCKED_FLAGS),
        "next_required_phase": "Phase 13G",
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


def build_phase13f_local_preview_runner_status_response() -> Dict[str, Any]:
    """Return metadata for the Phase 13E local preview target without side effects."""

    return _build_response(DEFAULT_APPROVED_PAYLOAD, require_approval=False)


def build_phase13f_local_preview_runner_response(payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Validate an approved local preview request and return metadata only."""

    return _build_response(payload, require_approval=True)
