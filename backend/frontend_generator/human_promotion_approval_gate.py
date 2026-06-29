from pathlib import Path
from typing import Any
import re


PROJECT_ROOT = Path("D:/APPS/IdeasForgeAI").resolve()

APPROVED_PROMOTION_SOURCE = (
    PROJECT_ROOT
    / "generated-apps"
    / "_phase17_controlled_section_patch_applied_copy"
).resolve()

APPROVED_PROMOTION_TARGET = (
    PROJECT_ROOT
    / "generated-apps"
    / "_phase18_promoted_section_patch_preview"
).resolve()


def _locked_flags() -> dict[str, Any]:
    return {
        "human_promotion_approval_gate_only": True,
        "human_promotion_approval_validated": False,
        "next_phase_allowed": False,
        "promotion_performed": False,
        "promotion_manifest_created": False,
        "promoted_folder_created": False,
        "file_write_allowed": False,
        "folder_creation_allowed": False,
        "real_generated_app_modified": False,
        "phase13e_sandbox_modified": False,
        "phase16f_sandbox_modified": False,
        "phase17_sandbox_modified": False,
        "ideasforgeai_preview_v1_touched": False,
        "generation_allowed": False,
        "backend_generation_unlocked": False,
        "deployment_unlocked": False,
        "provider_calls_allowed": False,
        "database_writes_allowed": False,
        "secrets_allowed": False,
        "supabase_allowed": False,
        "auth_allowed": False,
        "kisanmitra_production_touched": False,
    }


def _approval_id_valid(value: str) -> bool:
    return bool(re.fullmatch(r"HUMAN-PROMOTION-APPROVED-18C-[A-Za-z0-9-]{4,64}", value or ""))


def validate_phase18c_human_promotion_approval_gate(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = payload or {}

    errors: list[str] = []

    if payload.get("project_name") != "IdeasForgeAI":
        errors.append("project_name must equal IdeasForgeAI")

    if payload.get("source_phase") != "Phase 18C":
        errors.append("source_phase must equal Phase 18C")

    human_approval_id = str(payload.get("human_approval_id", ""))
    if not _approval_id_valid(human_approval_id):
        errors.append("human_approval_id must match HUMAN-PROMOTION-APPROVED-18C-* format")

    if payload.get("approved_by_human") is not True:
        errors.append("approved_by_human must be true")

    if payload.get("phase17g_frozen") is not True:
        errors.append("phase17g_frozen must be true")

    if int(payload.get("phase17f_validation_score", 0)) != 100:
        errors.append("phase17f_validation_score must be 100")

    if payload.get("phase17e_preview_route_working") is not True:
        errors.append("phase17e_preview_route_working must be true")

    source_folder = str(payload.get("source_folder", "")).replace("\\", "/")
    approved_source = str(APPROVED_PROMOTION_SOURCE).replace("\\", "/")

    if source_folder != approved_source:
        errors.append("source_folder must equal approved Phase 17 sandbox copy")

    target_folder = str(payload.get("target_folder", "")).replace("\\", "/")
    approved_target = str(APPROVED_PROMOTION_TARGET).replace("\\", "/")

    if target_folder != approved_target:
        errors.append("target_folder must equal approved Phase 18 promoted preview folder")

    if payload.get("promotion_dry_run_required") is not True:
        errors.append("promotion_dry_run_required must be true")

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

    validation_passed = not errors

    locked = _locked_flags()

    if validation_passed:
        locked["human_promotion_approval_validated"] = True
        locked["next_phase_allowed"] = True

    return {
        "status": "success" if validation_passed else "blocked",
        "phase": "Phase 18C - Human Promotion Approval Gate",
        "validation_passed": validation_passed,
        "validation_errors": errors,
        "approved_promotion_source": str(APPROVED_PROMOTION_SOURCE),
        "approved_promotion_target": str(APPROVED_PROMOTION_TARGET),
        "next_required_phase": "Phase 18D - Promotion Dry-Run Validator",
        **locked,
    }
