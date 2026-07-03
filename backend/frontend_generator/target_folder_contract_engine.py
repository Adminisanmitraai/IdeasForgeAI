
"""Phase 9B generation target folder contract engine.

Contract metadata only.
No folder creation.
No HTML/CSS/React generation.
No file writes.
No generated app creation.
"""

from typing import Any, Dict, List


FUTURE_TARGET_FOLDER = "generated-apps/ideasforgeai-preview-v1/"


BLOCKED_FIELDS: List[str] = [
    "html_output",
    "css_output",
    "react_output",
    "generated_files",
    "generated_app_path",
    "file_write_request",
    "deploy_request",
    "provider_prompt",
    "secret_value",
    "database_write",
    "supabase_config",
    "auth_config",
]


SAFE_FLAGS: Dict[str, bool] = {
    "generation_target_folder_contract_allowed": True,
    "target_folder_defined": True,
    "target_folder_created": False,
    "production_frontend_generation_allowed": False,
    "html_generation_allowed": False,
    "css_generation_allowed": False,
    "react_generation_allowed": False,
    "generated_app_write_allowed": False,
    "generated_files_allowed": False,
    "deployment_allowed": False,
    "provider_calls_allowed": False,
    "database_writes_allowed": False,
    "supabase_allowed": False,
    "auth_allowed": False,
    "approval_required": True,
}


def build_target_folder_contract_response(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}
    project_name = payload.get("project_name") or "IdeasForgeAI"

    return {
        "status": "success",
        "phase": "Phase 9B - Generation Target Folder Contract",
        "mode": "contract_only",
        "project_name": project_name,
        "future_target_folder": FUTURE_TARGET_FOLDER,
        "target_folder_status": {
            "defined": True,
            "created": False,
            "write_allowed": False,
            "approval_required": True,
        },
        "allowed_future_file_types": [
            "index.html",
            "styles.css",
            "app.js",
            "README.md",
            "manifest.json",
            "validation-report.md",
            "assets_placeholder_references",
        ],
        "blocked_write_locations": [
            "backend/",
            "frontend/pages/",
            "frontend/shared/",
            "docs/",
            "root production files",
            "existing generated app folders unless explicitly approved",
            "IdeasForgeAI folders",
            "any folder outside D:/APPS/IdeasForgeAI",
        ],
        "required_before_folder_creation": [
            "Phase 9B freeze review",
            "Explicit human approval",
            "Dry run file write check",
            "Rollback-safe plan",
            "generated-apps diff check",
        ],
        "safety_flags": SAFE_FLAGS,
        "blocked_fields": BLOCKED_FIELDS,
        "next_phase_handoff": {
            "current_phase": "Phase 9B - Generation Target Folder Contract",
            "next_phase": "Phase 9C - Single Page File Write Dry Run",
            "handoff_status": "approval_gated",
            "production_generation_status": "locked",
        },
    }

