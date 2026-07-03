# Phase 21A — Main Preview Replacement Planning

Status: Completed, not frozen.

## Purpose

Phase 21A defines the controlled plan for replacing the current main preview with the final polished Phase 20 frontend preview.

This phase is planning only.

No files are replaced.
No files are copied.
No generated-apps/ideasforgeai-preview-v1 files are touched.
No Phase 20 polish sandbox files are modified.
No production deployment is performed.
No provider calls are added.
No database writes are added.
No Supabase/auth/secrets are added.
IdeasForgeAI production is not touched.

## Current Frozen Source

The approved polished frontend source is:

D:/APPS/IdeasForgeAI/generated-apps/_phase20_final_apple_like_frontend_polish/

Frozen preview route:

http://127.0.0.1:8100/api/frontend-generator/phase20f-final-polished-preview/index.html

## Protected Replacement Target

The protected main preview target is:

D:/APPS/IdeasForgeAI/generated-apps/ideasforgeai-preview-v1/

This target must not be modified until explicit human approval in a later Phase 21 approval gate.

## Phase 21 Goal

Phase 21 should safely promote the final polished Phase 20 frontend into the main preview folder only after:

- Phase 20H is frozen
- Phase 20G validation score is 100
- Source and target contracts are defined
- Rollback manifest is prepared
- Human replacement approval is confirmed
- Replacement dry-run passes
- Existing main preview files are backed up or rollback-ready
- No deployment is triggered
- No provider calls are triggered
- No database writes are triggered
- No secrets are used

## Future Phase 21 Sequence

Phase 21A — Main Preview Replacement Planning  
Phase 21B — Replacement Contract + Manifest Schema  
Phase 21C — Human Replacement Approval Gate  
Phase 21D — Replacement Dry-Run Validator  
Phase 21E — Rollback Snapshot + Safety Manifest  
Phase 21F — Controlled Main Preview Replacement  
Phase 21G — Main Preview Output Validation Score  
Phase 21H — Main Preview Freeze Review  

## Replacement Safety Rules

Phase 21 must never modify:

- backend/
- frontend/pages/
- frontend/shared/
- deployment files
- env files
- secret files
- provider configuration
- database configuration
- Supabase/auth configuration
- IdeasForgeAI paths

Phase 21 may only modify:

D:/APPS/IdeasForgeAI/generated-apps/ideasforgeai-preview-v1/

and only after explicit human approval in the approved Phase 21 gate.

## Required Replacement Files

The final main preview replacement should contain:

- index.html
- styles.css
- app.js
- manifest.json
- README.md
- phase20-polish-report.md
- phase20-validation-report.md
- phase21-replacement-manifest.json
- phase21-rollback-manifest.json
- phase21-replacement-report.md
- phase21-validation-report.md

## Phase 21A Safety Confirmation

Phase 21A is planning only.

No files were copied.
No files were replaced.
No generated-apps/ideasforgeai-preview-v1 files were touched.
No Phase 20 polish sandbox files were modified.
No production replacement was performed.
No deployment was performed.
No provider calls were made.
No database writes were made.
No Supabase/auth/secrets were added.
IdeasForgeAI production was not touched.
Phase 21B was not implemented.

