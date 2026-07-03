# IdeasForgeAI

## Phase 6C â€” Component System & Screen Rules

### Version 1.0

## Purpose

This document defines the component system and screen rules for IdeasForgeAI Phase 6 â€” Design System Engine.

The goal is to make future generated screens consistent, clean, mobile-first, and approval-driven.

Core mantra:

**Less UI. More Intelligence.**

---

# 1. Component System Role

The component system defines reusable UI building blocks.

It should help IdeasForgeAI generate future screens without redesigning from scratch every time.

The component system should support:

* Create Mode
* Product Preview Mode
* Question flow
* Product Strategy display
* Requirements display
* Blueprint display
* Planning display
* Approval flow
* Product memory summary
* Future design preview
* Future frontend generation

The component system must keep the interface simple.

---

# 2. Component Philosophy

Every component should have a clear job.

A component should answer:

* What is this for?
* What should the user do here?
* What information matters?
* What should be hidden?
* What action is safe?
* What needs approval?

Avoid components that exist only for decoration.

---

# 3. Core Component Categories

## Input Components

Used when the user gives information.

Includes:

* Chat input
* Question answer input
* Text area
* File/image upload placeholder
* Voice/mic placeholder
* Choice chips

## Display Components

Used when IdeasForgeAI shows product intelligence.

Includes:

* Understanding card
* Product Strategy card
* Requirements card
* Blueprint card
* Planning card
* AI Team View card
* Product Memory summary card

## Action Components

Used when the user moves forward.

Includes:

* Continue button
* Send button
* Approve button
* Revise button
* Skip button
* Save Draft button
* Open Tools button

## Status Components

Used to show current state.

Includes:

* AI status
* Phase status
* Approval status
* Readiness status
* Safety status
* Local intelligence mode status

## Preview Components

Used when showing product output.

Includes:

* Product preview panel
* Screen map preview
* Design direction preview
* Build readiness preview
* Approval checkpoint preview

---

# 4. Chat Input Component

## Purpose

Allows the user to describe ideas naturally.

## Rules

* Keep input simple.
* Keep placeholder friendly.
* Keep Send button visible.
* Keep mobile typing comfortable.
* Do not overload with technical controls.
* Do not ask for secrets.
* Do not trigger production actions directly.

## Good Placeholder

â€œAsk IdeasForgeAI to build...â€

## Better Future Placeholder

â€œDescribe your product idea...â€

---

# 5. Question Card Component

## Purpose

Asks one smart question at a time.

## Required Elements

* Small label: One question at a time
* Main question
* Answer input
* Continue button
* Edit Answer button
* Skip button
* Save Draft button

## Rules

* Ask only one main question.
* Use simple language.
* Do not feel like a form.
* Skipped questions should remain unresolved, not failed.
* Continue should update product memory.

## Default First Question

â€œWho is the primary user?â€

---

# 6. Product Strategy Card

## Purpose

Shows product direction.

## Required Fields

* Product category
* Target users
* Main problem
* Value promise
* MVP scope
* Key differentiator
* Future expansion
* Risk level
* Complexity level
* Launch direction
* Assumptions
* Open questions

## Rules

* Avoid duplicate fields.
* Avoid hype.
* Keep language founder-friendly.
* Show MVP clearly.
* Separate future expansion from MVP.

---

# 7. Requirements Card

## Purpose

Shows what the product must do.

## Required Groups

* Functional requirements
* Screen requirements
* AI behavior requirements
* Data requirements
* Safety requirements
* Approval requirements
* Future phase requirements

## Rules

* Keep grouped requirements clear.
* Do not mix technical implementation into product requirements.
* Do not generate database schemas here.
* Do not start frontend/backend generation.

---

# 8. Blueprint Card

## Purpose

Shows the product source of truth.

## Required Sections

* Product identity
* Problem definition
* Product promise
* User types
* Core user journey
* Feature map
* Screen map
* Data map
* AI behavior map
* Risk map
* Build readiness
* Approval checkpoint

## Rules

* Blueprint must be reviewable by a non-technical founder.
* Blueprint must be useful for future Codex prompts.
* Blueprint should not be treated as frozen until approved.

---

# 9. Planning Card

## Purpose

Shows what happens next.

## Required Fields

* Current phase
* Recommended next phase
* Immediate next step
* ChatGPT Track responsibility
* Codex Track responsibility
* Approval needed
* Build readiness checklist
* Risks before next phase
* Do not do yet
* Success criteria

## Rules

* Do not show raw booleans like true/false.
* Do not show technical internal values.
* Use human-friendly labels.
* Do not move to next phase without approval.

---

# 10. AI Team View Card

## Purpose

Makes IdeasForgeAI feel like a product team.

## Required Roles

* Product Manager
* UX Strategist
* Visual Design Thinker
* Technical Architect
* QA / Risk Reviewer
* Business Strategy Advisor

## Rules

* Keep each role short.
* Do not show internal debate.
* Do not overload the user.
* Use this card to support decisions, not create noise.

---

# 11. Product Memory Summary Card

## Purpose

Shows what IdeasForgeAI remembers without exposing raw memory objects.

## Required Fields

* Product name
* Current phase
* Current status
* Last saved idea
* Pending approval
* Next step
* Memory safety note

## Rules

* Do not show raw JSON.
* Do not show secrets.
* Do not show hidden reasoning.
* Keep summary compact.

---

# 12. Approval Card

## Purpose

Stops premature generation.

## Required Message

â€œApprove Product Blueprint v1.0 before moving to Phase 6 Design System Engine.â€

## Possible Actions

* Approve
* Revise
* Save Draft
* Ask More Questions
* Freeze

## Rules

* Silence is not approval.
* Approval must be explicit.
* Do not unlock Phase 6/7/8 actions before approval.

---

# 13. Screen Rules

## Create Mode

Purpose:

User enters idea through chat.

Rules:

* Full-screen
* Chat-first
* Minimal controls
* No heavy forms
* No technical setup first
* No premature code generation

## Product Preview Mode

Purpose:

Shows structured product intelligence.

Rules:

* Full-screen
* Clear cards
* Strategy, Requirements, Blueprint, Planning visible
* Approval checkpoint visible
* Product memory summary visible
* No empty cards after idea submission

## Design Direction Preview

Purpose:

Phase 6 screen for showing visual direction.

Rules:

* Show brand personality
* Show visual style
* Show component rules
* Show mobile-first rules
* Show approval checkpoint
* Do not generate final frontend

## Future Frontend Preview

Purpose:

Later Phase 8 output preview.

Rules:

* Requires approved design system
* Requires approved screen map
* Must not start in Phase 6

---

# 14. Screen Layout Rules

## Mobile

* Stack cards vertically.
* Keep buttons thumb-friendly.
* Keep input visible.
* Keep text readable.
* Avoid dense grids.
* Avoid tiny labels.

## Desktop

* Cards may use two-column layout.
* Maintain reading clarity.
* Do not overuse sidebars.
* Do not become an admin dashboard.

---

# 15. Empty State Rules

Empty states should guide, not confuse.

Good empty state:

â€œDescribe your product idea to generate strategy, requirements, blueprint, and planning.â€

Bad empty state:

â€œNo data.â€

Every empty state should explain the next action.

---

# 16. Error State Rules

Error states should be human-readable.

Avoid:

* Raw HTTP provider codes
* Stack traces
* Provider failed
* Boolean errors
* Raw exception names

Use:

* â€œProduct Brain is running in local intelligence mode.â€
* â€œI can continue with safe local output.â€
* â€œThis step needs approval before generation.â€

---

# 17. Do-Not-Do Rules

Do not:

* Redesign Studio V3
* Add complex dashboards
* Add too many controls
* Generate frontend in Phase 6
* Generate backend in Phase 6
* Add database/auth/Supabase
* Deploy
* Show secrets
* Show raw JSON by default
* Show internal booleans
* Use IdeasForgeAI production references

---

# 18. Success Criteria

Phase 6C is successful when:

* Core components are clearly defined
* Future screens can be generated consistently
* Studio V3 remains protected
* Product Brain output stays clean
* Approval flow is visible
* Mobile-first behavior is clear
* Future Phase 7 and Phase 8 have usable design rules
* The product stays aligned with:

**Less UI. More Intelligence.**

