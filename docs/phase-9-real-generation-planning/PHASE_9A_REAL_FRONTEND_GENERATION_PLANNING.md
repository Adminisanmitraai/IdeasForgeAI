
# Phase 9A - Real Frontend Generation Planning & Safety Unlock Architecture

Status: Completed as planning-only.

## Purpose

Phase 9A starts the real generation planning track after the Phase 8 preview track was frozen.

This phase does not generate production files. It defines how future real frontend generation should be safely unlocked, reviewed, executed, and validated.

## What Phase 9A does

Phase 9A defines:

1. Real frontend generation architecture
2. Safe generation unlock gates
3. Required human approvals
4. Allowed future generated output types
5. File-writing safety rules
6. Generated app folder rules
7. HTML/CSS/React generation boundaries
8. Design System enforcement requirements
9. Product Brain dependency requirements
10. Pixel-Matched placeholder dependency requirements
11. Validation requirements
12. Rollback rules
13. Future Phase 9B to 9H roadmap

## What Phase 9A does not do

Phase 9A does not:

- Generate HTML
- Generate CSS
- Generate React
- Create generated app files
- Write to generated-apps/
- Add download/export behavior
- Deploy anything
- Add Supabase
- Add auth
- Add database writes
- Call providers
- Add secrets
- Touch KisanMitraAI production

## Required source dependencies before generation

Future real generation must depend on:

- Phase 5 Product Brain approved output
- Phase 6 Design System approved output
- Phase 7 Pixel-Matched placeholder track
- Phase 8 frontend preview track
- Human approval gate
- Safe target app folder
- Rollback-safe generated output plan

## Future real generation outputs

Future phases may eventually create:

- single-page HTML preview files
- CSS files
- vanilla JS files
- React components
- multi-page route structure
- asset manifest
- app README
- validation report

But Phase 9A does not create these.

## Generation unlock gates

Before any future file write:

1. User explicitly approves generation.
2. Target generated app folder is defined.
3. Existing generated app files are backed up or protected.
4. Design System enforcement is checked.
5. Product Brain requirements are checked.
6. Phase 8 preview approval is checked.
7. No production deployment is triggered.
8. No provider call is made unless separately approved.
9. No secrets are written.
10. Rollback notes are created.

## Safety locks in Phase 9A

- real_frontend_generation_planning_allowed=true
- production_frontend_generation_allowed=false
- html_generation_allowed=false
- css_generation_allowed=false
- react_generation_allowed=false
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

## Future roadmap

- Phase 9A - Real Frontend Generation Planning & Safety Unlock Architecture
- Phase 9B - Generation Target Folder Contract
- Phase 9C - Single Page File Write Dry Run
- Phase 9D - Single Page Real HTML/CSS Preview File Generation
- Phase 9E - Design System Enforcement Validation
- Phase 9F - Multi-page File Generation Plan
- Phase 9G - Generated App Preview Runner
- Phase 9H - Real Frontend Generation Freeze Review

## Next step

Phase 9B - Generation Target Folder Contract, only after Phase 9A freeze review.
