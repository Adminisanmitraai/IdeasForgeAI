
"""Phase 8F Studio-only Design System Enforcement Preview engine.

This module returns safe Design System enforcement preview metadata only.
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
    "design_system_enforcement_preview_allowed": True,
    "design_tokens_preview_allowed": True,
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


def build_design_system_enforcement_preview_response(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}
    project_name = payload.get("project_name") or "IdeasForgeAI"

    return {
        "status": "success",
        "phase": "Phase 8F - Design System Enforcement Preview",
        "mode": "studio_design_system_enforcement_preview_only",
        "project_name": project_name,
        "preview_type": "design_system_enforcement_preview",
        "enforcement_items": [
            {
                "rule_area": "Typography System",
                "design_rule": "Use approved type scale, strong hierarchy, large hero headline, readable body text.",
                "preview_status": "enforced_in_preview_only",
                "premium_effect": "Apple-like clarity and editorial hierarchy.",
                "approval_required": True,
            },
            {
                "rule_area": "Color Tokens",
                "design_rule": "Use approved brand tokens, soft surface colors, accessible contrast, restrained accent usage.",
                "preview_status": "enforced_in_preview_only",
                "premium_effect": "Consistent brand feel without visual noise.",
                "approval_required": True,
            },
            {
                "rule_area": "Spacing Scale",
                "design_rule": "Use consistent spacing rhythm, generous whitespace, and grouped sections.",
                "preview_status": "enforced_in_preview_only",
                "premium_effect": "More premium, calm, and professional layout.",
                "approval_required": True,
            },
            {
                "rule_area": "Component System",
                "design_rule": "Use reusable cards, badges, buttons, panels, device frames, and approval states.",
                "preview_status": "enforced_in_preview_only",
                "premium_effect": "Reusable product-grade interface patterns.",
                "approval_required": True,
            },
            {
                "rule_area": "Radius and Shadows",
                "design_rule": "Use soft radius, subtle elevation, and layered depth without heavy effects.",
                "preview_status": "enforced_in_preview_only",
                "premium_effect": "Modern Apple-like surfaces and depth.",
                "approval_required": True,
            },
            {
                "rule_area": "Accessibility",
                "design_rule": "Keep readable text, clear focus states, contrast, semantic structure, and touch targets.",
                "preview_status": "enforced_in_preview_only",
                "premium_effect": "Professional UI that remains usable and trustworthy.",
                "approval_required": True,
            },
            {
                "rule_area": "Mobile-first Behavior",
                "design_rule": "Prioritize single-column mobile flow, thumb-friendly controls, and adaptive cards.",
                "preview_status": "enforced_in_preview_only",
                "premium_effect": "App-like responsive experience.",
                "approval_required": True,
            },
            {
                "rule_area": "Approval Gate",
                "design_rule": "No production output until preview and design rules are approved.",
                "preview_status": "locked",
                "premium_effect": "Prevents low-quality accidental generation.",
                "approval_required": True,
            },
        ],
        "quality_bars": [
            {"label": "Visual hierarchy", "placeholder_score": "Preview ready", "status": "approval_required"},
            {"label": "Design consistency", "placeholder_score": "Preview ready", "status": "approval_required"},
            {"label": "Responsive discipline", "placeholder_score": "Preview ready", "status": "approval_required"},
            {"label": "Accessibility readiness", "placeholder_score": "Preview ready", "status": "approval_required"},
        ],
        "safety_labels": [
            "Design System enforcement preview only",
            "No generated files",
            "No production code output",
            "No generated-apps write",
            "Approval required before generation",
        ],
        "approval_gate": {
            "approval_required": True,
            "approval_status": "required_before_generation",
            "message": "Approve Design System enforcement before any future production generation step.",
        },
        "safety_flags": SAFE_FLAGS,
        "blocked_fields": BLOCKED_FIELDS,
        "next_phase_handoff": {
            "current_phase": "Phase 8F - Design System Enforcement Preview",
            "next_phase": "Phase 8G - Studio Preview + Approval Gate",
            "handoff_status": "approval_gated",
            "production_generation_status": "locked",
        },
    }
