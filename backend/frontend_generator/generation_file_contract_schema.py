from copy import deepcopy
from typing import Any, Dict, Optional


MANIFEST_SCHEMA_FIELDS = [
    "project_name",
    "generation_id",
    "target_folder",
    "generated_at",
    "generation_mode",
    "human_approval_id",
    "source_phase",
    "design_system_version",
    "product_brain_reference",
    "workspace_reference",
    "allowed_files",
    "blocked_files",
    "file_entries",
    "safety_flags",
    "validation_required",
    "backup_required",
    "rollback_required",
    "deployment_allowed",
    "provider_calls_allowed",
    "database_writes_allowed",
    "secrets_allowed",
]


FILE_ENTRY_SCHEMA = {
    "file_name": "Approved future file name only.",
    "relative_path": "Relative path inside the approved sandbox target folder.",
    "file_type": "html | css | js | markdown | json",
    "purpose": "Human-readable reason the file exists.",
    "write_status": "planned | dry_run_only | blocked | approved_later",
    "approval_required": True,
    "validation_required": True,
    "rollback_required": True,
    "allowed_to_overwrite": False,
    "checksum_placeholder": "sha256-placeholder-unavailable-until-dry-run",
    "generated_by_phase": "Future approved Phase 12 generation step.",
}


ALLOWED_FUTURE_FILES = [
    "index.html",
    "styles.css",
    "app.js",
    "README.md",
    "manifest.json",
    "validation-report.md",
]


BLOCKED_FILES_AND_LOCATIONS = [
    "backend/",
    "frontend/pages/",
    "frontend/shared/",
    "docs/ except documentation phases",
    "root production files",
    "deployment config",
    "secrets/env files",
    "KisanMitraAI folders",
    "any folder outside D:/APPS/IdeasForgeAI",
    "generated-apps existing folders unless explicitly approved",
]


SAFETY_FLAGS = {
    "generation_file_contract_defined": True,
    "manifest_schema_defined": True,
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


def build_generation_file_contract_response(payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Return static Phase 12B schema metadata only.

    This function intentionally performs no file writes, folder creation,
    generated app creation, provider calls, deployment, database writes, or
    generation of HTML/CSS/JS content.
    """

    payload = payload or {}
    project_name = payload.get("project_name") or "IdeasForgeAI"

    file_entries = [
        {
            **deepcopy(FILE_ENTRY_SCHEMA),
            "file_name": file_name,
            "relative_path": file_name,
            "file_type": file_name.rsplit(".", 1)[-1],
            "purpose": f"Future approved {file_name} output placeholder.",
        }
        for file_name in ALLOWED_FUTURE_FILES
    ]

    return {
        "status": "success",
        "phase": "Phase 12B - Generation File Contract + Manifest Schema",
        "mode": "schema_contract_only",
        "project_name": project_name,
        "request_echo": {
            "project_name": project_name,
            "approval_context": payload.get("approval_context", "approval_required"),
            "target_folder": payload.get("target_folder", "not_approved_yet"),
        },
        "manifest_schema": {
            "required_fields": MANIFEST_SCHEMA_FIELDS,
            "field_purpose": {
                "project_name": "Name of the generated product.",
                "generation_id": "Unique generation attempt identifier.",
                "target_folder": "Approved sandbox folder only.",
                "generated_at": "Timestamp produced during an approved future write.",
                "generation_mode": "dry_run | sandbox_write | approved_generation",
                "human_approval_id": "Explicit approval reference.",
                "source_phase": "Phase that initiated the generation request.",
                "design_system_version": "Approved Design System reference.",
                "product_brain_reference": "Approved Product Brain reference.",
                "workspace_reference": "Frozen Phase 11 Builder Workspace reference.",
                "allowed_files": "Whitelisted future files.",
                "blocked_files": "Denied files and locations.",
                "file_entries": "Per-file contract entries.",
                "safety_flags": "Generation lock state.",
                "validation_required": "Whether validation must run.",
                "backup_required": "Whether backup is required before write.",
                "rollback_required": "Whether rollback must be available.",
                "deployment_allowed": "Always false in Phase 12B.",
                "provider_calls_allowed": "Always false in Phase 12B.",
                "database_writes_allowed": "Always false in Phase 12B.",
                "secrets_allowed": "Always false.",
            },
        },
        "file_entry_schema": deepcopy(FILE_ENTRY_SCHEMA),
        "allowed_future_files": list(ALLOWED_FUTURE_FILES),
        "blocked_files_and_locations": list(BLOCKED_FILES_AND_LOCATIONS),
        "file_entries": file_entries,
        "safety_flags": deepcopy(SAFETY_FLAGS),
        "approval_gate": {
            "human_approval_required": True,
            "approval_required_before_file_writes": True,
            "approval_required_before_folder_creation": True,
            "approval_required_before_generation_unlock": True,
        },
        "next_phase_handoff": {
            "next_phase": "Phase 12C - Real Generation Dry-Run Validator",
            "phase_12c_implemented": False,
            "file_writes_remain_locked": True,
        },
        "safety_limits": [
            "Schema metadata only.",
            "No file writing.",
            "No folder creation.",
            "No generated app creation.",
            "No HTML/CSS/JS generation.",
            "No provider calls.",
            "No deployment.",
            "No Supabase, auth, database writes, or secrets.",
            "No KisanMitraAI production changes.",
        ],
    }
