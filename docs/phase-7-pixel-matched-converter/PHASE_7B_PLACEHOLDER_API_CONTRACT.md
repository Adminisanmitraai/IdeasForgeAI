# Phase 7B - Pixel-Matched Converter Placeholder API Contract

Status: Placeholder API contract only.

Phase 7B defines a safe backend contract for the future Pixel-Matched Converter. It does not implement real image analysis, OCR, upload storage, frontend generation, external provider calls, Supabase, authentication, database writes, deployment, or Phase 8 unlocks.

## Purpose

The contract gives Studio V3 and future backend modules a stable shape for Pixel-Matched Converter readiness without processing real files.

It prepares the future path from:

1. Visual reference metadata
2. File validation contract
3. Placeholder analysis contract
4. Design System enforcement
5. Human approval gate
6. Future Phase 7C-7G handoff
7. Future Phase 8 handoff only after freeze and explicit approval

## Backend Module

Created:

- `backend/pixel_converter/__init__.py`
- `backend/pixel_converter/schemas.py`
- `backend/pixel_converter/contract_engine.py`

The module is intentionally small and contract-only.

## Placeholder Route

Created:

- `POST /api/pixel-converter/contract`

The route accepts metadata only and returns static safe contract data.

It does not:

- Accept file binaries.
- Accept base64 image payloads.
- Store uploads.
- Perform OCR.
- Analyze pixels.
- Generate frontend code.
- Call external AI, image, or OCR providers.

## Request Shape

Current accepted fields:

```json
{
  "project_name": "IdeasForgeAI Product",
  "reference_source": "contract_preview",
  "design_system_version": "Phase 6 Design System v1.0"
}
```

Future upload fields are documented but blocked in Phase 7B:

- `asset_id`
- `file_name`
- `file_type`
- `file_size_bytes`
- `width`
- `height`
- `orientation`
- `screen_category`
- `source_type`

Blocked in Phase 7B:

- `file_binary`
- `base64_image`
- `ocr_text`
- `html_output`
- `css_output`
- `react_output`
- `provider_payload`

## Response Shape

Top-level fields:

- `status`
- `phase`
- `mode`
- `flags`
- `allowed_input_types`
- `max_future_file_size_mb`
- `validation_requirements`
- `request_shape`
- `response_shape`
- `output_placeholders`
- `design_system_enforcement`
- `approval_gate`
- `future_phase_handoff`
- `safety_limits`

Required locked flags:

```json
{
  "real_image_analysis_enabled": false,
  "frontend_generation_allowed": false,
  "phase_8_unlocked": false,
  "external_provider_calls_allowed": false,
  "approval_required": true
}
```

## Allowed Future Input Types

The contract reserves space for:

- Screenshot upload
- Pasted image
- Mobile app screenshot
- Website screenshot
- Dashboard screenshot
- Hand-drawn sketch
- Wireframe
- PDF page
- Figma export/reference image

Phase 7B does not process any of these yet.

## Max Future File Size Placeholder

Placeholder future size limit:

- `15 MB`

This is not enforced against real files in Phase 7B because real upload handling does not exist yet.

## Validation Requirements

Future validation must include:

- Metadata-only acceptance in Phase 7B.
- File type allowlist before uploads are enabled.
- Size limit enforcement before uploads are enabled.
- Malware and safety review before storage.
- Secret and private-content handling before logs/artifacts.
- Human approval before frontend generation.

## Output Placeholders

The contract reserves placeholders for:

- `uploaded_asset`
- `image_analysis_result`
- `layout_regions`
- `detected_components`
- `text_blocks`
- `color_palette`
- `typography_profile`
- `spacing_profile`
- `responsive_plan`
- `design_system_alignment`
- `pixel_match_score`
- `conversion_readiness`

All analysis values are placeholders. No real image intelligence runs in Phase 7B.

## Design System Enforcement

The contract requires Phase 6 Design System enforcement before any future conversion handoff.

Rules:

- Use the visual reference as guidance, not unsafe truth.
- Flag conflicts with the approved Design System.
- Do not blindly copy bad UI.
- Keep output mobile-first, accessible, and founder-friendly.
- Do not proceed to frontend generation without explicit approval.

## Approval Gate

Required approval message:

`Approve Pixel-Matched Conversion v1.0 before moving to frontend generation.`

Approval state:

- Approval required: yes
- Frontend generation allowed: no
- Phase 8 unlocked: no

## Future Phase Handoff

- Phase 7C: Upload UI and local metadata handling.
- Phase 7D: Layout detection placeholder.
- Phase 7E: Component mapping placeholder.
- Phase 7F: Design System alignment output.
- Phase 7G: Pixel-match score preview.
- Phase 7H: Freeze review.
- Phase 8: Locked until Phase 7 is frozen and explicitly approved.

## Safety Confirmation

Phase 7B keeps these locked:

- Real image analysis
- OCR
- File upload processing
- Uploaded file storage
- External provider calls
- HTML/CSS/React generation
- Database writes
- Deployment
- Phase 8

Phase 5, Phase 6, and Phase 7A remain frozen.

