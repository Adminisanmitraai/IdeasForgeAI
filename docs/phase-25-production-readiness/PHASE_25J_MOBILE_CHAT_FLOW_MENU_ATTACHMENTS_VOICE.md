# Phase 25J - Mobile Chat Flow, Menu Drawer, Attachments, and Voice

Status: Completed, not frozen.

## Chat Flow

Normal mobile text submit now stays on the chat screen. The user message is added on the right, and IdeasForgeAI replies locally on the left:

`Got it. I can help shape this into a product. Add more details, or tap Generate Preview when you're ready.`

The processing screen no longer opens from normal text submit.

## Explicit Preview Trigger

After at least one local user message, the chat stream shows a polished `Generate Preview` action. Processing starts only when that action is tapped. The existing swipe-left processing transition, processing cards, preview-ready state, and local View Preview action remain local-only.

## Menu Drawer

The mobile menu button opens a left-side drawer with the IdeasForgeAI header, menu items, backdrop close behavior, and `v1.0.0 Preview` footer.

`New Idea` resets the mobile chat locally, clears the prompt, clears local attachments, clears local voice note state, closes the drawer, and returns to the welcome chat. Other drawer items show a local coming-soon toast.

## Attachments

The attachment control opens a local bottom action sheet with Camera, Photos, and Files options. These options trigger hidden local file inputs only:

- Camera: `accept="image/*"` with `capture="environment"`
- Photos: `accept="image/*"`
- Files: `accept="*/*"`

Selected files are never uploaded or processed. They appear only as removable local chips in the composer.

## Voice Notes

The voice control uses browser `MediaRecorder` only after a user tap. Recording state, timer, stop behavior, local object URL creation, playback, and removal all remain in browser memory. If recording is unavailable or permission is denied, the UI shows a local message.

No transcription, upload, backend call, or provider call is performed.

## Safety Boundaries

- No real upload.
- No OCR, image analysis, file processing, transcription, or backend chat.
- No provider calls.
- No API keys or secrets.
- No database, auth, or Supabase integration.
- No deployment configuration changes.
- Desktop builder remains preserved.
- KisanMitraAI was not touched.

## Validation

- `node --check frontend/pages/studio-v3.js`
- `python -m compileall backend`
- Unsafe/backend term search completed for `frontend/pages/studio-v3.*`
- Confirmed attachments are local input/chip behavior only.
- Confirmed `MediaRecorder` is used only for local user-initiated voice recording.
