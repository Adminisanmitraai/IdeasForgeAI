# Phase 19E — Controlled Candidate Folder Creation

Status: Completed, not frozen.

## Purpose

Phase 19E creates a controlled main preview candidate folder from the validated Phase 18 promoted preview.

This phase writes only to:

D:/APPS/IdeasForgeAI/generated-apps/_phase19_main_preview_candidate/

## Approved Source

D:/APPS/IdeasForgeAI/generated-apps/_phase18_promoted_section_patch_preview/

## Approved Target

D:/APPS/IdeasForgeAI/generated-apps/_phase19_main_preview_candidate/

## Allowed Candidate Files

- index.html
- styles.css
- app.js
- manifest.json
- README.md
- validation-report.md
- rollback-manifest.json
- phase17-validation-report.md
- section-patch-application-report.md
- promotion-manifest.json
- phase18-promotion-report.md
- phase18-validation-report.md
- candidate-manifest.json
- phase19-candidate-report.md
- phase19-validation-report.md

## Safety Confirmation

Phase 19E creates only the approved Phase 19 candidate folder.

No generated-apps/ideasforgeai-preview-v1 files are touched.
No Phase 13E sandbox files are changed.
No Phase 16F sandbox files are changed.
No Phase 17 sandbox files are changed.
No Phase 18 promoted files are changed.
No production replacement is allowed.
No backend generation is unlocked.
No deployment is added.
No provider calls are added.
No Supabase/auth/database/secrets are added.
KisanMitraAI production is not touched.
Phase 19F is not implemented.
