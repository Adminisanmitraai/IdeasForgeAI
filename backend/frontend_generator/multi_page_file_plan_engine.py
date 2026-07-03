
"""Phase 9F multi-page file generation plan engine.

Plan metadata only.
No page creation.
No folder creation.
No file writes.
No HTML/CSS/React output.
"""

from typing import Any, Dict, List


TARGET_FOLDER = "generated-apps/ideasforgeai-preview-v1/"


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
    "multi_page_generation_plan_allowed": True,
    "multi_page_file_write_allowed": False,
    "new_page_files_created": False,
    "production_frontend_generation_allowed": False,
    "html_generation_allowed": False,
    "css_generation_allowed": False,
    "react_generation_allowed": False,
    "generated_app_write_allowed": False,
    "deployment_allowed": False,
    "provider_calls_allowed": False,
    "database_writes_allowed": False,
    "supabase_allowed": False,
    "auth_allowed": False,
    "approval_required": True,
}


def build_multi_page_file_plan_response(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}
    project_name = payload.get("project_name") or "IdeasForgeAI"

    planned_pages = [
        {"file_name": "index.html", "purpose": "Landing page and product positioning", "write_status": "planned_not_written"},
        {"file_name": "features.html", "purpose": "Product modules and value explanation", "write_status": "planned_not_written"},
        {"file_name": "workflow.html", "purpose": "Idea-to-product process", "write_status": "planned_not_written"},
        {"file_name": "preview.html", "purpose": "Generated preview explanation", "write_status": "planned_not_written"},
        {"file_name": "pricing.html", "purpose": "Future plan/pricing placeholder", "write_status": "planned_not_written"},
        {"file_name": "login.html", "purpose": "Future auth placeholder, no real auth", "write_status": "planned_not_written"},
        {"file_name": "dashboard.html", "purpose": "Future app dashboard preview, no backend connection", "write_status": "planned_not_written"},
        {"file_name": "settings.html", "purpose": "Future settings preview, no persistent storage", "write_status": "planned_not_written"},
    ]

    return {
        "status": "success",
        "phase": "Phase 9F - Multi-page File Generation Plan",
        "mode": "plan_only",
        "project_name": project_name,
        "target_folder": TARGET_FOLDER,
        "planned_pages": planned_pages,
        "planned_shared_files": [
            "styles.css",
            "app.js",
            "manifest.json",
            "README.md",
            "validation-report.md",
        ],
        "plan_summary": {
            "multi_page_plan_created": True,
            "new_page_files_created": False,
            "file_write_performed": False,
            "deployment_added": False,
            "provider_calls_added": False,
            "auth_added": False,
            "database_added": False,
            "approval_required": True,
        },
        "safety_flags": SAFE_FLAGS,
        "blocked_fields": BLOCKED_FIELDS,
        "next_phase_handoff": {
            "current_phase": "Phase 9F - Multi-page File Generation Plan",
            "next_phase": "Phase 9G - Generated App Preview Runner",
            "handoff_status": "approval_gated",
            "production_generation_status": "locked",
        },
    }

