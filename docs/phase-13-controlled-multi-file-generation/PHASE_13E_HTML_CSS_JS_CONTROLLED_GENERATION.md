# Phase 13E - HTML/CSS/JS Controlled Generation

Status: Completed, not frozen.

Phase 13E creates the first controlled multi-file frontend output that includes HTML, CSS, and safe static JavaScript. This phase is a sandbox generation test only. It is not production generation, not deployment, not provider-based generation, and not a general app generation unlock.

## Approved Target

The generator may create and write only this folder:

`D:/APPS/IdeasForgeAI/generated-apps/_phase13e_controlled_html_css_js_generation/`

It must not write to `generated-apps/ideasforgeai-preview-v1`, Phase 12 sandbox folders, the Phase 13D sandbox folder, backend files, frontend files, docs, root production files, deployment config, secrets/env files, IdeasForgeAI paths, or any path outside `D:/APPS/IdeasForgeAI`.

## Approved Files and Write Order

1. `manifest.json`
2. `index.html`
3. `styles.css`
4. `app.js`
5. `README.md`
6. `validation-report.md`

No other files or subfolders are allowed in the Phase 13E sandbox folder.

## Generated App Concept

The static sandbox app is named `IdeasForgeAI Controlled App Preview`.

It includes:

- Hero title: IdeasForgeAI Controlled App Preview
- Subtitle: First approval-gated HTML/CSS/JS output
- Safety badges for controlled sandbox, no deployment, no provider calls, no database writes, and no secrets
- A static product card area
- A static generated-page preview area
- One safe local-only JavaScript interaction that toggles a visual preview state and shows `Preview check passed.`

## Required Approval Payload

The generator requires all of the following before it writes:

- `project_name = IdeasForgeAI`
- `human_approval_id` present
- `approved_by_human = true`
- `dry_run_validation_passed = true`
- `backup_required = true`
- `rollback_required = true`
- `source_phase = Phase 13E`
- `target_folder` exactly equals the approved Phase 13E sandbox folder
- `deployment_allowed = false`
- `provider_calls_allowed = false`
- `database_writes_allowed = false`
- `secrets_allowed = false`
- `supabase_allowed = false`
- `auth_allowed = false`

Payload fields containing arbitrary generated content, deployment requests, provider prompts, secret values, database writes, Supabase config, auth config, API keys, tracking scripts, or external URLs are rejected.

## Static Content Limits

The generated files follow these limits:

- No external scripts.
- No external CSS imports.
- No external URLs.
- No iframe.
- No API calls.
- No fetch or XMLHttpRequest.
- No imports.
- No localStorage or sessionStorage.
- No API keys or tracking scripts.
- No deployment scripts.
- No database/auth/Supabase logic.
- No IdeasForgeAI reference.

## Endpoint

`POST /api/frontend-generator/phase13e-controlled-html-css-js-generation`

The endpoint returns metadata about the controlled sandbox generation result:

- `status`
- `controlled_html_css_js_generation_only`
- `files_written`
- `write_order_used`
- `target_folder`
- `manifest_path`
- `validation_report_path`
- locked safety flags
- `next_required_phase = Phase 13F`

## Safety Outcome

Phase 13E proves a controlled static HTML/CSS/JS output can be created inside a dedicated sandbox folder after explicit approval and dry-run validation. It does not unlock general real generation, backend generation, deployment, provider calls, Supabase, authentication, database writes, or secrets.

Phase 13F remains the next approval-gated phase and is not implemented here.
