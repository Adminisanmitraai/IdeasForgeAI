
"""Phase 9A real frontend generation planning engine.

Planning metadata only.
No HTML/CSS/React generation.
No file writes.
No generated app creation.
"""

from typing import Any, Dict, List


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
    "real_frontend_generation_planning_allowed": True,
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


def build_real_generation_planning_response(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}
    project_name = payload.get("project_name") or "IdeasForgeAI"

    return {
        "status": "success",
        "phase": "Phase 9A - Real Frontend Generation Planning",
        "mode": "planning_only",
        "project_name": project_name,
        "planning_summary": {
            "real_generation_planning_started": True,
            "production_generation_unlocked": False,
            "generated_app_write_unlocked": False,
            "html_css_react_generation_unlocked": False,
            "approval_required": True,
        },
        "required_inputs_before_future_generation": [
            "Approved Product Brain output",
            "Approved Design System output",
            "Approved Pixel-Matched placeholder track",
            "Approved Phase 8 preview track",
            "Explicit human generation approval",
            "Safe target generated app folder",
            "Rollback-safe file plan",
        ],
        "future_unlock_gates": [
            "Generation target folder contract",
            "Dry run file write check",
            "Design System validation",
            "Product Brain validation",
            "Preview approval validation",
            "No deployment confirmation",
            "No secrets confirmation",
            "Manual approval confirmation",
        ],
        "future_output_types": [
            "single_page_html_preview",
            "css_preview_file",
            "vanilla_js_preview_file",
            "react_component_preview",
            "multi_page_structure",
            "asset_manifest",
            "validation_report",
        ],
        "safety_flags": SAFE_FLAGS,
        "blocked_fields": BLOCKED_FIELDS,
        "next_phase_handoff": {
            "current_phase": "Phase 9A - Real Frontend Generation Planning",
            "next_phase": "Phase 9B - Generation Target Folder Contract",
            "handoff_status": "approval_gated",
            "production_generation_status": "locked",
        },
    }
