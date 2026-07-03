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
]

BLOCKED_TARGET_MARKERS = [
    "generated-apps/ideasforgeai-preview-v1",
    "generated-apps/_phase13e_controlled_html_css_js_generation",
    "generated-apps/_phase16f_controlled_section_patch_sandbox",
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
    "IdeasForgeAI",
]


def _locked_flags() -> dict[str, Any]:
    return {
        "promotion_dry_run_only": True,
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
        "IdeasForgeAI_production_touched": False,
    }


def _promotion_id_valid(value: str) -> bool:
    return bool(re.fullmatch(r"IF-PROMOTION-DRYRUN-18D-[A-Za-z0-9-]{4,64}", value or ""))


def _approval_id_valid(value: str) -> bool:
    return bool(re.fullmatch(r"HUMAN-PROMOTION-APPROVED-18C-[A-Za-z0-9-]{4,64}", value or ""))


def validate_phase18d_promotion_dry_run(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = payload or {}

    errors: list[str] = []
    warnings: list[str] = []

    if payload.get("project_name") != "IdeasForgeAI":
        errors.append("project_name must equal IdeasForgeAI")

    if payload.get("source_phase") != "Phase 18D":
        errors.append("source_phase must equal Phase 18D")

    promotion_id = str(payload.get("promotion_id", ""))
    if not _promotion_id_valid(promotion_id):
        errors.append("promotion_id must match IF-PROMOTION-DRYRUN-18D-* format")

    human_approval_id = str(payload.get("human_approval_id", ""))
    if not _approval_id_valid(human_approval_id):
        errors.append("human_approval_id must match HUMAN-PROMOTION-APPROVED-18C-* format")

    if payload.get("approved_by_human") is not True:
        errors.append("approved_by_human must be true")

    if payload.get("phase18c_approval_validated") is not True:
        errors.append("phase18c_approval_validated must be true")

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

    if payload.get("rollback_required") is not True:
        errors.append("rollback_required must be true")

    if payload.get("promotion_manifest_required") is not True:
        errors.append("promotion_manifest_required must be true")

    if not APPROVED_PROMOTION_SOURCE.exists():
        errors.append("approved Phase 17 promotion source folder does not exist")
    else:
        existing_source_files = sorted(
            item.name for item in APPROVED_PROMOTION_SOURCE.iterdir() if item.is_file()
        )
        missing_source_files = [
            name for name in REQUIRED_SOURCE_FILES if name not in existing_source_files
        ]
        if missing_source_files:
            errors.append("missing required source files: " + ", ".join(missing_source_files))
    existing_source_files = sorted(
        item.name for item in APPROVED_PROMOTION_SOURCE.iterdir() if item.is_file()
    ) if APPROVED_PROMOTION_SOURCE.exists() else []

    if (APPROVED_PROMOTION_SOURCE / "rollback-manifest.json").exists() is False:
        errors.append("rollback-manifest.json is required in the Phase 17 source folder")

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
        "phase": "Phase 18D - Promotion Dry-Run Validator",
        "validation_passed": validation_passed,
        "validation_errors": errors,
        "validation_warnings": warnings,
        "approved_promotion_source": str(APPROVED_PROMOTION_SOURCE),
        "approved_promotion_target": str(APPROVED_PROMOTION_TARGET),
        "existing_source_files": existing_source_files,
        "required_source_files": REQUIRED_SOURCE_FILES,
        "next_required_phase": "Phase 18E - Controlled Promotion to Approved Preview Folder",
        **_locked_flags(),
    }

