# Phase 21F — Controlled Main Preview Replacement

Status: Completed, not frozen.

## Purpose

Phase 21F performs the controlled replacement of the protected main preview folder using the frozen Phase 20 polished frontend.

This phase writes only to:

D:/APPS/IdeasForgeAI/generated-apps/ideasforgeai-preview-v1/

## Approved Replacement Source

D:/APPS/IdeasForgeAI/generated-apps/_phase20_final_apple_like_frontend_polish/

## Protected Replacement Target

D:/APPS/IdeasForgeAI/generated-apps/ideasforgeai-preview-v1/

## Rollback Snapshot

D:/APPS/IdeasForgeAI/generated-apps/_phase21_rollback_snapshot_before_main_preview_replacement/

## Safety Confirmation

Phase 21F is controlled main preview replacement only.

Allowed:
- replace files only inside generated-apps/ideasforgeai-preview-v1/
- write replacement manifest
- write rollback manifest copy
- write replacement report
- write validation report

Not allowed:
- deployment
- provider calls
- database writes
- Supabase/auth/secrets
- backend generation unlock
- IdeasForgeAI changes
- backend/frontend source changes during replacement action

## Result

After this phase, the polished Phase 20 frontend becomes the local main preview.

Deployment remains locked.
Production deployment remains locked.

