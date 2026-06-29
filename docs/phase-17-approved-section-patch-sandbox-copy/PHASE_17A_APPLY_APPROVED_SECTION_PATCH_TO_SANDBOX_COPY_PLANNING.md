# Phase 17A — Apply Approved Section Patch to Sandbox Copy Planning

Status: Completed, not frozen.

## Purpose

Phase 17A defines how IdeasForgeAI will safely apply an approved selected-section patch to a sandbox copy only.

This phase is planning only.

No section patch is applied.
No real generated app files are modified.
No Phase 13E sandbox files are modified.
No generated-apps/ideasforgeai-preview-v1 files are touched.
No backend generation is unlocked.
No deployment is added.
No provider calls are added.
No Supabase/auth/database/secrets are added.

## What Phase 16 Proved

Phase 16 proved:
- selected-section edit planning
- section registry and marker contract
- section edit prompt contract
- section regeneration dry-run validation
- controlled section patch sandbox proposal
- section preview validation score
- no real generated app modification
- no deployment unlock
- no provider/database/secrets unlock

## Phase 17 Goal

Phase 17 will move one step closer to real editing by applying an approved selected-section patch to a controlled sandbox copy only.

The original generated output must remain untouched.

## Approved Source

Future sandbox copy source:

D:/APPS/IdeasForgeAI/generated-apps/_phase13e_controlled_html_css_js_generation/

## Approved Patch Proposal Source

Future patch proposal source:

D:/APPS/IdeasForgeAI/generated-apps/_phase16f_controlled_section_patch_sandbox/

## Future Phase 17 Sandbox Copy Target

Future controlled copy target:

D:/APPS/IdeasForgeAI/generated-apps/_phase17_controlled_section_patch_applied_copy/

## Safety Rule

Phase 17 must never directly modify:
- generated-apps/ideasforgeai-preview-v1
- generated-apps/_phase13e_controlled_html_css_js_generation
- backend/
- frontend/pages/
- frontend/shared/
- docs/ except Phase 17 docs
- root project files
- secrets/env files
- deployment config
- KisanMitraAI files

## Required Future Files

Future Phase 17 sandbox copy may contain only approved copied/generated files:

- manifest.json
- index.html
- styles.css
- app.js
- README.md
- validation-report.md
- section-patch-application-report.md
- rollback-manifest.json

## Future Phase 17 Sequence

Phase 17A — Apply Approved Section Patch to Sandbox Copy Planning  
Phase 17B — Sandbox Copy Contract + Rollback Manifest  
Phase 17C — Create Read-Only Source Copy Sandbox  
Phase 17D — Apply Approved Section Patch to Copied HTML Only  
Phase 17E — Patched Copy Preview Route  
Phase 17F — Patched Copy Validation Score  
Phase 17G — Phase 17 Freeze Review

## Human Approval Requirements

Before a patch can be applied to a sandbox copy:
- Phase 16E dry-run validation must pass.
- Phase 16F patch proposal must exist.
- Phase 16G validation score must pass.
- human_approval_id must be present.
- approved_by_human must be true.
- rollback manifest must be prepared.

## Patch Application Rules

Future patch application must:
- target one section only
- match section_id
- match start marker
- match end marker
- preserve all other sections
- preserve file structure
- avoid external scripts
- avoid iframe
- avoid provider/database/auth/secrets
- avoid deployment logic
- avoid KisanMitraAI reference
- write only to the Phase 17 sandbox copy
- create rollback manifest before patch

## Phase 17A Safety Confirmation

Phase 17A is planning only.

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
Phase 17B was not implemented.
