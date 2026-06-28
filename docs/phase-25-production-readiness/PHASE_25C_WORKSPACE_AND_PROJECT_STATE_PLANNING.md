# Phase 25C - Workspace and Project State Planning

Status: Completed, not frozen

Date: 2026-06-28

Scope: documentation and planning only.

This phase defines the future production state model for IdeasForgeAI workspaces, projects, pages, chat messages, preview state, and approval gates. It does not modify frontend behavior, backend APIs, database, auth, provider integrations, secrets, deployment, OCR, upload, image analysis, pixel reading, or canvas analysis.

## 1. Workspace Model

Purpose: represents the top-level account or team space where projects live.

Fields:

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `workspace_id` | string | Yes | Stable unique workspace identifier |
| `workspace_name` | string | Yes | User-visible workspace name |
| `owner_user_id` | string | Yes, future | Owner account identifier after auth exists |
| `plan_type` | string | Yes | Example values: `free`, `pro`, `team`, `enterprise` |
| `created_at` | ISO datetime | Yes | Workspace creation timestamp |
| `updated_at` | ISO datetime | Yes | Last workspace update timestamp |
| `status` | string | Yes | Example values: `active`, `paused`, `archived` |

Initial static-shell placeholder:

```json
{
  "workspace_id": "workspace_local_ranjan",
  "workspace_name": "Ranjan Workplace",
  "owner_user_id": "local_user_pending_auth",
  "plan_type": "local_preview",
  "created_at": "2026-06-28T00:00:00Z",
  "updated_at": "2026-06-28T00:00:00Z",
  "status": "active"
}
```

## 2. Project Model

Purpose: represents one app, site, product, or builder output inside a workspace.

Fields:

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `project_id` | string | Yes | Stable unique project identifier |
| `workspace_id` | string | Yes | Parent workspace |
| `project_name` | string | Yes | User-visible project name |
| `project_type` | string | Yes | Example values: `saas_landing_page`, `dashboard_app`, `marketplace`, `crm`, `custom` |
| `current_phase` | string | Yes | Current build/planning phase |
| `approval_status` | string | Yes | Example values: `not_required`, `pending`, `approved`, `rejected` |
| `preview_status` | string | Yes | Example values: `not_started`, `mock`, `generated`, `validated`, `stale` |
| `created_at` | ISO datetime | Yes | Project creation timestamp |
| `updated_at` | ISO datetime | Yes | Last project update timestamp |

Initial static-shell placeholder:

```json
{
  "project_id": "project_local_saas_landing",
  "workspace_id": "workspace_local_ranjan",
  "project_name": "SaaS Landing Page",
  "project_type": "saas_landing_page",
  "current_phase": "static_builder_preview",
  "approval_status": "not_required",
  "preview_status": "mock",
  "created_at": "2026-06-28T00:00:00Z",
  "updated_at": "2026-06-28T00:00:00Z"
}
```

## 3. Page Model

Purpose: represents a page or route inside a generated app/site plan.

Fields:

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `page_id` | string | Yes | Stable unique page identifier |
| `project_id` | string | Yes | Parent project |
| `page_name` | string | Yes | User-visible page name |
| `route_path` | string | Yes | Example: `/`, `/pricing`, `/dashboard` |
| `page_type` | string | Yes | Example values: `landing`, `pricing`, `dashboard`, `auth`, `settings`, `custom` |
| `layout_status` | string | Yes | Example values: `mock`, `planned`, `approved`, `needs_revision` |
| `generated_status` | string | Yes | Example values: `not_generated`, `preview_only`, `generated`, `validated`, `stale` |

Initial static-shell placeholder:

```json
{
  "page_id": "page_local_home",
  "project_id": "project_local_saas_landing",
  "page_name": "Home",
  "route_path": "/",
  "page_type": "landing",
  "layout_status": "mock",
  "generated_status": "preview_only"
}
```

## 4. Chat Message Model

Purpose: represents AI Assistant and user messages inside the builder conversation.

Fields:

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `message_id` | string | Yes | Stable unique message identifier |
| `project_id` | string | Yes | Parent project |
| `sender_type` | string | Yes | Example values: `user`, `assistant`, `system` |
| `message_text` | string | Yes | Message body |
| `created_at` | ISO datetime | Yes | Message timestamp |
| `linked_action` | string or null | No | Optional related action such as `generate_preview`, `approve_strategy`, `revise_design` |
| `approval_required` | boolean | Yes | Whether this message asks for explicit approval before side effects |

Initial static-shell placeholder:

```json
{
  "message_id": "message_local_001",
  "project_id": "project_local_saas_landing",
  "sender_type": "assistant",
  "message_text": "I redesigned the app into a graphite builder shell with a white preview canvas and a SaaS landing page draft.",
  "created_at": "2026-06-28T00:00:00Z",
  "linked_action": null,
  "approval_required": false
}
```

## 5. Preview State Model

Purpose: represents a preview artifact and its validation state.

Fields:

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `preview_id` | string | Yes | Stable unique preview identifier |
| `project_id` | string | Yes | Parent project |
| `preview_url` | string | Yes | Local or production preview URL |
| `source_type` | string | Yes | Example values: `static_mock`, `local_generated`, `approved_generated`, `deployed` |
| `status` | string | Yes | Example values: `draft`, `ready`, `valid`, `invalid`, `stale` |
| `generated_files` | array | Yes | File paths created or referenced by preview; empty for static mock |
| `last_validated_at` | ISO datetime or null | No | Last validation timestamp |

Initial static-shell placeholder:

```json
{
  "preview_id": "preview_local_studio_v3",
  "project_id": "project_local_saas_landing",
  "preview_url": "/pages/studio-v3.html",
  "source_type": "static_mock",
  "status": "valid",
  "generated_files": [],
  "last_validated_at": "2026-06-28T00:00:00Z"
}
```

## 6. Approval Gate Model

Purpose: records explicit approval requirements before side effects.

Fields:

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `approval_id` | string | Yes | Stable unique approval identifier |
| `project_id` | string | Yes | Parent project |
| `phase` | string | Yes | Phase requiring approval |
| `approval_type` | string | Yes | Example values: `strategy`, `design`, `preview_generation`, `file_write`, `backend_generation`, `provider_setup`, `database_setup`, `deployment` |
| `approved_by` | string or null | No | Future user identifier after auth exists |
| `approved_at` | ISO datetime or null | No | Approval timestamp |
| `approval_status` | string | Yes | Example values: `not_required`, `pending`, `approved`, `rejected`, `expired` |
| `rollback_available` | boolean | Yes | Whether a rollback path exists for the approved action |

Initial static-shell placeholder:

```json
{
  "approval_id": "approval_local_none",
  "project_id": "project_local_saas_landing",
  "phase": "static_builder_preview",
  "approval_type": "preview_generation",
  "approved_by": null,
  "approved_at": null,
  "approval_status": "not_required",
  "rollback_available": true
}
```

## 7. Local Frontend State Plan

The current frontend may temporarily hold mock state in JavaScript in a future approved phase. This should remain local-only and non-persistent until auth/database planning is separately approved.

Temporary frontend state fields:

| Field | Purpose | Persistence |
| --- | --- | --- |
| `selected_workspace` | Currently selected workspace display object | In-memory only |
| `selected_project` | Currently selected project display object | In-memory only |
| `selected_preview_mode` | Current preview mode such as `desktop`, `tablet`, or `mobile` | In-memory only |
| `chat_messages_mock` | Static/local mock chat transcript | In-memory only |
| `current_builder_status` | Local status label such as `saved`, `draft`, `needs_approval` | In-memory only |

Rules for temporary frontend state:
- It must not use `localStorage` or `sessionStorage` unless a later phase explicitly approves browser persistence.
- It must not call backend APIs.
- It must not write files.
- It must not call providers.
- It must not include secrets.
- It must be easy to replace with a real API/database model later.

## 8. Future Database Plan

Real persistence must come later in a separate approved phase.

Current Phase 25C database policy:
- No database added now.
- No Supabase added now.
- No auth added now.
- No migrations added now.
- No database writes added now.
- No secrets added now.

Future database planning should define:
- Workspace table.
- Project table.
- Page table.
- Chat message table.
- Preview artifact table.
- Approval gate table.
- Ownership and access rules.
- Audit trail.
- Rollback strategy.
- Backup policy.

## 9. Safety Rules

Phase 25C safety rules:
- No real writes.
- No backend generation.
- No provider calls.
- No secrets.
- No Supabase/auth/database.
- No deployment.
- No OCR.
- No upload.
- No image analysis.
- No pixel reading.
- No canvas analysis.
- No KisanMitraAI files, services, domains, credentials, or status files.

## 10. Recommended Next Phase

Recommended next phase: Phase 25D - Safe Frontend Mock State Integration.

Phase 25D should:
- Add local-only mock state to the Studio V3 frontend.
- Keep state in memory only.
- Use the Phase 25C model names as guidance.
- Avoid backend APIs.
- Avoid database/auth/provider/secrets.
- Avoid deployment changes.
- Preserve the current Apple-like black/white builder layout.

## Acceptance Confirmation

Confirmed:
- Workspace/project state planning created.
- Workspace, project, page, chat message, preview state, and approval gate models defined.
- Local temporary frontend state plan defined.
- Future database plan documented.
- No frontend behavior changes.
- No backend API changes.
- No backend generation/provider/database/auth/secrets/deployment added.
- KisanMitraAI not touched.
