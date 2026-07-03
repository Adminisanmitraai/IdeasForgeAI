from pathlib import Path
from typing import Any


PROJECT_ROOT = Path("D:/APPS/IdeasForgeAI").resolve()

APPROVED_SOURCE_FOLDER = (
    PROJECT_ROOT
    / "generated-apps"
    / "_phase13e_controlled_html_css_js_generation"
).resolve()

APPROVED_PATCH_PROPOSAL_FOLDER = (
    PROJECT_ROOT
    / "generated-apps"
    / "_phase16f_controlled_section_patch_sandbox"
).resolve()

APPROVED_PHASE17_TARGET = (
    PROJECT_ROOT
    / "generated-apps"
    / "_phase17_controlled_section_patch_applied_copy"
).resolve()

APPROVED_COPY_FILES = [
    "index.html",
    "styles.css",
    "app.js",
    "manifest.json",
    "README.md",
    "validation-report.md",
]

APPROVED_CONTROL_FILES = [
    "section-patch-application-report.md",
    "rollback-manifest.json",
    "phase17-validation-report.md",
]

ROLLBACK_MANIFEST_REQUIRED_FIELDS = [
    "rollback_manifest_version",
    "phase",
    "created_at",
    "source_folder",
    "patch_proposal_folder",
    "sandbox_copy_target",
    "copied_files",
    "original_file_hashes",
    "patched_file_hashes",
    "selected_section_id",
    "selected_section_type",
    "source_file",
    "start_marker",
    "end_marker",
    "patch_applied_to_copy_only",
    "real_generated_app_modified",
    "ideasforgeai_preview_v1_touched",
    "phase13e_sandbox_modified",
    "deployment_unlocked",
    "provider_calls_allowed",
    "database_writes_allowed",
    "secrets_allowed",
    "rollback_available",
]


def _locked_flags() -> dict[str, Any]:
    return {
        "contract_schema_only": True,
        "sandbox_copy_created": False,
        "section_patch_applied": False,
        "real_generated_app_modified": False,
        "phase13e_sandbox_modified": False,
        "phase16f_sandbox_modified": False,
        "ideasforgeai_preview_v1_touched": False,
        "file_write_allowed": False,
        "folder_creation_allowed": False,
        "generation_allowed": False,
        "backend_generation_unlocked": False,
        "deployment_unlocked": False,
        "provider_calls_allowed": False,
        "database_writes_allowed": False,
        "secrets_allowed": False,
        "supabase_allowed": False,
        "auth_allowed": False,
    }


def get_phase17b_sandbox_copy_rollback_manifest_contract() -> dict[str, Any]:
    return {
        "status": "success",
        "phase": "Phase 17B - Sandbox Copy Contract + Rollback Manifest",
        "approved_source_folder": str(APPROVED_SOURCE_FOLDER),
        "approved_patch_proposal_folder": str(APPROVED_PATCH_PROPOSAL_FOLDER),
        "approved_phase17_target": str(APPROVED_PHASE17_TARGET),
        "approved_copy_files": APPROVED_COPY_FILES,
        "approved_control_files": APPROVED_CONTROL_FILES,
        "rollback_manifest_required_fields": ROLLBACK_MANIFEST_REQUIRED_FIELDS,
        "blocked_targets": [
            "generated-apps/ideasforgeai-preview-v1",
            "generated-apps/_phase13e_controlled_html_css_js_generation direct modification",
            "generated-apps/_phase16f_controlled_section_patch_sandbox direct modification",
            "backend/",
            "frontend/pages/",
            "frontend/shared/",
            "docs/ except phase docs",
            "root production files",
            "deployment config",
            "env/secrets files",
            "IdeasForgeAI paths",
        ],
        "next_required_phase": "Phase 17C - Create Read-Only Source Copy Sandbox",
        **_locked_flags(),
    }

