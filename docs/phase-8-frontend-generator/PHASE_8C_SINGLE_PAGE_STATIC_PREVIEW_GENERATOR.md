# Phase 8C - Single Page Static Preview Generator

Status: Completed as Studio-only static preview.

Phase 8C adds the first visible frontend preview experience inside Studio V3. It renders structured preview data in the Studio interface only. It does not generate production HTML, CSS, React, generated app files, downloadable frontend output, deployment output, provider prompts, database writes, Supabase configuration, authentication configuration, or production code.

## 1. Purpose

The Single Page Static Preview Generator lets a founder see the first safe frontend direction before real generation exists.

It is intended to:

- Make the future product feel tangible.
- Use Product Brain and Design System context.
- Stay inside Studio V3.
- Keep production generation locked.
- Require human approval before later Phase 8 steps.

## 2. Studio V3 Preview Experience

Studio V3 now includes a contained single-page preview panel.

The panel displays:

- Page title.
- Page type.
- Hero section.
- Navigation items.
- Feature cards.
- Primary CTA.
- Trust badges.
- Preview status.
- Approval requirement.
- Safety flags.

The preview is rendered by Studio V3 HTML, CSS, and JavaScript. It is not written to disk as a generated app.

## 3. Static Preview Route

The preview data is exposed through:

`POST /api/frontend-generator/static-preview`

This route returns safe preview data only. It does not return HTML, CSS, React, generated files, generated app paths, provider prompts, deployment requests, secrets, database writes, Supabase config, or auth config.

## 4. Preview-Only Fields

Allowed preview fields:

- `page_title`
- `page_type`
- `hero_section`
- `navigation_items`
- `feature_cards`
- `primary_cta`
- `trust_badges`
- `preview_status`
- `approval_required`

## 5. Required Safety Flags

Required lock values:

```json
{
  "static_preview_allowed": true,
  "production_frontend_generation_allowed": false,
  "html_output_allowed": false,
  "css_output_allowed": false,
  "react_output_allowed": false,
  "generated_app_write_allowed": false,
  "generated_files_allowed": false,
  "deployment_allowed": false,
  "provider_calls_allowed": false,
  "database_writes_allowed": false,
  "supabase_allowed": false,
  "auth_allowed": false,
  "approval_required": true
}
```

## 6. Blocked Fields

Blocked fields remain:

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

## 7. What Phase 8C Does Not Do

Phase 8C does not:

- Write to `generated-apps/`.
- Create generated app folders.
- Create downloadable HTML, CSS, or React output.
- Generate production frontend code.
- Add deployment.
- Add provider calls.
- Add Supabase, authentication, database writes, or secrets.
- Modify Product Brain logic.
- Modify Design System Engine logic.
- Modify Pixel Converter behavior.
- Touch KisanMitraAI production.

## 8. Approval Boundary

The preview labels remain explicit:

- Static preview only.
- No generated files.
- No production code output.
- Approval required before generation.

Production frontend generation remains locked until a later approved phase.

## 9. Next Phase Handoff

Current phase:

Phase 8C - Single Page Static Preview Generator

Next approval-gated phase:

Phase 8D - Multi-page App Structure Preview

Phase 8D must not start until Phase 8C is reviewed and explicitly approved.

## 10. Validation Criteria

Phase 8C is valid only if:

- Studio V3 shows a single-page static preview.
- The preview is Studio-only and preview-only.
- No generated app files are created.
- No HTML, CSS, or React output is generated.
- `generated-apps/` has no diffs.
- Blocked fields remain blocked.
- Production frontend generation remains locked.
- Phase 8D is not implemented.
