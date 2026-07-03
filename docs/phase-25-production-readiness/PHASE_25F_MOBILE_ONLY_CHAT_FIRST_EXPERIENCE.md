# Phase 25F - Mobile-Only Chat First Experience

Status: Completed, not frozen.

## Purpose

Phase 25F repairs the Studio V3 mobile experience so phones see a dedicated chat-first creation flow instead of the desktop builder shell stacked vertically.

## Scope

- Frontend-only mobile shell refinement.
- Local-only mock state behavior.
- No backend generation.
- No provider calls.
- No database, auth, Supabase, or secrets.
- No deployment changes.

## Desktop Behavior

Desktop widths at 1024px and above preserve the existing Apple-like black/white builder shell:

- Top toolbar remains visible.
- Ranjan Workplace panel remains visible.
- AI Assistant panel remains visible.
- Right preview canvas remains visible.
- Bottom controls remain visible.
- Existing static mock state remains local-only.

## Mobile Behavior

At 767px and below, Studio V3 now presents a dedicated mobile creation flow:

- Desktop toolbar is hidden.
- Desktop AI workspace rail is hidden.
- Desktop preview canvas is hidden on the initial chat screen.
- Desktop bottom controls are hidden.
- The mobile screen uses full viewport width.
- Horizontal overflow is blocked.
- Text and chat bubbles wrap within the viewport.

The first mobile screen shows only:

- IdeasForgeAI icon and name.
- Workspace/project label.
- Local mock state / Preview only status.
- AI intro chat messages.
- Prompt input.
- Prompt chips:
  - Create SaaS landing page
  - Build dashboard app
  - Create booking website
- Start building button.

## Processing Flow

Clicking Start building:

- Adds the user prompt to local in-memory mock chat.
- Sets `mobileFlow.currentStep` to `processing`.
- Sets `mobileFlow.jobStatus` to `processing`.
- Slides the chat screen left with CSS transform.
- Shows the processing screen.

The processing screen includes animated overlapping cards:

- Understanding idea
- Planning product structure
- Designing interface
- Creating preview
- Preparing approval gate

After the mock timeout, the flow sets:

- `mobileFlow.jobStatus = "preview_ready"`
- Preview ready status text.
- View preview button.

## Preview Flow

Clicking View preview:

- Sets `mobileFlow.currentStep` to `preview`.
- Reveals the existing preview canvas locally.
- Does not call backend APIs.
- Does not generate files.
- Does not deploy.

## Safety Boundaries

- No `fetch`.
- No `XMLHttpRequest`.
- No localStorage or sessionStorage.
- No provider calls.
- No Supabase, database, auth, or secrets.
- No real backend generation unlock.
- No upload, OCR, image analysis, pixel reading, or canvas analysis.
- No deployment or deployment config changes.
- IdeasForgeAI was not touched.

## Validation

Required validation for this phase:

- `node --check frontend/pages/studio-v3.js`
- `python -m compileall backend`
- Search Studio V3 frontend files for unsafe terms.
- Open local route:
  - `http://127.0.0.1:8100/frontend/pages/studio-v3.html?v=phase25f-mobile-only-chat`

## Result

Phase 25F makes the mobile Studio V3 experience chat-first while preserving the desktop builder exactly for production-readiness continuity.

