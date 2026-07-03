
"""Phase 9C single-page file write dry-run engine.

Dry-run metadata only.
No folder creation.
No file writes.
No generated app creation.
No HTML/CSS/React output.
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
    "single_page_file_write_dry_run_allowed": True,
    "target_folder_created": False,
    "file_write_performed": False,
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


def build_file_write_dry_run_response(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}
    project_name = payload.get("project_name") or "IdeasForgeAI"

    planned_files = [
        {
            "file_name": "index.html",
            "future_path": FUTURE_TARGET_FOLDER + "index.html",
            "write_status": "dry_run_only_not_written",
            "approval_required": True,
        },
        {
            "file_name": "styles.css",
            "future_path": FUTURE_TARGET_FOLDER + "styles.css",
            "write_status": "dry_run_only_not_written",
            "approval_required": True,
        },
        {
            "file_name": "app.js",
            "future_path": FUTURE_TARGET_FOLDER + "app.js",
            "write_status": "dry_run_only_not_written",
            "approval_required": True,
        },
        {
            "file_name": "README.md",
            "future_path": FUTURE_TARGET_FOLDER + "README.md",
            "write_status": "dry_run_only_not_written",
            "approval_required": True,
        },
        {
            "file_name": "validation-report.md",
            "future_path": FUTURE_TARGET_FOLDER + "validation-report.md",
            "write_status": "dry_run_only_not_written",
            "approval_required": True,
        },
    ]

    return {
        "status": "success",
        "phase": "Phase 9C - Single Page File Write Dry Run",
        "mode": "dry_run_only",
        "project_name": project_name,
        "future_target_folder": FUTURE_TARGET_FOLDER,
        "dry_run_summary": {
            "target_folder_defined": True,
            "target_folder_created": False,
            "file_write_performed": False,
            "generated_files_created": False,
            "production_generation_unlocked": False,
            "approval_required": True,
        },
        "planned_future_files": planned_files,
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
        "dry_run_checks": [
            "Target folder path is inside generated-apps/",
            "Target folder does not exist yet",
            "No file write request accepted",
            "No generated files created",
            "No HTML/CSS/React output returned",
            "Manual approval still required",
        ],
        "rollback_plan_preview": [
            "No rollback needed in Phase 9C because no files are written",
            "Future file writes must include backup or cleanup instructions",
            "Future generated app changes must be isolated to the target folder",
        ],
        "safety_flags": SAFE_FLAGS,
        "blocked_fields": BLOCKED_FIELDS,
        "next_phase_handoff": {
            "current_phase": "Phase 9C - Single Page File Write Dry Run",
            "next_phase": "Phase 9D - Single Page Real HTML/CSS Preview File Generation",
            "handoff_status": "approval_gated",
            "production_generation_status": "locked",
        },
    }

