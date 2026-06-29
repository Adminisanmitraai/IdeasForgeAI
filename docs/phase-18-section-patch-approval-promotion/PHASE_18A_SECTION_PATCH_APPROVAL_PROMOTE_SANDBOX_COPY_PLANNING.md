# Phase 18A — Section Patch Approval + Promote Sandbox Copy Planning

Status: Completed, not frozen.

## Purpose

Phase 18A defines how IdeasForgeAI will safely approve a patched sandbox copy and later promote it to a controlled approved output.

This phase is planning only.

No sandbox copy is promoted.
No real generated app files are modified.
No generated-apps/ideasforgeai-preview-v1 files are touched.
No backend generation is unlocked.
No deployment is added.
No provider calls are added.
No Supabase/auth/database/secrets are added.

## What Phase 17 Proved

Phase 17 proved:
- a Phase 17 sandbox copy can be created
- an approved section patch can be applied only to copied HTML
- rollback manifest can track the patched copy
- patched copy preview route can serve the copy read-only
- patched copy validation score can reach 100
- real generated app remains untouched
- deployment/provider/database/secrets remain locked

## Phase 18 Goal

Phase 18 will plan the approval and controlled promotion layer.

The user should eventually be able to:
1. review the patched sandbox copy
2. approve the patch result
3. run promotion dry-run validation
4. promote only to an approved controlled output folder
5. preserve rollback
6. validate promoted output
7. keep production deployment locked

## Approved Source for Future Promotion

Future promotion source:

D:/APPS/IdeasForgeAI/generated-apps/_phase17_controlled_section_patch_applied_copy/

## Future Controlled Promotion Target

Future promotion target:

D:/APPS/IdeasForgeAI/generated-apps/_phase18_promoted_section_patch_preview/

## Promotion Safety Rules

Promotion must never directly modify:
- generated-apps/ideasforgeai-preview-v1
- generated-apps/_phase13e_controlled_html_css_js_generation
- generated-apps/_phase16f_controlled_section_patch_sandbox
- backend/
- frontend/pages/
- frontend/shared/
- docs/ except Phase 18 docs
- root project files
- secrets/env files
- deployment config
- KisanMitraAI files

## Required Approval Conditions

Before promotion can happen:
- Phase 17G must be frozen.
- Phase 17F validation score must be 100.
- Phase 17E preview route must be working.
- human_approval_id must be present.
- approved_by_human must be true.
- rollback manifest must exist.
- promotion dry-run validation must pass.
- deployment_allowed must be false.
- provider_calls_allowed must be false.
- database_writes_allowed must be false.
- secrets_allowed must be false.

## Future Phase 18 Sequence

Phase 18A — Section Patch Approval + Promote Sandbox Copy Planning  
Phase 18B — Promotion Contract + Manifest Schema  
Phase 18C — Human Promotion Approval Gate  
Phase 18D — Promotion Dry-Run Validator  
Phase 18E — Controlled Promotion to Approved Preview Folder  
Phase 18F — Promoted Preview Route  
Phase 18G — Promoted Output Validation Score  
Phase 18H — Phase 18 Freeze Review

## Phase 18A Safety Confirmation

Phase 18A is planning only.

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
Phase 18B was not implemented.
