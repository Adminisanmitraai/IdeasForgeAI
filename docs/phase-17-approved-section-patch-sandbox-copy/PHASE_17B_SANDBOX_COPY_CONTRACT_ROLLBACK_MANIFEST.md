# Phase 17B — Sandbox Copy Contract + Rollback Manifest

Status: Completed, not frozen.

## Purpose

Phase 17B defines the contract for creating a controlled sandbox copy and rollback manifest before any approved section patch is applied.

This phase is contract/schema only.

No sandbox copy is created.
No section patch is applied.
No generated app files are modified.
No Phase 13E sandbox files are modified.
No generated-apps/ideasforgeai-preview-v1 files are touched.
No backend generation is unlocked.
No deployment is added.
No provider calls are added.
No Supabase/auth/database/secrets are added.

## Approved Source Folder

Future copy source:

D:/APPS/IdeasForgeAI/generated-apps/_phase13e_controlled_html_css_js_generation/

## Approved Patch Proposal Source

Future patch proposal source:

D:/APPS/IdeasForgeAI/generated-apps/_phase16f_controlled_section_patch_sandbox/

## Approved Phase 17 Sandbox Copy Target

Future copy target:

D:/APPS/IdeasForgeAI/generated-apps/_phase17_controlled_section_patch_applied_copy/

## Approved Files for Future Copy

Only these app files may be copied forward:

- index.html
- styles.css
- app.js
- manifest.json
- README.md
- validation-report.md

## Approved Phase 17 Control Files

Only these Phase 17 control files may be added:

- section-patch-application-report.md
- rollback-manifest.json
- phase17-validation-report.md

## Rollback Manifest Requirements

Rollback manifest must include:

- rollback_manifest_version
- phase
- created_at
- source_folder
- patch_proposal_folder
- sandbox_copy_target
- copied_files
- original_file_hashes
- patched_file_hashes
- selected_section_id
- selected_section_type
- source_file
- start_marker
- end_marker
- patch_applied_to_copy_only
- real_generated_app_modified=false
- ideasforgeai_preview_v1_touched=false
- phase13e_sandbox_modified=false
- deployment_unlocked=false
- provider_calls_allowed=false
- database_writes_allowed=false
- secrets_allowed=false
- rollback_available=true

## Safety Rules

Phase 17B must not:
- create sandbox copy
- apply patch
- modify Phase 13E files
- modify Phase 16F files
- modify generated-apps/ideasforgeai-preview-v1
- write generated app files
- deploy
- call providers
- add Supabase/auth/database/secrets
- touch KisanMitraAI

## Future Phase 17C

Phase 17C will create the read-only source copy sandbox after this contract is frozen.

## Phase 17B Safety Confirmation

Phase 17B is contract/schema only.

No generated app files were changed.
No Phase 13E sandbox files were changed.
No Phase 16F sandbox files were changed.
generated-apps/ideasforgeai-preview-v1 was not touched.
General real generation remains locked.
Backend generation remains locked.
Deployment remains locked.
Provider calls remain locked.
Supabase/auth/database/secrets remain locked.
KisanMitraAI production was not touched.
Phase 17C was not implemented.
