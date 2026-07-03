# Phase 25G - Mobile Production Chat App Shell

Status: Completed, not frozen.

## Purpose

Phase 25G turns the Studio V3 mobile experience into a polished production-style chat app shell while preserving the existing desktop builder.

## Mobile Production Chat Shell

For mobile widths at 767px and below:

- The mobile creation flow owns the viewport.
- The header is compact and app-like.
- The IdeasForgeAI icon and name are shown clearly.
- A small Ready status pill is shown.
- The chat body scrolls independently.
- The composer remains available at the bottom.
- Safe-area padding and `100dvh` sizing remain active.
- Horizontal overflow is prevented.

## User-Facing Test Text Removed

Mobile no longer shows user-facing internal/test wording such as:

- Preview only / Local mock state
- Mobile builder
- Local mock
- Developer safety copy
- Desktop mock-state chat messages

Safety information remains documented in project reports and status files, not in the user-facing mobile chat screen.

## Welcome-First Chat Experience

The mobile chat starts with:

> Hi, I'm IdeasForgeAI. Tell me what you want to build, and I'll turn your idea into a polished app or website preview.

Then a helper line:

> Describe your product, audience, and the outcome you want.

## Composer Behavior

The mobile composer is local-only and live-chat-ready:

- User can type a message.
- Pressing Build adds the user message immediately.
- IdeasForgeAI replies locally:
  - Got it. I'm turning this into a product plan and preview flow.
- The flow then slides into the processing screen.

No backend API, provider call, storage, auth, or database integration is active.

## Processing Flow Polish

The processing screen now uses production-facing stage labels:

- Understanding your idea
- Creating product structure
- Designing the interface
- Preparing responsive preview
- Creating approval checkpoint

Cards remain animated with CSS only.

After the local mock completion:

- Preview ready appears.
- View preview becomes available.

## Preview Screen

The mobile preview step includes:

- Compact Preview ready header.
- Back to chat button.
- Existing local preview canvas.

## Deferred Integration

Real chat, backend generation, provider calls, auth, database, storage, billing, and deployment are deferred to later explicitly approved phases.

## Safety Boundaries

- No `fetch`.
- No `XMLHttpRequest`.
- No localStorage or sessionStorage.
- No provider calls.
- No Supabase, database, auth, or secrets.
- No real backend generation unlock.
- No upload, OCR, image analysis, pixel reading, or canvas analysis.
- No deployment changes.
- IdeasForgeAI was not touched.

## Validation

Required validation:

- `node --check frontend/pages/studio-v3.js`
- `python -m compileall backend`
- Unsafe frontend scan for blocked terms.
- Local route:
  - `http://127.0.0.1:8100/frontend/pages/studio-v3.html?v=phase25g-mobile-production-chat`
- LAN route:
  - `http://192.168.1.7:8100/frontend/pages/studio-v3.html?v=phase25g-mobile-production-chat`

