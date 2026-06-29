
"""Phase 8D Studio-only multi-page app structure preview engine.

This module returns safe preview metadata only.
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
    "multi_page_preview_allowed": True,
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


def _preview_pages() -> List[Dict[str, Any]]:
    return [
        {
            "page_name": "Home / Landing Page",
            "route": "/",
            "page_type": "marketing_landing",
            "purpose": "Introduce the product, value proposition, hero CTA, trust layer, and key benefits.",
            "primary_sections": ["Top navigation", "Hero", "Feature highlights", "Trust badges", "Primary CTA"],
            "connected_navigation": ["Features", "Pricing", "Login / Signup", "Support / Contact"],
            "preview_status": "studio_preview_only",
            "approval_required": True,
        },
        {
            "page_name": "About / Product Overview",
            "route": "/about",
            "page_type": "product_story",
            "purpose": "Explain what the product does, who it serves, and why it is different.",
            "primary_sections": ["Problem", "Solution", "Product story", "Differentiators"],
            "connected_navigation": ["Home", "Features", "Support / Contact"],
            "preview_status": "studio_preview_only",
            "approval_required": True,
        },
        {
            "page_name": "Features",
            "route": "/features",
            "page_type": "feature_showcase",
            "purpose": "Show the main product modules and benefits in a structured premium layout.",
            "primary_sections": ["Feature grid", "Workflow preview", "Use cases", "CTA"],
            "connected_navigation": ["Home", "Dashboard", "Pricing"],
            "preview_status": "studio_preview_only",
            "approval_required": True,
        },
        {
            "page_name": "Dashboard",
            "route": "/dashboard",
            "page_type": "app_dashboard",
            "purpose": "Preview the logged-in control center with cards, insights, and product status.",
            "primary_sections": ["Metrics", "Recent activity", "AI recommendations", "Quick actions"],
            "connected_navigation": ["Settings", "Support / Contact"],
            "preview_status": "studio_preview_only",
            "approval_required": True,
        },
        {
            "page_name": "User Onboarding",
            "route": "/onboarding",
            "page_type": "guided_flow",
            "purpose": "Guide new users through product setup, goals, and first action.",
            "primary_sections": ["Welcome", "Goal selection", "Setup steps", "Finish CTA"],
            "connected_navigation": ["Dashboard", "Support / Contact"],
            "preview_status": "studio_preview_only",
            "approval_required": True,
        },
        {
            "page_name": "Login / Signup",
            "route": "/auth",
            "page_type": "authentication_preview",
            "purpose": "Preview future authentication entry without implementing auth.",
            "primary_sections": ["Login card", "Signup card", "Security note"],
            "connected_navigation": ["Home", "Dashboard"],
            "preview_status": "studio_preview_only_no_auth",
            "approval_required": True,
        },
        {
            "page_name": "Pricing",
            "route": "/pricing",
            "page_type": "pricing_preview",
            "purpose": "Show future plan structure, feature tiers, and upgrade CTA.",
            "primary_sections": ["Plan cards", "Feature comparison", "FAQ", "CTA"],
            "connected_navigation": ["Home", "Features", "Login / Signup"],
            "preview_status": "studio_preview_only",
            "approval_required": True,
        },
        {
            "page_name": "Settings",
            "route": "/settings",
            "page_type": "account_settings_preview",
            "purpose": "Preview future profile, workspace, language, and preferences layout.",
            "primary_sections": ["Profile", "Workspace", "Preferences", "Safety"],
            "connected_navigation": ["Dashboard", "Support / Contact"],
            "preview_status": "studio_preview_only_no_auth",
            "approval_required": True,
        },
        {
            "page_name": "Support / Contact",
            "route": "/support",
            "page_type": "support_preview",
            "purpose": "Help users contact support, read FAQs, and access help resources.",
            "primary_sections": ["Help center", "Contact card", "FAQ", "Status note"],
            "connected_navigation": ["Home", "Dashboard", "Settings"],
            "preview_status": "studio_preview_only",
            "approval_required": True,
        },
    ]


def build_multi_page_preview_response(payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}
    project_name = payload.get("project_name") or "IdeasForgeAI"

    return {
        "status": "success",
        "phase": "Phase 8D - Multi-page App Structure Preview",
        "mode": "studio_multi_page_preview_only",
        "project_name": project_name,
        "preview_type": "multi_page_app_structure",
        "sitemap": [
            "/",
            "/about",
            "/features",
            "/dashboard",
            "/onboarding",
            "/auth",
            "/pricing",
            "/settings",
            "/support",
        ],
        "pages": _preview_pages(),
        "navigation_structure": {
            "primary_navigation": ["Home", "Features", "Pricing", "Support"],
            "app_navigation": ["Dashboard", "Onboarding", "Settings"],
            "auth_navigation": ["Login / Signup"],
            "navigation_status": "preview_only",
        },
        "user_journey_flow": [
            "Visitor lands on Home",
            "Visitor reviews Features",
            "Visitor checks Pricing",
            "Visitor signs up through Login / Signup",
            "New user completes Onboarding",
            "User enters Dashboard",
            "User manages preferences in Settings",
            "User can access Support / Contact",
        ],
        "preview_sections": [
            "App sitemap",
            "Navigation structure",
            "Page cards",
            "User journey flow",
            "Responsive planning note",
            "Design System dependency",
            "Approval gate",
        ],
        "responsive_planning_note": "Future Phase 8E will preview mobile and desktop behavior. No responsive production code is generated in Phase 8D.",
        "design_system_dependency": "All future page generation must follow Phase 6 Design System rules before any production output.",
        "approval_gate": {
            "approval_required": True,
            "approval_status": "required_before_generation",
            "message": "Approve the multi-page preview structure before any future generation step.",
        },
        "safety_labels": [
            "Multi-page preview only",
            "No generated files",
            "No production code output",
            "No generated-apps write",
            "Approval required before generation",
        ],
        "safety_flags": SAFE_FLAGS,
        "blocked_fields": BLOCKED_FIELDS,
        "next_phase_handoff": {
            "current_phase": "Phase 8D - Multi-page App Structure Preview",
            "next_phase": "Phase 8E - Responsive Mobile/Desktop Preview",
            "handoff_status": "approval_gated",
            "production_generation_status": "locked",
        },
    }
