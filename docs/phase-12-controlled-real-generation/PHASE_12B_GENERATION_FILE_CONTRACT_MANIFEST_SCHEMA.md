# Phase 12B - Generation File Contract + Manifest Schema

Status: Completed, not frozen.

## Purpose

Phase 12B defines the exact future file generation contract and generated app manifest schema before any real generated file writes are allowed.

This phase is contract/schema/documentation only.

## Hard Boundary

Phase 12B does not:

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
- Implement Phase 12C

## Static Backend Contract

Static schema-only endpoint:

`POST /api/frontend-generator/generation-file-contract`

The endpoint returns contract metadata only. It must not accept or return real generated file contents. It must not write files, create folders, or unlock generation.

Schema-only module:

`backend/frontend_generator/generation_file_contract_schema.py`

## Future Manifest Schema

Required manifest fields:

1. `project_name`
2. `generation_id`
3. `target_folder`
4. `generated_at`
5. `generation_mode`
6. `human_approval_id`
7. `source_phase`
8. `design_system_version`
9. `product_brain_reference`
10. `workspace_reference`
11. `allowed_files`
12. `blocked_files`
13. `file_entries`
14. `safety_flags`
15. `validation_required`
16. `backup_required`
17. `rollback_required`
18. `deployment_allowed`
19. `provider_calls_allowed`
20. `database_writes_allowed`
21. `secrets_allowed`

## File Entry Schema

Each future file entry must include:

- `file_name`
- `relative_path`
- `file_type`
- `purpose`
- `write_status`
- `approval_required`
- `validation_required`
- `rollback_required`
- `allowed_to_overwrite`
- `checksum_placeholder`
- `generated_by_phase`

## Allowed Future Files

Only these future files are allowed by the initial contract:

- `index.html`
- `styles.css`
- `app.js`
- `README.md`
- `manifest.json`
- `validation-report.md`

Any additional file requires a later approved contract update.

## Blocked Files And Locations

Blocked:

- `backend/`
- `frontend/pages/`
- `frontend/shared/`
- `docs/` except documentation phases
- Root production files
- Deployment config
- Secrets/env files
- KisanMitraAI folders
- Any folder outside `D:/APPS/IdeasForgeAI`
- Generated-apps existing folders unless explicitly approved

## Safety Flags

Safety flags must remain:

- `generation_file_contract_defined=true`
- `manifest_schema_defined=true`
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

## Approval Rules

Future generation cannot write files until a human explicitly approves:

- Target folder
- Allowed file list
- Manifest schema
- Dry-run report
- Backup requirement
- Rollback requirement
- Validation requirement
- First write scope

## Future Manifest Example Shape

```json
{
  "project_name": "IdeasForgeAI",
  "generation_id": "future-approved-generation-id",
  "target_folder": "generated-apps/future-approved-folder/",
  "generated_at": "future-approved-timestamp",
  "generation_mode": "dry_run",
  "human_approval_id": "approval-required",
  "source_phase": "future-approved-phase",
  "design_system_version": "Phase 6 Design System v1.0",
  "product_brain_reference": "Phase 5 Product Brain approved output",
  "workspace_reference": "Phase 11 Builder Workspace frozen output",
  "allowed_files": ["index.html", "styles.css", "app.js", "README.md", "manifest.json", "validation-report.md"],
  "blocked_files": ["backend/", "frontend/pages/", "secrets/env files"],
  "file_entries": [],
  "safety_flags": {},
  "validation_required": true,
  "backup_required": true,
  "rollback_required": true,
  "deployment_allowed": false,
  "provider_calls_allowed": false,
  "database_writes_allowed": false,
  "secrets_allowed": false
}
```

## Phase 12C Status

Phase 12C - Real Generation Dry-Run Validator is not implemented.

## Next Step

Phase 12B Freeze Review, then Phase 12C only after explicit approval.
