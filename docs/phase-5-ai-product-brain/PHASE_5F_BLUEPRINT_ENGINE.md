# IdeasForgeAI

## Phase 5F â€” Blueprint Engine Specification

### Version 1.0

## Purpose

The Blueprint Engine creates the central product document for every idea inside IdeasForgeAI.

The blueprint is the source of truth before design, frontend, backend, database, authentication, export, deployment, or SaaS launch begins.

Core mantra:

**Less UI. More Intelligence.**

---

# 1. Engine Responsibility

The Blueprint Engine converts:

* User idea
* Intent
* User answers
* Smart assumptions
* Product strategy
* Requirements
* Product memory

into one structured product blueprint.

The blueprint should make the product clear enough that future design, code, and deployment phases can follow it safely.

The Blueprint Engine must not generate production code.

---

# 2. Blueprint Role in IdeasForgeAI

The blueprint acts as the approved product foundation.

No major build phase should start before the blueprint is approved.

The blueprint controls:

* Product identity
* Product purpose
* User types
* Core journey
* MVP features
* Screen map
* Data map
* AI behavior
* Risk map
* Build readiness
* Approval status

---

# 3. Blueprint Input

The engine receives:

* Original idea
* Refined idea
* Intent Engine output
* Dynamic Question Engine output
* Product Strategy output
* Requirements output
* Product Memory
* Approval status
* Current roadmap phase

The engine should clearly mark:

* Confirmed information
* Safe assumptions
* Open questions
* Items requiring approval

---

# 4. Blueprint Output Object

The engine should produce:

## product_blueprint

* blueprint_version
* blueprint_status
* product_identity
* problem_definition
* product_promise
* user_types
* core_user_journey
* feature_map
* screen_map
* data_map
* ai_behavior_map
* risk_map
* build_readiness
* approval_checkpoint
* next_phase_recommendation

---

# 5. Blueprint Status Values

Supported statuses:

* draft
* needs_clarification
* ready_for_approval
* approved
* frozen
* superseded
* blocked

Default status:

* draft

Status should become:

* ready_for_approval when the blueprint is complete enough for user review
* approved when the user approves it
* frozen when the user says freeze/finalize
* blocked only when serious missing information or unsafe request prevents progress

---

# 6. Blueprint Sections

## 6.1 Product Identity

Defines what the product is.

Fields:

* Product name
* Product type
* One-line summary
* Target users
* Main goal
* Current phase

Example:

* Product name: IdeasForgeAI
* Product type: AI Product Factory
* Summary: A chat-first system that turns rough ideas into product blueprints, design direction, and future build plans.
* Target users: founders, creators, agencies, non-technical product builders
* Main goal: help users think, design, and plan before building

---

## 6.2 Problem Definition

Defines why the product is needed.

Fields:

* Pain point
* Current workaround
* Why current tools are not enough
* Why this product matters

Example:

Non-technical founders often have ideas but cannot convert them into clear product strategy, screen plans, requirements, and build-ready specifications. Normal app builders jump to UI or code too early, which creates weak products.

---

## 6.3 Product Promise

Defines what result the product gives.

Fields:

* Main user result
* Value delivered
* Time saved
* Confusion reduced
* Trust created

Example:

IdeasForgeAI helps users turn rough ideas into structured product blueprints with AI team guidance before any design or code begins.

---

## 6.4 User Types

Defines who uses the product.

Fields:

* Primary user
* Secondary user
* Admin or owner
* Future roles

Example:

* Primary user: founder or creator
* Secondary user: agency or product consultant
* Admin: product owner
* Future roles: team member, client reviewer, developer, designer

---

## 6.5 Core User Journey

Defines the basic flow.

Recommended journey:

1. User opens Studio V3 Create Mode.
2. User describes a rough product idea.
3. Intent Engine detects the request.
4. Dynamic Question Engine asks important missing questions.
5. Product Strategy Engine creates strategy.
6. Requirements Engine creates grouped requirements.
7. Blueprint Engine creates Product Blueprint v1.0.
8. Preview Mode shows the structured product plan.
9. User approves, revises, skips, or saves draft.
10. Planning Engine recommends the next phase.

---

## 6.6 Feature Map

Feature map should separate features by timing.

### MVP Features

* Chat-first idea input
* Intent detection
* One-question-at-a-time discovery
* Product strategy generation
* Requirements generation
* Blueprint generation
* AI team summary
* Approval checkpoint
* Product memory draft

### Later Features

* Design System Engine
* Pixel-Matched Converter
* Frontend Generator
* Backend Generator
* Authentication and roles
* Supabase Safe Mode
* Export / PWA / mobile readiness
* Deployment readiness
* Public SaaS launch

### Advanced Features

* Team collaboration
* Client review links
* Marketplace templates
* Paid plans
* Multi-project workspaces
* Version comparison
* Auto documentation export

### Avoid for Now

* Production deployment automation
* Payment systems
* Complex role permissions
* Real database writes
* Secret handling
* Overbuilt dashboards
* Heavy UI panels

---

## 6.7 Screen Map

Screen map defines visible product areas.

For Phase 5, respect frozen Studio V3.

Required screens or modes:

* Create Mode
* Product Preview Mode
* AI Product Brain card
* Question card
* Product Strategy card
* Requirements card
* Blueprint card
* Planning card
* Approval checkpoint

Future screens:

* Design System Preview
* Pixel Converter Workspace
* Frontend Preview
* Backend Plan View
* Auth/Roles Planner
* Supabase Safe Mode Console
* Export Center
* Deployment Readiness View
* SaaS Launch Console

---

## 6.8 Data Map

Data map defines what must be remembered.

Phase 5 local memory should include:

* Product profile
* Original idea
* Refined idea
* User answers
* Skipped questions
* Smart assumptions
* Strategy output
* Requirements output
* Blueprint output
* Planning output
* Approval status
* Revision history

Do not create final database schema in Phase 5.

Database planning belongs to later phases.

---

## 6.9 AI Behavior Map

Defines how the AI should act.

The AI should:

* Behave like a product team
* Ask fewer, smarter questions
* Infer safely
* Explain assumptions
* Avoid premature code
* Wait for human approval
* Preserve frozen Studio V3 UI
* Route future work to the correct roadmap phase
* Keep the user experience simple and clean

The AI should not:

* Generate production code without request
* Expose secrets
* Touch unrelated projects
* Touch IdeasForgeAI production
* Skip approval gates
* Push deployment too early

---

## 6.10 Risk Map

Risk map should include:

### Product Risk

Is the product direction unclear or too broad?

### UX Risk

Will users feel overwhelmed or confused?

### Technical Risk

Will future build phases require backend, database, roles, or integrations?

### Data Risk

Will user data, project memory, or sensitive information be stored?

### Safety Risk

Could the product expose secrets, change production systems, or deploy too early?

### Scope Risk

Is the MVP becoming too large?

---

## 6.11 Build Readiness

Build readiness should be marked by phase.

Use this format:

* Ready for Phase 6 Design System Engine: yes/no/partial
* Ready for Phase 7 Pixel-Matched Converter: yes/no/partial
* Ready for Phase 8 Frontend Generator: yes/no/partial
* Ready for Phase 9 Backend Generator: yes/no/partial
* Ready for Phase 10 Authentication + Roles: yes/no/partial
* Ready for Phase 11 Supabase Safe Mode: yes/no/partial
* Ready for Phase 12 Export / PWA / Mobile readiness: yes/no/partial
* Ready for Phase 13 Deployment Readiness: yes/no/partial
* Ready for Phase 14 Public SaaS Launch: yes/no/partial

In Phase 5, most later phases should usually be marked partial or no until approval and more planning are complete.

---

# 7. Approval Checkpoint

Every blueprint must include an approval checkpoint.

Format:

## Approval Needed

Approve Product Blueprint v1.0 before moving to Phase 6 Design System Engine.

Options:

* Approve
* Revise
* Save Draft
* Ask More Questions
* Freeze

Approval should be explicit.

Do not treat silence as approval.

---

# 8. Blueprint Response Format

When showing blueprint output, use:

## Product Blueprint

### Product Identity

* Name:
* Type:
* Summary:
* Target users:
* Main goal:

### Problem Definition

* Pain point:
* Current workaround:
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

1. Step one
2. Step two
3. Step three

### Feature Map

* MVP:
* Later:
* Advanced:
* Avoid for now:

### Screen Map

* Required:
* Optional:
* Future:

### Data Map

* Inputs:
* Saved data:
* Generated outputs:
* Approval records:
* Memory records:

### AI Behavior Map

* AI role:
* AI tone:
* AI boundaries:
* Approval behavior:

### Risk Map

* Product risk:
* UX risk:
* Technical risk:
* Data risk:
* Safety risk:

### Build Readiness

* Ready for Phase 6:
* Ready for Phase 7:
* Ready for Phase 8:
* Ready for Phase 9:

### Approval Needed

State what must be approved.

---

# 9. Example Blueprint

User idea:

â€œI want to create an AI app where a person writes a rough app idea and the system turns it into a product blueprint, screen plan, design direction, and future build plan.â€

## Product Identity

* Name: IdeasForgeAI
* Type: AI Product Factory
* Summary: A chat-first system that turns rough product ideas into structured blueprints and build plans.
* Target users: founders, creators, agencies, non-technical product builders
* Main goal: help users think before building

## Problem Definition

Users often have ideas but do not know how to convert them into clear product strategy, requirements, screens, and build-ready plans. Normal builders jump too quickly to code or UI.

## Product Promise

IdeasForgeAI helps users transform rough ideas into structured product plans through an AI product team workflow.

## User Types

* Primary user: founder or creator
* Secondary user: agency or product consultant
* Admin: product owner
* Future roles: designer, developer, client reviewer

## Core User Journey

1. User enters a rough idea.
2. AI detects intent.
3. AI asks smart missing questions.
4. AI generates strategy.
5. AI generates requirements.
6. AI creates blueprint.
7. User approves blueprint.
8. System recommends next phase.

## Feature Map

* MVP: idea intake, intent detection, smart questions, strategy, requirements, blueprint, planning, approval
* Later: design system, pixel converter, frontend/backend generator, auth, database safe mode, export, deployment
* Avoid now: payment, public launch automation, complex admin dashboards

## Build Readiness

* Ready for Phase 6: partial, after approval
* Ready for Phase 7: no, needs visual reference
* Ready for Phase 8: no, needs design system
* Ready for Phase 9: no, needs backend plan

## Approval Needed

Approve Product Blueprint v1.0 before moving to Phase 6 Design System Engine.

---

# 10. Success Criteria

The Blueprint Engine is successful when:

* Product direction becomes clear
* MVP scope is visible
* Screens are mapped
* Data needs are captured safely
* AI behavior is defined
* Risks are visible
* Approval is required before next phase
* Studio V3 Preview can show the blueprint cleanly
* Future Codex prompts can follow the blueprint safely
* The product remains aligned with:

**Less UI. More Intelligence.**

