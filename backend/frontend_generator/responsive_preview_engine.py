
"""Phase 8E Studio-only responsive mobile/desktop preview engine.

This module returns safe responsive preview metadata only.
It does not generate HTML/CSS/React, does not write files,
and does not create generated apps.
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
    "responsive_preview_allowed": True,
    "desktop_preview_allowed": True,
    "tablet_preview_allowed": True,
    "mobile_preview_allowed": True,
    "production_frontend_generation_allowed": False,
    "html_output_allowed": False,
    "css_output_allowed": False,
    "react_output_allowed": False,
    "generated_app_write_allowed": False,
    "generated_files_allowed": False,
    "deployment_allowed": False,
    "provider_calls_allowed": False,
    "database_writes_allowed": False,
    "supabase_allowed": False,
    "auth_allowed": False,
    "approval_required": True,
}


def build_responsive_preview_response(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}
    project_name = payload.get("project_name") or "IdeasForgeAI"

    return {
        "status": "success",
        "phase": "Phase 8E - Responsive Mobile/Desktop Preview",
        "mode": "studio_responsive_preview_only",
        "project_name": project_name,
        "preview_type": "responsive_mobile_desktop_preview",
        "viewport_previews": [
            {
                "viewport_name": "Desktop Preview",
                "viewport_size": "1440px",
                "layout_behavior": "Wide hero, three-column cards, full navigation, roomy spacing.",
                "preview_status": "studio_preview_only",
                "approval_required": True,
            },
            {
                "viewport_name": "Tablet Preview",
                "viewport_size": "834px",
                "layout_behavior": "Two-column cards, condensed navigation, balanced spacing.",
                "preview_status": "studio_preview_only",
                "approval_required": True,
            },
            {
                "viewport_name": "Mobile Preview",
                "viewport_size": "390px",
                "layout_behavior": "Single-column flow, compact navigation, thumb-friendly CTA placement.",
                "preview_status": "studio_preview_only",
                "approval_required": True,
            },
        ],
        "responsive_rules": [
            "Mobile-first layout planning",
            "Desktop, tablet, and mobile preview surfaces",
            "No production CSS generated",
            "No generated files",
            "Design System must control spacing, typography, and component behavior",
            "Approval required before future production generation",
        ],
        "design_system_dependency": "Responsive preview must follow Phase 6 Design System rules before any future generated output.",
        "approval_gate": {
            "approval_required": True,
            "approval_status": "required_before_generation",
            "message": "Approve responsive preview behavior before any future production generation step.",
        },
        "safety_labels": [
            "Responsive preview only",
            "Desktop / tablet / mobile preview",
            "No generated files",
            "No production code output",
            "No generated-apps write",
            "Approval required before generation",
        ],
        "safety_flags": SAFE_FLAGS,
        "blocked_fields": BLOCKED_FIELDS,
        "next_phase_handoff": {
            "current_phase": "Phase 8E - Responsive Mobile/Desktop Preview",
            "next_phase": "Phase 8F - Design System Enforcement Preview",
            "handoff_status": "approval_gated",
            "production_generation_status": "locked",
        },
    }
