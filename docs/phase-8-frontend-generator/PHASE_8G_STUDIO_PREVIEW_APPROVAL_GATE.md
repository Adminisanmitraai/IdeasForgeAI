
# Phase 8G - Studio Preview + Approval Gate

Status: Completed as Studio-only preview.

## Purpose

Phase 8G adds the final Studio preview approval gate before any future production frontend generation step.

It clearly shows that the preview stack may be ready, but generation remains locked until human approval and a future explicit generation phase.

## Scope

Phase 8G is preview-only.

It does not generate production HTML, CSS, React, or generated app files.

## Approval gates

- Product Brain approval
- Design System approval
- Pixel-Matched placeholder approval
- Static page preview approval
- Multi-page structure approval
- Responsive preview approval
- Final generation unlock approval

## Safety labels

- Studio approval gate preview only
- No generated files
- No production code output
- No generated-apps write
- Human approval required before generation

## Safety locks

- studio_approval_gate_preview_allowed=true
- approval_gate_required=true
- production_frontend_generation_allowed=false
- html_output_allowed=false
- css_output_allowed=false
- react_output_allowed=false
- generated_app_write_allowed=false
- generated_files_allowed=false
- deployment_allowed=false
- provider_calls_allowed=false
- database_writes_allowed=false
- supabase_allowed=false
- auth_allowed=false
- approval_required=true

## Blocked fields

- html_output
- css_output
- react_output
- generated_files
- generated_app_path
- file_write_request
- deploy_request
- provider_prompt
- secret_value
- database_write
- supabase_config
- auth_config

## Next step

Phase 8G Freeze Review, then Phase 8H - Frontend Generator Freeze Review.

