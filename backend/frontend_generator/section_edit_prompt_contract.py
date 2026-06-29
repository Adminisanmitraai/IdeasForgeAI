def _locked_flags() -> dict:
    return {
        "section_edit_prompt_contract_defined": True,
        "section_patch_allowed": False,
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


REQUIRED_PROMPT_INPUTS = [
    "project_name",
    "generation_id",
    "source_phase",
    "human_approval_id",
    "approved_by_human",
    "selected_section_id",
    "selected_section_type",
    "selected_section_name",
    "source_file",
    "start_marker",
    "end_marker",
    "current_section_summary",
    "current_section_html",
    "user_requested_change",
    "design_system_reference",
    "product_brain_reference",
    "validation_required",
    "approval_required",
    "rollback_required",
    "deployment_allowed",
    "provider_calls_allowed",
    "database_writes_allowed",
    "secrets_allowed",
]


ALLOWED_PROMPT_SCOPE = [
    "selected section content",
    "selected section copy",
    "selected section layout",
    "selected section visual polish",
    "selected section accessible labels",
    "selected section static UI behavior after future approval",
]


BLOCKED_PROMPT_SCOPE = [
    "full app rewrite",
    "unrelated section changes",
    "backend code",
    "deployment config",
    "provider calls",
    "Supabase/auth/database logic",
    "secrets/API keys",
    "tracking scripts",
    "external scripts",
    "external URLs",
    "generated-apps/ideasforgeai-preview-v1 changes",
    "KisanMitraAI changes",
]


def get_phase16d_section_edit_prompt_contract() -> dict:
    return {
        "status": "success",
        "phase": "Phase 16D - Section Edit Prompt Contract",
        "contract_schema_only": True,
        "required_prompt_inputs": REQUIRED_PROMPT_INPUTS,
        "allowed_prompt_scope": ALLOWED_PROMPT_SCOPE,
        "blocked_prompt_scope": BLOCKED_PROMPT_SCOPE,
        "required_output_contract": {
            "status": "metadata_only",
            "selected_section_id": "required",
            "selected_section_type": "required",
            "requested_change_summary": "required",
            "proposed_patch_allowed": False,
            "file_write_allowed": False,
            "generation_allowed": False,
            "validation_required": True,
            "approval_required": True,
            "rollback_required": True,
            "next_required_phase": "Phase 16E - Section Regeneration Dry-Run Validator",
        },
        "future_patch_rules": [
            "one selected section only",
            "matching section_id required",
            "matching start marker required",
            "matching end marker required",
            "no external scripts",
            "no iframe",
            "no API calls",
            "no provider/database/auth/secrets",
            "no deployment logic",
            "no KisanMitraAI reference",
            "validation before write",
            "rollback before write",
        ],
        "next_required_phase": "Phase 16E - Section Regeneration Dry-Run Validator",
        **_locked_flags(),
    }
