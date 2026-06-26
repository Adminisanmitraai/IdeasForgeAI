# IdeasForgeAI

## Phase 5G — Planning Engine Specification

### Version 1.0

## Purpose

The Planning Engine converts an approved or draft product blueprint into a clear next-step execution plan.

It decides what should happen next, what should wait, what requires approval, and what belongs to ChatGPT Track A versus Codex Track.

Core mantra:

**Less UI. More Intelligence.**

---

# 1. Engine Responsibility

The Planning Engine defines:

* Recommended next phase
* Immediate next step
* ChatGPT Track responsibility
* Codex Track responsibility
* Approval needed
* Build readiness checklist
* Risks before next phase
* What should not be done yet

The Planning Engine must prevent premature building.

It should help IdeasForgeAI move forward safely, step by step.

---

# 2. Roadmap Awareness

The Planning Engine must respect the IdeasForgeAI roadmap:

1. Phase 5 — AI Product Brain
2. Phase 6 — Design System Engine
3. Phase 7 — Pixel-Matched Converter
4. Phase 8 — Frontend Generator
5. Phase 9 — Backend Generator
6. Phase 10 — Authentication + Roles
7. Phase 11 — Supabase Safe Mode
8. Phase 12 — Export / PWA / Mobile readiness
9. Phase 13 — Deployment Readiness
10. Phase 14 — Public SaaS Launch

The engine should not skip phases unless the user explicitly asks and the risk is explained.

---

# 3. Planning Input

The engine receives:

* Original idea
* Product strategy
* Requirements output
* Product blueprint
* AI team view
* Product memory
* Approval status
* Current phase
* User request
* Known blockers

---

# 4. Planning Output Object

The engine should produce:

## planning_output

* current_phase
* recommended_next_phase
* immediate_next_step
* chatgpt_track_responsibility
* codex_track_responsibility
* approval_needed
* build_readiness_checklist
* blockers
* risks_before_next_phase
* do_not_do_yet
* success_criteria
* suggested_codex_prompt_needed

---

# 5. ChatGPT Track A Responsibility

ChatGPT Track A owns:

* Product architecture
* UX logic
* Agent behavior
* Product intelligence
* Output templates
* Documentation
* Planning
* Specifications
* Approval logic
* Codex prompts
* Safety rules
* Product memory structure
* Phase boundaries

ChatGPT Track A should not directly modify production code unless explicitly requested.

---

# 6. Codex Track Responsibility

Codex Track owns implementation after clear approval.

Codex can work on:

* Local files
* Modular implementation
* UI wiring
* Placeholder engines
* Safe frontend logic
* Safe backend routes
* Local tests
* Documentation updates

Codex must not:

* Touch KisanMitraAI production
* Expose secrets
* Deploy publicly without approval
* Redesign frozen Studio V3
* Make database changes without approval
* Add authentication without approval
* Skip roadmap phases
* Decide product direction alone

---

# 7. Approval Logic

The Planning Engine must clearly say what requires approval.

Approval is required before:

* Freezing blueprint
* Moving to Phase 6
* Starting design system generation
* Starting pixel-matched conversion
* Starting frontend generation
* Starting backend generation
* Adding authentication
* Creating database schema
* Connecting Supabase
* Exporting PWA/mobile
* Preparing deployment
* Launching public SaaS

Approval must be explicit.

Examples:

* “Approve Product Blueprint v1.0 before moving to Phase 6.”
* “Approve Design Direction before starting frontend generation.”
* “Approve Data Map before database planning.”

---

# 8. Build Readiness Checklist

The Planning Engine should check readiness by phase.

## Phase 6 — Design System Engine

Ready when:

* Product blueprint is approved
* Target user is clear
* Screen map is clear
* Design direction is roughly known
* Design Constitution is available

## Phase 7 — Pixel-Matched Converter

Ready when:

* Visual reference image is provided
* Pixel matching rules are approved
* Text replacement rules are clear
* Layout preservation rules are clear

## Phase 8 — Frontend Generator

Ready when:

* Design system is approved
* Screen map is approved
* Component behavior is clear
* Mobile-first rules are clear

## Phase 9 — Backend Generator

Ready when:

* Data flow is approved
* API behavior is clear
* AI behavior is clear
* Backend safety rules are clear

## Phase 10 — Authentication + Roles

Ready when:

* User roles are approved
* Permission model is approved
* Login/signup flow is approved
* Admin boundary is clear

## Phase 11 — Supabase Safe Mode

Ready when:

* Data requirements are approved
* Tables are planned
* RLS/safety rules are planned
* No secrets are exposed

## Phase 12 — Export / PWA / Mobile Readiness

Ready when:

* Frontend is stable
* App shell is clear
* PWA assets are planned
* Mobile experience is tested

## Phase 13 — Deployment Readiness

Ready when:

* Build is stable
* Environment variables are separated
* Domain plan is approved
* Rollback plan is ready

## Phase 14 — Public SaaS Launch

Ready when:

* Pricing is approved
* Onboarding is ready
* Legal/privacy basics are ready
* Support flow is ready
* Launch checklist is complete

---

# 9. Risk Logic

The Planning Engine should identify risks before moving forward.

Risk categories:

## Scope Risk

The product is becoming too large too early.

## UX Risk

The user journey is unclear or too complex.

## Design Risk

Design direction is not approved.

## Technical Risk

Frontend/backend/data requirements are unclear.

## Safety Risk

The next step could expose secrets, touch production, or deploy too early.

## Product Risk

The target user, problem, or value promise is unclear.

## Approval Risk

The system is trying to move forward without human approval.

---

# 10. Do-Not-Do-Yet Logic

For each phase, the Planning Engine should state what should not happen yet.

Examples:

During Phase 5:

* Do not generate final frontend.
* Do not generate backend.
* Do not create database schema.
* Do not connect Supabase.
* Do not add authentication.
* Do not deploy.
* Do not redesign Studio V3.

During Phase 6:

* Do not code full frontend before design system approval.
* Do not create backend logic.
* Do not deploy.

During Phase 8:

* Do not create database tables unless Phase 11 is approved.
* Do not deploy unless Phase 13 is approved.

---

# 11. Planning Response Format

When showing planning output, use:

## Planning

### Current Phase

Phase name.

### Recommended Next Phase

Next phase name.

### Immediate Next Step

One clear action.

### ChatGPT Track A Responsibility

What ChatGPT should prepare.

### Codex Track Responsibility

What Codex should implement only after approval.

### Approval Needed

What user must approve.

### Build Readiness Checklist

* Item 1
* Item 2
* Item 3

### Risks Before Next Phase

* Risk 1
* Risk 2

### Do Not Do Yet

* Item 1
* Item 2

### Success Criteria

What confirms the next phase is ready.

---

# 12. Example

User idea:

“I want to create an AI app where a person writes a rough app idea and the system turns it into a product blueprint, screen plan, design direction, and future build plan.”

## Planning

### Current Phase

Phase 5 — AI Product Brain.

### Recommended Next Phase

Phase 6 — Design System Engine.

### Immediate Next Step

Approve Product Blueprint v1.0, then define the design system rules.

### ChatGPT Track A Responsibility

Prepare design system architecture, UX rules, design logic, and Codex prompt.

### Codex Track Responsibility

After approval, implement safe Phase 6 placeholder structure without redesigning Studio V3.

### Approval Needed

Approve the Phase 5 Product Blueprint before moving to Phase 6.

### Build Readiness Checklist

* Product strategy exists.
* Requirements are grouped.
* Blueprint is created.
* Screen map is clear.
* Human approval is recorded.
* Design Constitution v1.0 exists.

### Risks Before Next Phase

* Design system may become too visual-heavy if not controlled.
* Frontend generation may start too early.
* Studio V3 frozen UI must be protected.

### Do Not Do Yet

* Do not generate final frontend.
* Do not generate backend.
* Do not create database schema.
* Do not deploy.
* Do not touch KisanMitraAI production.

### Success Criteria

Phase 6 is ready when the design system can guide future UI generation without adding UI clutter or breaking the frozen Studio V3 flow.

---

# 13. Success Criteria

The Planning Engine is successful when:

* The next step is always clear.
* The roadmap is respected.
* ChatGPT and Codex responsibilities are separated.
* Human approval gates are visible.
* The system avoids premature building.
* Risks are shown before moving forward.
* Studio V3 remains clean.
* Product work stays aligned with:

**Less UI. More Intelligence.**
