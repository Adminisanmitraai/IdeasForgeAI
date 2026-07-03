"""Phase 13B multi-file generation contract + manifest schema.

Static schema metadata only.
No file writes.
No folder creation.
No generated app creation.
No HTML/CSS/JS generation.
No provider calls.
No deployment.
No Supabase/auth/database/secrets.
"""

from copy import deepcopy
from typing import Any, Dict, Optional


MANIFEST_SCHEMA_FIELDS = [
    "project_name",
    "generation_id",
    "target_folder",
    "generation_mode",
    "source_phase",
    "human_approval_id",
    "approved_by_human",
    "dry_run_validation_passed",
    "backup_required",
    "rollback_required",
    "manifest_version",
    "design_system_version",
    "product_brain_reference",
    "workspace_reference",
    "allowed_files",
    "blocked_files",
    "file_entries",
    "write_order",
    "validation_rules",
    "safety_flags",
    "rollback_plan",
    "preview_runner_allowed",
    "deployment_allowed",
    "provider_calls_allowed",
    "database_writes_allowed",
    "secrets_allowed",
    "next_required_phase",
]

ALLOWED_FUTURE_FILES = [
    "index.html",
    "styles.css",
    "app.js",
    "manifest.json",
    "validation-report.md",
    "README.md",
]

WRITE_ORDER = [
    "manifest.json",
    "index.html",
    "styles.css",
    "app.js",
    "README.md",
    "validation-report.md",
]

FILE_ENTRY_SCHEMA = {
    "file_name": "Approved future file name only.",
    "relative_path": "Relative path inside the approved Phase 13 sandbox target folder.",
    "file_type": "html | css | js | json | markdown",
    "purpose": "Human-readable reason the file exists.",
    "write_status": "planned | dry_run_only | blocked | approved_later",
    "required": True,
    "approval_required": True,
    "validation_required": True,
    "backup_required": True,
    "rollback_required": True,
    "allowed_to_overwrite": False,
    "checksum_placeholder": "sha256-placeholder-unavailable-until-approved-dry-run",
    "dependency_order": "Integer write-order position, starting at 1.",
    "generated_by_phase": "Future approved Phase 13 generation step.",
}

BLOCKED_FILES_AND_LOCATIONS = [
    "backend/",
    "frontend/pages/",
    "frontend/shared/",
    "docs/ except documentation phases",
    "root production files",
    "deployment config files",
    ".env or secrets files",
    "database/auth/Supabase files",
    "IdeasForgeAI folders",
    "any path outside D:/APPS/IdeasForgeAI",
    "generated-apps/ideasforgeai-preview-v1 unless explicitly approved in a later phase",
    "Phase 12 sandbox folders",
]

VALIDATION_RULES = [
    "project_name must equal IdeasForgeAI",
    "target_folder must be an approved Phase 13 sandbox folder",
    "allowed_files must exactly match the approved contract",
    "write_order must match the required Phase 13 sequence",
    "file_entries must match the file entry schema",
    "dry_run_validation_passed must be true before any future write",
    "approved_by_human must be true before any future write",
    "backup_required and rollback_required must be true",
    "deployment_allowed must be false",
    "provider_calls_allowed must be false",
    "database_writes_allowed must be false",
    "secrets_allowed must be false",
    "Supabase/auth unlock must be false",
    "IdeasForgeAI paths must be rejected",
]

SAFETY_FLAGS = {
    "multi_file_contract_defined": True,
    "manifest_schema_upgraded": True,
    "file_write_allowed": False,
    "folder_creation_allowed": False,
    "generated_app_write_allowed": False,
    "html_generation_allowed": False,
    "css_generation_allowed": False,
    "js_generation_allowed": False,
    "backend_generation_allowed": False,
    "deployment_allowed": False,
    "provider_calls_allowed": False,
    "database_writes_allowed": False,
    "supabase_allowed": False,
    "auth_allowed": False,
    "secrets_allowed": False,
    "approval_required": True,
}

ROLLBACK_PLAN_SCHEMA = {
    "rollback_required": True,
    "backup_required_before_write": True,
    "restore_previous_folder_state": True,
    "remove_new_files_on_failure": True,
    "rollback_scope": "Approved Phase 13 sandbox folder only.",
    "blocked_rollback_targets": BLOCKED_FILES_AND_LOCATIONS,
}


def _build_file_entries() -> list[Dict[str, Any]]:
    entries = []
    for file_name in ALLOWED_FUTURE_FILES:
        entries.append(
            {
                **deepcopy(FILE_ENTRY_SCHEMA),
                "file_name": file_name,
                "relative_path": file_name,
                "file_type": "markdown" if file_name.endswith(".md") else file_name.rsplit(".", 1)[-1],
                "purpose": f"Future approved Phase 13 {file_name} output placeholder.",
                "write_status": "dry_run_only",
                "dependency_order": WRITE_ORDER.index(file_name) + 1,
                "generated_by_phase": "Future approved Phase 13 controlled multi-file generation step.",
            }
        )
    return entries


def build_phase13b_multi_file_contract_response(payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Return Phase 13B static multi-file contract metadata only."""

    payload = payload or {}
    project_name = payload.get("project_name") or "IdeasForgeAI"

    return {
        "status": "success",
        "phase": "Phase 13B - Multi-File Contract + Manifest Upgrade",
        "mode": "schema_contract_only",
        "project_name": project_name,
        "manifest_schema": {
            "manifest_version": "phase13b-multi-file-contract-v1",
            "required_fields": MANIFEST_SCHEMA_FIELDS,
        },
        "allowed_future_files": list(ALLOWED_FUTURE_FILES),
        "blocked_files_and_locations": list(BLOCKED_FILES_AND_LOCATIONS),
        "file_entry_schema": deepcopy(FILE_ENTRY_SCHEMA),
        "file_entries": _build_file_entries(),
        "write_order": list(WRITE_ORDER),
        "validation_rules": list(VALIDATION_RULES),
        "safety_flags": deepcopy(SAFETY_FLAGS),
        "rollback_plan": deepcopy(ROLLBACK_PLAN_SCHEMA),
        "preview_runner_allowed": False,
        "deployment_allowed": False,
        "provider_calls_allowed": False,
        "database_writes_allowed": False,
        "secrets_allowed": False,
        "next_required_phase": "Phase 13C - Multi-File Dry-Run Validator",
        "side_effects": {
            "files_written": False,
            "folders_created": False,
            "generated_app_created": False,
            "html_css_js_generated": False,
            "providers_called": False,
            "deployment_started": False,
            "database_writes_made": False,
            "secrets_used": False,
        },
        "safety_limits": [
            "Static schema metadata only.",
            "No file writing.",
            "No folder creation.",
            "No generated app creation.",
            "No HTML/CSS/JS generation.",
            "No provider calls.",
            "No deployment.",
            "No Supabase, auth, database writes, or secrets.",
            "No IdeasForgeAI production changes.",
            "Phase 13C is not implemented.",
        ],
    }
