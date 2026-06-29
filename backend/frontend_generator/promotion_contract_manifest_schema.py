from pathlib import Path
from typing import Any


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

REQUIRED_PROMOTION_MANIFEST_FIELDS = [
    "promotion_manifest_version",
    "phase",
    "created_at",
    "project_name",
    "promotion_id",
    "human_approval_id",
    "approved_by_human",
    "source_folder",
    "target_folder",
    "source_validation_score",
    "phase17f_validation_passed",
    "copied_files",
    "source_file_hashes",
    "promoted_file_hashes",
    "rollback_manifest_source",
    "rollback_available",
    "promoted_preview_route",
    "promoted_output_validation_required",
    "deployment_allowed",
    "provider_calls_allowed",
    "database_writes_allowed",
    "secrets_allowed",
    "supabase_allowed",
    "auth_allowed",
    "real_generated_app_modified",
    "ideasforgeai_preview_v1_touched",
    "kisanmitra_production_touched",
]

APPROVED_PROMOTED_FILES = [
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

REQUIRED_PROMOTION_GATES = [
    "Phase 17G frozen",
    "Phase 17F validation score 100",
    "human approval true",
    "human approval id present",
    "source folder equals approved Phase 17 sandbox copy",
    "target folder equals approved Phase 18 promoted preview folder",
    "no generated-apps/ideasforgeai-preview-v1 write",
    "no backend write",
    "no Studio V3 source write",
    "no deployment write",
    "no provider call",
    "no database write",
    "no secrets",
    "no Supabase/auth unlock",
    "no KisanMitraAI touch",
]

BLOCKED_TARGETS = [
    "generated-apps/ideasforgeai-preview-v1",
    "generated-apps/_phase13e_controlled_html_css_js_generation",
    "generated-apps/_phase16f_controlled_section_patch_sandbox",
    "generated-apps/_phase17_controlled_section_patch_applied_copy direct modification after promotion source read",
    "backend/",
    "frontend/pages/",
    "frontend/shared/",
    "docs/ except Phase 18 docs",
    "root production files",
    "deployment config",
    "env/secrets files",
    "KisanMitraAI paths",
]


def _locked_flags() -> dict[str, Any]:
    return {
        "contract_schema_only": True,
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


def get_phase18b_promotion_contract_manifest_schema() -> dict[str, Any]:
    return {
        "status": "success",
        "phase": "Phase 18B - Promotion Contract + Manifest Schema",
        "approved_promotion_source": str(APPROVED_PROMOTION_SOURCE),
        "approved_promotion_target": str(APPROVED_PROMOTION_TARGET),
        "required_promotion_manifest_fields": REQUIRED_PROMOTION_MANIFEST_FIELDS,
        "approved_promoted_files": APPROVED_PROMOTED_FILES,
        "required_promotion_gates": REQUIRED_PROMOTION_GATES,
        "blocked_targets": BLOCKED_TARGETS,
        "next_required_phase": "Phase 18C - Human Promotion Approval Gate",
        **_locked_flags(),
    }
