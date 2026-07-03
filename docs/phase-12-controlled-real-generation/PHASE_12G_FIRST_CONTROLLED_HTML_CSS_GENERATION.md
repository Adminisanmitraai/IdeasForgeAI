# Phase 12G - First Controlled HTML/CSS Generation

Status: Completed, not frozen.

## Purpose

Phase 12G creates the first controlled static HTML/CSS output in a dedicated sandbox folder after the dry-run, approval, backup, and rollback gates.

This is not production generation, not deployment, not provider-based generation, and not full app generation.

## Approved Target Folder

Only this folder is allowed:

`D:/APPS/IdeasForgeAI/generated-apps/_phase12g_controlled_html_css_generation/`

## Allowed Files

Only these files may be written:

- `index.html`
- `styles.css`
- `manifest.json`
- `validation-report.md`

Blocked files include `app.js`, backend files, deployment files, env/secrets, database/auth/Supabase files, and all files outside the Phase 12G sandbox folder.

## Backend Module

Module:

`backend/frontend_generator/controlled_html_css_generation.py`

Optional endpoint:

`POST /api/frontend-generator/phase12g-controlled-html-css-generation`

## Required Approval Payload

The endpoint requires:

- `project_name=IdeasForgeAI`
- `human_approval_id` present
- `approved_by_human=true`
- `dry_run_validation_passed=true`
- `backup_required=true`
- `rollback_required=true`
- `source_phase=Phase 12G`
- `deployment_allowed=false`
- `provider_calls_allowed=false`
- `database_writes_allowed=false`
- `secrets_allowed=false`

## Content Safety Rules

The generated page is static and safe:

- No external scripts
- No provider calls
- No API keys
- No tracking scripts
- No deployment scripts
- No iframe
- No database/auth/Supabase logic
- No IdeasForgeAI connection

## Safety Locks

The endpoint returns:

- `real_generation_unlocked=false`
- `backend_generation_unlocked=false`
- `deployment_unlocked=false`
- `provider_calls_allowed=false`
- `database_writes_allowed=false`
- `secrets_allowed=false`
- `next_required_phase=Phase 12H`

## Next Step

Phase 12G Freeze Review, then Phase 12H only after explicit approval.
