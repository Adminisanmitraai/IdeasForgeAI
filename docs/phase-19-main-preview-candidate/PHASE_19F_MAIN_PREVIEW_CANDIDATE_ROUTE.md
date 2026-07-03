# Phase 19F — Main Preview Candidate Route

Status: Completed, not frozen.

## Purpose

Phase 19F adds a read-only local preview route for the Phase 19 main preview candidate output.

This phase serves files only from:

D:/APPS/IdeasForgeAI/generated-apps/_phase19_main_preview_candidate/

## Scope

Allowed:
- read-only candidate preview status endpoint
- read-only candidate preview file route
- serve approved Phase 19 candidate files inline
- no file writes

Not allowed:
- modify Phase 19 candidate files
- modify Phase 18 promoted files
- modify Phase 17 sandbox files
- modify Phase 13E source files
- modify generated-apps/ideasforgeai-preview-v1
- replace production preview
- unlock backend generation
- deploy
- call providers
- add Supabase/auth/database/secrets
- touch IdeasForgeAI

## Preview Routes

Status:
GET /api/frontend-generator/phase19f-main-preview-candidate-status

Preview:
GET /api/frontend-generator/phase19f-main-preview-candidate/index.html
GET /api/frontend-generator/phase19f-main-preview-candidate/styles.css
GET /api/frontend-generator/phase19f-main-preview-candidate/app.js
GET /api/frontend-generator/phase19f-main-preview-candidate/manifest.json

## Safety Confirmation

Phase 19F is main-preview-candidate-route only.

No files are written.
No production replacement is performed.
No real generated app is modified.
generated-apps/ideasforgeai-preview-v1 remains untouched.
General real generation remains locked.
Backend generation remains locked.
Deployment remains locked.
Provider calls remain locked.
Supabase/auth/database/secrets remain locked.
IdeasForgeAI production is not touched.
Phase 19G is not implemented.

