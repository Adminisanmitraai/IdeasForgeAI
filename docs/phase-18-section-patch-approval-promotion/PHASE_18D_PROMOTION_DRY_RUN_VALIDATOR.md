# Phase 18D — Promotion Dry-Run Validator

Status: Completed, not frozen.

## Purpose

Phase 18D adds a dry-run validator before any Phase 17 patched sandbox copy can be promoted to a Phase 18 promoted preview folder.

This phase is validation-only.

No promotion is performed.
No files are copied.
No folders are created.
No generated app files are modified.
No deployment is added.
No provider calls are added.
No Supabase/auth/database/secrets are added.

## What Phase 18D Validates

The validator checks:

- project_name = IdeasForgeAI
- source_phase = Phase 18D
- promotion_id is valid
- human_approval_id is present and valid
- approved_by_human = true
- phase18c_approval_validated = true
- phase17g_frozen = true
- phase17f_validation_score = 100
- phase17e_preview_route_working = true
- source_folder equals approved Phase 17 sandbox copy
- target_folder equals approved Phase 18 promoted preview folder
- source folder exists
- required source files exist
- rollback manifest exists
- promotion manifest will be required later
- rollback is required
- deployment/provider/database/secrets/Supabase/auth flags are false

## Safety Confirmation

Phase 18D is dry-run validation only.

No promotion was performed.
No promotion manifest was created.
No promoted folder was created.
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
IdeasForgeAI production was not touched.
Phase 18E was not implemented.

