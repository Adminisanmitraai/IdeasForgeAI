# IdeasForgeAI

## Phase 5E — Requirements Engine Specification

### Version 1.0

## Purpose

The Requirements Engine converts a product idea and strategy into clear, structured requirements.

It should help IdeasForgeAI define what the product must do before any design, frontend, backend, database, authentication, export, or deployment work begins.

Core mantra:

**Less UI. More Intelligence.**

---

# 1. Engine Responsibility

The Requirements Engine creates organized requirements for:

* Product behavior
* User flows
* Screens
* AI behavior
* Data
* Safety
* Human approval
* Future build readiness

It must not generate production code.

It must not create database schemas.

It must not start frontend or backend generation.

Its job is to create clarity.

---

# 2. Inputs

The Requirements Engine receives:

* Original user idea
* Refined idea
* Intent Engine output
* Dynamic Question Engine answers
* Smart assumptions
* Product Strategy output
* Product memory
* Current phase
* Approval status

The engine should use available information and clearly mark missing or assumed details.

---

# 3. Requirements Output Object

The engine should produce:

## requirements_output

* functional_requirements
* screen_requirements
* ai_behavior_requirements
* data_requirements
* safety_requirements
* approval_requirements
* non_functional_requirements
* future_phase_requirements
* open_questions
* readiness_status

---

# 4. Functional Requirements

Functional requirements define what the product must do.

Examples:

* User can enter a product idea in natural language.
* System can detect the user’s intent.
* System can ask smart follow-up questions.
* System can generate product strategy.
* System can generate requirements.
* System can generate a product blueprint.
* System can prepare a future build plan.
* User can approve, revise, skip, or save draft.

Functional requirements should be written in simple product language.

Avoid technical implementation details unless needed.

---

# 5. Screen Requirements

Screen requirements define what visible modes, pages, or views are needed.

For IdeasForgeAI, Phase 5 should respect the frozen Studio V3 structure:

* Create Mode
* Product Preview Mode
* Product Brain cards
* Question card
* Approval checkpoint
* Planning summary

Screen requirements should not redesign Studio V3.

They should describe what information appears inside the existing structure.

Example:

* Create Mode should allow the user to submit a rough product idea.
* Preview Mode should show strategy, requirements, blueprint, planning, and approval status.
* Question card should ask one question at a time.
* Product Strategy card should show product category, target users, problem, MVP, and differentiator.

---

# 6. AI Behavior Requirements

AI behavior requirements define how IdeasForgeAI should act.

The AI should:

* Behave like a compact product team.
* Ask fewer but smarter questions.
* Make safe assumptions.
* Explain uncertainty clearly.
* Avoid jumping to code.
* Wait for approval before major phase transitions.
* Keep the product direction clean and founder-friendly.
* Route design work to Phase 6.
* Route pixel conversion to Phase 7.
* Route frontend generation to Phase 8.
* Route backend generation to Phase 9.

The AI should not:

* Generate production code by default.
* Expose secrets.
* Touch unrelated projects.
* Modify production systems.
* Skip approval gates.
* Overload the user with technical questions.

---

# 7. Data Requirements

Data requirements define what information should be remembered or stored later.

In Phase 5, this should be a safe local product memory structure only.

Possible data objects:

* Product profile
* Original idea
* Refined idea
* User answers
* Smart assumptions
* Strategy output
* Requirements output
* Blueprint output
* Planning output
* Approval status
* Revision history
* Skipped questions

The Requirements Engine should not create a final database schema.

Database planning belongs to later phases.

Supabase Safe Mode belongs to Phase 11.

---

# 8. Safety Requirements

Safety requirements define what must be protected.

IdeasForgeAI must protect:

* User secrets
* API keys
* Production systems
* KisanMitraAI production
* Frozen Studio V3 UI
* Human approval gates
* Deployment safety
* Database safety
* Project separation

Safety rules:

* No production deployment without approval.
* No database write logic without safe mode.
* No authentication or role system without approval.
* No secret handling in chat.
* No unrelated project changes.
* No hidden build steps.
* No automatic public publishing.

---

# 9. Approval Requirements

Approval requirements define what the human must approve before moving forward.

Approval is required before:

* Freezing product blueprint
* Moving to Phase 6 Design System Engine
* Starting pixel-matched conversion
* Generating frontend
* Generating backend
* Creating database structure
* Adding authentication and roles
* Connecting Supabase
* Exporting app or PWA
* Preparing deployment
* Public SaaS launch

Approval status values:

* draft
* needs_clarification
* ready_for_approval
* approved
* frozen
* superseded
* blocked

---

# 10. Non-Functional Requirements

Non-functional requirements define product quality expectations.

For IdeasForgeAI, include:

* Mobile-first experience
* Light mode by default
* Clean interface
* Fast perceived response
* Founder-friendly language
* Structured output
* Safe fallback mode
* No visible technical overload
* Human-readable product documents
* Future-ready modular structure

---

# 11. Future Phase Requirements

The Requirements Engine should capture future needs without building them now.

Future phase mapping:

## Phase 6 — Design System Engine

Needs approved product blueprint and design direction.

## Phase 7 — Pixel-Matched Converter

Needs uploaded reference image or approved visual target.

## Phase 8 — Frontend Generator

Needs approved screen map and design system.

## Phase 9 — Backend Generator

Needs approved data flow and backend logic plan.

## Phase 10 — Authentication + Roles

Needs approved user roles and permission model.

## Phase 11 — Supabase Safe Mode

Needs approved data requirements and safety rules.

## Phase 12 — Export / PWA / Mobile Readiness

Needs approved frontend and app structure.

## Phase 13 — Deployment Readiness

Needs approved production checklist.

## Phase 14 — Public SaaS Launch

Needs approved launch, pricing, onboarding, and safety plan.

---

# 12. Requirement Quality Rules

Good requirements should be:

* Clear
* Short
* Testable
* Grouped by type
* Founder-friendly
* Build-ready later
* Safe by default

Bad requirements are:

* Too vague
* Too technical too early
* Mixed together
* Not connected to user value
* Missing approval gates
* Jumping directly into implementation

Example weak requirement:

“Build AI.”

Example strong requirement:

“The system should analyze the user’s rough product idea and generate a structured product strategy before any design or code is created.”

---

# 13. Requirements Response Format

When showing requirements to the user, use:

## Requirements

### Functional Requirements

* Requirement 1
* Requirement 2
* Requirement 3

### Screen Requirements

* Requirement 1
* Requirement 2

### AI Behavior Requirements

* Requirement 1
* Requirement 2

### Data Requirements

* Requirement 1
* Requirement 2

### Safety Requirements

* Requirement 1
* Requirement 2

### Approval Requirements

* Requirement 1
* Requirement 2

### Future Phase Requirements

* Requirement 1
* Requirement 2

---

# 14. Readiness Logic

The Requirements Engine should decide whether the product is ready for blueprint.

## Ready for Blueprint

Yes, if:

* Product purpose is clear
* Target user is clear or safely assumed
* Main workflow is clear
* MVP boundary is clear
* AI role is clear
* Safety assumptions are clear

## Needs Clarification

Use when:

* Target user is unknown
* Main output is unclear
* AI role is unclear
* Product type is unclear

## Blocked

Use only when:

* The product cannot be understood
* The user requests unsafe work
* Required approval is missing
* The next phase would create serious risk

---

# 15. Example

User idea:

“I want to create an AI app where a person writes a rough app idea and the system turns it into a product blueprint, screen plan, design direction, and future build plan.”

## Functional Requirements

* User can submit a rough app idea.
* System detects whether the user is starting a new product or improving an existing one.
* System asks one smart question at a time.
* System generates product strategy.
* System generates grouped requirements.
* System generates a product blueprint.
* System creates a future phase plan.
* User can approve before moving to design or build.

## Screen Requirements

* Create Mode for idea entry.
* Product Preview Mode for structured output.
* Question card for one-question-at-a-time discovery.
* Strategy, Requirements, Blueprint, and Planning cards.

## AI Behavior Requirements

* AI behaves like a product team.
* AI asks only important questions.
* AI makes safe assumptions.
* AI does not jump to code.
* AI waits for approval before future phases.

## Data Requirements

* Store original idea.
* Store user answers.
* Store assumptions.
* Store strategy.
* Store requirements.
* Store blueprint.
* Store approval status.

## Safety Requirements

* No secrets.
* No production changes.
* No deployment without approval.
* No database generation in Phase 5.
* No KisanMitraAI production touch.

## Approval Requirements

* User must approve Product Blueprint v1.0 before Phase 6.
* User must approve design direction before frontend generation.
* User must approve database and deployment steps later.

---

# 16. Success Criteria

The Requirements Engine is successful when:

* Product needs are clearly grouped.
* The user can understand what will be built.
* Codex can later follow the requirements safely.
* Future phases receive clean inputs.
* Studio V3 Preview shows requirements clearly.
* The system avoids premature coding.
* Human approval gates are visible.
* The product remains aligned with:

**Less UI. More Intelligence.**
