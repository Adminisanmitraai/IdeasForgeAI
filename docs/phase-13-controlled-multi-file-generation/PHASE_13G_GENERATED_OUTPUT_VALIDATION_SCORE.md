# Phase 13G - Generated Output Validation Score

Status: Completed, not frozen.

Phase 13G adds a read-only validation scoring system for the existing Phase 13E sandbox output. It analyzes the generated HTML/CSS/JS sandbox files and returns metadata plus scores only. It does not create, modify, delete, or generate files, and it does not deploy or unlock generation.

## Target Folder

The only scoring target is:

`D:/APPS/IdeasForgeAI/generated-apps/_phase13e_controlled_html_css_js_generation/`

## Required Files

The validator expects exactly these files:

1. `manifest.json`
2. `index.html`
3. `styles.css`
4. `app.js`
5. `README.md`
6. `validation-report.md`

Extra files or missing files lower/block the validation result.

## Score Categories

- `required_files_score`
- `html_safety_score`
- `css_safety_score`
- `js_safety_score`
- `manifest_score`
- `validation_report_score`
- `readme_score`
- `no_external_dependency_score`
- `no_provider_call_score`
- `no_database_auth_secret_score`
- `IdeasForgeAI_separation_score`
- `preview_runner_compatibility_score`
- `overall_score`

## Safety Checks

Phase 13G confirms:

- `index.html` has no external script, iframe, external URL, or IdeasForgeAI reference.
- `styles.css` has no `http`, `https`, or `@import`.
- `app.js` has no `fetch`, `XMLHttpRequest`, `import`, `http`, `https`, localStorage, sessionStorage, provider references, Supabase references, auth references, database references, API key markers, or deployment markers.
- `manifest.json` is valid JSON.
- `validation-report.md` exists and is non-empty.
- `README.md` exists and is non-empty.

## Endpoint

`POST /api/frontend-generator/phase13g-generated-output-validation-score`

The endpoint accepts optional approval metadata and returns score metadata only:

- `status`
- `validation_score_only`
- `target_folder`
- `files_checked`
- `extra_files_found`
- `missing_files_found`
- `score_categories`
- `overall_score`
- `validation_passed`
- `validation_errors`
- `validation_warnings`
- locked safety flags
- `next_required_phase = Phase 13H`

## Studio V3 Reference

Studio V3 includes a small read-only right-panel reference for Phase 13G. It does not iframe the generated page, call providers, deploy, or write generated-app files.

## Safety Outcome

Phase 13G proves the Phase 13E sandbox output can be scored with a validation-only backend path. General real generation, backend generation, deployment, provider calls, Supabase, authentication, database writes, and secrets remain locked.

Phase 13H remains the next approval-gated phase and is not implemented here.
