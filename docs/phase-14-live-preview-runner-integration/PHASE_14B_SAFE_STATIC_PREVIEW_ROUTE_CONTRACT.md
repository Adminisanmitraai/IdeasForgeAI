# Phase 14B — Safe Static Preview Route Contract

Status: Completed, not frozen.

## Purpose

Phase 14B defines the safe static preview route contract for IdeasForgeAI.

This phase is contract/documentation only. It does not create a live static file server yet. It does not iframe the generated app. It does not modify generated app files. It does not unlock generation or deployment.

## Current Source of Truth

- Phase 11 Builder Workspace is frozen.
- Phase 12 Controlled Real Generation Unlock track is frozen.
- Phase 13 Controlled Multi-File Real Generation track is frozen.
- Phase 13G validation score is 100.
- Phase 14A Live Preview Runner Integration Planning is frozen.
- General real generation remains locked.
- Backend generation remains locked.
- Deployment remains locked.

## Approved Preview Target

Only this folder may be considered for future safe static preview routing:

D:/APPS/IdeasForgeAI/generated-apps/_phase13e_controlled_html_css_js_generation/

## Approved Preview Entry File

Only this entry file is allowed:

index.html

## Approved Preview Route Pattern

Future route contract:

GET /api/frontend-generator/phase14-static-preview/{file_name}

Allowed file_name values only:
- index.html
- styles.css
- app.js
- manifest.json
- README.md
- validation-report.md

No directory traversal is allowed.
No arbitrary path is allowed.
No query parameter may override the target folder.
No user-supplied absolute path is allowed.

## Required Route Safety Rules

The future static preview route must:

1. Serve only files from the approved Phase 13E sandbox folder.
2. Reject generated-apps/ideasforgeai-preview-v1.
3. Reject Phase 12 sandbox folders.
4. Reject Phase 13D sandbox folder.
5. Reject backend folders.
6. Reject frontend source folders.
7. Reject docs folders.
8. Reject project root files.
9. Reject deployment config.
10. Reject .env, key, pem, secret, credential, token, database, auth, and Supabase files.
11. Reject IdeasForgeAI paths.
12. Reject any path outside D:/APPS/IdeasForgeAI.
13. Reject any filename not explicitly listed in the allowed file list.
14. Reject directory traversal strings such as ../, ..\, encoded traversal, or absolute paths.
15. Return 404 or blocked metadata for rejected files.
16. Never write files.
17. Never create folders.
18. Never modify generated app output.
19. Never call providers.
20. Never deploy.

## Allowed MIME Types

Future static preview route may return only safe static content types:

- text/html for index.html
- text/css for styles.css
- application/javascript for app.js
- application/json for manifest.json
- text/markdown or text/plain for README.md
- text/markdown or text/plain for validation-report.md

## Blocked File Types

Blocked:
- .env
- .key
- .pem
- .p12
- .sqlite
- .db
- .py
- .ps1
- .sh
- .bat
- .cmd
- .exe
- .dll
- .zip
- .tar
- .gz
- .yml
- .yaml
- deployment configs
- unknown binary files

## Same-Origin Policy

The future preview route must run under the existing local IdeasForgeAI backend origin:

http://127.0.0.1:8100

No public hosting is allowed in Phase 14.

## Studio V3 Preview Policy

Studio V3 may later reference the safe preview route in the right preview panel only after Phase 14C/14D.

Phase 14B does not add iframe embedding.

## Iframe Policy

Iframe rendering remains locked in Phase 14B.

Iframe may only be considered after:
- route contract is frozen
- read-only file server is implemented
- validation score remains 100
- preview target remains approved
- no external scripts or unsafe markers exist

## Endpoint Contract for Future Phase 14C

Future metadata endpoint may return:

- status
- route_contract_ready
- preview_target_folder
- preview_entry_file
- allowed_route_pattern
- allowed_files
- blocked_files
- same_origin_required
- iframe_allowed=false
- file_write_allowed=false
- folder_creation_allowed=false
- generation_allowed=false
- backend_generation_unlocked=false
- deployment_unlocked=false
- provider_calls_allowed=false
- database_writes_allowed=false
- secrets_allowed=false
- next_required_phase=Phase 14C

## No Unlock Confirmation

Phase 14B does not unlock:
- general real generation
- backend generation
- deployment
- provider calls
- Supabase
- auth
- database writes
- secrets
- export/download/deploy

## IdeasForgeAI Separation

IdeasForgeAI remains completely separate from IdeasForgeAI.

This phase must not touch:
- IdeasForgeAI files
- IdeasForgeAI production
- IdeasForgeAI GitHub
- IdeasForgeAI Render
- IdeasForgeAI DNS
- IdeasForgeAI credentials

## Phase 14B Completion Criteria

Phase 14B is complete when:
- this route contract document exists
- PROJECT_STATUS.md is updated
- no generated-app files changed
- generated-apps/ideasforgeai-preview-v1 remains untouched
- Phase 12/13 sandbox files remain untouched
- backend compiles
- Studio V3 JS passes node check
- deployment remains locked
- Phase 14C is not implemented

