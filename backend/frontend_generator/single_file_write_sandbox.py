"""Phase 12D single-file write sandbox.

Approval-gated sandbox write only.
Exactly one approved proof file path is allowed.
No real frontend generation.
No HTML/CSS/JS generation.
No provider calls.
No deployment.
"""

from pathlib import Path, PureWindowsPath
from typing import Any, Dict, List, Optional, Tuple


IDEASFORGEAI_ROOT = PureWindowsPath("D:/APPS/IdeasForgeAI")
APPROVED_SANDBOX_FOLDER = PureWindowsPath("D:/APPS/IdeasForgeAI/generated-apps/_phase12d_write_sandbox")
APPROVED_FILE_NAME = "phase12d-write-proof.txt"
APPROVED_FILE_PATH = APPROVED_SANDBOX_FOLDER / APPROVED_FILE_NAME
LOCAL_APPROVED_FILE_PATH = Path("D:/APPS/IdeasForgeAI/generated-apps/_phase12d_write_sandbox/phase12d-write-proof.txt")

PROOF_FILE_CONTENT = """IdeasForgeAI Phase 12D single-file write sandbox proof.
This file was created by an approval-gated sandbox write.
This is not real generation.
This is not deployment.
Backend generation remains locked.
Deployment remains locked.
Provider calls remain locked.
Supabase/auth/database/secrets remain locked.
KisanMitraAI production was not touched.
"""

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


DEFAULT_APPROVED_PAYLOAD = {
    "approval_required": True,
    "human_approval_id": "phase12d-approved-single-file-write-sandbox",
    "dry_run_validation_passed": True,
    "target_folder": str(APPROVED_SANDBOX_FOLDER).replace("\\", "/"),
    "file_name": APPROVED_FILE_NAME,
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
    if lower_path.startswith("backend/") or first_part == "backend":
        return "backend paths are blocked."
    if lower_path.startswith("frontend/") or first_part == "frontend":
        return "frontend paths are blocked."
    if lower_path.startswith("docs/") or first_part == "docs":
        return "docs paths are blocked."
    if first_part in {".", ".git", ".venv", "__pycache__"}:
        return "repository metadata, virtualenv, and cache paths are blocked."
    if file_name in DEPLOYMENT_CONFIG_FILES:
        return "deployment config writes are blocked."
    if file_name in SECRET_FILE_NAMES or file_name.startswith(".env"):
        return "secrets/env file writes are blocked."
    if "kisanmitra" in lower_path:
        return "KisanMitraAI paths are blocked."
    return None


def _validate_payload(payload: Dict[str, Any]) -> List[str]:
    errors: List[str] = []

    for blocked_field in sorted(BLOCKED_PAYLOAD_FIELDS):
        if blocked_field in payload:
            errors.append(f"Payload contains blocked field: {blocked_field}")

    if payload.get("approval_required") is not True:
        errors.append("approval_required must be true.")
    if not str(payload.get("human_approval_id") or "").strip():
        errors.append("human_approval_id is required.")
    if payload.get("dry_run_validation_passed") is not True:
        errors.append("dry_run_validation_passed must be true.")

    requested_folder, checked_folder = _normalize_windows_path(payload.get("target_folder") or APPROVED_SANDBOX_FOLDER)
    requested_file_name = str(payload.get("file_name") or APPROVED_FILE_NAME).strip()
    requested_path, checked_path = _normalize_windows_path(payload.get("file_path") or (APPROVED_SANDBOX_FOLDER / requested_file_name))

    for label, value in {
        "target_folder": checked_folder,
        "file_name": requested_file_name,
        "file_path": checked_path,
    }.items():
        reason = _blocked_path_reason(value)
        if reason and not value.replace("\\", "/").endswith("generated-apps/_phase12d_write_sandbox/phase12d-write-proof.txt"):
            errors.append(f"{label} rejected: {reason}")

    if requested_folder is None or requested_folder != APPROVED_SANDBOX_FOLDER:
        errors.append("target_folder must be D:/APPS/IdeasForgeAI/generated-apps/_phase12d_write_sandbox/.")
    if requested_file_name != APPROVED_FILE_NAME:
        errors.append("file_name must be phase12d-write-proof.txt.")
    if requested_path is None or requested_path != APPROVED_FILE_PATH:
        errors.append("file_path must resolve to the approved Phase 12D proof file path.")
    if requested_path is not None and not _is_relative_to(requested_path, IDEASFORGEAI_ROOT):
        errors.append("file_path must stay inside D:/APPS/IdeasForgeAI.")
    if "ideasforgeai-preview-v1" in checked_path.lower() or "ideasforgeai-preview-v1" in checked_folder.lower():
        errors.append("generated-apps/ideasforgeai-preview-v1 must not be touched.")
    if "kisanmitra" in checked_path.lower() or "kisanmitra" in checked_folder.lower():
        errors.append("KisanMitraAI paths are blocked.")

    return errors


def build_single_file_write_sandbox_response(payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Write the approved Phase 12D proof file only when all gates pass."""

    payload = payload or {}
    validation_errors = _validate_payload(payload)
    file_already_existed = LOCAL_APPROVED_FILE_PATH.exists()
    file_written = False

    if not validation_errors:
        LOCAL_APPROVED_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
        existing_content = LOCAL_APPROVED_FILE_PATH.read_text(encoding="utf-8") if file_already_existed else None
        if existing_content != PROOF_FILE_CONTENT:
            LOCAL_APPROVED_FILE_PATH.write_text(PROOF_FILE_CONTENT, encoding="utf-8")
            file_written = True
        else:
            file_written = False

    status = "success" if not validation_errors else "blocked"

    return {
        "status": status,
        "phase": "Phase 12D - Single-File Write Sandbox",
        "sandbox_write_only": True,
        "file_write_allowed_for_this_file_only": not validation_errors,
        "written_file_path": str(APPROVED_FILE_PATH).replace("\\", "/") if not validation_errors else None,
        "proof_file_created": LOCAL_APPROVED_FILE_PATH.exists() if not validation_errors else False,
        "file_written_this_request": file_written,
        "file_already_existed_before_request": file_already_existed,
        "validation_errors": validation_errors,
        "generated_app_write_unlocked": False,
        "backend_generation_unlocked": False,
        "deployment_unlocked": False,
        "provider_calls_allowed": False,
        "database_writes_allowed": False,
        "secrets_allowed": False,
        "html_css_js_generation_allowed": False,
        "preview_folder_touched": False,
        "next_required_phase": "Phase 12E requires explicit approval and is not implemented.",
        "safety_flags": {
            "single_file_sandbox_write": True,
            "approved_folder_only": str(APPROVED_SANDBOX_FOLDER).replace("\\", "/"),
            "approved_file_only": APPROVED_FILE_NAME,
            "arbitrary_content_allowed": False,
            "real_generation_allowed": False,
            "generated_app_write_unlocked": False,
            "backend_generation_unlocked": False,
            "deployment_unlocked": False,
            "provider_calls_allowed": False,
            "database_writes_allowed": False,
            "secrets_allowed": False,
        },
    }