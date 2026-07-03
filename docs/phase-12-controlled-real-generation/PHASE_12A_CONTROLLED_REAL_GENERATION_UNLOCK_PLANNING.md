# Phase 12A - Controlled Real Generation Unlock Planning

Status: Completed, not frozen.

## 1. Phase 12 Purpose

Phase 12 defines how IdeasForgeAI will safely move from preview-only Studio UI into controlled real frontend generation in later approved phases.

Phase 12A is planning only. It does not write generated app files, unlock production generation, call providers, deploy, or modify IdeasForgeAI production.

## 2. Current Locked State

- Phase 11 Builder Workspace is fully frozen.
- Studio V3 shows a preview-only builder workspace with left sidebar, center AI build conversation, and right generated output preview.
- Backend generation remains locked.
- Deployment remains locked.
- Generated-app writes remain locked.
- Provider calls remain locked.
- Supabase, authentication, database writes, and secrets remain locked.

## 3. Why Real Generation Is Still Locked

Real generation is still locked because file writes can create broken apps, overwrite existing work, expose secrets, introduce unsafe deployment behavior, or damage unrelated generated outputs.

Before writes are allowed, IdeasForgeAI needs a strict file contract, dry-run validator, manifest, backup, rollback, validation report, and explicit human approval gate.

## 4. Required Approvals Before File Writes

File writes may only begin after explicit human approval that names:

- Target generated app folder
- Allowed file list
- Approved generation scope
- Backup location
- Rollback expectations
- Validation command expectations
- Confirmation that deployment remains locked

## 5. Safe Generation Target Folder Rules

Future generated files must be written only inside a dedicated approved sandbox folder, for example:

`generated-apps/ideasforgeai-controlled-generation-v1/`

Rules:

- Folder must be created only after approval.
- Folder must not reuse or overwrite `generated-apps/ideasforgeai-preview-v1/`.
- Folder must not point outside `generated-apps/`.
- Folder must not contain path traversal such as `..`.
- Folder must not be a production IdeasForgeAI path.

## 6. Allowed Future Generated File List

Initial controlled frontend generation may only allow a small explicit file list:

- `index.html`
- `styles.css`
- `app.js`
- `manifest.json`
- `README.md`
- `validation-report.json`

Any additional file requires a later approved contract update.

## 7. Blocked Write Locations

Blocked locations include:

- `generated-apps/ideasforgeai-preview-v1/`
- IdeasForgeAI production folders
- `frontend/pages/`
- `backend/`
- `.env` files
- `.git/`
- `.venv/`
- `__pycache__/`
- Any absolute path outside the approved IdeasForgeAI generated app sandbox

## 8. File Write Permission Model

Future writes require a deny-by-default permission model:

- Only approved target folder is writable.
- Only approved file names are writable.
- Existing files cannot be overwritten unless the approval explicitly allows it.
- Binary writes are blocked unless a later image-asset phase approves them.
- Secret-like values are rejected before write.

## 9. Dry-Run Requirement

Every generation request must first run in dry-run mode.

Dry-run must report:

- Intended target folder
- Intended files
- File sizes
- File hashes or preview checksums
- Blocked paths
- Safety flags
- Validation plan
- Whether human approval is still required

Dry-run must not write files.

## 10. Backup Requirement

Before any approved write, IdeasForgeAI must create a backup snapshot of the approved target folder if it already exists.

Backup metadata must include:

- Timestamp
- Target folder
- File list
- File hashes
- Rollback location
- Approval reference

## 11. Rollback Requirement

Every write phase must include a rollback plan.

Rollback must be able to:

- Restore previous files from backup
- Remove newly created files
- Preserve validation logs
- Report rollback success or failure

## 12. Validation Report Requirement

Every future write must produce a validation report.

The report must include:

- Files created
- Files skipped
- Files blocked
- Syntax checks
- Accessibility notes
- Responsive notes
- Design System compliance notes
- Safety lock status
- Approval reference

## 13. Generated App Manifest Requirement

Every generated app folder must include `manifest.json`.

Manifest fields:

- `project_name`
- `generation_phase`
- `created_at`
- `approved_by_human`
- `target_folder`
- `allowed_files`
- `generated_files`
- `blocked_files`
- `design_system_version`
- `product_brain_reference`
- `phase_11_workspace_reference`
- `deployment_allowed`
- `provider_calls_allowed`
- `database_writes_allowed`
- `rollback_available`

## 14. Human Approval Gates

Required gates:

- Approve generation folder
- Approve file contract
- Approve dry-run report
- Approve backup plan
- Approve rollback plan
- Approve first file write
- Approve validation report before any further generation

## 15. Security Limits

Security limits:

- No secrets in frontend files.
- No API keys in generated output.
- No production domains hardcoded.
- No external provider calls.
- No deployment commands.
- No database writes.
- No authentication setup.
- No Supabase configuration.
- No IdeasForgeAI production references or writes.

## 16. No Provider-Call Rule

Phase 12 planning and early unlock phases must use local deterministic generation only.

No OpenAI, Anthropic, Google, Azure, local model server, OCR, image provider, or external generation provider may be called until a later explicit provider phase.

## 17. No Deployment Rule

Deployment remains locked.

Blocked:

- Render deployment
- Netlify deployment
- Vercel deployment
- GitHub Pages deployment
- FTP/SFTP upload
- Production sync
- Domain configuration

## 18. No Supabase/Auth/Database Rule

Phase 12 frontend generation unlock does not add:

- Supabase
- Authentication
- Database schemas
- Database writes
- RLS policies
- Storage buckets
- Edge Functions

## 19. No Secrets Rule

Generated files must not contain:

- API keys
- Private keys
- Tokens
- Passwords
- Connection strings
- JWT secrets
- Supabase service role keys
- Provider credentials

## 20. No IdeasForgeAI-Touch Rule

IdeasForgeAI remains separate from IdeasForgeAI.

Phase 12 must not read from, write to, deploy, sync, or modify IdeasForgeAI production folders.

## 21. Future Phase 12B Plan

Phase 12B - Generation File Contract + Manifest Schema.

Define the exact request/response schema for approved generated file contracts and `manifest.json`. No writes yet.

## 22. Future Phase 12C Plan

Phase 12C - Real Generation Dry-Run Validator.

Implement a dry-run validator that reports intended files, blocked paths, safety flags, and validation plan without writing files.

## 23. Future Phase 12D Plan

Phase 12D - Single-File Write Sandbox.

Allow one approved file write into a new approved sandbox folder only after dry-run approval and backup confirmation.

## 24. Future Phase 12E Plan

Phase 12E - Rollback + Backup System.

Add backup metadata, rollback records, restore flow, and validation report persistence.

## 25. Recommended Final Unlock Checklist

Before real generation unlock:

- Phase 12A planning complete.
- Phase 12B file contract approved.
- Phase 12C dry-run validator passed.
- Phase 12D sandbox write approved.
- Phase 12E backup and rollback passed.
- Phase 12F human approval gate passed.
- Generated-app writes limited to approved sandbox.
- `generated-apps/ideasforgeai-preview-v1/` untouched.
- Backend generation locked.
- Deployment locked.
- Provider calls locked.
- Supabase/auth/database locked.
- Secrets scan passed.
- IdeasForgeAI production untouched.

## Recommended Future Phase 12 Sequence

- Phase 12A - Controlled Real Generation Unlock Planning
- Phase 12B - Generation File Contract + Manifest Schema
- Phase 12C - Real Generation Dry-Run Validator
- Phase 12D - Single-File Write Sandbox
- Phase 12E - Rollback + Backup System
- Phase 12F - Human Approval Unlock Gate
- Phase 12G - First Controlled HTML/CSS Generation
- Phase 12H - Phase 12 Freeze Review

