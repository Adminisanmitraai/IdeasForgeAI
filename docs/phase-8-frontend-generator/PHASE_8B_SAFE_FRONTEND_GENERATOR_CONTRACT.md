# Phase 8B - Safe Frontend Generator Contract

Status: Completed as contract only.

Phase 8B defines the safe request and response contract for the future Frontend Generator. It does not generate HTML, CSS, React, generated app files, deployment output, provider prompts, database writes, Supabase configuration, authentication configuration, or production frontend output.

## 1. Purpose

The Safe Frontend Generator Contract establishes how later Phase 8 steps may ask for preview-ready frontend planning data without unlocking real generation.

The contract is designed to:

- Accept only safe project metadata.
- Require approved Product Brain output.
- Require approved Design System output.
- Respect Phase 7 Pixel-Matched placeholder outputs.
- Block generated code and file writes.
- Keep human approval mandatory before Phase 8C.

## 2. Contract Scope

Phase 8B may return:

- Request shape.
- Response shape.
- Safe input metadata.
- Required upstream inputs.
- Future screen target placeholders.
- Future output type placeholders.
- Approval gate fields.
- Safety lock fields.
- Blocked output fields.
- Next phase handoff.

Phase 8B must not create preview artifacts or generated app files.

## 3. Optional Backend Route

The contract is exposed through a static/status-only route:

`POST /api/frontend-generator/contract`

The route returns contract data only. It does not generate frontend code, write files, call providers, deploy, use Supabase, use authentication, or write to a database.

## 4. Allowed Safe Request Fields

Only these request fields are allowed:

- `project_name`
- `target_platform`
- `target_screen_type`
- `design_system_version`
- `product_brain_reference`
- `pixel_converter_reference`
- `approval_context`

These fields are metadata references only. They are not prompts for generation.

## 5. Required Product Brain Inputs

Future generation must require approved Phase 5 output:

- Approved Product Strategy.
- Approved Requirements.
- Approved Product Blueprint.
- Approved screen plan.
- Approval checkpoint.

If Product Brain approval is missing, generation must remain locked.

## 6. Required Design System Inputs

Future generation must require approved Phase 6 output:

- Approved Design System version.
- Design positioning.
- Typography rules.
- Color token rules.
- Component rules.
- Mobile-first rules.
- Accessibility rules.

If Design System approval is missing, generation must remain locked.

## 7. Required Pixel-Matched Placeholder Inputs

Future generation may reference Phase 7 placeholder outputs:

- Pixel Converter contract status.
- Layout detection placeholder.
- Component mapping placeholder.
- Design System alignment placeholder.
- Pixel Match Score preview placeholder.
- Human approval state.

Phase 7 placeholder data must not be treated as real image analysis.

## 8. Future Screen Target Fields

The contract defines future target placeholders for:

- Single page preview.
- Multi-page app structure.
- Responsive preview.
- Design-system-enforced preview.

These targets remain locked in Phase 8B.

## 9. Future Output Type Placeholders

Future output placeholders are explicitly blocked in Phase 8B:

- `html_output`: blocked.
- `css_output`: blocked.
- `react_output`: blocked.
- `generated_files`: empty.
- `generated_app_path`: null.
- `preview_artifact`: not created in Phase 8B.

## 10. Blocked Request and Output Fields

The contract blocks:

- `html_output`
- `css_output`
- `react_output`
- `generated_files`
- `generated_app_path`
- `file_write_request`
- `deploy_request`
- `provider_prompt`
- `secret_value`
- `database_write`
- `supabase_config`
- `auth_config`

Any future implementation must reject or ignore these fields until the relevant approved phase unlocks them.

## 11. Required Safety Locks

Required lock values:

```json
{
  "frontend_generation_allowed": false,
  "html_generation_allowed": false,
  "css_generation_allowed": false,
  "react_generation_allowed": false,
  "generated_app_write_allowed": false,
  "generated_files_allowed": false,
  "deployment_allowed": false,
  "provider_calls_allowed": false,
  "database_writes_allowed": false,
  "supabase_allowed": false,
  "auth_allowed": false,
  "phase_8_generation_unlocked": false,
  "approval_required": true
}
```

## 12. Approval Gate

Approval message:

Approve Safe Frontend Generator Contract v1.0 before moving to Phase 8C Single Page Static Preview Generator.

Phase 8 generation remains locked until explicit approval.

## 13. Next Phase Handoff

Current phase:

Phase 8B - Safe Frontend Generator Contract

Next approval-gated phase:

Phase 8C - Single Page Static Preview Generator

Phase 8C must remain locked until the Phase 8B contract is reviewed and approved.

## 14. Validation Criteria

Phase 8B is valid only if:

- No real frontend generation exists.
- No HTML, CSS, or React output is generated.
- No generated app files are created.
- `generated-apps/` is not modified.
- No backend generation logic is added.
- No provider calls are added.
- No Supabase, authentication, database writes, deployment, or secrets are added.
- Product Brain, Design System Engine, Pixel Converter, and Studio V3 frozen behavior remain intact.
- Phase 8 generation remains locked.

## 15. Freeze Criteria

Phase 8B can be frozen after review confirms:

- The contract route is static/status-only.
- The schema includes all required safe input metadata.
- The schema includes all blocked fields.
- All safety locks remain false except `approval_required=true`.
- Phase 8C is listed only as the next approval-gated step.
- No generated output or generated app files exist.
