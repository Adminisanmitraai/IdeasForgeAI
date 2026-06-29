# Phase 18B — Promotion Contract + Manifest Schema

Status: Completed, not frozen.

## Purpose

Phase 18B defines the promotion contract and manifest schema for safely promoting a validated Phase 17 patched sandbox copy into a controlled Phase 18 promoted preview folder.

This phase is contract/schema only.

No promotion happens in Phase 18B.
No generated app files are copied.
No generated app files are modified.
No deployment is added.
No provider calls are added.
No Supabase/auth/database/secrets are added.

## Approved Future Promotion Source

D:/APPS/IdeasForgeAI/generated-apps/_phase17_controlled_section_patch_applied_copy/

## Approved Future Promotion Target

D:/APPS/IdeasForgeAI/generated-apps/_phase18_promoted_section_patch_preview/

## Required Promotion Manifest Fields

A future promotion manifest must include:

- promotion_manifest_version
- phase
- created_at
- project_name
- promotion_id
- human_approval_id
- approved_by_human
- source_folder
- target_folder
- source_validation_score
- phase17f_validation_passed
- copied_files
- source_file_hashes
- promoted_file_hashes
- rollback_manifest_source
- rollback_available
- promoted_preview_route
- promoted_output_validation_required
- deployment_allowed=false
- provider_calls_allowed=false
- database_writes_allowed=false
- secrets_allowed=false
- supabase_allowed=false
- auth_allowed=false
- real_generated_app_modified=false
- ideasforgeai_preview_v1_touched=false
- kisanmitra_production_touched=false

## Approved Promoted Files

Future promotion may include only:

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

## Required Promotion Safety Gates

Future promotion must require:

- Phase 17G frozen
- Phase 17F validation score 100
- human approval true
- human approval id present
- source folder equals approved Phase 17 sandbox copy
- target folder equals approved Phase 18 promoted preview folder
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

Promotion must never write to:

- generated-apps/ideasforgeai-preview-v1
- generated-apps/_phase13e_controlled_html_css_js_generation
- generated-apps/_phase16f_controlled_section_patch_sandbox
- generated-apps/_phase17_controlled_section_patch_applied_copy
- backend/
- frontend/pages/
- frontend/shared/
- docs/ except Phase 18 docs
- root production files
- deployment config
- env/secrets files
- KisanMitraAI paths

## Future Phase 18C

Phase 18C will add the Human Promotion Approval Gate.

## Phase 18B Safety Confirmation

Phase 18B is contract/schema only.

No promotion was performed.
No generated app files were changed.
No Phase 13E sandbox files were changed.
No Phase 16F sandbox files were changed.
No Phase 17 sandbox files were changed.
generated-apps/ideasforgeai-preview-v1 was not touched.
General real generation remains locked.
Backend generation remains locked.
Deployment remains locked.
Provider calls remain locked.
Supabase/auth/database/secrets remain locked.
KisanMitraAI production was not touched.
Phase 18C was not implemented.
