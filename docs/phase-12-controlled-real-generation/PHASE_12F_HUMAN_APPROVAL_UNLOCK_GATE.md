# Phase 12F - Human Approval Unlock Gate

Status: Completed, not frozen.

## Purpose

Phase 12F adds a human approval gate that validates whether a future controlled generation planning action may proceed to Phase 12G.

This phase returns approval metadata only. It does not unlock real generation, write generated app files, create folders, deploy, or call providers.

## Hard Boundary

Phase 12F does not:

- Unlock real frontend generation
- Unlock generated-app writes
- Unlock backend generation
- Write files under `generated-apps/`
- Touch `generated-apps/ideasforgeai-preview-v1/`
- Create folders
- Generate HTML, CSS, or JavaScript
- Deploy
- Call providers
- Add Supabase, authentication, database writes, or secrets
- Touch IdeasForgeAI production
- Implement Phase 12G

## Backend Module

Module:

`backend/frontend_generator/human_approval_unlock_gate.py`

Optional static endpoint:

`POST /api/frontend-generator/human-approval-unlock-gate`

The endpoint accepts confirmation metadata and returns approval gate metadata only.

## Required Approval Fields

The approval gate requires:

- `project_name=IdeasForgeAI`
- `human_approval_id` present
- `approval_required=true`
- `approved_by_human=true`
- `dry_run_validation_passed=true`
- `backup_required=true`
- `rollback_required=true`
- `source_phase=Phase 12F`
- `target_next_phase=Phase 12G`
- `generation_mode=controlled_single_generation_planning`

## Rejected Conditions

The gate rejects:

- Missing approval
- False approval
- Missing dry-run validation
- Missing backup requirement
- Missing rollback requirement
- `deployment_allowed=true`
- `provider_calls_allowed=true`
- `database_writes_allowed=true`
- `secrets_allowed=true`
- Supabase unlock
- Auth unlock
- IdeasForgeAI paths
- Paths outside `D:/APPS/IdeasForgeAI`
- Generated output fields such as HTML, CSS, JS, React, generated files, provider prompts, deployment requests, database writes, auth config, or secrets

## Return Metadata

The response includes:

- `status`
- `approval_gate_only`
- `human_approval_validated`
- `next_phase_allowed`
- `next_phase`
- `real_generation_unlocked=false`
- `generated_app_write_unlocked=false`
- `backend_generation_unlocked=false`
- `deployment_unlocked=false`
- `provider_calls_allowed=false`
- `database_writes_allowed=false`
- `secrets_allowed=false`
- `validation_errors`
- `validation_warnings`
- `required_next_action`

## Safety Result

`next_phase_allowed` may become `true` only for Phase 12G planning consideration. It does not permit immediate generation, file writing, backend generation, provider calls, or deployment.

## Next Step

Phase 12F Freeze Review, then Phase 12G only after explicit approval.
