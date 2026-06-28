# Phase 25A - Production Readiness Architecture

Status: Completed, not frozen

Date: 2026-06-28

Scope: documentation and planning only.

This phase does not modify the live frontend, deployment configuration, backend generation, provider integrations, authentication, database, billing, secrets, OCR, image analysis, pixel reading, canvas analysis, uploads, or production automation.

## 1. Current State

IdeasForgeAI currently has a polished Apple-like black/white frontend shell live in production.

Current production references:
- GitHub repo: `https://github.com/Adminisanmitraai/IdeasForgeAI.git`
- Render service: `ideasforgeai-web`
- Live URL: `https://www.ideasforgeai.com`
- Live studio: `https://www.ideasforgeai.com/pages/studio-v3.html`
- Render publish directory: `frontend`

Current product state:
- The Apple-like frontend shell is live.
- The UI is mostly static and visual.
- Real app/site generation is not unlocked.
- Backend generation is not unlocked.
- No provider/API-call layer is connected.
- No Supabase, authentication, database, or secrets layer is connected.
- Deployment automation is not added.
- Export/deploy workflows are not enabled.

The current frontend should be treated as the visual product shell and not as proof that production generation, accounts, persistence, billing, or deployment are ready.

## 2. Production Product Goal

IdeasForgeAI should become a real AI app builder product where a founder can type a rough idea and receive a structured, editable build plan and preview.

The founder should be able to receive:
- Product strategy
- App/site structure
- Page sections
- Visual direction
- Responsive frontend preview
- Editable project workspace
- Approval-gated generation
- Export/deploy later

The product should preserve a high-trust workflow:
- The AI proposes and explains.
- The founder reviews and edits.
- Generation happens only after explicit approval.
- File writes, provider calls, database changes, and deployment remain gated by phase and user approval.

## 3. Production Modules Needed

### Frontend App Shell

Owns the visible Studio experience:
- Top toolbar
- Workspace selector
- AI Assistant panel
- Preview canvas
- Project controls
- Device/zoom controls
- Future route surfaces for Code, Database, Billing, and Deployment

Initial production focus: keep the current layout, clean the semantic structure, and improve maintainability without changing product behavior.

### Workspace / Project Manager

Owns project lifecycle:
- Create project
- Rename project
- Select project
- Track project status
- Store current phase/state
- Track artifacts produced by Product Brain, Design System, Preview Generator, and Code Generator

Future persistence must be added only after explicit database/auth planning approval.

### AI Assistant Conversation Layer

Owns user-facing build conversation:
- Receives founder idea
- Asks clarifying questions
- Tracks decisions
- Routes tasks to Product Brain, Design System, Preview Generator, and Code Generator
- Presents proposals and approval checkpoints

Provider calls must remain locked until a separate provider/API-key setup phase is approved.

### Product Brain Engine

Owns product thinking:
- Idea understanding
- Target user
- Problem statement
- Positioning
- Feature scope
- MVP definition
- Page/app structure
- Requirements
- Launch priorities

The Product Brain should produce structured artifacts before any code generation is considered.

### Design System Engine

Owns visual language:
- Brand personality
- Typography direction
- Color system
- Spacing scale
- Component style
- Layout patterns
- Responsive behavior rules

The engine should output editable design tokens and design rationale before preview generation.

### Preview Generator Engine

Owns static preview generation:
- Landing page preview
- App dashboard preview
- Multi-section page preview
- Responsive preview
- Local-only rendered artifacts

Preview generation should be approval-gated and sandboxed before any production write path is enabled.

### Code Generator Engine

Owns eventual generated project source:
- HTML/CSS/JS generation
- Framework-specific frontend generation later
- Backend source generation later
- Test scaffold generation later
- Export packaging later

Backend generation remains locked until a separate approval phase.

### Approval Gate Engine

Owns explicit user approvals:
- Approve product strategy
- Approve design system
- Approve preview generation
- Approve file writes
- Approve backend generation
- Approve provider/API setup
- Approve database/auth setup
- Approve export/deployment

Every action with side effects must pass through a visible approval gate.

### File / Project Storage

Owns durable project artifacts:
- Project metadata
- Conversation summaries
- Product Brain output
- Design tokens
- Generated previews
- Approved files
- Rollback snapshots
- Validation reports

Storage must be planned before database or object-storage implementation.

### Auth / Account System

Owns users and access:
- Sign up/sign in
- Account ownership
- Project ownership
- Workspace membership
- Session security
- Role/permission model

Auth must not be implemented until a dedicated auth planning phase is approved.

### Billing / Credits System

Owns monetization and usage:
- Credits
- Plans
- Usage events
- Provider-cost mapping
- Limits
- Invoices/subscriptions later

Billing must be planned before any paid production usage.

### Deployment / Export System

Owns final delivery:
- Download/export project
- GitHub export later
- Static deploy later
- Render deploy later
- Custom domain later

Deployment automation requires separate approval and must never be silently enabled.

### Admin / Observability System

Owns operational visibility:
- Build logs
- Generation events
- Error tracking
- Safety gate audit trail
- Usage metrics
- Admin review tools

Observability should be added before broad beta usage.

## 4. Safe Phase Sequence

### Phase 25B: Frontend App Shell Cleanup

Goal: clean and stabilize the existing static frontend shell.

Allowed:
- Modify frontend structure/styles/scripts only as approved.
- Keep current layout.
- Improve semantic HTML structure.
- Split UI sections clearly.
- Improve responsive behavior.

Locked:
- No backend generation.
- No provider calls.
- No auth/database.
- No secrets.
- No deployment changes.

### Phase 25C: Workspace and Project State

Goal: define local project/workspace state contracts.

Allowed:
- Add frontend-only local state model or documentation/contracts.
- Define project metadata shape.
- Define workspace selection behavior.

Locked:
- No database writes.
- No auth.
- No provider calls.
- No deployment changes.

### Phase 25D: Backend API Contract

Goal: define backend API request/response contracts before implementation.

Allowed:
- Add contract documents and static schemas.
- Add dry-run endpoints only if separately approved.

Locked:
- No real generation.
- No provider calls.
- No database writes.
- No secrets.
- No deployment changes.

### Phase 25E: AI Build Conversation API

Goal: introduce a safe conversation API boundary.

Allowed:
- Local deterministic responses or dry-run API behavior.
- Typed conversation contracts.

Locked:
- No provider calls unless separately approved.
- No secrets.
- No database writes.
- No deployment changes.

### Phase 25F: Product Brain Real API

Goal: expose structured Product Brain output through a real API.

Allowed:
- Product strategy, requirements, and build-plan API responses.
- Local deterministic engine first.

Locked:
- No provider calls unless separately approved.
- No code generation.
- No deployment changes.

### Phase 25G: Design System Real API

Goal: expose structured design-system output.

Allowed:
- Design tokens.
- Component style rules.
- Layout guidance.

Locked:
- No image/OCR/pixel/canvas analysis.
- No provider calls unless separately approved.
- No deployment changes.

### Phase 25H: Preview Generator

Goal: generate safe static previews from approved artifacts.

Allowed:
- Local static preview generation after approval.
- Sandbox-only file writes if separately approved.
- Validation and rollback reports.

Locked:
- No backend generation.
- No deployment.
- No provider calls unless separately approved.

### Phase 25I: Approval Gates

Goal: centralize approval controls for side effects.

Allowed:
- Approval metadata.
- Approval UI.
- Approval contracts.
- Dry-run gate validation.

Locked:
- No automatic deployment.
- No automatic provider setup.
- No automatic database/auth setup.

### Phase 25J: Auth Planning

Goal: plan account and project ownership.

Allowed:
- Auth architecture document.
- Role and permission model.
- Session/security requirements.

Locked:
- No auth implementation.
- No secrets.
- No database changes.

### Phase 25K: Database Planning

Goal: plan persistence.

Allowed:
- Data model document.
- Migration strategy.
- RLS/security plan.
- Backup/rollback plan.

Locked:
- No database implementation.
- No Supabase connection.
- No secrets.

### Phase 25L: Billing Planning

Goal: plan usage, credits, and billing.

Allowed:
- Billing architecture.
- Credit model.
- Usage-event schema.
- Provider-cost mapping plan.

Locked:
- No payment provider integration.
- No secrets.
- No billing automation.

### Phase 25M: Deployment Planning

Goal: plan export/deployment safely.

Allowed:
- Deployment architecture document.
- Export flow design.
- Rollback and approval model.

Locked:
- No deployment automation.
- No live publish changes.
- No credentials.

### Phase 25N: Production QA

Goal: validate readiness before wider production usage.

Allowed:
- QA checklist.
- Security checklist.
- Runtime validation.
- Rollback validation.
- Manual browser QA.

Locked:
- No new features unless separately approved.
- No deployment changes unless separately approved.

## 5. Safety Gates Required For Every Future Phase

Every future phase must explicitly declare:
- Whether it modifies frontend.
- Whether it modifies backend.
- Whether it adds generation.
- Whether it adds provider calls.
- Whether it adds auth/database.
- Whether it touches secrets.
- Whether it affects deployment.
- Whether rollback is possible.

Required safety table for future phase documents:

| Safety question | Required answer |
| --- | --- |
| Modifies frontend? | Yes/No, with file list |
| Modifies backend? | Yes/No, with file list |
| Adds generation? | Yes/No, with scope |
| Adds provider calls? | Yes/No, with provider and key handling |
| Adds auth/database? | Yes/No, with system and data model |
| Touches secrets? | Yes/No, with storage policy |
| Affects deployment? | Yes/No, with rollback path |
| Rollback possible? | Yes/No, with exact rollback method |

No phase should proceed if the safety answers are ambiguous.

## 6. Recommended First Real Coding Phase

Recommended next phase: Phase 25B - Frontend App Shell Cleanup.

Phase 25B should:
- Keep the current Apple-like black/white builder layout.
- Clean HTML semantic structure.
- Split UI sections clearly.
- Improve responsive behavior.
- Preserve the current visual direction.
- Preserve local/static behavior.
- Avoid backend generation.
- Avoid provider calls.
- Avoid auth/database.
- Avoid deployment changes.

Phase 25B is the safest first real coding step because it improves maintainability without unlocking production risk.

## 7. Deployment Policy

Production deployment remains gated.

Policy:
- Live frontend updates are allowed only after local validation.
- Backend generation unlock requires separate approval.
- Provider/API-key setup requires separate approval.
- Database/auth requires separate approval.
- Deployment automation requires separate approval.
- Secrets must never be committed.
- `.env`, API keys, tokens, `node_modules`, cache folders, backup folders, and temporary files must not be committed.
- Rollback must be documented before any production-facing change.

Current Phase 25A deployment result:
- No deployment was performed.
- No deployment files were changed.
- No Render configuration was changed.
- No GitHub automation was changed.

## Phase 25A Acceptance Confirmation

Confirmed:
- Production readiness architecture created.
- Current frontend is live and static.
- Production module plan defined.
- Future phase sequence defined.
- Safety gates defined.
- Recommended first coding phase is Phase 25B Frontend App Shell Cleanup.
- No live frontend changes.
- No backend generation.
- No provider calls.
- No Supabase/auth/database/secrets.
- No deployment changes.
- KisanMitraAI was not touched.
