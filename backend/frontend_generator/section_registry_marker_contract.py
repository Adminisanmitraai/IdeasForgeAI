from pathlib import Path


PROJECT_ROOT = Path("D:/APPS/IdeasForgeAI").resolve()

APPROVED_REFERENCE_TARGET = (
    PROJECT_ROOT
    / "generated-apps"
    / "_phase13e_controlled_html_css_js_generation"
).resolve()

ALLOWED_SECTION_TYPES = [
    "navbar",
    "hero",
    "features",
    "product_card",
    "pricing",
    "cta",
    "footer",
    "form",
    "dashboard_panel",
    "sidebar",
    "preview_card",
    "trust_section",
    "approval_section",
]

REQUIRED_SECTION_FIELDS = [
    "section_id",
    "section_name",
    "section_type",
    "page_id",
    "source_file",
    "relative_path",
    "start_marker",
    "end_marker",
    "editable_allowed",
    "regenerate_allowed",
    "validation_required",
    "approval_required",
    "rollback_required",
    "current_summary",
    "design_system_reference",
    "product_brain_reference",
    "last_validated_phase",
    "safety_flags",
]

MARKER_CONTRACT = {
    "start_marker_pattern": "<!-- IF_SECTION_START:section_id={section_id};section_type={section_type};editable=true;regenerate=true -->",
    "end_marker_pattern": "<!-- IF_SECTION_END:section_id={section_id} -->",
    "matching_section_id_required": True,
    "overlapping_sections_allowed": False,
    "nested_editable_sections_allowed": False,
}


def _locked_flags() -> dict:
    return {
        "section_registry_defined": True,
        "marker_contract_defined": True,
        "section_ui_added": False,
        "section_regeneration_allowed": False,
        "file_write_allowed": False,
        "folder_creation_allowed": False,
        "generation_allowed": False,
        "backend_generation_unlocked": False,
        "deployment_unlocked": False,
        "provider_calls_allowed": False,
        "database_writes_allowed": False,
        "secrets_allowed": False,
        "supabase_allowed": False,
        "auth_allowed": False,
    }


def get_phase16b_section_registry_marker_contract() -> dict:
    return {
        "status": "success",
        "phase": "Phase 16B - Section Registry + Marker Contract",
        "contract_schema_only": True,
        "approved_reference_target": str(APPROVED_REFERENCE_TARGET),
        "required_section_fields": REQUIRED_SECTION_FIELDS,
        "allowed_section_types": ALLOWED_SECTION_TYPES,
        "blocked_section_types": [
            "backend",
            "deployment",
            "secrets",
            "auth",
            "database",
            "supabase",
            "provider_config",
            "root_config",
            "environment_config",
            "IdeasForgeAI",
        ],
        "marker_contract": MARKER_CONTRACT,
        "blocked_targets": [
            "generated-apps/ideasforgeai-preview-v1",
            "backend/",
            "frontend/pages/",
            "frontend/shared/",
            "docs/ except phase docs",
            "root production files",
            "deployment config",
            "env/secrets files",
            "IdeasForgeAI paths",
            "any path outside D:/APPS/IdeasForgeAI",
        ],
        "next_required_phase": "Phase 16C - Section Selection UI Planning",
        **_locked_flags(),
    }

