# Phase 13C - Multi-File Dry-Run Validator

Status: Completed, not frozen.

## Purpose

Phase 13C adds a validation-only dry-run validator for future controlled multi-file generation before any Phase 13 generated app files can be written.

This phase does not write files, create folders, create generated apps, generate HTML/CSS/JS, call providers, deploy, add Supabase/auth/database writes/secrets, or touch KisanMitraAI production.

## Backend Validator Module

Module:

`backend/frontend_generator/multi_file_dry_run_validator.py`

Static endpoint:

`POST /api/frontend-generator/phase13c-multi-file-dry-run-validator`

The endpoint may accept JSON payloads and returns validation metadata only.

## Validation Scope

The dry-run validator checks:

- `project_name=IdeasForgeAI`
- `generation_id` format
- Target folder is inside an approved future Phase 13 generated-apps sandbox
- `generated-apps/ideasforgeai-preview-v1` is rejected
- Phase 12 sandbox folders are rejected
- `backend/`, `frontend/pages/`, `frontend/shared/`, unsafe `docs/`, root production files, deployment files, secrets/env files, database/auth/Supabase files, KisanMitraAI paths, and paths outside `D:/APPS/IdeasForgeAI` are rejected
- Allowed files exactly match the Phase 13B contract
- Blocked file list is present
- File entries match the Phase 13B schema
- Write order matches the Phase 13B contract
- Approval, human approval, backup, and rollback requirements are true
- Deployment, provider calls, database writes, secrets, Supabase, and auth remain false

## Allowed Files

Only these files are valid for future controlled multi-file generation:

- `index.html`
- `styles.css`
- `app.js`
- `manifest.json`
- `validation-report.md`
- `README.md`

## Required Write Order

1. `manifest.json`
2. `index.html`
3. `styles.css`
4. `app.js`
5. `README.md`
6. `validation-report.md`

## Return Metadata

The response includes:

- `status`
- `dry_run_only`
- `multi_file_validation_only`
- `file_write_allowed=false`
- `folder_creation_allowed=false`
- `generation_allowed=false`
- `validation_passed`
- `validation_errors`
- `validation_warnings`
- `checked_target_folder`
- `checked_allowed_files`
- `checked_file_entries`
- `checked_write_order`
- `safety_flags`
- `next_required_approval`
- `next_required_phase`

## Safety Result

Even when validation passes, Phase 13C does not unlock file writes, folder creation, generation, backend generation, deployment, provider calls, database writes, secrets, Supabase, or auth.

## Next Step

Phase 13C Freeze Review, then Phase 13D - Controlled Multi-File Sandbox Writer only after explicit approval.