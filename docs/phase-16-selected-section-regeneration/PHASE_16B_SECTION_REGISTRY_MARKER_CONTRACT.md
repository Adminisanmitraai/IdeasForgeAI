# Phase 16B — Section Registry + Marker Contract

Status: Completed, not frozen.

## Purpose

Phase 16B defines the section registry and marker contract required before IdeasForgeAI can safely edit or regenerate selected sections.

This phase is contract/schema only.

No generated app files are modified.
No section is regenerated.
No backend generation is unlocked.
No deployment is added.
No provider calls are added.
No Supabase/auth/database/secrets are added.

## Why Section Registry Is Needed

Selected section regeneration must know exactly:
- which section is selected
- which file owns the section
- where the section begins
- where the section ends
- whether the section is editable
- whether regeneration is allowed
- whether validation and rollback are required

Without this contract, section regeneration could accidentally rewrite too much of the app.

## Approved Future Target

Future section editing may only target an approved sandbox output after explicit approval.

Initial safe reference target:

D:/APPS/IdeasForgeAI/generated-apps/_phase13e_controlled_html_css_js_generation/

## Required Marker Format

Future generated HTML sections must use this marker format:

<!-- IF_SECTION_START:section_id=hero;section_type=hero;editable=true;regenerate=true -->
<section>
  ...
</section>
<!-- IF_SECTION_END:section_id=hero -->

Every editable section must have:
- one start marker
- one matching end marker
- matching section_id
- no overlapping sections
- no nested editable sections unless explicitly approved later

## Required Section Registry Fields

Each section registry entry must include:

- section_id
- section_name
- section_type
- page_id
- source_file
- relative_path
- start_marker
- end_marker
- editable_allowed
- regenerate_allowed
- validation_required
- approval_required
- rollback_required
- current_summary
- design_system_reference
- product_brain_reference
- last_validated_phase
- safety_flags

## Allowed Section Types

Allowed future section types:
- navbar
- hero
- features
- product_card
- pricing
- cta
- footer
- form
- dashboard_panel
- sidebar
- preview_card
- trust_section
- approval_section

## Blocked Section Types

Blocked:
- backend
- deployment
- secrets
- auth
- database
- Supabase
- provider_config
- root_config
- environment_config
- IdeasForgeAI

## Safety Rules

Section registry must:
- never allow editing outside approved sandbox files
- never target generated-apps/ideasforgeai-preview-v1
- never target backend files
- never target frontend/pages source files
- never target frontend/shared source files
- never target docs except phase docs
- never target root production files
- never target secrets/env files
- never target deployment files
- never target IdeasForgeAI folders
- never accept arbitrary absolute paths
- always require validation
- always require approval
- always require rollback support

## Future Phase 16C

Phase 16C will plan the section selection UI.

Phase 16B does not add selection UI.

## Phase 16B Safety Confirmation

Phase 16B is contract/schema only.

No generated app files were changed.
generated-apps/ideasforgeai-preview-v1 was not touched.
General real generation remains locked.
Backend generation remains locked.
Deployment remains locked.
Provider calls remain locked.
Supabase/auth/database/secrets remain locked.
IdeasForgeAI production was not touched.
Phase 16C was not implemented.

