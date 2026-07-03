# Phase 16D — Section Edit Prompt Contract

Status: Completed, not frozen.

## Purpose

Phase 16D defines the prompt contract for safely editing one selected section.

This phase is contract/schema only.

No section regeneration is implemented.
No selected section patch is written.
No generated app files are changed.
No backend generation is unlocked.
No deployment is added.
No provider calls are added.
No Supabase/auth/database/secrets are added.

## Why This Contract Is Needed

Before IdeasForgeAI can regenerate one section, it must know exactly what context can be sent into an edit prompt and what output is allowed back.

Without a prompt contract, the model could:
- rewrite too much
- change unrelated sections
- add unsafe code
- introduce external scripts
- add provider/database/auth/deployment logic
- break rollback safety

## Required Prompt Inputs

A future selected-section edit prompt must include:

- project_name
- generation_id
- source_phase
- human_approval_id
- approved_by_human
- selected_section_id
- selected_section_type
- selected_section_name
- source_file
- start_marker
- end_marker
- current_section_summary
- current_section_html
- user_requested_change
- design_system_reference
- product_brain_reference
- validation_required
- approval_required
- rollback_required
- deployment_allowed=false
- provider_calls_allowed=false
- database_writes_allowed=false
- secrets_allowed=false

## Allowed Prompt Scope

The prompt may ask for changes only inside:

- selected section content
- selected section copy
- selected section layout
- selected section visual polish
- selected section accessible labels
- selected section static UI behavior if approved later

## Blocked Prompt Scope

The prompt must not request:

- full app rewrite
- unrelated section changes
- backend code
- deployment config
- provider calls
- Supabase/auth/database logic
- secrets/API keys
- tracking scripts
- external scripts
- external URLs
- generated-apps/ideasforgeai-preview-v1 changes
- IdeasForgeAI changes

## Required Prompt Output Contract

Future response must return metadata only until later phases:

- status
- selected_section_id
- selected_section_type
- requested_change_summary
- proposed_patch_allowed=false
- file_write_allowed=false
- generation_allowed=false
- validation_required=true
- approval_required=true
- rollback_required=true
- next_required_phase=Phase 16E

## Future Patch Output Rules

When patching becomes allowed in later phases, output must be constrained to:

- one selected section only
- matching section_id
- matching start marker
- matching end marker
- no external scripts
- no iframe
- no API calls
- no provider/database/auth/secrets
- no deployment logic
- no IdeasForgeAI reference
- validation before write
- rollback before write

## Phase 16D Safety Confirmation

Phase 16D is contract/schema only.

No frontend UI code was changed.
No section regeneration was implemented.
No generated app files were changed.
generated-apps/ideasforgeai-preview-v1 was not touched.
General real generation remains locked.
Backend generation remains locked.
Deployment remains locked.
Provider calls remain locked.
Supabase/auth/database/secrets remain locked.
IdeasForgeAI production was not touched.
Phase 16E was not implemented.

