# Phase 11A - Builder Workspace Architecture

Generated at: 2026-06-26T22:02:18

Status: Completed, not frozen.

## Purpose

Phase 11A defines the real IdeasForgeAI Builder Workspace architecture.

This is the workspace users will use after the polished landing preview phase.

Phase 11A is architecture-only.

## Source of truth

- Phase 10 generated app polish track is frozen.
- Generated preview remains isolated to generated-apps/ideasforgeai-preview-v1/.
- Deployment remains locked.
- IdeasForgeAI production must not be touched.

Phase 10 ready check: True

## Workspace layout

The Builder Workspace will use a three-panel professional layout.

### 1. Left Sidebar

Purpose:

- Project history
- Current project list
- Page tree
- File tree preview
- Builder sessions
- Saved ideas
- App type/category shortcuts

Planned sections:

- Workspace switcher
- Recent projects
- Current build pages
- Generated files preview
- Approval checkpoints
- Settings shortcut

### 2. Center AI Chat / Build Conversation

Purpose:

- Main AI build conversation
- Idea input
- Follow-up questions
- Product Brain output
- Design System output
- Generation planning
- Approval actions

Planned sections:

- Conversation timeline
- AI build cards
- User idea messages
- Approval request cards
- Composer with text, mic, upload placeholder
- Build status rail

### 3. Right Live Preview / Inspector

Purpose:

- Live preview of generated page/app
- Device preview
- Selected component inspector
- Generated output summary
- Safety/lock status

Planned sections:

- Preview iframe placeholder
- Desktop/tablet/mobile toggle
- Page inspector
- Component metadata
- Generation safety locks
- Validation status

## Phase 11 planned gates

### Phase 11A
Builder Workspace Architecture only.

### Phase 11B
Left Sidebar + Center Chat Layout.

### Phase 11C
Chat Composer + AI Build Conversation UI.

### Phase 11D
Right Live Preview / Generated Output Panel.

### Phase 11E
Project Memory + Page/File Tree Preview.

### Phase 11F
Workspace State and Safety Locks.

### Phase 11G
Builder Workspace Freeze Review.

## Files allowed in future UI phases

Future approved Phase 11 UI phases may modify:

- frontend/pages/studio-v3.html
- frontend/pages/studio-v3.css
- frontend/pages/studio-v3.js

Future phases may add isolated docs in:

- docs/phase-11-builder-workspace/

## Files not allowed without explicit approval

- generated-apps/ideasforgeai-preview-v1/
- backend production logic
- deployment config
- Supabase/auth/database config
- secrets
- IdeasForgeAI folders or production files

## Safety locks

- builder_workspace_architecture_allowed=true
- studio_v3_layout_change_allowed=false
- generated_preview_modification_allowed=false
- backend_generation_allowed=false
- deployment_allowed=false
- provider_calls_allowed=false
- database_writes_allowed=false
- supabase_allowed=false
- auth_allowed=false
- secrets_allowed=false
- approval_required=true

## Next step

Phase 11A Freeze Review, then Phase 11B - Left Sidebar + Center Chat Layout.

