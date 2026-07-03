
# Phase 9B - Generation Target Folder Contract

Status: Completed as contract-only.

## Purpose

Phase 9B defines the safe future target folder contract for real frontend generation.

This phase does not create files, does not create folders, and does not write to generated-apps/.

## Future target folder

Recommended future target folder:

generated-apps/ideasforgeai-preview-v1/

## What Phase 9B allows

Phase 9B allows:

- Defining the future generated app folder name
- Defining allowed future file categories
- Defining blocked write locations
- Defining rollback and validation rules
- Defining approval requirements before file writing

## What Phase 9B does not allow

Phase 9B does not:

- Create generated-apps/ideasforgeai-preview-v1/
- Write files to generated-apps/
- Generate HTML
- Generate CSS
- Generate React
- Generate app files
- Add export/download behavior
- Deploy anything
- Add Supabase
- Add auth
- Add database writes
- Call providers
- Add secrets
- Touch IdeasForgeAI production

## Allowed future file types after later approval

Future phases may allow:

- index.html
- styles.css
- app.js
- README.md
- manifest.json
- validation-report.md
- assets/ placeholder references

But Phase 9B does not create them.

## Blocked locations

Future generation must never write to:

- backend/
- frontend/pages/
- frontend/shared/
- docs/
- root production files
- existing generated app folders unless explicitly approved
- IdeasForgeAI folders
- any folder outside D:\APPS\IdeasForgeAI

## Safety locks

- generation_target_folder_contract_allowed=true
- target_folder_defined=true
- target_folder_created=false
- production_frontend_generation_allowed=false
- html_generation_allowed=false
- css_generation_allowed=false
- react_generation_allowed=false
- generated_app_write_allowed=false
- generated_files_allowed=false
- deployment_allowed=false
- provider_calls_allowed=false
- database_writes_allowed=false
- supabase_allowed=false
- auth_allowed=false
- approval_required=true

## Next step

Phase 9B Freeze Review, then Phase 9C - Single Page File Write Dry Run.

