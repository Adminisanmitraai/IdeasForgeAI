"""Phase 12E rollback + backup system for the Phase 12D proof file only.

Backup/rollback sandbox only.
No real frontend generation.
No HTML/CSS/JS generation.
No provider calls.
No deployment.
"""

from datetime import datetime, timezone
from pathlib import Path, PureWindowsPath
from typing import Any, Dict, List, Optional, Tuple


IDEASFORGEAI_ROOT = PureWindowsPath("D:/APPS/IdeasForgeAI")
APPROVED_SOURCE_FILE = PureWindowsPath("D:/APPS/IdeasForgeAI/generated-apps/_phase12d_write_sandbox/phase12d-write-proof.txt")
APPROVED_BACKUP_FOLDER = PureWindowsPath("D:/APPS/IdeasForgeAI/generated-apps/_phase12e_backup_sandbox")
LOCAL_SOURCE_FILE = Path("D:/APPS/IdeasForgeAI/generated-apps/_phase12d_write_sandbox/phase12d-write-proof.txt")
LOCAL_BACKUP_FOLDER = Path("D:/APPS/IdeasForgeAI/generated-apps/_phase12e_backup_sandbox")
BACKUP_FILE_PREFIX = "phase12d-write-proof."
BACKUP_FILE_SUFFIX = ".backup.txt"

DEFAULT_APPROVAL_PAYLOAD = {
    "approval_required": True,
    "human_approval_id": "phase12e-approved-rollback-backup-sandbox",
    "source_phase": "Phase 12E",
}

LOCKED_FLAGS = {
    "real_generation_unlocked": False,
    "backend_generation_unlocked": False,
    "deployment_unlocked": False,
    "provider_calls_allowed": False,
    "database_writes_allowed": False,
    "secrets_allowed": False,
    "html_css_js_generation_allowed": False,
    "general_generated_app_writes_unlocked": False,
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
    "deploy_request",
    "provider_prompt",
    "secret_value",
    "database_write",
    "supabase_config",
    "auth_config",
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

SECRET_FILE_NAMES = {
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",
    ".env.supabase",
    "secrets.json",
}


def _normalize_windows_path(path_value: Any) -> Tuple[Optional[PureWindowsPath], str]:
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


def _blocked_path_reason(path_value: str) -> Optional[str]:
    normalized = path_value.strip().replace("\\", "/").lstrip("/")
    lower_path = normalized.lower()
    first_part = lower_path.split("/", 1)[0]
    file_name = lower_path.rsplit("/", 1)[-1]

    if _contains_path_traversal(normalized):
        return "Path traversal is blocked."
    if "ideasforgeai-preview-v1" in lower_path:
        return "generated-apps/ideasforgeai-preview-v1 is blocked."
    if lower_path.startswith("backend/") or first_part == "backend":
        return "backend paths are blocked."
    if lower_path.startswith("frontend/") or first_part == "frontend":
        return "frontend paths are blocked."
    if lower_path.startswith("docs/") or first_part == "docs":
        return "docs paths are blocked."
    if first_part in {".", ".git", ".venv", "__pycache__"}:
        return "repository metadata, virtualenv, and cache paths are blocked."
    if file_name in DEPLOYMENT_CONFIG_FILES:
        return "deployment config files are blocked."
    if file_name in SECRET_FILE_NAMES or file_name.startswith(".env"):
        return "secrets/env files are blocked."
    if "IdeasForgeAI" in lower_path:
        return "IdeasForgeAI paths are blocked."
    return None


def _validate_approval_payload(payload: Dict[str, Any]) -> List[str]:
    errors: List[str] = []

    for blocked_field in sorted(BLOCKED_PAYLOAD_FIELDS):
        if blocked_field in payload:
            errors.append(f"Payload contains blocked field: {blocked_field}")

    if payload.get("approval_required") is not True:
        errors.append("approval_required must be true.")
    if not str(payload.get("human_approval_id") or "").strip():
        errors.append("human_approval_id is required.")
    if payload.get("source_phase") != "Phase 12E":
        errors.append("source_phase must be Phase 12E.")

    source_path, checked_source = _normalize_windows_path(payload.get("source_file") or APPROVED_SOURCE_FILE)
    backup_folder, checked_backup_folder = _normalize_windows_path(payload.get("backup_folder") or APPROVED_BACKUP_FOLDER)

    for label, value in {"source_file": checked_source, "backup_folder": checked_backup_folder}.items():
        reason = _blocked_path_reason(value)
        if reason:
            errors.append(f"{label} rejected: {reason}")

    if source_path is None or source_path != APPROVED_SOURCE_FILE:
        errors.append("source_file must be the approved Phase 12D proof file only.")
    if backup_folder is None or backup_folder != APPROVED_BACKUP_FOLDER:
        errors.append("backup_folder must be D:/APPS/IdeasForgeAI/generated-apps/_phase12e_backup_sandbox/.")
    if source_path is not None and not _is_relative_to(source_path, IDEASFORGEAI_ROOT):
        errors.append("source_file must stay inside D:/APPS/IdeasForgeAI.")
    if backup_folder is not None and not _is_relative_to(backup_folder, IDEASFORGEAI_ROOT):
        errors.append("backup_folder must stay inside D:/APPS/IdeasForgeAI.")

    return errors


def _base_response(status: str, validation_errors: List[str]) -> Dict[str, Any]:
    return {
        "status": status,
        "phase": "Phase 12E - Rollback + Backup System",
        "sandbox_backup_rollback_only": True,
        "validation_errors": validation_errors,
        **LOCKED_FLAGS,
    }


def _latest_valid_backup() -> Optional[Path]:
    if not LOCAL_BACKUP_FOLDER.exists():
        return None
    candidates = [
        path
        for path in LOCAL_BACKUP_FOLDER.glob(f"{BACKUP_FILE_PREFIX}*{BACKUP_FILE_SUFFIX}")
        if path.is_file() and path.parent == LOCAL_BACKUP_FOLDER
    ]
    return sorted(candidates, key=lambda path: path.stat().st_mtime, reverse=True)[0] if candidates else None


def build_phase12e_backup_sandbox_file_response(payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create a timestamped backup of the approved Phase 12D proof file only."""

    payload = payload or {}
    validation_errors = _validate_approval_payload(payload)

    if not LOCAL_SOURCE_FILE.exists():
        validation_errors.append("Approved Phase 12D proof file does not exist.")

    if validation_errors:
        response = _base_response("blocked", validation_errors)
        response.update(
            {
                "backup_created": False,
                "backup_path": None,
                "source_file": str(APPROVED_SOURCE_FILE).replace("\\", "/"),
                "rollback_available": _latest_valid_backup() is not None,
            }
        )
        return response

    LOCAL_BACKUP_FOLDER.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    backup_path = LOCAL_BACKUP_FOLDER / f"{BACKUP_FILE_PREFIX}{timestamp}{BACKUP_FILE_SUFFIX}"
    backup_path.write_text(LOCAL_SOURCE_FILE.read_text(encoding="utf-8"), encoding="utf-8")

    response = _base_response("success", [])
    response.update(
        {
            "backup_created": True,
            "backup_path": str(backup_path).replace("\\", "/"),
            "source_file": str(APPROVED_SOURCE_FILE).replace("\\", "/"),
            "rollback_available": True,
            "backup_folder": str(APPROVED_BACKUP_FOLDER).replace("\\", "/"),
            "backup_scope": "Phase 12D proof file only",
        }
    )
    return response


def build_phase12e_rollback_sandbox_file_response(payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Restore the approved Phase 12D proof file from the latest valid backup only."""

    payload = payload or {}
    validation_errors = _validate_approval_payload(payload)
    latest_backup = _latest_valid_backup()

    if latest_backup is None:
        validation_errors.append("No valid Phase 12E backup is available for rollback.")

    if validation_errors:
        response = _base_response("blocked", validation_errors)
        response.update(
            {
                "rollback_completed": False,
                "restored_file": None,
                "backup_path": str(latest_backup).replace("\\", "/") if latest_backup else None,
                "source_file": str(APPROVED_SOURCE_FILE).replace("\\", "/"),
                "rollback_available": latest_backup is not None,
            }
        )
        return response

    LOCAL_SOURCE_FILE.parent.mkdir(parents=True, exist_ok=True)
    LOCAL_SOURCE_FILE.write_text(latest_backup.read_text(encoding="utf-8"), encoding="utf-8")

    response = _base_response("success", [])
    response.update(
        {
            "rollback_completed": True,
            "restored_file": str(APPROVED_SOURCE_FILE).replace("\\", "/"),
            "backup_path": str(latest_backup).replace("\\", "/"),
            "source_file": str(APPROVED_SOURCE_FILE).replace("\\", "/"),
            "rollback_available": True,
            "rollback_scope": "Phase 12D proof file only",
        }
    )
    return response
