# Phase 12C - Real Generation Dry-Run Validator

Status: Completed, not frozen.

## Purpose

Phase 12C adds a validation-only dry-run gate for future real generation requests before any folder creation or file write can be considered.

The validator checks an in-memory planned generation payload and returns metadata only.

## Hard Boundary

Phase 12C does not:

- Write files
- Create folders
- Create generated apps
- Generate HTML, CSS, or JavaScript
- Unlock backend generation
- Deploy
- Call providers
- Add Supabase, authentication, database writes, or secrets
- Touch KisanMitraAI production
- Modify `generated-apps/ideasforgeai-preview-v1/`
- Implement Phase 12D

## Backend Validator

Module:

`backend/frontend_generator/real_generation_dry_run_validator.py`

Optional static/in-memory endpoint:

`POST /api/frontend-generator/real-generation-dry-run-validator`

The endpoint accepts JSON and returns validation metadata only. It does not write files, create folders, generate code, call providers, deploy, or unlock generation.

## Validation Scope

The validator checks:

- `project_name`
- `generation_id`
- `target_folder`
- Target folder is inside `D:/APPS/IdeasForgeAI/generated-apps/`
- Target folder does not reuse `generated-apps/ideasforgeai-preview-v1/`
- Target folder does not point to KisanMitraAI
- Target folder does not escape `D:/APPS/IdeasForgeAI`
- `allowed_files`
- `blocked_files`
- `file_entries` schema
- `approval_required=true`
- `backup_required=true`
- `rollback_required=true`
- `deployment_allowed=false`
- `provider_calls_allowed=false`
- `database_writes_allowed=false`
- `secrets_allowed=false`

## Blocked Paths

The validator rejects planned writes targeting:

- `backend/`
- `frontend/pages/`
- `frontend/shared/`
- `docs/` unless this is a documentation phase
- Root production files
- Deployment config files
- Secrets/env files
- KisanMitraAI paths
- Any path outside `D:/APPS/IdeasForgeAI`
- Any path outside the allowed IdeasForgeAI `generated-apps` sandbox

## Allowed Files

The initial allowed file list stays limited to the Phase 12B contract:

- `index.html`
- `styles.css`
- `app.js`
- `README.md`
- `manifest.json`
- `validation-report.md`

Any additional file requires a later approved contract update.

## Return Structure

The dry-run response includes:

- `status`
- `dry_run_only`
- `file_write_allowed`
- `folder_creation_allowed`
- `generation_allowed`
- `validation_passed`
- `validation_errors`
- `validation_warnings`
- `checked_target_folder`
- `checked_file_entries`
- `safety_flags`
- `next_required_approval`

## Safety Result

Even when validation passes, the safety flags remain locked:

- `dry_run_only=true`
- `file_write_allowed=false`
- `folder_creation_allowed=false`
- `generation_allowed=false`
- `deployment_allowed=false`
- `provider_calls_allowed=false`
- `database_writes_allowed=false`
- `secrets_allowed=false`
- `approval_required=true`
- `backup_required=true`
- `rollback_required=true`

## Next Step

Phase 12C Freeze Review, then Phase 12D only after explicit approval.
