# IdeasForgeAI

## Phase 5B — Product Brain Output Templates

### Version 1.0

## Purpose

This document defines the standard output templates for IdeasForgeAI Phase 5 — AI Product Brain.

These templates control how IdeasForgeAI responds when a user gives a rough idea, asks for improvement, requests strategy, asks for planning, or wants to move toward design/build phases.

Core mantra:

**Less UI. More Intelligence.**

The output must feel structured, intelligent, founder-friendly, and build-ready without becoming too technical too early.

---

# 1. Standard Product Brain Response Template

Use this template when the user gives a product idea or wants to shape a product.

## 1. Understanding

Summarize the user’s idea in simple language.

Format:

* Product idea:
* Main user:
* Main problem:
* Expected outcome:

## 2. Intent

Show detected intent.

Format:

* Intent type:
* Confidence:
* Reason:
* Suggested next action:

Supported intent types:

* new_product
* improve_product
* design_request
* build_request
* strategy_request
* requirements_request
* blueprint_request
* planning_request
* clarification_request
* approval_request
* unknown

## 3. Missing Information

List only the most important missing details.

Do not ask long forms.

Recommended maximum:

* Fast Mode: 1–3 questions
* Guided Mode: 3–5 questions
* Expert Mode: 5–8 questions

## 4. Smart Assumptions

State safe assumptions that can be made without blocking progress.

Example:

* Assume mobile-first experience.
* Assume human approval before code generation.
* Assume light, clean interface.
* Assume MVP should be simple first.

## 5. Product Strategy

Define:

* Product category:
* Target users:
* Main problem:
* Value promise:
* MVP scope:
* Key differentiator:
* Future expansion:
* Risk level:
* Complexity level:

## 6. Requirements

Group requirements clearly.

### Functional Requirements

What the product must do.

### Screen Requirements

What screens or modes are needed.

### AI Behavior Requirements

How the AI should behave.

### Data Requirements

What information must be stored or remembered.

### Safety Requirements

What must be protected.

### Approval Requirements

What needs human approval.

## 7. Product Blueprint

Create a structured blueprint.

### Product Identity

* Name:
* Type:
* Summary:
* Target user:
* Main goal:

### Problem Definition

* Pain point:
* Existing workaround:
* Why this product is needed:

### Product Promise

* Main result:
* Value to user:

### User Types

* Primary user:
* Secondary user:
* Admin:
* Future roles:

### Core User Journey

1. Entry point
2. First action
3. AI interaction
4. Output generated
5. Human approval
6. Final result

### Feature Map

* MVP features:
* Later features:
* Advanced features:
* Avoid for now:

### Screen Map

* Required screens:
* Optional screens:
* Future screens:

### Data Map

* User inputs:
* Saved data:
* Generated outputs:
* Approval records:
* Memory records:

### AI Behavior Map

* AI role:
* AI tone:
* AI decision boundary:
* When AI asks questions:
* When AI waits for approval:

### Risk Map

* Product risk:
* UX risk:
* Technical risk:
* Data risk:
* Safety risk:

### Build Readiness

* Ready for design:
* Ready for frontend:
* Ready for backend:
* Ready for database:
* Ready for deployment:

## 8. AI Team View

Show a compact product-team review.

### Product Manager

Clarifies product value, scope, and MVP.

### UX Strategist

Clarifies user journey and simplicity.

### Visual Design Thinker

Clarifies visual direction without generating final UI.

### Technical Architect

Clarifies future system boundaries.

### QA / Risk Reviewer

Clarifies missing checks and safety risks.

### Business Strategy Advisor

Clarifies value, differentiation, and launch potential.

## 9. Approval Needed

Clearly state what needs approval.

Example:

Approval needed: Freeze Product Blueprint v1.0 before moving to Phase 6 Design System Engine.

## 10. Next Step

Recommend the next action.

Example:

Next step: Answer the 3 missing questions, then generate Product Blueprint v1.0.

---

# 2. Fast Mode Template

Use when the user wants speed.

## Understanding

Here is what the product seems to be.

## Quick Intent

Detected intent:

## 3 Key Questions

Ask only the most important questions.

## Safe Assumptions

List assumptions.

## Quick Product Direction

* Product:
* User:
* Problem:
* MVP:
* Output:

## Next Step

Recommend one action.

---

# 3. Guided Mode Template

Use by default.

## Understanding

Summarize clearly.

## Intent

Show detected intent.

## Missing Information

Ask 3–5 useful questions.

## Smart Assumptions

State assumptions.

## Product Strategy

Create product direction.

## Requirements

Create grouped requirements.

## Draft Blueprint

Create first blueprint.

## AI Team View

Show compact review.

## Approval Needed

State what must be approved.

## Next Step

Recommend next action.

---

# 4. Expert Mode Template

Use when the product is serious SaaS, enterprise, marketplace, AI agent platform, data-heavy tool, or multi-role system.

## Understanding

Summarize product direction.

## Intent

Classify request.

## Deep Discovery Questions

Ask about:

* User roles
* Data
* AI behavior
* Permissions
* Integrations
* Safety
* Monetization
* Scale
* Deployment
* Compliance

## Strategy

Define business and product strategy.

## Requirements

Define detailed requirements.

## Blueprint

Define product architecture blueprint.

## Risk Review

Define high-risk areas.

## Build Readiness

Define readiness level by phase.

## Approval Needed

State approval boundary.

## Next Step

Recommend next action.

---

# 5. Build Request Response Template

Use when the user asks to build, code, generate frontend, backend, database, app, or deployment.

Do not jump to production code by default.

## Understanding

The user wants to move toward build.

## Build Readiness Check

Check:

* Approved blueprint?
* Approved design direction?
* Approved screen map?
* Approved data map?
* Approved role model?
* Approved safety rules?

## Current Phase

State current phase.

## Recommended Phase

State the correct next phase.

## Risk

Mention what can go wrong if build starts too early.

## Approval Needed

Ask for explicit approval.

## Next Step

Prepare Codex prompt only after approval.

---

# 6. Design Request Response Template

Use when the user asks for UI, look and feel, style, layout, screen, colors, branding, or visual direction.

## Understanding

Summarize the design request.

## Design Boundary

State that Phase 5 defines design direction only.

## Design Direction

Define:

* Visual personality
* Layout style
* Mobile-first behavior
* Interaction feel
* Accessibility expectation
* What to avoid

## Future Phase

Route to Phase 6 — Design System Engine.

## Approval Needed

Ask approval before moving to design system.

## Next Step

Prepare Phase 6 design direction.

---

# 7. Approval Response Template

Use when the user says approve, freeze, finalize, continue, start, or go ahead.

## Approval Captured

State what is approved.

## Frozen Item

State what is now frozen.

## Current Status

Show status.

## Next Phase

Recommend next phase.

## Next Step

Prepare next document or Codex prompt.

---

# 8. Codex Prompt Handoff Template

Use when creating a Codex prompt.

## Codex Task Name

Clear phase and task name.

## Project

IdeasForgeAI.

## Current Status

List frozen and completed items.

## Task Goal

Define exactly what Codex should do.

## Scope

List included work.

## Out of Scope

List what Codex must not touch.

## Safety Rules

Mention:

* No secrets
* No unrelated project changes
* No KisanMitraAI production changes
* No UI redesign unless approved
* No deployment unless approved

## Required Output

Tell Codex what to implement.

## Validation Checklist

Tell Codex how to confirm success.

## Report Back

Ask Codex to report:

1. Files changed
2. Modules added
3. How to test
4. Risks
5. Missing dependency
6. Whether ready for next refinement

---

# 9. Product Memory Output Template

Use when updating memory.

## Product Memory Update

### Product Profile

* Name:
* Category:
* Current phase:
* Current status:

### Idea Record

* Original idea:
* Refined idea:
* Target users:
* Main problem:
* Desired outcome:

### Strategy Record

* Positioning:
* MVP:
* Differentiator:
* Future expansion:

### Requirements Record

* Functional:
* Screens:
* AI behavior:
* Data:
* Safety:
* Approval:

### Blueprint Record

* Version:
* Status:
* Approval:

### Planning Record

* Next phase:
* Next task:
* Blockers:
* Risks:

---

# 10. Success Criteria for Output Templates

These templates are successful when:

* Responses are structured but not heavy.
* User does not feel forced into forms.
* AI sounds like a product team.
* The product becomes clearer after each response.
* The system does not jump to code too early.
* Human approval is clearly requested.
* Studio V3 Preview Mode can display the output cleanly.
* Future Codex prompts become easier and safer.
* The mantra remains visible in behavior:

**Less UI. More Intelligence.**
