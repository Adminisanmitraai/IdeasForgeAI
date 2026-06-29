# Phase 16C — Section Selection UI Planning

Status: Completed, not frozen.

## Purpose

Phase 16C defines how IdeasForgeAI Studio V3 will allow users to select one section of a generated app before requesting edits or regeneration.

This phase is planning only.

No section selection UI is implemented in Phase 16C.
No section regeneration is implemented.
No generated app files are changed.
No backend generation is unlocked.
No deployment is added.
No provider calls are added.
No Supabase/auth/database/secrets are added.

## What Phase 16B Proved

Phase 16B defined:
- section registry contract
- section marker contract
- required section metadata
- allowed section types
- blocked section types
- safety rules
- static backend schema endpoint

## Section Selection Goal

The user should eventually be able to:

1. Open a generated preview.
2. Hover over a section.
3. See a soft selectable outline.
4. Click one section.
5. See selected section details.
6. Ask IdeasForgeAI to change only that section.
7. Preview the proposed change.
8. Validate and approve before writing.

## Future UI Placement

Section selection UI should appear in Studio V3 right preview panel and/or preview canvas.

Possible locations:
- right preview panel overlay
- preview frame hover layer
- side inspector panel
- bottom selected-section control bar
- center chat selected-section context card

## Future Selected Section Inspector

The inspector should show:

- section name
- section type
- section ID
- source file
- editable status
- regenerate status
- validation required
- approval required
- rollback required
- current section summary

## Future Selection Behavior

Allowed behavior:
- hover outline
- click to select
- selected section highlight
- selected section metadata display
- clear selection
- send selected section context to chat

Blocked behavior:
- direct file write
- direct regeneration
- provider call
- deployment
- database write
- secret access
- backend file edit
- full app rewrite

## Future Section Selection States

States:
- no section selected
- section hover
- section selected
- section locked
- section editable
- section pending validation
- section approved for dry-run only
- section blocked

## Required UI Safety Labels

Future UI must show:

- Preview only
- Section edit requires approval
- No full app rewrite
- No deployment
- No provider calls
- No database writes
- No secrets
- Rollback required

## Future Phase 16D

Phase 16D will define the Section Edit Prompt Contract.

It will decide how the selected section context is passed into the edit prompt safely.

## Phase 16C Safety Confirmation

Phase 16C is planning only.

No frontend UI code was changed.
No generated app files were changed.
generated-apps/ideasforgeai-preview-v1 was not touched.
General real generation remains locked.
Backend generation remains locked.
Deployment remains locked.
Provider calls remain locked.
Supabase/auth/database/secrets remain locked.
KisanMitraAI production was not touched.
Phase 16D was not implemented.
