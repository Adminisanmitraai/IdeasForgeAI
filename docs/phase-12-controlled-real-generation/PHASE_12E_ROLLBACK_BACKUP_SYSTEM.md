# Phase 12E - Rollback + Backup System

Status: Completed, not frozen.

## Purpose

Phase 12E adds backup and rollback safety for the Phase 12D sandbox proof file only.

This is not real app generation. This is not production generation. This is not deployment. It is only a controlled backup and rollback mechanism for one approved sandbox proof file.

## Hard Boundary

Phase 12E does not:

- Backup or rollback `generated-apps/ideasforgeai-preview-v1/`
- Backup or rollback `backend/`
- Backup or rollback `frontend/`
- Backup or rollback `docs/`
- Backup or rollback project root files
- Touch deployment config
- Touch secrets/env files
- Touch IdeasForgeAI paths
- Generate HTML, CSS, or JavaScript
- Unlock general generated-app writes
- Unlock backend generation
- Unlock deployment
- Call providers
- Add Supabase, authentication, database writes, or secrets
- Implement Phase 12F

## Approved Source File

Only this file can be backed up or restored:

`D:/APPS/IdeasForgeAI/generated-apps/_phase12d_write_sandbox/phase12d-write-proof.txt`

## Approved Backup Folder

Only this backup folder can be used:

`D:/APPS/IdeasForgeAI/generated-apps/_phase12e_backup_sandbox/`

Backups are timestamped copies of the approved Phase 12D proof file.

## Backend Module

Module:

`backend/frontend_generator/rollback_backup_system.py`

Optional static endpoints:

`POST /api/frontend-generator/phase12e-backup-sandbox-file`

`POST /api/frontend-generator/phase12e-rollback-sandbox-file`

Both endpoints require:

- `approval_required=true`
- `human_approval_id` present
- `source_phase=Phase 12E`

## Backup Behavior

The backup endpoint creates a timestamped backup copy of the Phase 12D proof file inside `_phase12e_backup_sandbox/` and returns metadata only.

Returned safety values remain locked:

- `real_generation_unlocked=false`
- `backend_generation_unlocked=false`
- `deployment_unlocked=false`
- `provider_calls_allowed=false`
- `database_writes_allowed=false`
- `secrets_allowed=false`

## Rollback Behavior

The rollback endpoint restores only `phase12d-write-proof.txt` from the latest valid backup in `_phase12e_backup_sandbox/`.

It does not rollback any other file or folder.

## Rejected Targets

The system rejects:

- Arbitrary source paths
- Arbitrary backup folders
- Arbitrary content
- `generated-apps/ideasforgeai-preview-v1/`
- `backend/`
- `frontend/`
- `docs/`
- Project root files
- Deployment config files
- Secrets/env files
- IdeasForgeAI paths
- Any path outside `D:/APPS/IdeasForgeAI`

## Next Step

Phase 12E Freeze Review, then Phase 12F only after explicit approval.
