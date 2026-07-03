from pathlib import Path
from typing import Any
import re


PROJECT_ROOT = Path("D:/APPS/IdeasForgeAI").resolve()

APPROVED_CANDIDATE_SOURCE = (
    PROJECT_ROOT
    / "generated-apps"
    / "_phase18_promoted_section_patch_preview"
).resolve()

APPROVED_CANDIDATE_TARGET = (
    PROJECT_ROOT
    / "generated-apps"
    / "_phase19_main_preview_candidate"
).resolve()


def _locked_flags() -> dict[str, Any]:
    return {
        "human_candidate_approval_gate_only": True,
        "human_candidate_approval_validated": False,
        "next_phase_allowed": False,
        "candidate_creation_performed": False,
        "candidate_manifest_created": False,
        "candidate_folder_created": False,
        "file_write_allowed": False,
        "folder_creation_allowed": False,
        "production_replacement_allowed": False,
        "real_generated_app_modified": False,
        "phase13e_sandbox_modified": False,
        "phase16f_sandbox_modified": False,
        "phase17_sandbox_modified": False,
        "phase18_promoted_folder_modified": False,
        "ideasforgeai_preview_v1_touched": False,
        "generation_allowed": False,
        "backend_generation_unlocked": False,
        "deployment_unlocked": False,
        "provider_calls_allowed": False,
        "database_writes_allowed": False,
        "secrets_allowed": False,
        "supabase_allowed": False,
        "auth_allowed": False,
        "IdeasForgeAI_production_touched": False,
    }


def _approval_id_valid(value: str) -> bool:
    return bool(re.fullmatch(r"HUMAN-CANDIDATE-APPROVED-19C-[A-Za-z0-9-]{4,64}", value or ""))


def validate_phase19c_human_candidate_approval_gate(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = payload or {}

    errors: list[str] = []

    if payload.get("project_name") != "IdeasForgeAI":
        errors.append("project_name must equal IdeasForgeAI")

    if payload.get("source_phase") != "Phase 19C":
        errors.append("source_phase must equal Phase 19C")

    human_approval_id = str(payload.get("human_approval_id", ""))
    if not _approval_id_valid(human_approval_id):
        errors.append("human_approval_id must match HUMAN-CANDIDATE-APPROVED-19C-* format")

    if payload.get("approved_by_human") is not True:
        errors.append("approved_by_human must be true")

    if payload.get("phase18h_frozen") is not True:
        errors.append("phase18h_frozen must be true")

    if int(payload.get("phase18g_validation_score", 0)) != 100:
        errors.append("phase18g_validation_score must be 100")

    if payload.get("phase18f_promoted_preview_route_working") is not True:
        errors.append("phase18f_promoted_preview_route_working must be true")

    source_folder = str(payload.get("source_folder", "")).replace("\\", "/")
    approved_source = str(APPROVED_CANDIDATE_SOURCE).replace("\\", "/")

    if source_folder != approved_source:
        errors.append("source_folder must equal approved Phase 18 promoted preview folder")

    target_folder = str(payload.get("target_folder", "")).replace("\\", "/")
    approved_target = str(APPROVED_CANDIDATE_TARGET).replace("\\", "/")

    if target_folder != approved_target:
        errors.append("target_folder must equal approved Phase 19 main preview candidate folder")

    if payload.get("candidate_dry_run_required") is not True:
        errors.append("candidate_dry_run_required must be true")

    if payload.get("rollback_required") is not True:
        errors.append("rollback_required must be true")

    if payload.get("candidate_manifest_required") is not True:
        errors.append("candidate_manifest_required must be true")

    locked_false_fields = [
        "production_replacement_allowed",
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
        locked["human_candidate_approval_validated"] = True
        locked["next_phase_allowed"] = True

    return {
        "status": "success" if validation_passed else "blocked",
        "phase": "Phase 19C - Human Candidate Approval Gate",
        "validation_passed": validation_passed,
        "validation_errors": errors,
        "approved_candidate_source": str(APPROVED_CANDIDATE_SOURCE),
        "approved_candidate_target": str(APPROVED_CANDIDATE_TARGET),
        "next_required_phase": "Phase 19D - Candidate Promotion Dry-Run Validator",
        **locked,
    }

