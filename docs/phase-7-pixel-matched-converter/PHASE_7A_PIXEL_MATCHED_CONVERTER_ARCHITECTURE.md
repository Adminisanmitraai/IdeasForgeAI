# Phase 7A - Pixel-Matched Converter Architecture Specification

Status: Architecture specification only.

Phase 7A defines how the future Pixel-Matched Converter should understand screenshots, sketches, references, and page images before any frontend code is generated. It does not implement real screenshot-to-code, does not unlock frontend generation, and does not unlock Phase 8.

## 1. Phase 7 Purpose

Phase 7 will convert visual references into structured UI intelligence.

Supported future direction:

- Screenshot, image, sketch, PDF page, or Figma-like reference to structured UI intelligence.
- Extract layout, components, color, typography, spacing, responsive intent, and readiness.
- Use the approved Phase 6 Design System as the guardrail before any code generation.
- Produce reviewable intelligence for humans before the future frontend generator receives anything.

Explicit boundaries:

- Phase 7 is not direct production frontend generation.
- Phase 7 is not deployment.
- Phase 7 is not database generation.
- Phase 7 must not bypass Phase 6 Design System approval.
- Phase 8 remains locked until Phase 7 is frozen and approved.

## 2. Supported Future Inputs

The converter architecture should be ready for:

- Screenshot upload.
- Pasted image.
- Mobile app screenshot.
- Website screenshot.
- Dashboard screenshot.
- Hand-drawn sketch.
- Wireframe.
- PDF page.
- Figma export or reference image.
- Multi-screen upload in a later subphase.

Phase 7A does not add upload processing. It only defines the future intake surface.

## 3. Processing Pipeline

Future Phase 7 processing should follow this order:

1. Upload intake
2. File validation
3. Image normalization
4. Visual region detection
5. Layout grid detection
6. Component detection
7. Text detection strategy
8. Color extraction
9. Typography estimation
10. Spacing and rhythm extraction
11. Responsive interpretation
12. Component mapping
13. Design System alignment
14. Pixel-match scoring
15. Human approval
16. Output handoff to later frontend generation

Pipeline rule:

The screenshot is a reference, not an unsafe source of truth. Every result must be interpreted through the approved Design System, accessibility expectations, and user approval.

## 4. Output Contracts

These structures are documentation contracts only. They are not implemented in Phase 7A.

### UploadedAsset

```json
{
  "asset_id": "local-session-id",
  "file_name": "dashboard-reference.png",
  "file_type": "image/png",
  "source_type": "upload | paste | pdf | figma_export | sketch",
  "width": 1440,
  "height": 1024,
  "orientation": "landscape | portrait",
  "screen_category": "mobile | tablet | desktop | dashboard | landing_page | unknown",
  "session_only": true
}
```

### ImageAnalysisResult

```json
{
  "asset_id": "local-session-id",
  "summary": "Reference appears to be a SaaS dashboard with sidebar navigation and KPI cards.",
  "regions": [],
  "components": [],
  "text_blocks": [],
  "color_palette": {},
  "typography_profile": {},
  "spacing_profile": {},
  "responsive_plan": {},
  "confidence": "low | medium | high",
  "requires_human_review": true
}
```

### LayoutRegion

```json
{
  "region_id": "region-header",
  "type": "header | sidebar | content | footer | modal | unknown",
  "bounds": {"x": 0, "y": 0, "width": 1440, "height": 80},
  "visual_priority": "primary | secondary | support",
  "notes": "Top navigation with brand and action controls."
}
```

### DetectedComponent

```json
{
  "component_id": "component-primary-button",
  "component_type": "button",
  "region_id": "region-header",
  "bounds": {"x": 1180, "y": 20, "width": 160, "height": 44},
  "label_hint": "Start",
  "state_hint": "default",
  "confidence": 0.82
}
```

### TextBlock

```json
{
  "text_id": "text-hero-title",
  "content_hint": "Review required before use",
  "role": "heading | body | label | button | caption",
  "bounds": {"x": 120, "y": 180, "width": 680, "height": 72},
  "requires_review": true
}
```

### ColorPalette

```json
{
  "primary": "#0F766E",
  "secondary": "#E0F2FE",
  "accent": "#F59E0B",
  "background": "#FFFFFF",
  "surface": "#F8FAFC",
  "text": "#111827",
  "contrast_notes": ["Primary text appears readable on white."]
}
```

### TypographyProfile

```json
{
  "heading_style": "Large, semi-bold, modern sans-serif",
  "body_style": "Readable sans-serif body copy",
  "estimated_scale": ["12", "14", "16", "24", "32"],
  "font_confidence": "estimated",
  "accessibility_notes": ["Avoid text below readable mobile sizes."]
}
```

### SpacingProfile

```json
{
  "base_unit": 8,
  "section_spacing": "medium",
  "card_padding": "16-24",
  "grid_gap": "16",
  "rhythm_notes": ["Consistent card gaps detected across main content."]
}
```

### ResponsivePlan

```json
{
  "desktop": "Preserve sidebar and multi-column grid.",
  "tablet": "Collapse grid to two columns and reduce sidebar prominence.",
  "mobile_portrait": "Stack content, move navigation to top or bottom.",
  "mobile_landscape": "Use compact horizontal navigation and two-column summaries.",
  "approval_needed": true
}
```

### DesignSystemAlignment

```json
{
  "design_system_version": "Phase 6 Design System v1.0",
  "alignment_status": "aligned | partial | conflict",
  "matches": ["Mobile-first layout direction", "Clean card language"],
  "conflicts": ["Screenshot uses low-contrast secondary labels"],
  "recommended_adjustments": ["Increase label contrast before conversion."]
}
```

### PixelMatchScore

```json
{
  "layout_match": 0.0,
  "spacing_match": 0.0,
  "typography_match": 0.0,
  "color_match": 0.0,
  "component_match": 0.0,
  "responsive_behavior": 0.0,
  "accessibility": 0.0,
  "design_system_consistency": 0.0,
  "overall_confidence": 0.0,
  "review_notes": ["Scoring is unavailable until real analysis is implemented."]
}
```

### ConversionReadiness

```json
{
  "ready_for_phase_7_review": true,
  "ready_for_frontend_generation": false,
  "blocking_reasons": ["Human approval is required.", "Phase 8 remains locked."],
  "next_step": "Review analysis and approve Pixel-Matched Conversion v1.0 when available."
}
```

### ApprovalState

```json
{
  "approval_required": true,
  "approved": false,
  "approved_by": null,
  "approval_message": "Approve Pixel-Matched Conversion v1.0 before moving to frontend generation.",
  "phase_8_unlocked": false
}
```

## 5. Component Mapping Rules

Future detection must map visual elements to known UI concepts before any generation handoff.

Required component categories:

- Header
- Sidebar
- Bottom navigation
- Hero section
- Card
- Button
- Form input
- Table
- Chart placeholder
- Image or media block
- Modal
- Chat composer
- Navigation tabs
- KPI or stat card

Mapping rules:

- Prefer semantic component names over visual-only labels.
- Treat uncertain regions as `unknown` and request review.
- Do not infer sensitive content as final product text without human approval.
- Preserve mobile-first interpretation even when the reference is desktop-only.
- If a detected component conflicts with the Design System, flag it instead of copying it blindly.

## 6. Design System Enforcement

Phase 7 must read the approved Phase 6 Design System output before any future generation handoff.

Enforcement rules:

- If the screenshot aligns with the Design System, preserve its useful structure.
- If the screenshot conflicts with the Design System, flag the conflict.
- Never blindly copy bad UI.
- Use the screenshot as a reference, not as the only source of truth.
- Keep output founder-friendly, mobile-first, accessible, and approval-gated.
- Do not proceed to frontend generation unless Phase 7 output is approved.

Examples of conflicts:

- Low contrast text.
- Tiny tap targets.
- Overcrowded dashboard controls.
- Desktop-only layouts without mobile interpretation.
- Brand colors that conflict with the approved Design System.
- Unclear hierarchy or hidden primary action.

## 7. Pixel-Match Scoring

Future scoring should be understandable to founders and useful to builders.

Scoring categories:

- Layout match
- Spacing match
- Typography match
- Color match
- Component match
- Responsive behavior
- Accessibility
- Design System consistency
- Overall confidence

Scoring rules:

- Scores should be confidence indicators, not automatic approval.
- Low accessibility should reduce overall confidence.
- Strong screenshot similarity must not override Design System conflicts.
- Human approval is required before any future frontend generation.

## 8. Safety and Limits

Safety boundaries:

- No hidden code execution from image content.
- No raw OCR trust without review.
- No automatic production deployment.
- No direct database writes.
- No secrets in generated output.
- No copying sensitive or private UI content into logs.
- No copyrighted brand cloning without user permission.
- Human approval required before frontend generation.

Operational limits:

- Phase 7A is documentation only.
- No external AI or image providers are called.
- No image files are stored by this specification.
- No backend rebuild starts in Phase 7A.
- No Studio V3 redesign is required.

## 9. Phase Gates

Phase 7 must move in controlled steps:

- Phase 7A: Architecture spec only.
- Phase 7B: Placeholder API contract.
- Phase 7C: Upload UI and local metadata handling.
- Phase 7D: Layout detection placeholder.
- Phase 7E: Component mapping placeholder.
- Phase 7F: Design System alignment output.
- Phase 7G: Pixel-match score preview.
- Phase 7H: Freeze review.

Phase 8 remains locked until Phase 7 is frozen and explicitly approved.

## 10. Recommended Future Files and Modules

These paths are recommended for future implementation only. They are not created in Phase 7A unless a later phase requests them.

Backend:

- `backend/pixel_converter/`
- `backend/pixel_converter/intake_engine.py`
- `backend/pixel_converter/image_analysis_engine.py`
- `backend/pixel_converter/layout_detection_engine.py`
- `backend/pixel_converter/component_mapping_engine.py`
- `backend/pixel_converter/design_alignment_engine.py`
- `backend/pixel_converter/pixel_score_engine.py`
- `backend/pixel_converter/approval_engine.py`
- `backend/pixel_converter/schemas.py`

Frontend:

- `frontend/pages/studio-v3.js` future integration points.
- `frontend/pages/studio-v3.html` future upload panel.

Docs:

- `docs/phase-7-pixel-matched-converter/`

## 11. Existing Project Integration Notes

Current inspected references:

- `backend/agents/pixel_matched_page_converter_agent.py` already provides a safe placeholder result.
- `backend/main.py` already exposes `/api/pixel-convert` through placeholder agent wiring.
- `frontend/pages/studio-v2.html` and `frontend/pages/studio-v2.js` include the original placeholder workflow.
- `frontend/pages/studio-v3.html` and `frontend/pages/studio-v3.js` include the frozen Studio V3 placeholder surface.
- `docs/pixel-matched-page-converter.md` documents the earlier placeholder agent.
- `docs/phase-6-design-system-engine/` defines the frozen Design System guardrails.
- `backend/design_system_engine/` contains the local Phase 6 Design System Engine modules.

Phase 7A does not change these files.

## 12. Freeze Boundaries

Phase 7A completion means:

- The Pixel-Matched Converter architecture is documented.
- Phase 7 implementation remains locked.
- Phase 8 remains locked.
- Frontend generation remains locked.
- Backend generation remains locked.
- Deployment remains locked.
- Supabase, authentication, and database writes remain absent.
- IdeasForgeAI production remains untouched.

