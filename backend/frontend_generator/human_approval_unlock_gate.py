"""Phase 12F human approval unlock gate.

Approval metadata only.
No real frontend generation.
No generated app file writes.
No folder creation.
No HTML/CSS/JS generation.
No provider calls.
No deployment.
"""

from pathlib import PureWindowsPath
from typing import Any, Dict, List, Optional


EXPECTED_PROJECT_NAME = "IdeasForgeAI"
EXPECTED_SOURCE_PHASE = "Phase 12F"
EXPECTED_TARGET_NEXT_PHASE = "Phase 12G"
EXPECTED_GENERATION_MODE = "controlled_single_generation_planning"
IDEASFORGEAI_ROOT = PureWindowsPath("D:/APPS/IdeasForgeAI")

DEFAULT_APPROVED_PAYLOAD = {
    "project_name": EXPECTED_PROJECT_NAME,
    "human_approval_id": "phase12f-human-approved-planning-gate",
    "approval_required": True,
    "approved_by_human": True,
    "dry_run_validation_passed": True,
    "backup_required": True,
    "rollback_required": True,
    "source_phase": EXPECTED_SOURCE_PHASE,
    "target_next_phase": EXPECTED_TARGET_NEXT_PHASE,
    "generation_mode": EXPECTED_GENERATION_MODE,
    "deployment_allowed": False,
    "provider_calls_allowed": False,
    "database_writes_allowed": False,
    "secrets_allowed": False,
    "supabase_allowed": False,
    "auth_allowed": False,
}

DEFAULT_REJECTED_PAYLOAD = {
    "project_name": EXPECTED_PROJECT_NAME,
    "approval_required": True,
    "approved_by_human": False,
    "dry_run_validation_passed": False,
    "backup_required": True,
    "rollback_required": True,
    "source_phase": EXPECTED_SOURCE_PHASE,
    "target_next_phase": EXPECTED_TARGET_NEXT_PHASE,
    "generation_mode": EXPECTED_GENERATION_MODE,
    "deployment_allowed": False,
    "provider_calls_allowed": False,
    "database_writes_allowed": False,
    "secrets_allowed": False,
    "supabase_allowed": False,
    "auth_allowed": False,
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

LOCKED_RETURN_FLAGS = {
    "real_generation_unlocked": False,
    "generated_app_write_unlocked": False,
    "backend_generation_unlocked": False,
    "deployment_unlocked": False,
    "provider_calls_allowed": False,
    "database_writes_allowed": False,
    "secrets_allowed": False,
}


def _path_text_values(payload: Dict[str, Any]) -> List[str]:
    path_like_keys = [
        "target_folder",
        "target_path",
        "file_path",
        "source_file",
        "backup_folder",
        "generated_app_path",
        "deployment_path",
        "IdeasForgeAI_path",
    ]
    return [str(payload.get(key) or "") for key in path_like_keys if payload.get(key)]


def _is_outside_ideasforgeai(path_text: str) -> bool:
    normalized = path_text.strip().replace("\\", "/")
    if not normalized:
        return False
    path = PureWindowsPath(normalized)
    if not path.is_absolute():
        return False
    try:
        path.relative_to(IDEASFORGEAI_ROOT)
        return False
    except ValueError:
        return True


def _validate_payload(payload: Dict[str, Any]) -> tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []

    for blocked_field in sorted(BLOCKED_PAYLOAD_FIELDS):
        if blocked_field in payload:
            errors.append(f"Payload contains blocked field: {blocked_field}")

    if payload.get("project_name") != EXPECTED_PROJECT_NAME:
        errors.append("project_name must equal IdeasForgeAI.")
    if not str(payload.get("human_approval_id") or "").strip():
        errors.append("human_approval_id is required.")
    if payload.get("approval_required") is not True:
        errors.append("approval_required must be true.")
    if payload.get("approved_by_human") is not True:
        errors.append("approved_by_human must be true.")
    if payload.get("dry_run_validation_passed") is not True:
        errors.append("dry_run_validation_passed must be true.")
    if payload.get("backup_required") is not True:
        errors.append("backup_required must be true.")
    if payload.get("rollback_required") is not True:
        errors.append("rollback_required must be true.")
    if payload.get("source_phase") != EXPECTED_SOURCE_PHASE:
        errors.append("source_phase must be Phase 12F.")
    if payload.get("target_next_phase") != EXPECTED_TARGET_NEXT_PHASE:
        errors.append("target_next_phase must be Phase 12G.")
    if payload.get("generation_mode") != EXPECTED_GENERATION_MODE:
        errors.append("generation_mode must be controlled_single_generation_planning.")

    if payload.get("deployment_allowed") is True:
        errors.append("deployment_allowed must not be true.")
    if payload.get("provider_calls_allowed") is True:
        errors.append("provider_calls_allowed must not be true.")
    if payload.get("database_writes_allowed") is True:
        errors.append("database_writes_allowed must not be true.")
    if payload.get("secrets_allowed") is True:
        errors.append("secrets_allowed must not be true.")
    if payload.get("supabase_allowed") is True or payload.get("supabase_unlocked") is True:
        errors.append("Supabase unlock is rejected.")
    if payload.get("auth_allowed") is True or payload.get("auth_unlocked") is True:
        errors.append("Auth unlock is rejected.")

    for value in _path_text_values(payload):
        lower_value = value.lower().replace("\\", "/")
        if "IdeasForgeAI" in lower_value:
            errors.append("IdeasForgeAI paths are rejected.")
        if _is_outside_ideasforgeai(value):
            errors.append("Paths outside D:/APPS/IdeasForgeAI are rejected.")
        if "ideasforgeai-preview-v1" in lower_value:
            warnings.append("generated-apps/ideasforgeai-preview-v1 remains untouched and is not part of this approval gate.")

    return errors, warnings


def build_human_approval_unlock_gate_response(payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Validate human approval metadata without unlocking generation."""

    payload = payload or {}
    validation_errors, validation_warnings = _validate_payload(payload)
    human_approval_validated = not validation_errors

    return {
        "status": "success" if human_approval_validated else "blocked",
        "phase": "Phase 12F - Human Approval Unlock Gate",
        "approval_gate_only": True,
        "human_approval_validated": human_approval_validated,
        "next_phase_allowed": human_approval_validated,
        "next_phase": EXPECTED_TARGET_NEXT_PHASE if human_approval_validated else None,
        **LOCKED_RETURN_FLAGS,
        "validation_errors": validation_errors,
        "validation_warnings": validation_warnings,
        "required_next_action": (
            "Phase 12G planning may be considered after explicit approval, but real generation remains locked."
            if human_approval_validated
            else "Resolve approval gate validation errors before Phase 12G planning can be considered."
        ),
        "safety_limits": {
            "metadata_only": True,
            "files_written": False,
            "folders_created": False,
            "html_css_js_generated": False,
            "providers_called": False,
            "deployment_started": False,
            "generation_directly_unlocked": False,
            "phase_12g_implemented": False,
        },
    }
