# Phase 14A — Live Preview Runner Integration Planning

Status: Completed, not frozen.

## 1. Phase 14 Purpose

Phase 14 defines how IdeasForgeAI will safely render controlled generated frontend output inside Studio V3 through a local live preview runner.

The goal is to move beyond metadata-only preview and prepare a safe rendered preview experience, while keeping deployment, provider calls, database writes, secrets, and general real generation locked.

## 2. What Phase 13 Proved

Phase 13 proved:
- Controlled multi-file generation planning.
- Multi-file contract and manifest schema.
- Multi-file dry-run validation.
- Controlled multi-file sandbox writing.
- Controlled HTML/CSS/JS sandbox generation.
- Local preview runner metadata.
- Generated output validation scoring.
- Phase 13G validation score reached 100.
- generated-apps/ideasforgeai-preview-v1 remained untouched.
- General real generation remained locked.
- Backend generation remained locked.
- Deployment remained locked.

## 3. Why Deployment Remains Locked

Deployment remains locked because Phase 14 is only about safe local preview rendering.

No Render, GitHub Pages, domain, production hosting, export, download, or deploy action is allowed in Phase 14A.

## 4. What Live Preview Runner Means

Live Preview Runner means a controlled local mechanism that can display a generated frontend output from an approved sandbox folder inside Studio V3.

It is not production deployment.
It is not public hosting.
It is not provider execution.
It is not backend app generation.

## 5. Metadata Preview vs Rendered Preview

Metadata preview shows:
- target folder
- entry file
- allowed files
- safety flags
- validation score

Rendered preview will show:
- actual generated HTML/CSS/JS output
- inside a safe preview boundary
- only after validation
- only from an approved sandbox folder

## 6. Allowed Preview Target Folder Rules

Allowed preview target for the next safe phases:

D:/APPS/IdeasForgeAI/generated-apps/_phase13e_controlled_html_css_js_generation/

The preview runner may only reference files inside the approved sandbox folder.

## 7. Blocked Preview Target Folders

Blocked:
- generated-apps/ideasforgeai-preview-v1
- generated-apps/_phase12d_write_sandbox
- generated-apps/_phase12e_backup_sandbox
- generated-apps/_phase12g_controlled_html_css_generation
- generated-apps/_phase13d_multi_file_write_sandbox
- backend/
- frontend/pages/
- frontend/shared/
- docs/
- project root files
- deployment config
- env/secrets files
- KisanMitraAI folders
- any path outside D:/APPS/IdeasForgeAI

## 8. Safe Preview Serving Rules

Preview serving must:
- be read-only
- serve only approved static files
- never expose backend source files
- never expose frontend source files
- never expose docs
- never expose root files
- never expose secrets
- never expose deployment config
- never expose KisanMitraAI files
- never allow arbitrary path input
- never write files
- never delete files
- never modify files

## 9. Iframe Risk Policy

Iframe embedding must remain locked until a dedicated embed gate validates:
- allowed source path
- same-origin route
- no external scripts
- no iframe inside generated page
- no external URL
- no provider call
- no database/auth/Supabase call
- no secrets
- no unsafe postMessage behavior

Phase 14A does not add iframe rendering.

## 10. Same-Origin Local Preview Policy

Future preview should use same-origin local backend routes under:

http://127.0.0.1:8100

The preview route must not expose arbitrary folders.

## 11. Static-File Serving Limitations

Only static generated app files may be considered for preview:
- index.html
- styles.css
- app.js
- manifest.json
- README.md
- validation-report.md

No backend code execution is allowed.

## 12. Allowed Files for Preview

Allowed preview files:
- index.html
- styles.css
- app.js
- manifest.json
- README.md
- validation-report.md

## 13. Blocked File Types

Blocked:
- .env
- .key
- .pem
- .json secrets
- deployment files
- backend source files
- database files
- auth files
- Supabase files
- executable scripts
- shell scripts
- PowerShell scripts
- unknown binary files

## 14. No Backend Exposure Rule

The preview runner must never expose:
- backend/
- backend/main.py
- backend/frontend_generator/
- backend secrets
- Python source files

## 15. No Frontend Source Exposure Rule

The preview runner must never expose:
- frontend/pages/
- frontend/shared/
- Studio V3 source files
- internal UI files

## 16. No Docs / Root / Secrets Exposure Rule

The preview runner must never expose:
- docs/
- PROJECT_STATUS.md
- root package files
- git files
- env files
- secrets
- deployment config

## 17. No Provider-Call Rule

The preview runner must not call:
- OpenAI
- external APIs
- provider SDKs
- analytics
- telemetry
- external scripts

## 18. No Deployment Rule

The preview runner must not deploy, publish, push, upload, export, or host publicly.

## 19. No Supabase / Auth / Database Rule

The preview runner must not connect to:
- Supabase
- auth systems
- databases
- user accounts
- credentials
- sessions

## 20. No KisanMitraAI-Touch Rule

IdeasForgeAI remains completely separate from KisanMitraAI.

Phase 14 must not touch:
- KisanMitraAI files
- KisanMitraAI GitHub
- KisanMitraAI Render
- KisanMitraAI DNS
- KisanMitraAI credentials
- KisanMitraAI production

## 21. Future Studio V3 Right-Panel Preview Behavior

Future Studio V3 right preview may show:
- preview runner status
- validation score
- approved target folder
- entry file
- preview-only badge
- no deployment badge
- no provider call badge
- no database write badge
- no secrets badge

Rendered preview may be added only after Phase 14C/14D safety gates.

## 22. Future Preview Status Endpoint Behavior

Future endpoint should return metadata only:
- status
- preview_runner_ready
- preview_target_folder
- preview_entry_file
- allowed_files_found
- blocked_files_found
- validation_score
- file_write_allowed=false
- folder_creation_allowed=false
- generation_allowed=false
- deployment_unlocked=false
- provider_calls_allowed=false
- database_writes_allowed=false
- secrets_allowed=false

## 23. Future Validation-Before-Preview Requirement

Before any rendered preview is shown:
- Phase 13G validation score must be available.
- Required files must exist.
- No extra files must exist.
- No external scripts.
- No external URLs.
- No iframe.
- No provider/database/auth/secrets markers.
- KisanMitraAI reference must be absent.

## 24. Future Phase 14B Plan

Phase 14B — Safe Static Preview Route Contract:
- define exact preview URL contract
- define allowed route path
- define blocked route paths
- define same-origin policy
- keep route contract metadata-only if needed

## 25. Future Phase 14C Plan

Phase 14C — Read-Only Preview File Server:
- serve approved static files only
- serve only Phase 13E sandbox output
- no file writes
- no folder creation
- no arbitrary path access

## 26. Future Phase 14D Plan

Phase 14D — Studio V3 Preview Panel Embed Gate:
- add safe embed gate
- decide iframe vs safe preview shell
- keep security labels visible
- avoid breaking frozen Phase 11 workspace

## 27. Future Phase 14E Plan

Phase 14E — Preview Runner Validation + Freeze Review:
- validate preview route
- validate Studio V3 right panel
- validate no unsafe file exposure
- freeze Phase 14

## 28. Final Phase 14 Unlock Checklist

Before Phase 14 can be frozen:
- Preview target folder is approved.
- Preview route is same-origin.
- Preview route is read-only.
- Only approved files are served.
- No backend source is exposed.
- No frontend source is exposed.
- No docs/root/secrets are exposed.
- No deployment is added.
- No provider calls are added.
- No Supabase/auth/database is added.
- No KisanMitraAI files are touched.
- Studio V3 remains stable.
- Phase 11 workspace remains frozen.
- generated-apps/ideasforgeai-preview-v1 remains untouched.

## 29. Phase 14A Safety Confirmation

Phase 14A is planning only.

No generated app files were changed.
No Phase 12 sandbox files were changed.
No Phase 13 sandbox files were changed.
generated-apps/ideasforgeai-preview-v1 was not touched.
General real generation remains locked.
Backend generation remains locked.
Deployment remains locked.
Provider calls remain locked.
Supabase/auth/database/secrets remain locked.
KisanMitraAI production was not touched.
Phase 14B was not implemented.
