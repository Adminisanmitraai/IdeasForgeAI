# Phase 19B — Main Preview Candidate Contract + Manifest Schema

Status: Completed, not frozen.

## Purpose

Phase 19B defines the contract and manifest schema for promoting a validated Phase 18 promoted preview into a controlled main preview candidate folder.

This phase is contract/schema only.

No candidate folder is created.
No files are copied.
No files are modified.
No generated-apps/ideasforgeai-preview-v1 files are touched.
No deployment is added.
No backend generation is unlocked.
No provider calls are added.
No Supabase/auth/database/secrets are added.

## Approved Future Candidate Source

D:/APPS/IdeasForgeAI/generated-apps/_phase18_promoted_section_patch_preview/

## Approved Future Candidate Target

D:/APPS/IdeasForgeAI/generated-apps/_phase19_main_preview_candidate/

## Required Candidate Manifest Fields

A future candidate manifest must include:

- candidate_manifest_version
- phase
- created_at
- project_name
- candidate_id
- human_approval_id
- approved_by_human
- source_folder
- target_folder
- source_validation_score
- phase18g_validation_passed
- phase18h_frozen
- copied_files
- source_file_hashes
- candidate_file_hashes
- promotion_manifest_source
- rollback_manifest_source
- rollback_available
- candidate_preview_route
- candidate_output_validation_required
- production_replacement_allowed=false
- deployment_allowed=false
- provider_calls_allowed=false
- database_writes_allowed=false
- secrets_allowed=false
- supabase_allowed=false
- auth_allowed=false
- real_generated_app_modified=false
- ideasforgeai_preview_v1_touched=false
- kisanmitra_production_touched=false

## Approved Candidate Files

Future candidate creation may include only:

- index.html
- styles.css
- app.js
- manifest.json
- README.md
- validation-report.md
- rollback-manifest.json
- phase17-validation-report.md
- section-patch-application-report.md
- promotion-manifest.json
- phase18-promotion-report.md
- phase18-validation-report.md
- candidate-manifest.json
- phase19-candidate-report.md
- phase19-validation-report.md

## Required Candidate Safety Gates

Future candidate creation must require:

- Phase 18H frozen
- Phase 18G validation score 100
- Phase 18F promoted preview route working
- human approval true
- human approval id present
- source folder equals approved Phase 18 promoted preview folder
- target folder equals approved Phase 19 main preview candidate folder
- no generated-apps/ideasforgeai-preview-v1 write
- no backend write
- no Studio V3 source write
- no deployment write
- no provider call
- no database write
- no secrets
- no Supabase/auth unlock
- no KisanMitraAI touch

## Blocked Targets

Candidate creation must never write to:

- generated-apps/ideasforgeai-preview-v1
- generated-apps/_phase13e_controlled_html_css_js_generation
- generated-apps/_phase16f_controlled_section_patch_sandbox
- generated-apps/_phase17_controlled_section_patch_applied_copy
- generated-apps/_phase18_promoted_section_patch_preview
- backend/
- frontend/pages/
- frontend/shared/
- docs/ except Phase 19 docs
- root production files
- deployment config
- env/secrets files
- KisanMitraAI paths

## Future Phase 19C

Phase 19C will add the Human Candidate Approval Gate.

## Phase 19B Safety Confirmation

Phase 19B is contract/schema only.

No candidate folder was created.
No candidate manifest was created.
No files were copied.
No generated app files were changed.
No Phase 13E sandbox files were changed.
No Phase 16F sandbox files were changed.
No Phase 17 sandbox files were changed.
No Phase 18 promoted files were changed.
generated-apps/ideasforgeai-preview-v1 was not touched.
General real generation remains locked.
Backend generation remains locked.
Deployment remains locked.
Provider calls remain locked.
Supabase/auth/database/secrets remain locked.
KisanMitraAI production was not touched.
Phase 19C was not implemented.
