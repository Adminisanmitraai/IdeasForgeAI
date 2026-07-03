from pathlib import Path
from typing import Any


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

REQUIRED_CANDIDATE_MANIFEST_FIELDS = [
    "candidate_manifest_version",
    "phase",
    "created_at",
    "project_name",
    "candidate_id",
    "human_approval_id",
    "approved_by_human",
    "source_folder",
    "target_folder",
    "source_validation_score",
    "phase18g_validation_passed",
    "phase18h_frozen",
    "copied_files",
    "source_file_hashes",
    "candidate_file_hashes",
    "promotion_manifest_source",
    "rollback_manifest_source",
    "rollback_available",
    "candidate_preview_route",
    "candidate_output_validation_required",
    "production_replacement_allowed",
    "deployment_allowed",
    "provider_calls_allowed",
    "database_writes_allowed",
    "secrets_allowed",
    "supabase_allowed",
    "auth_allowed",
    "real_generated_app_modified",
    "ideasforgeai_preview_v1_touched",
    "IdeasForgeAI_production_touched",
]

APPROVED_CANDIDATE_FILES = [
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
    "candidate-manifest.json",
    "phase19-candidate-report.md",
    "phase19-validation-report.md",
]

REQUIRED_CANDIDATE_GATES = [
    "Phase 18H frozen",
    "Phase 18G validation score 100",
    "Phase 18F promoted preview route working",
    "human approval true",
    "human approval id present",
    "source folder equals approved Phase 18 promoted preview folder",
    "target folder equals approved Phase 19 main preview candidate folder",
    "no generated-apps/ideasforgeai-preview-v1 write",
    "no backend write",
    "no Studio V3 source write",
    "no deployment write",
    "no provider call",
    "no database write",
    "no secrets",
    "no Supabase/auth unlock",
    "no IdeasForgeAI touch",
]

BLOCKED_TARGETS = [
    "generated-apps/ideasforgeai-preview-v1",
    "generated-apps/_phase13e_controlled_html_css_js_generation",
    "generated-apps/_phase16f_controlled_section_patch_sandbox",
    "generated-apps/_phase17_controlled_section_patch_applied_copy",
    "generated-apps/_phase18_promoted_section_patch_preview direct modification after candidate source read",
    "backend/",
    "frontend/pages/",
    "frontend/shared/",
    "docs/ except Phase 19 docs",
    "root production files",
    "deployment config",
    "env/secrets files",
    "IdeasForgeAI paths",
]


def _locked_flags() -> dict[str, Any]:
    return {
        "contract_schema_only": True,
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


def get_phase19b_main_preview_candidate_contract_schema() -> dict[str, Any]:
    return {
        "status": "success",
        "phase": "Phase 19B - Main Preview Candidate Contract + Manifest Schema",
        "approved_candidate_source": str(APPROVED_CANDIDATE_SOURCE),
        "approved_candidate_target": str(APPROVED_CANDIDATE_TARGET),
        "required_candidate_manifest_fields": REQUIRED_CANDIDATE_MANIFEST_FIELDS,
        "approved_candidate_files": APPROVED_CANDIDATE_FILES,
        "required_candidate_gates": REQUIRED_CANDIDATE_GATES,
        "blocked_targets": BLOCKED_TARGETS,
        "next_required_phase": "Phase 19C - Human Candidate Approval Gate",
        **_locked_flags(),
    }

