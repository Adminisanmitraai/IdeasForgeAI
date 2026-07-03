
"""Phase 8G Studio-only Preview + Approval Gate engine.

This module returns safe approval gate preview metadata only.
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
    "studio_approval_gate_preview_allowed": True,
    "approval_gate_required": True,
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


def build_approval_gate_preview_response(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}
    project_name = payload.get("project_name") or "IdeasForgeAI"

    return {
        "status": "success",
        "phase": "Phase 8G - Studio Preview + Approval Gate",
        "mode": "studio_approval_gate_preview_only",
        "project_name": project_name,
        "preview_type": "approval_gate_preview",
        "approval_steps": [
            {
                "step_name": "Product Brain approval",
                "requirement": "Approved product strategy, requirements, blueprint, and planning output.",
                "status": "required_before_generation",
                "approval_required": True,
            },
            {
                "step_name": "Design System approval",
                "requirement": "Approved visual rules for typography, color, spacing, components, accessibility, and mobile-first behavior.",
                "status": "required_before_generation",
                "approval_required": True,
            },
            {
                "step_name": "Pixel-Matched placeholder approval",
                "requirement": "Approved placeholder track: upload metadata, layout, component mapping, Design System alignment, and pixel-match score preview.",
                "status": "required_before_generation",
                "approval_required": True,
            },
            {
                "step_name": "Static page preview approval",
                "requirement": "Approved single-page Studio static preview.",
                "status": "required_before_generation",
                "approval_required": True,
            },
            {
                "step_name": "Multi-page structure approval",
                "requirement": "Approved sitemap, route map, page cards, navigation flow, and user journey.",
                "status": "required_before_generation",
                "approval_required": True,
            },
            {
                "step_name": "Responsive preview approval",
                "requirement": "Approved desktop, tablet, and mobile preview behavior.",
                "status": "required_before_generation",
                "approval_required": True,
            },
            {
                "step_name": "Final generation unlock approval",
                "requirement": "Human approval required before any future generated-apps write or production output.",
                "status": "locked",
                "approval_required": True,
            },
        ],
        "readiness_summary": {
            "studio_preview_ready": True,
            "production_generation_ready": False,
            "generated_app_write_ready": False,
            "requires_human_approval": True,
            "next_phase": "Phase 8H - Frontend Generator Freeze Review",
        },
        "safety_labels": [
            "Studio approval gate preview only",
            "No generated files",
            "No production code output",
            "No generated-apps write",
            "Human approval required before generation",
        ],
        "safety_flags": SAFE_FLAGS,
        "blocked_fields": BLOCKED_FIELDS,
        "next_phase_handoff": {
            "current_phase": "Phase 8G - Studio Preview + Approval Gate",
            "next_phase": "Phase 8H - Frontend Generator Freeze Review",
            "handoff_status": "approval_gated",
            "production_generation_status": "locked",
        },
    }

