# Phase 13D - Controlled Multi-File Sandbox Writer

Status: Completed, not frozen.

Phase 13D adds the first controlled multi-file sandbox writer for the Phase 13 track. This phase is a sandbox proof only. It does not unlock general real generation, backend generation, deployment, provider calls, Supabase, authentication, database writes, or secrets.

## Approved Target

The writer may create and write only this folder:

`D:/APPS/IdeasForgeAI/generated-apps/_phase13d_multi_file_write_sandbox/`

It must not write to `generated-apps/ideasforgeai-preview-v1`, Phase 12 sandbox folders, backend files, frontend files, docs, root production files, deployment config, secrets/env files, IdeasForgeAI paths, or any path outside `D:/APPS/IdeasForgeAI`.

## Approved Files and Write Order

1. `manifest.json`
2. `index.html`
3. `styles.css`
4. `app.js`
5. `README.md`
6. `validation-report.md`

No other files or subfolders are allowed in the Phase 13D sandbox folder.

## Required Approval Payload

The writer requires all of the following before it writes:

- `project_name = IdeasForgeAI`
- `human_approval_id` present
- `approved_by_human = true`
- `dry_run_validation_passed = true`
- `backup_required = true`
- `rollback_required = true`
- `source_phase = Phase 13D`
- `target_folder` exactly equals the approved Phase 13D sandbox folder
- `deployment_allowed = false`
- `provider_calls_allowed = false`
- `database_writes_allowed = false`
- `secrets_allowed = false`
- `supabase_allowed = false`
- `auth_allowed = false`

Payload fields containing arbitrary generated content, deployment requests, provider prompts, secret values, database writes, Supabase config, or auth config are rejected.

## Static Content Limits

The written sandbox files contain static proof content only.

- `index.html` uses local `styles.css` and local `app.js` only.
- `index.html` contains no external URL, no iframe, and no IdeasForgeAI visible reference.
- `styles.css` contains no `http`, `https`, or `@import`.
- `app.js` is a local static proof script only and contains no network calls, imports, localStorage usage, provider references, Supabase references, auth references, or database calls.

## Endpoint

`POST /api/frontend-generator/phase13d-multi-file-sandbox-writer`

The endpoint returns metadata only about the controlled sandbox write result:

- `status`
- `controlled_multi_file_sandbox_only`
- `files_written`
- `write_order_used`
- `target_folder`
- `manifest_path`
- `validation_report_path`
- locked safety flags
- `next_required_phase = Phase 13E`

## Safety Outcome

Phase 13D proves that IdeasForgeAI can perform a constrained multi-file write in an approved sandbox folder after explicit approval and dry-run validation. It does not create a real generated app and does not unlock any general generation capability.

Phase 13E remains the next approval-gated phase and is not implemented here.
