
"""Phase 9G generated app preview runner engine.

Local preview runner only.
No generated app file writes.
No new page generation.
No deployment.
"""

from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[2]
TARGET_FOLDER = ROOT / "generated-apps" / "ideasforgeai-preview-v1"
TARGET_FOLDER_LABEL = "generated-apps/ideasforgeai-preview-v1/"
PREVIEW_URL = "http://127.0.0.1:8100/api/frontend-generator/generated-app-preview-runner/index.html"

REQUIRED_FILES: List[str] = [
    "index.html",
    "styles.css",
    "app.js",
    "README.md",
    "validation-report.md",
]

SAFE_FLAGS: Dict[str, bool] = {
    "generated_app_preview_runner_allowed": True,
    "existing_preview_folder_required": True,
    "new_page_files_created": False,
    "generated_app_write_allowed": False,
    "production_frontend_generation_allowed": False,
    "html_generation_allowed": False,
    "css_generation_allowed": False,
    "react_generation_allowed": False,
    "deployment_allowed": False,
    "provider_calls_allowed": False,
    "database_writes_allowed": False,
    "supabase_allowed": False,
    "auth_allowed": False,
    "approval_required": True,
}


def build_generated_app_preview_runner_response(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}
    project_name = payload.get("project_name") or "IdeasForgeAI"

    existing_files = [name for name in REQUIRED_FILES if (TARGET_FOLDER / name).exists()]
    missing_files = [name for name in REQUIRED_FILES if not (TARGET_FOLDER / name).exists()]

    return {
        "status": "success" if not missing_files else "blocked",
        "phase": "Phase 9G - Generated App Preview Runner",
        "mode": "local_preview_runner_only",
        "project_name": project_name,
        "target_folder": TARGET_FOLDER_LABEL,
        "preview_url": PREVIEW_URL,
        "runner_summary": {
            "preview_folder_exists": TARGET_FOLDER.exists(),
            "existing_files": existing_files,
            "missing_files": missing_files,
            "new_page_files_created": False,
            "generated_app_write_performed": False,
            "deployment_added": False,
            "provider_calls_added": False,
            "approval_required": True,
        },
        "safety_flags": SAFE_FLAGS,
        "next_phase_handoff": {
            "current_phase": "Phase 9G - Generated App Preview Runner",
            "next_phase": "Phase 9H - Real Frontend Generation Freeze Review",
            "handoff_status": "approval_gated",
            "deployment_status": "locked",
        },
    }
