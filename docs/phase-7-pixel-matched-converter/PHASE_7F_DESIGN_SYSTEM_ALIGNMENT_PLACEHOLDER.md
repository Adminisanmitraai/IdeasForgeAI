# Phase 7F - Pixel-Matched Design System Alignment Placeholder

Status: Completed as placeholder only.

Phase 7F adds a static Design System Alignment preview for the future Pixel-Matched Converter. It shows how a future uploaded screenshot would be checked against the frozen Phase 6 Design System after approval. It does not analyze selected images, score real screenshots, read pixels, use OCR, use canvas, generate layout JSON, generate component JSON, or generate frontend code.

## Placeholder Purpose

The Design System Alignment preview helps founders understand that future screenshot conversion will not blindly copy a reference image. Future conversion must honor the approved Phase 6 Design System before any frontend generation handoff.

This phase remains locked and approval-gated:

- Alignment output is static placeholder guidance.
- Selected files remain frontend-local only.
- No selected file is sent to the backend.
- No real Design System scoring is performed.
- No frontend code is generated.
- Human approval is required before any future generation.

## Required Alignment Categories

Each alignment item uses the same safe fields:

- `alignment_area`
- `expected_design_system_rule`
- `current_status`
- `placeholder_score`
- `risk_level`
- `required_human_review`

Alignment categories shown in Studio V3:

- Color token alignment
- Typography alignment
- Spacing scale alignment
- Component system alignment
- Border radius and shadow alignment
- Responsive behavior alignment
- Accessibility alignment
- Brand personality alignment
- Mobile-first alignment
- Approval readiness

## Locked Flags

```json
{
  "real_image_analysis_enabled": false,
  "ocr_enabled": false,
  "pixel_reading_enabled": false,
  "canvas_analysis_enabled": false,
  "component_mapping_is_placeholder": true,
  "design_system_alignment_is_placeholder": true,
  "frontend_generation_allowed": false,
  "phase_8_unlocked": false,
  "external_provider_calls_allowed": false,
  "approval_required": true
}
```

## Explicit Non-Goals

Phase 7F does not:

- Read image pixels.
- Use browser canvas.
- Perform OCR.
- Store uploaded files.
- Send selected files to the backend.
- Generate real Design System scores from uploaded files.
- Generate real layout JSON.
- Generate real component JSON.
- Generate HTML/CSS/React.
- Unlock frontend generation.
- Unlock Phase 8.
- Add backend upload endpoints.
- Add Supabase, authentication, database writes, deployment, provider calls, or secrets.

## Freeze Preservation

- Phase 5 remains frozen.
- Phase 6 remains frozen.
- Phase 7A remains frozen.
- Phase 7B remains frozen.
- Phase 7C remains frozen.
- Phase 7D remains frozen.
- Phase 7E remains frozen.
- Studio V3 visual polish remains visual-only.
- Historical note: Phase 7G was the next approval-gated step during Phase 7F completion.
- Phase 8 remains locked.

