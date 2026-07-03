
# Phase 9G - Generated App Preview Runner

Status: Completed, not frozen.

## Purpose

Phase 9G adds a safe local preview runner for the existing generated Phase 9D preview.

This phase does not create new app pages, does not generate new HTML/CSS/React, and does not deploy anything.

## Existing preview folder

generated-apps/ideasforgeai-preview-v1/

## Runner URL

http://127.0.0.1:8100/api/frontend-generator/generated-app-preview-runner/index.html

## What Phase 9G allows

- Serve the existing generated preview locally through the backend.
- Return preview-runner metadata.
- Confirm required preview files exist.
- Open the generated preview in browser without deployment.

## What Phase 9G does not allow

- No new generated app pages.
- No new generated app file writes.
- No production deployment.
- No provider calls.
- No Supabase.
- No auth.
- No database writes.
- No secrets.
- No IdeasForgeAI production changes.

## Safety locks

- generated_app_preview_runner_allowed=true
- existing_preview_folder_required=true
- new_page_files_created=false
- generated_app_write_allowed=false
- production_frontend_generation_allowed=false
- deployment_allowed=false
- provider_calls_allowed=false
- database_writes_allowed=false
- supabase_allowed=false
- auth_allowed=false
- approval_required=true

## Next step

Phase 9G Freeze Review, then Phase 9H - Real Frontend Generation Freeze Review.

