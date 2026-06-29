# Phase 19A — Controlled Promote to Main Preview Candidate Planning

Status: Completed, not frozen.

## Purpose

Phase 19A defines how IdeasForgeAI will safely promote a validated Phase 18 promoted preview into a controlled main preview candidate.

This phase is planning only.

No files are promoted.
No files are copied.
No folders are created.
No generated-apps/ideasforgeai-preview-v1 files are touched.
No deployment is added.
No backend generation is unlocked.
No provider calls are added.
No Supabase/auth/database/secrets are added.

## What Phase 18 Proved

Phase 18 proved:
- section patch promotion planning exists
- promotion contract and manifest schema exists
- human promotion approval gate works
- promotion dry-run validator works
- controlled promotion to approved Phase 18 preview folder works
- promoted preview route works
- promoted output validation score returns 100
- generated-apps/ideasforgeai-preview-v1 remains untouched
- deployment remains locked

## Phase 19 Goal

Phase 19 will plan how a validated promoted preview can become a main preview candidate without touching production deployment.

The main preview candidate is still not production.

It is a controlled candidate folder that can later be reviewed before any real main preview replacement.

## Approved Source for Future Candidate Promotion

Future source:

D:/APPS/IdeasForgeAI/generated-apps/_phase18_promoted_section_patch_preview/

## Future Controlled Candidate Target

Future target:

D:/APPS/IdeasForgeAI/generated-apps/_phase19_main_preview_candidate/

## Important Safety Rule

Phase 19 must not directly modify:

- generated-apps/ideasforgeai-preview-v1
- generated-apps/_phase13e_controlled_html_css_js_generation
- generated-apps/_phase16f_controlled_section_patch_sandbox
- generated-apps/_phase17_controlled_section_patch_applied_copy
- generated-apps/_phase18_promoted_section_patch_preview
- backend/
- frontend/pages/
- frontend/shared/
- docs/ except Phase 19 docs
- deployment config
- env/secrets files
- KisanMitraAI files

## Required Future Approval Conditions

Before a main preview candidate can be created:

- Phase 18H must be frozen.
- Phase 18G validation score must be 100.
- Phase 18F promoted preview route must be working.
- human_approval_id must be present.
- approved_by_human must be true.
- candidate dry-run validation must pass.
- rollback manifest must exist.
- promotion manifest must exist.
- deployment_allowed must be false.
- provider_calls_allowed must be false.
- database_writes_allowed must be false.
- secrets_allowed must be false.
- supabase_allowed must be false.
- auth_allowed must be false.

## Future Phase 19 Sequence

Phase 19A — Controlled Promote to Main Preview Candidate Planning  
Phase 19B — Main Preview Candidate Contract + Manifest Schema  
Phase 19C — Human Candidate Approval Gate  
Phase 19D — Candidate Promotion Dry-Run Validator  
Phase 19E — Controlled Candidate Folder Creation  
Phase 19F — Main Preview Candidate Route  
Phase 19G — Candidate Output Validation Score  
Phase 19H — Phase 19 Freeze Review

## Phase 19A Safety Confirmation

Phase 19A is planning only.

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
Phase 19B was not implemented.
