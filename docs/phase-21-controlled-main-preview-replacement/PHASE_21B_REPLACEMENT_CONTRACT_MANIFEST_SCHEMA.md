# Phase 21B — Replacement Contract + Manifest Schema

Status: Completed, not frozen.

## Purpose

Phase 21B defines the controlled replacement contract and manifest schema for replacing the protected main preview with the frozen Phase 20 polished frontend.

This phase is contract/schema only.

No files are copied.
No files are replaced.
No generated-apps/ideasforgeai-preview-v1 files are touched.
No Phase 20 polish sandbox files are modified.
No production deployment is performed.
No provider calls are added.
No database writes are added.
No Supabase/auth/secrets are added.
KisanMitraAI production is not touched.

## Approved Replacement Source

D:/APPS/IdeasForgeAI/generated-apps/_phase20_final_apple_like_frontend_polish/

## Protected Replacement Target

D:/APPS/IdeasForgeAI/generated-apps/ideasforgeai-preview-v1/

## Required Source Files

- index.html
- styles.css
- app.js
- manifest.json
- README.md
- phase20-polish-report.md
- phase20-validation-report.md

## Required Replacement Output Files

When replacement is later approved, the protected target should contain:

- index.html
- styles.css
- app.js
- manifest.json
- README.md
- phase20-polish-report.md
- phase20-validation-report.md
- phase21-replacement-manifest.json
- phase21-rollback-manifest.json
- phase21-replacement-report.md
- phase21-validation-report.md

## Required Approval Gates

Future replacement must require:

- Phase 20H frozen
- Phase 20G validation score 100
- Phase 20F preview route working
- Phase 21A frozen
- Phase 21B frozen
- Human replacement approval in Phase 21C
- Replacement dry-run pass in Phase 21D
- Rollback snapshot prepared in Phase 21E

## Replacement Manifest Required Fields

- replacement_manifest_version
- phase
- created_at
- project_name
- source_folder
- target_folder
- approved_by_human
- human_approval_id
- phase20h_frozen
- phase20g_validation_score
- phase20f_preview_route_working
- phase21c_approval_validated
- phase21d_dry_run_passed
- phase21e_rollback_snapshot_ready
- source_files
- target_files
- source_file_hashes
- previous_target_hashes
- replacement_file_hashes
- rollback_manifest_path
- production_replacement_allowed
- deployment_allowed
- provider_calls_allowed
- database_writes_allowed
- supabase_allowed
- auth_allowed
- secrets_allowed
- kisanmitra_production_touched

## Rollback Manifest Required Fields

- rollback_manifest_version
- created_at
- project_name
- original_target_folder
- rollback_snapshot_folder
- replacement_source_folder
- rollback_available
- original_file_hashes
- restored_file_list
- production_replacement_allowed
- deployment_allowed
- provider_calls_allowed
- database_writes_allowed
- secrets_allowed

## Blocked Paths

Phase 21 must not modify:

- backend/
- frontend/pages/
- frontend/shared/
- docs/ except Phase 21 documentation
- deployment files
- .env files
- secret files
- provider configuration
- database configuration
- Supabase/auth configuration
- KisanMitraAI paths

## Phase 21B Safety Confirmation

Phase 21B is contract/schema only.

No files were copied.
No files were replaced.
No generated-apps/ideasforgeai-preview-v1 files were touched.
No Phase 20 polish sandbox files were modified.
No production replacement was performed.
No deployment was performed.
No provider calls were made.
No database writes were made.
No Supabase/auth/secrets were added.
KisanMitraAI production was not touched.
Phase 21C was not implemented.
