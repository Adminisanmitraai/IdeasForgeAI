# Phase 7C - Upload UI and Local Metadata Placeholder

Status: Placeholder UI and local metadata only.

Phase 7C adds a safe Studio V3 upload placeholder experience for the Pixel-Matched Converter. It lets the user select a future reference image and see local metadata, but it does not upload, store, analyze, OCR, convert, or generate frontend code.

## What Was Added

Studio V3 now shows:

- Upload placeholder message.
- File input restricted to future-safe image formats.
- Local-only selected file metadata.
- Validation status for allowed future formats.
- Future conversion status.
- Locked safety flags.
- Static placeholder contract check.

## Local Metadata Shown

After selecting a file, Studio V3 shows:

- File name
- File type
- File size
- Last modified date
- Validation status
- Future conversion status

This metadata is rendered in the browser only.

## Allowed Future Formats

Frontend-only validation recognizes:

- `png`
- `jpg`
- `jpeg`
- `webp`

Unsupported formats show a local warning. No file is uploaded.

## Required Safety Message

Studio V3 displays:

`Upload placeholder only. No image analysis or frontend generation is performed yet.`

## Locked Flags

The UI and contract keep these flags visible:

```json
{
  "real_image_analysis_enabled": false,
  "frontend_generation_allowed": false,
  "phase_8_unlocked": false,
  "external_provider_calls_allowed": false,
  "approval_required": true
}
```

## Backend Behavior

No new upload endpoint was added.

The existing static contract endpoint remains:

- `POST /api/pixel-converter/contract`

Studio V3 can call this endpoint to read locked placeholder contract status. It does not send the selected file, file name, file type, file size, pixels, base64 content, or OCR text.

## Explicit Non-Goals

Phase 7C does not:

- Send selected files to the backend.
- Store files.
- Read pixels.
- Use canvas for image analysis.
- Perform OCR.
- Generate layout JSON.
- Generate HTML/CSS/React.
- Generate frontend code.
- Unlock frontend generation.
- Unlock Phase 8.
- Connect external AI/image/OCR providers.
- Add Supabase.
- Add authentication.
- Add database writes.
- Deploy.

## Preserved Frozen Behavior

Confirmed boundaries:

- Phase 5 Product Brain remains frozen.
- Phase 6 Design System Engine remains frozen.
- Phase 7A architecture remains frozen.
- Phase 7B placeholder API contract remains frozen.
- Phase 8 remains locked.

## Next Phase

Phase 7D - Local image analysis placeholder, only after explicit approval.
