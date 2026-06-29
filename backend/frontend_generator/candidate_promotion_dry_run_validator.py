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

REQUIRED_SOURCE_FILES = [
    "index.html",
    "styles.css",
    "app.js",
    "manifest.json",
    "README.md",
    "validation-report.md",
    "rollback-manifest.json",
    "phase17-validation-report.md",
    "section-patch-application-report.md",
    "promotion-manifest.json",
    "phase18-promotion-report.md",
    "phase18-validation-report.md",
]

BLOCKED_TARGET_MARKERS = [
    "generated-apps/ideasforgeai-preview-v1",
    "generated-apps/_phase13e_controlled_html_css_js_generation",
    "generated-apps/_phase16f_controlled_section_patch_sandbox",
    "generated-apps/_phase17_controlled_section_patch_applied_copy",
    "backend/",
    "frontend/pages/",
    "frontend/shared/",
    "docs/",
    ".env",
    "secret",
    "token",
    "api_key",
    "apikey",
    "deploy",
    "deployment",
    "render.yaml",
    "supabase",
    "auth",
    "database",
    "kisanmitra",
]


def _locked_flags() -> dict[str, Any]:
    return {
        "candidate_promotion_dry_run_only": True,
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
        "kisanmitra_production_touched": False,
    }


def _candidate_id_valid(value: str) -> bool:
    return bool(re.fullmatch(r"IF-CANDIDATE-DRYRUN-19D-[A-Za-z0-9-]{4,64}", value or ""))


def _approval_id_valid(value: str) -> bool:
    return bool(re.fullmatch(r"HUMAN-CANDIDATE-APPROVED-19C-[A-Za-z0-9-]{4,64}", value or ""))


def validate_phase19d_candidate_promotion_dry_run(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = payload or {}

    errors: list[str] = []
    warnings: list[str] = []

    if payload.get("project_name") != "IdeasForgeAI":
        errors.append("project_name must equal IdeasForgeAI")

    if payload.get("source_phase") != "Phase 19D":
        errors.append("source_phase must equal Phase 19D")

    candidate_id = str(payload.get("candidate_id", ""))
    if not _candidate_id_valid(candidate_id):
        errors.append("candidate_id must match IF-CANDIDATE-DRYRUN-19D-* format")

    human_approval_id = str(payload.get("human_approval_id", ""))
    if not _approval_id_valid(human_approval_id):
        errors.append("human_approval_id must match HUMAN-CANDIDATE-APPROVED-19C-* format")

    if payload.get("approved_by_human") is not True:
        errors.append("approved_by_human must be true")

    if payload.get("phase19c_approval_validated") is not True:
        errors.append("phase19c_approval_validated must be true")

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

    if payload.get("rollback_required") is not True:
        errors.append("rollback_required must be true")

    if payload.get("candidate_manifest_required") is not True:
        errors.append("candidate_manifest_required must be true")

    if payload.get("promotion_manifest_required") is not True:
        errors.append("promotion_manifest_required must be true")

    existing_source_files = []

    if not APPROVED_CANDIDATE_SOURCE.exists():
        errors.append("approved Phase 18 candidate source folder does not exist")
    else:
        existing_source_files = sorted(
            item.name for item in APPROVED_CANDIDATE_SOURCE.iterdir() if item.is_file()
        )

        missing_source_files = [
            name for name in REQUIRED_SOURCE_FILES if name not in existing_source_files
        ]

        if missing_source_files:
            errors.append("missing required source files: " + ", ".join(missing_source_files))

    if not (APPROVED_CANDIDATE_SOURCE / "promotion-manifest.json").exists():
        errors.append("promotion-manifest.json is required in the Phase 18 source folder")

    if not (APPROVED_CANDIDATE_SOURCE / "rollback-manifest.json").exists():
        errors.append("rollback-manifest.json is required in the Phase 18 source folder")

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

    combined_payload = " ".join(str(v) for v in payload.values()).replace("\\", "/").lower()
    approved_source_lower = approved_source.lower()
    approved_target_lower = approved_target.lower()

    for marker in BLOCKED_TARGET_MARKERS:
        marker_lower = marker.lower()
        if marker_lower in combined_payload:
            if marker_lower not in approved_source_lower and marker_lower not in approved_target_lower:
                errors.append(f"blocked target marker found: {marker}")

    validation_passed = not errors

    return {
        "status": "success" if validation_passed else "blocked",
        "phase": "Phase 19D - Candidate Promotion Dry-Run Validator",
        "validation_passed": validation_passed,
        "validation_errors": errors,
        "validation_warnings": warnings,
        "approved_candidate_source": str(APPROVED_CANDIDATE_SOURCE),
        "approved_candidate_target": str(APPROVED_CANDIDATE_TARGET),
        "existing_source_files": existing_source_files,
        "required_source_files": REQUIRED_SOURCE_FILES,
        "next_required_phase": "Phase 19E - Controlled Candidate Folder Creation",
        **_locked_flags(),
    }
