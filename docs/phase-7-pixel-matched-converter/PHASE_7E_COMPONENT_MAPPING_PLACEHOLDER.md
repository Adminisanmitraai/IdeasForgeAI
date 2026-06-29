# Phase 7E - Pixel-Matched Component Mapping Placeholder

Status: Completed as placeholder only.

Phase 7E adds a static Component Mapping preview for the future Pixel-Matched Converter. It shows how future detected screenshot regions may map to reusable UI components after approval. It does not analyze selected images, detect real components, read pixels, use OCR, use canvas, generate layout JSON, or generate frontend code.

## Placeholder Purpose

The Component Mapping preview helps founders understand how future screenshot references will be translated into reusable product UI building blocks.

This phase remains locked and approval-gated:

- Mapping is static placeholder guidance.
- Selected files remain frontend-local only.
- No selected file is sent to the backend.
- No real component detection is performed.
- Design System rules remain required before any future conversion.
- Human approval is required before any frontend generation.

## Required Placeholder Mappings

Each mapping uses the same safe fields:

- `source_region`
- `suggested_component`
- `confidence_placeholder`
- `design_system_rule`
- `responsive_behavior`
- `approval_status`

Mappings shown in Studio V3:

- Header region -> Header / Top Navigation component
- Sidebar region -> Sidebar Navigation component
- Hero region -> Hero Section component
- Card region -> Content Card / KPI Card component
- Button region -> Primary / Secondary Button component
- Form region -> Form Field Group component
- Table region -> Data Table component
- Chart region -> Chart Placeholder component
- Image/media region -> Media Block component
- Modal region -> Modal / Dialog component
- Chat composer region -> Chat Input / Composer component
- Tab region -> Navigation Tabs component
- Mobile bottom region -> Bottom Navigation component

## Locked Flags

```json
{
  "real_image_analysis_enabled": false,
  "ocr_enabled": false,
  "pixel_reading_enabled": false,
  "canvas_analysis_enabled": false,
  "component_mapping_is_placeholder": true,
  "frontend_generation_allowed": false,
  "phase_8_unlocked": false,
  "external_provider_calls_allowed": false,
  "approval_required": true
}
```

## Explicit Non-Goals

Phase 7E does not:

- Read image pixels.
- Use browser canvas.
- Perform OCR.
- Store uploaded files.
- Send selected files to the backend.
- Generate real component JSON from uploaded files.
- Generate layout JSON.
- Generate HTML/CSS/React.
- Unlock frontend generation.
- Unlock Phase 8.
- Add backend upload processing.
- Add Supabase, authentication, database writes, deployment, provider calls, or secrets.

## Freeze Preservation

- Phase 5 remains frozen.
- Phase 6 remains frozen.
- Phase 7A remains frozen.
- Phase 7B remains frozen.
- Phase 7C remains frozen.
- Phase 7D remains frozen.
- Studio V3 visual polish remains visual-only.
- Historical note: Phase 7F was the next approval-gated step during Phase 7E completion.
- Phase 8 remains locked.
