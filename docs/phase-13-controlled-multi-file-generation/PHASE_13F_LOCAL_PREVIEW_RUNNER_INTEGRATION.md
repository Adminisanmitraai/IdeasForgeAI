# Phase 13F - Local Preview Runner Integration

Status: Completed, not frozen.

Phase 13F adds a metadata-only local preview runner integration for the existing Phase 13E sandbox output. It does not create, modify, delete, or generate app files. It does not deploy and does not unlock general real generation.

## Preview Target

The only preview target is:

`D:/APPS/IdeasForgeAI/generated-apps/_phase13e_controlled_html_css_js_generation/`

The entry file is:

`index.html`

## Safety Rules

The preview runner:

- Returns preview metadata only.
- Does not write files.
- Does not create folders.
- Does not modify files.
- Does not delete files.
- Does not generate HTML/CSS/JS.
- Does not write to `generated-apps/ideasforgeai-preview-v1`.
- Does not write to Phase 12 sandbox folders.
- Does not write to the Phase 13D sandbox folder.
- Does not write to the Phase 13E sandbox folder.
- Does not serve backend, frontend, docs, root production files, env/secrets, deployment config, database/auth/Supabase files, or IdeasForgeAI paths.
- Rejects preview targets outside the Phase 13E sandbox folder.
- Keeps general real generation, backend generation, deployment, provider calls, Supabase, authentication, database writes, and secrets locked.

## Endpoints

`GET /api/frontend-generator/phase13f-local-preview-runner-status`

Returns metadata about the existing Phase 13E preview target without requiring a payload.

`POST /api/frontend-generator/phase13f-local-preview-runner`

Requires:

- `project_name = IdeasForgeAI`
- `human_approval_id` present
- `approved_by_human = true`
- `source_phase = Phase 13F`

The POST endpoint returns metadata only:

- `status`
- `preview_runner_only`
- `preview_target_folder`
- `preview_entry_file`
- `preview_url_or_path`
- `allowed_files_found`
- `blocked_files_found`
- locked safety flags
- `next_required_phase = Phase 13G`

## Studio V3 Reference

Studio V3 receives a small read-only right-panel reference for Phase 13F. It does not iframe the generated page, does not call the preview runner, and does not alter the frozen Phase 11 workspace structure. It keeps one `phase11bBuilderWorkspacePanel` and one `phase11dRightPreviewPanel`.

## Safety Outcome

Phase 13F proves that IdeasForgeAI can describe and validate a local preview target for the Phase 13E static sandbox output without writing files or deploying anything.

Phase 13G remains the next approval-gated phase and is not implemented here.
