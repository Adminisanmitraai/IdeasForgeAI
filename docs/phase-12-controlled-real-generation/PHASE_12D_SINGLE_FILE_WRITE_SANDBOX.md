# Phase 12D - Single-File Write Sandbox

Status: Completed, not frozen.

## Purpose

Phase 12D creates the first approval-gated single-file write sandbox for IdeasForgeAI.

This is not real frontend generation. This is not production generation. This is not deployment. It is only a tightly controlled proof that one approved static file can be written to one approved sandbox folder.

## Hard Boundary

Phase 12D does not:

- Unlock real generated-app writes
- Unlock backend generation
- Generate HTML, CSS, or JavaScript
- Accept arbitrary file content
- Touch `generated-apps/ideasforgeai-preview-v1/`
- Overwrite any existing generated app
- Deploy
- Call providers
- Add Supabase, authentication, database writes, or secrets
- Touch IdeasForgeAI production
- Implement Phase 12E

## Approved Sandbox

Only this folder is allowed:

`D:/APPS/IdeasForgeAI/generated-apps/_phase12d_write_sandbox/`

Only this file name is allowed:

`phase12d-write-proof.txt`

Only this exact file path may be written:

`D:/APPS/IdeasForgeAI/generated-apps/_phase12d_write_sandbox/phase12d-write-proof.txt`

## Static Proof Content

The file content is static and defined in the backend module. User-provided file content is rejected.

```text
IdeasForgeAI Phase 12D single-file write sandbox proof.
This file was created by an approval-gated sandbox write.
This is not real generation.
This is not deployment.
Backend generation remains locked.
Deployment remains locked.
Provider calls remain locked.
Supabase/auth/database/secrets remain locked.
IdeasForgeAI production was not touched.
```

## Backend Sandbox Module

Module:

`backend/frontend_generator/single_file_write_sandbox.py`

Optional static endpoint:

`POST /api/frontend-generator/single-file-write-sandbox`

The endpoint requires:

- `approval_required=true`
- `human_approval_id` present
- `dry_run_validation_passed=true`

## Rejected Targets

The sandbox rejects:

- Any file name other than `phase12d-write-proof.txt`
- Any folder other than `_phase12d_write_sandbox/`
- `backend/` paths
- `frontend/` paths
- `docs/` paths
- Root project file writes
- Deployment config writes
- Secrets/env file writes
- IdeasForgeAI paths
- Any path outside `D:/APPS/IdeasForgeAI`
- `generated-apps/ideasforgeai-preview-v1/`

## Return Metadata

The response includes:

- `status`
- `sandbox_write_only`
- `file_write_allowed_for_this_file_only`
- `written_file_path`
- `generated_app_write_unlocked=false`
- `backend_generation_unlocked=false`
- `deployment_unlocked=false`
- `provider_calls_allowed=false`
- `database_writes_allowed=false`
- `secrets_allowed=false`
- `next_required_phase`

## Safety Result

The only allowed write is the proof file in the Phase 12D sandbox folder. General generated-app writes, backend generation, deployment, provider calls, database writes, and secrets remain locked.

## Next Step

Phase 12D Freeze Review, then Phase 12E only after explicit approval.
