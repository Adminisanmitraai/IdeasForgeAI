# Phase 19D — Candidate Promotion Dry-Run Validator

Status: Completed, not frozen.

## Purpose

Phase 19D adds a dry-run validator before any Phase 18 promoted preview can become a Phase 19 main preview candidate.

This phase is validation-only.

No candidate folder is created.
No candidate manifest is created.
No files are copied.
No files are modified.
No generated-apps/ideasforgeai-preview-v1 files are touched.
No production replacement is allowed.
No deployment is added.
No backend generation is unlocked.
No provider calls are added.
No Supabase/auth/database/secrets are added.

## What Phase 19D Validates

The validator checks:

- project_name = IdeasForgeAI
- source_phase = Phase 19D
- candidate_id is valid
- human_approval_id is valid
- approved_by_human = true
- phase19c_approval_validated = true
- phase18h_frozen = true
- phase18g_validation_score = 100
- phase18f_promoted_preview_route_working = true
- source_folder equals approved Phase 18 promoted preview folder
- target_folder equals approved Phase 19 main preview candidate folder
- source folder exists
- required source files exist
- promotion manifest exists
- rollback manifest exists
- candidate manifest will be required later
- rollback is required
- production replacement/deployment/provider/database/secrets/Supabase/auth flags are false

## Safety Confirmation

Phase 19D is dry-run validation only.

No candidate folder was created.
No candidate manifest was created.
No files were copied.
No generated app files were changed.
No Phase 13E sandbox files were changed.
No Phase 16F sandbox files were changed.
No Phase 17 sandbox files were changed.
No Phase 18 promoted files were changed.
generated-apps/ideasforgeai-preview-v1 was not touched.
Production replacement remains locked.
General real generation remains locked.
Backend generation remains locked.
Deployment remains locked.
Provider calls remain locked.
Supabase/auth/database/secrets remain locked.
IdeasForgeAI production was not touched.
Phase 19E was not implemented.

