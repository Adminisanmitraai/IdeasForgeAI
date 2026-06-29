# Phase 13A - Controlled Multi-File Real Generation Planning

Status: Completed, not frozen.

## 1. Phase 13 Purpose

Phase 13 plans the next controlled step from the Phase 12G static HTML/CSS sandbox proof toward controlled multi-file frontend generation.

Phase 13A is planning and architecture only. It does not generate app files, modify Phase 12 sandbox files, unlock production generation, unlock backend generation, deploy, call providers, add Supabase/auth/database writes/secrets, or touch KisanMitraAI production.

## 2. What Phase 12 Proved

Phase 12 proved that IdeasForgeAI can safely define a controlled generation track with:

- Planning and safety boundaries.
- A manifest and file contract schema.
- Real generation dry-run validation.
- A single-file sandbox write.
- Backup and rollback safety for that sandbox file.
- A human approval unlock gate.
- A first controlled HTML/CSS sandbox output with only approved files.

## 3. Why General Real Generation Is Still Locked

General real generation remains locked because multi-file writes introduce larger risk: overwrites, broken app state, unsafe JavaScript, hidden provider calls, accidental deployment files, secrets, database/auth configuration, and accidental writes to existing generated apps.

Phase 13 must keep a deny-by-default model until contract, dry-run, backup, rollback, validation, and human approval checks pass for the exact future sandbox folder and file list.

## 4. What Controlled Multi-File Generation Means

Controlled multi-file generation means deterministic frontend file creation inside one approved sandbox folder, with a pre-approved manifest, exact file list, fixed write order, validation report, backup/rollback requirements, and locked safety flags.

It does not mean production generation, backend generation, provider-based generation, deployment, export/download behavior, or unrestricted generated-app writes.

## 5. Future Allowed Target Sandbox Folder Rules

Future target folders must:

- Live inside `D:/APPS/IdeasForgeAI/generated-apps/`.
- Use a new dedicated Phase 13 sandbox name.
- Not reuse `generated-apps/ideasforgeai-preview-v1/`.
- Not overwrite any existing generated app.
- Not contain path traversal.
- Not point to KisanMitraAI production or any external project.
- Be created only after explicit approval.

## 6. Future Allowed Files

Initial controlled multi-file generation may allow only:

- `index.html`
- `styles.css`
- `app.js`
- `manifest.json`
- `validation-report.md`
- `README.md`

Any extra file requires a later approved contract update.

## 7. Future Blocked Files And Folders

Blocked targets include:

- `generated-apps/ideasforgeai-preview-v1/`
- Existing generated app folders unless explicitly approved in a future contract.
- `backend/`
- `frontend/`
- `docs/` except documentation phases.
- Project root files.
- Deployment config files.
- `.env`, secret, token, key, credential, or connection string files.
- Supabase, auth, database, or migration files.
- KisanMitraAI paths.
- Any path outside `D:/APPS/IdeasForgeAI`.

## 8. Multi-File Write Order

Future controlled writes should use this order:

1. Validate approval payload and target folder.
2. Validate manifest contract.
3. Validate dry-run report.
4. Confirm backup requirement.
5. Confirm rollback requirement.
6. Create target sandbox folder only if approved.
7. Write `manifest.json` first.
8. Write `index.html`.
9. Write `styles.css`.
10. Write `app.js` only after JavaScript safety checks.
11. Write `README.md`.
12. Write `validation-report.md` last.
13. Re-run validation and return metadata.

## 9. Required Manifest Before Write

A manifest must exist in memory before any write and include:

- `project_name`
- `phase`
- `generation_mode`
- `target_folder`
- `allowed_files`
- `blocked_files`
- `human_approval_id`
- `dry_run_validation_id`
- `backup_required`
- `rollback_required`
- `deployment_allowed=false`
- `provider_calls_allowed=false`
- `database_writes_allowed=false`
- `secrets_allowed=false`

## 10. Required Validation Before Write

Before writing, validation must confirm:

- Project is `IdeasForgeAI`.
- Human approval is present and valid.
- Dry-run validation passed.
- Target folder is an approved Phase 13 sandbox folder.
- File list exactly matches the approved contract.
- No blocked paths or blocked file types are present.
- No scripts call external providers.
- No deployment, Supabase, auth, database, or secrets behavior is included.

## 11. Required Backup Before Write

Before any write, the target folder state must be backed up if it exists. Backup metadata must include timestamp, approval id, source folder, file hashes, and rollback instructions.

If the folder does not exist, the backup report must still record that there was no prior folder state.

## 12. Required Rollback After Write

Rollback must be able to restore the previous folder state, remove newly created files, and report exactly which files were restored, removed, skipped, or blocked.

Rollback must not touch any file outside the approved Phase 13 sandbox folder.

## 13. Human Approval Requirements

Human approval must name:

- Target sandbox folder.
- Exact allowed file list.
- Generation mode.
- Dry-run validation result.
- Backup requirement.
- Rollback requirement.
- Deployment lock confirmation.
- Provider-call lock confirmation.
- Supabase/auth/database/secrets lock confirmation.

## 14. Safety Flags That Must Remain Locked

These flags must remain locked through Phase 13A:

- `general_real_generation_unlocked=false`
- `backend_generation_unlocked=false`
- `deployment_unlocked=false`
- `provider_calls_allowed=false`
- `database_writes_allowed=false`
- `supabase_allowed=false`
- `auth_allowed=false`
- `secrets_allowed=false`

## 15. No Deployment Rule

Phase 13 must not add Render, Vercel, Netlify, GitHub Pages, FTP/SFTP, domain, TLS, production sync, or CI/CD deployment behavior.

## 16. No Provider-Call Rule

Phase 13 must not call OpenAI, Anthropic, Google, Azure, local model servers, image providers, OCR services, browser providers, analytics providers, or external generation APIs.

## 17. No Supabase/Auth/Database Rule

Phase 13 must not add Supabase clients, auth flows, schema files, migrations, RLS policies, database writes, storage buckets, realtime channels, or Edge Functions.

## 18. No Secrets Rule

Phase 13 generated outputs must not contain API keys, private keys, tokens, passwords, connection strings, JWT secrets, Supabase service role keys, provider credentials, or `.env` files.

## 19. No KisanMitraAI-Touch Rule

IdeasForgeAI remains separate from KisanMitraAI. Phase 13 must not read from, write to, deploy, sync, reference production paths, or modify KisanMitraAI production.

## 20. Future Preview Runner Requirements

A future local preview runner must:

- Serve only the approved Phase 13 sandbox folder.
- Refuse `generated-apps/ideasforgeai-preview-v1/` unless explicitly part of a separate review.
- Serve only approved static files.
- Avoid deployment behavior.
- Avoid provider calls.
- Return metadata showing generation and deployment locks.

## 21. Future Validation Report Requirements

Future validation reports must include:

- Files written.
- Files blocked.
- Target folder.
- Manifest path.
- Syntax checks.
- Static safety checks.
- Script safety checks for `app.js`.
- CSS import and URL checks.
- No secrets check.
- No deployment check.
- No provider-call check.
- Rollback availability.
- Human approval id.

## 22. Future Phase 13B Plan

Phase 13B - Multi-File Contract + Manifest Upgrade.

Define the exact contract and manifest schema for controlled multi-file generation. No writes yet.

## 23. Future Phase 13C Plan

Phase 13C - Multi-File Dry-Run Validator.

Validate a proposed multi-file generation request and return metadata only. No writes yet.

## 24. Future Phase 13D Plan

Phase 13D - Controlled Multi-File Sandbox Writer.

Write only approved files into one new approved Phase 13 sandbox folder after contract, dry-run, backup, rollback, and human approval checks.

## 25. Final Phase 13 Unlock Checklist

Before any Phase 13 controlled write:

- Phase 13A planning is complete.
- Phase 13B contract is approved.
- Phase 13C dry-run passes.
- Human approval names the target folder and file list.
- Backup plan is ready.
- Rollback plan is ready.
- Manifest is valid.
- Validation report format is ready.
- `generated-apps/ideasforgeai-preview-v1/` remains untouched.
- Existing generated apps remain untouched.
- Backend generation remains locked.
- Deployment remains locked.
- Provider calls remain locked.
- Supabase/auth/database/secrets remain locked.
- KisanMitraAI production remains untouched.

## Recommended Phase 13 Sequence

- Phase 13A - Controlled Multi-File Real Generation Planning
- Phase 13B - Multi-File Contract + Manifest Upgrade
- Phase 13C - Multi-File Dry-Run Validator
- Phase 13D - Controlled Multi-File Sandbox Writer
- Phase 13E - HTML/CSS/JS Controlled Generation
- Phase 13F - Local Preview Runner Integration
- Phase 13G - Generated Output Validation Score
- Phase 13H - Phase 13 Freeze Review