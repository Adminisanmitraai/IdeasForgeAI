# Phase 7G - Pixel Match Score Preview Placeholder

Status: Completed as placeholder only.

Phase 7G adds a static Pixel Match Score preview for the future Pixel-Matched Converter. It shows how future screenshot-to-design scoring will be presented after approved analysis. It does not analyze selected images, calculate real scores, read pixels, use OCR, use canvas, generate layout JSON, generate component JSON, or generate frontend code.

## Placeholder Purpose

The Pixel Match Score preview helps founders understand how future screenshot references may be reviewed before any frontend generation handoff.

This phase remains locked and approval-gated:

- Score output is static placeholder guidance.
- Selected files remain frontend-local only.
- No selected file is sent to the backend.
- No real pixel-match score is calculated.
- No real Design System score is calculated.
- No frontend code is generated.
- Human approval is required before any future generation.

## Required Score Categories

Each score item uses the same safe fields:

- `score_area`
- `placeholder_score`
- `scoring_status`
- `score_basis`
- `risk_level`
- `required_human_review`

Score categories shown in Studio V3:

- Layout structure match
- Spacing match
- Typography match
- Color token match
- Component mapping match
- Responsive behavior match
- Accessibility match
- Brand personality match
- Mobile-first match
- Overall pixel-match readiness

## Locked Flags

```json
{
  "real_image_analysis_enabled": false,
  "ocr_enabled": false,
  "pixel_reading_enabled": false,
  "canvas_analysis_enabled": false,
  "component_mapping_is_placeholder": true,
  "design_system_alignment_is_placeholder": true,
  "pixel_match_scoring_is_placeholder": true,
  "frontend_generation_allowed": false,
  "phase_8_unlocked": false,
  "external_provider_calls_allowed": false,
  "approval_required": true
}
```

## Explicit Non-Goals

Phase 7G does not:

- Read image pixels.
- Use browser canvas.
- Perform OCR.
- Store uploaded files.
- Send selected files to the backend.
- Generate real pixel-match scores from uploaded files.
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
- Phase 7F remains frozen.
- Studio V3 visual polish remains visual-only.
- Phase 7H / Phase 7 Final Freeze Review remains the next approval-gated step.
- Phase 8 remains locked.
