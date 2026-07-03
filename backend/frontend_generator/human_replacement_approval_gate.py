from pathlib import Path
from typing import Any
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


def _locked_flags() -> dict[str, Any]:
    return {
        "human_replacement_approval_gate_only": True,
        "human_replacement_approval_validated": False,
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


def validate_phase21c_human_replacement_approval_gate(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = payload or {}

    errors: list[str] = []
    warnings: list[str] = []

    if payload.get("project_name") != "IdeasForgeAI":
        errors.append("project_name must equal IdeasForgeAI")

    if payload.get("source_phase") != "Phase 21C":
        errors.append("source_phase must equal Phase 21C")

    human_approval_id = str(payload.get("human_approval_id", ""))
    if not _approval_id_valid(human_approval_id):
        errors.append("human_approval_id must match HUMAN-REPLACEMENT-APPROVED-21C-* format")

    if payload.get("approved_by_human") is not True:
        errors.append("approved_by_human must be true")

    if payload.get("phase20h_frozen") is not True:
        errors.append("phase20h_frozen must be true")

    if int(payload.get("phase20g_validation_score", 0)) != 100:
        errors.append("phase20g_validation_score must be 100")

    if payload.get("phase20f_preview_route_working") is not True:
        errors.append("phase20f_preview_route_working must be true")

    if payload.get("phase21a_frozen") is not True:
        errors.append("phase21a_frozen must be true")

    if payload.get("phase21b_frozen") is not True:
        errors.append("phase21b_frozen must be true")

    source_folder = str(payload.get("source_folder", "")).replace("\\", "/")
    approved_source = str(APPROVED_REPLACEMENT_SOURCE).replace("\\", "/")
    if source_folder != approved_source:
        errors.append("source_folder must equal approved Phase 20 polished source folder")

    target_folder = str(payload.get("target_folder", "")).replace("\\", "/")
    protected_target = str(PROTECTED_REPLACEMENT_TARGET).replace("\\", "/")
    if target_folder != protected_target:
        errors.append("target_folder must equal protected main preview target folder")

    if payload.get("rollback_required") is not True:
        errors.append("rollback_required must be true")

    if payload.get("replacement_dry_run_required") is not True:
        errors.append("replacement_dry_run_required must be true")

    if payload.get("replacement_manifest_required") is not True:
        errors.append("replacement_manifest_required must be true")

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

    validation_passed = not errors

    locked = _locked_flags()
    locked["human_replacement_approval_validated"] = validation_passed
    locked["next_phase_allowed"] = validation_passed

    return {
        "status": "success" if validation_passed else "blocked",
        "phase": "Phase 21C - Human Replacement Approval Gate",
        "validation_passed": validation_passed,
        "validation_errors": errors,
        "validation_warnings": warnings,
        "approved_replacement_source": str(APPROVED_REPLACEMENT_SOURCE),
        "protected_replacement_target": str(PROTECTED_REPLACEMENT_TARGET),
        "required_human_approval_format": "HUMAN-REPLACEMENT-APPROVED-21C-*",
        "next_required_phase": "Phase 21D - Replacement Dry-Run Validator",
        **locked,
    }

