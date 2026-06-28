# Phase 25I - Mobile Light Chat Interface Alignment

Status: Completed, not frozen.

## Approved Mobile Direction

Phase 25I aligns the mobile IdeasForgeAI experience with the approved clean, light, ChatGPT-like app direction. The mobile viewport now uses a very light gray background, white surfaces, soft shadows, rounded cards, and minimal app-like spacing instead of the previous heavy dark mobile shell.

Desktop behavior remains preserved for widths at or above 1024px.

## Header Alignment

- Added a compact three-line menu button on the far left.
- Kept the IdeasForgeAI logo immediately after the menu.
- Kept the IdeasForgeAI title left aligned beside the logo.
- Added the `AI Product Builder` tagline below the title.
- Added a right-side profile/chat icon button.
- Removed clutter from the mobile header while keeping the brand lockup visible and compact.

## Chat Bubbles

- Added clean left-aligned assistant bubbles with the IdeasForgeAI avatar.
- Added right-aligned user bubbles with a subtle purple tint.
- Preserved speech-tail bubble treatment for both assistant and user messages.
- Updated the welcome assistant message to introduce IdeasForgeAI as the local idea-to-preview assistant.
- Added the optional second assistant prompt: `What kind of product should we start with?`

## Composer

- Reworked the mobile composer into a large white rounded bottom card.
- Preserved safe-area bottom support.
- Kept the spacious multiline input with the placeholder `Describe your idea...`.
- Kept attachment and voice controls as UI-only placeholders.
- Kept the purple circular send button inside the composer.
- Removed prompt-chip usage from the mobile composer.
- Added extra chat-body bottom padding so the sticky composer does not cover messages.

## Local-Only Behavior

Submitting the mobile composer adds the user message locally, then adds the local assistant reply:

`Great! I can help you build that. Tell me your target audience, key features, and preferred style.`

The existing local processing flow remains local-only after the reply. No backend calls, provider calls, fetch/XHR, upload handling, microphone capture, OCR, image analysis, pixel reading, canvas analysis, database, auth, secrets, or deployment behavior was added.

## Safety Boundaries

- Attachment icon is visual-only.
- Voice icon is visual-only.
- No real upload behavior was added.
- No real microphone capture was added.
- No API keys or secrets were added to the frontend.
- No Supabase, auth, database, or deployment configuration was added.
- Real backend generation remains locked.
- KisanMitraAI was not touched.

## Validation

- `node --check frontend/pages/studio-v3.js`
- `python -m compileall backend`
- Target search completed for unsafe terms in `frontend/pages/studio-v3.*`
