# Phase 16A — Selected Section Edit + Regenerate Planning

Status: Completed, not frozen.

## Purpose

Phase 16A defines how IdeasForgeAI will safely allow users to select one section of a generated app and request changes without regenerating or breaking the full app.

This phase is planning only.

No frontend generation is unlocked.
No backend generation is unlocked.
No files are modified.
No deployment is added.
No provider calls are added.
No Supabase/auth/database/secrets are added.

## What Phase 15 Proved

Phase 15 proved that Studio V3 can now support an Apple-like premium builder interface with:
- polished top bar
- refined category cards
- premium builder workspace
- improved right preview panel
- responsive polish
- micro-interaction polish
- stable IF avatar
- stable workspace layout

## Why Phase 16 Matters

Phase 16 is the phase that will make IdeasForgeAI feel like a real AI builder.

The user should be able to:
1. select a section
2. describe a change
3. regenerate only that section
4. keep surrounding layout unchanged
5. preview the result
6. validate output
7. approve before writing

## Selected Section Concept

A selectable section may be:
- hero
- navbar
- feature card
- pricing card
- CTA
- dashboard panel
- footer
- form
- preview card
- sidebar section
- page block

## Required Section Metadata

Every editable section must eventually have:
- section_id
- section_name
- section_type
- source_file
- start_marker
- end_marker
- current_summary
- editable_allowed
- regenerate_allowed
- validation_required
- approval_required
- rollback_required

## Safety Rules

Selected section regeneration must:
- never rewrite full app unless approved
- never overwrite generated-apps/ideasforgeai-preview-v1
- never touch backend files
- never touch Studio V3 source files
- never touch docs except phase docs
- never touch root production files
- never touch secrets/env files
- never touch deployment files
- never touch KisanMitraAI
- never call providers without future approval
- never deploy
- always require validation
- always require rollback support

## Future Phase 16 Sequence

Phase 16A — Selected Section Edit + Regenerate Planning  
Phase 16B — Section Registry + Marker Contract  
Phase 16C — Section Selection UI Planning  
Phase 16D — Section Edit Prompt Contract  
Phase 16E — Section Regeneration Dry-Run Validator  
Phase 16F — Controlled Section Patch Sandbox  
Phase 16G — Section Preview + Validation Score  
Phase 16H — Phase 16 Freeze Review

## Phase 16A Safety Confirmation

Phase 16A is planning only.

No generated app files were changed.
generated-apps/ideasforgeai-preview-v1 was not touched.
General real generation remains locked.
Backend generation remains locked.
Deployment remains locked.
Provider calls remain locked.
Supabase/auth/database/secrets remain locked.
KisanMitraAI production was not touched.
Phase 16B was not implemented.
