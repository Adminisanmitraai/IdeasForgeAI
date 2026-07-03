from pathlib import Path
from typing import Any


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

REQUIRED_SOURCE_FILES = [
    "index.html",
    "styles.css",
    "app.js",
    "manifest.json",
    "README.md",
    "phase20-polish-report.md",
    "phase20-validation-report.md",
]

REQUIRED_REPLACEMENT_FILES = REQUIRED_SOURCE_FILES + [
    "phase21-replacement-manifest.json",
    "phase21-rollback-manifest.json",
    "phase21-replacement-report.md",
    "phase21-validation-report.md",
]

REQUIRED_REPLACEMENT_MANIFEST_FIELDS = [
    "replacement_manifest_version",
    "phase",
    "created_at",
    "project_name",
    "source_folder",
    "target_folder",
    "approved_by_human",
    "human_approval_id",
    "phase20h_frozen",
    "phase20g_validation_score",
    "phase20f_preview_route_working",
    "phase21c_approval_validated",
    "phase21d_dry_run_passed",
    "phase21e_rollback_snapshot_ready",
    "source_files",
    "target_files",
    "source_file_hashes",
    "previous_target_hashes",
    "replacement_file_hashes",
    "rollback_manifest_path",
    "production_replacement_allowed",
    "deployment_allowed",
    "provider_calls_allowed",
    "database_writes_allowed",
    "supabase_allowed",
    "auth_allowed",
    "secrets_allowed",
    "IdeasForgeAI_production_touched",
]

REQUIRED_ROLLBACK_MANIFEST_FIELDS = [
    "rollback_manifest_version",
    "created_at",
    "project_name",
    "original_target_folder",
    "rollback_snapshot_folder",
    "replacement_source_folder",
    "rollback_available",
    "original_file_hashes",
    "restored_file_list",
    "production_replacement_allowed",
    "deployment_allowed",
    "provider_calls_allowed",
    "database_writes_allowed",
    "secrets_allowed",
]


def _locked_flags() -> dict[str, Any]:
    return {
        "replacement_contract_schema_only": True,
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


def get_phase21b_replacement_contract_manifest_schema() -> dict[str, Any]:
    return {
        "status": "success",
        "phase": "Phase 21B - Replacement Contract + Manifest Schema",
        "approved_replacement_source": str(APPROVED_REPLACEMENT_SOURCE),
        "protected_replacement_target": str(PROTECTED_REPLACEMENT_TARGET),
        "required_source_files": REQUIRED_SOURCE_FILES,
        "required_replacement_files": REQUIRED_REPLACEMENT_FILES,
        "required_approval_gates": [
            "Phase 20H frozen",
            "Phase 20G validation score 100",
            "Phase 20F preview route working",
            "Phase 21A frozen",
            "Phase 21B frozen",
            "Human replacement approval in Phase 21C",
            "Replacement dry-run pass in Phase 21D",
            "Rollback snapshot prepared in Phase 21E",
        ],
        "replacement_manifest_required_fields": REQUIRED_REPLACEMENT_MANIFEST_FIELDS,
        "rollback_manifest_required_fields": REQUIRED_ROLLBACK_MANIFEST_FIELDS,
        "blocked_paths": [
            "backend/",
            "frontend/pages/",
            "frontend/shared/",
            "deployment files",
            ".env files",
            "secret files",
            "provider configuration",
            "database configuration",
            "Supabase/auth configuration",
            "IdeasForgeAI paths",
        ],
        "next_required_phase": "Phase 21C - Human Replacement Approval Gate",
        **_locked_flags(),
    }

