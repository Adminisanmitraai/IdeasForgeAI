# Phase 13B - Multi-File Contract + Manifest Upgrade

Status: Completed, not frozen.

## Purpose

Phase 13B upgrades the Phase 12 single/limited generation contract into a Phase 13 controlled multi-file generation contract for future app outputs.

This phase is schema/contract work only. It does not write files, create folders, create generated apps, generate HTML/CSS/JS, call providers, deploy, add Supabase/auth/database writes/secrets, or touch IdeasForgeAI production.

## Backend Schema Module

Module:

`backend/frontend_generator/multi_file_generation_contract_schema.py`

Static endpoint:

`POST /api/frontend-generator/phase13b-multi-file-contract`

The endpoint returns static contract/schema metadata only. It must not accept or return generated file contents and must not unlock generation.

## Phase 13 Multi-File Manifest Schema

Required manifest fields:

1. `project_name`
2. `generation_id`
3. `target_folder`
4. `generation_mode`
5. `source_phase`
6. `human_approval_id`
7. `approved_by_human`
8. `dry_run_validation_passed`
9. `backup_required`
10. `rollback_required`
11. `manifest_version`
12. `design_system_version`
13. `product_brain_reference`
14. `workspace_reference`
15. `allowed_files`
16. `blocked_files`
17. `file_entries`
18. `write_order`
19. `validation_rules`
20. `safety_flags`
21. `rollback_plan`
22. `preview_runner_allowed`
23. `deployment_allowed`
24. `provider_calls_allowed`
25. `database_writes_allowed`
26. `secrets_allowed`
27. `next_required_phase`

## Allowed Future Files

Only these future files are allowed by the initial Phase 13B contract:

- `index.html`
- `styles.css`
- `app.js`
- `manifest.json`
- `validation-report.md`
- `README.md`

Any additional file requires a later approved contract update.

## File Entry Schema

Each file entry must include:

- `file_name`
- `relative_path`
- `file_type`
- `purpose`
- `write_status`
- `required`
- `approval_required`
- `validation_required`
- `backup_required`
- `rollback_required`
- `allowed_to_overwrite`
- `checksum_placeholder`
- `dependency_order`
- `generated_by_phase`

## Required Write Order

1. `manifest.json`
2. `index.html`
3. `styles.css`
4. `app.js`
5. `README.md`
6. `validation-report.md`

## Blocked Files And Locations

Blocked targets include:

- `backend/`
- `frontend/pages/`
- `frontend/shared/`
- `docs/` except documentation phases
- Root production files
- Deployment config files
- `.env` or secrets files
- Database/auth/Supabase files
- IdeasForgeAI folders
- Any path outside `D:/APPS/IdeasForgeAI`
- `generated-apps/ideasforgeai-preview-v1` unless explicitly approved in a later phase
- Phase 12 sandbox folders

## Safety Flags

Safety flags must remain:

- `multi_file_contract_defined=true`
- `manifest_schema_upgraded=true`
- `file_write_allowed=false`
- `folder_creation_allowed=false`
- `generated_app_write_allowed=false`
- `html_generation_allowed=false`
- `css_generation_allowed=false`
- `js_generation_allowed=false`
- `backend_generation_allowed=false`
- `deployment_allowed=false`
- `provider_calls_allowed=false`
- `database_writes_allowed=false`
- `supabase_allowed=false`
- `auth_allowed=false`
- `secrets_allowed=false`
- `approval_required=true`

## Next Step

Phase 13B Freeze Review, then Phase 13C - Multi-File Dry-Run Validator only after explicit approval.
