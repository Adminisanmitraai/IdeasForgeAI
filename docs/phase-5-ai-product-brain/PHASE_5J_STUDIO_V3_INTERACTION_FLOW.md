# IdeasForgeAI

## Phase 5J â€” Studio V3 Interaction Flow Specification

### Version 1.0

## Purpose

This document defines how the AI Product Brain should behave inside Studio V3.

Studio V3 is the primary product experience.
It must remain clean, chat-first, full-screen, light-mode, and mobile-first.

Core mantra:

**Less UI. More Intelligence.**

---

# 1. Current Studio V3 Status

Studio V3 is frozen.

Current state:

* Create Mode is complete.
* Product Preview Mode is complete.
* Visual Design Engine placeholder exists.
* Design Constitution v1.0 exists.
* Product Brain local intelligence mode exists.
* Studio V2 remains backup/admin workspace.

Do not redesign Studio V3.

Do not add heavy panels.

Do not make it feel like a form builder.

---

# 2. Studio V3 Main Experience

Studio V3 should feel like this:

The user writes a rough product idea.
IdeasForgeAI thinks like a product team.
Preview Mode shows the product becoming structured.
The user approves before design or build begins.

The experience should not feel technical too early.

---

# 3. Main Flow

## Step 1 â€” User Enters Idea

User types a natural-language product idea in Create Mode.

Example:

â€œI want to create an AI app where a person writes a rough app idea and the system turns it into a product blueprint, screen plan, design direction, and future build plan.â€

## Step 2 â€” Intent Engine Runs

The system detects the userâ€™s intent.

Possible output:

* new_product
* improve_product
* design_request
* build_request
* strategy_request
* requirements_request
* blueprint_request
* planning_request
* approval_request
* unknown

## Step 3 â€” Product Brain Creates First Understanding

The system should show a short understanding summary.

It should not jump to code.

## Step 4 â€” Dynamic Question Engine Starts

The system asks one question at a time.

Default first question:

â€œWho is the primary user?â€

But the system should still generate draft strategy, requirements, blueprint, and planning using safe assumptions.

## Step 5 â€” Preview Cards Populate

Preview Mode should populate:

* Product Strategy
* Requirements
* Blueprint
* Planning
* AI Team View
* Product Memory Summary
* Approval Needed

Cards should not remain empty after a valid idea is submitted.

## Step 6 â€” User Answers or Skips

User can:

* Continue
* Edit Answer
* Skip
* Save Draft

Skipped questions should be remembered as unresolved, not treated as failure.

## Step 7 â€” Product Memory Updates

Product memory should update with:

* Original idea
* User answers
* Skipped questions
* Smart assumptions
* Strategy
* Requirements
* Blueprint
* Planning
* Approval status

## Step 8 â€” Approval Checkpoint Appears

The system should clearly show:

â€œApprove Product Blueprint v1.0 before moving to Phase 6 Design System Engine.â€

No future build phase should start without approval.

---

# 4. Studio V3 Preview Contract

Preview Mode must show structured product intelligence.

Required sections:

## Understanding

What the product idea means.

## Intent

Detected intent and confidence.

## Missing Information

Only important missing items.

## Smart Assumptions

Safe defaults used to move forward.

## Product Strategy

Product category, users, problem, value, MVP, differentiator, future expansion.

## Requirements

Functional, screen, AI behavior, data, safety, approval, and future phase requirements.

## Product Blueprint

Product identity, problem, promise, journey, feature map, screen map, data map, AI behavior, risks, readiness.

## AI Team View

Product Manager, UX Strategist, Visual Design Thinker, Technical Architect, QA/Risk, Business Strategy.

## Product Memory Summary

Current phase, current status, last saved idea, pending approval, next step.

## Approval Needed

What the user must approve before moving forward.

## Next Step

Recommended next action.

---

# 5. Create Mode Rules

Create Mode should:

* Accept natural language
* Stay chat-first
* Avoid long forms
* Avoid technical overload
* Ask smart questions
* Show progress calmly
* Keep bottom input simple

Create Mode should not:

* Force a wizard
* Ask too many questions
* Generate code immediately
* Ask for secrets
* Ask for deployment information too early

---

# 6. Preview Mode Rules

Preview Mode should:

* Make the product feel real before code
* Show structured output clearly
* Keep cards concise
* Show approval status
* Show next phase recommendation
* Support safe revision

Preview Mode should not:

* Show raw JSON to the user by default
* Show hidden reasoning
* Become a heavy admin dashboard
* Show empty cards after product idea submission
* Trigger build automatically

---

# 7. AI Status Rules

AI status should be calm and useful.

Good statuses:

* Ready
* Product Brain running in local intelligence mode
* Draft blueprint ready
* Waiting for approval
* Ready for Phase 6 after approval

Avoid statuses:

* Raw Product Brain provider failure codes
* Server error
* Provider missing
* Cannot proceed
* Unknown failure

If real AI provider is not available, fallback mode should still work.

---

# 8. Local Intelligence Mode

Local intelligence mode should generate useful draft output without external AI.

It should produce:

* Intent
* One current question
* Smart assumptions
* Product strategy
* Requirements
* Blueprint
* AI team view
* Planning
* Approval checkpoint
* Product memory update

It should not feel broken or empty.

---

# 9. Product Brain Card Behavior

## Product Strategy Card

Should show:

* Product category
* Target users
* Main problem
* Value promise
* MVP scope
* Differentiator

## Requirements Card

Should show:

* Functional requirements
* Screen requirements
* AI behavior requirements
* Data requirements
* Safety requirements
* Approval requirements

## Blueprint Card

Should show:

* Product identity
* User journey
* Feature map
* Screen map
* Risk map
* Build readiness

## Planning Card

Should show:

* Current phase
* Recommended next phase
* Approval needed
* Do not do yet
* Next step

## AI Team View Card

Should show compact expert views.

## Memory Summary Card

Should show simple status, not raw memory objects.

---

# 10. Approval Behavior

Studio V3 must require explicit approval before moving forward.

Approval options:

* Approve Blueprint
* Revise
* Save Draft
* Ask More Questions
* Freeze

Default approval message:

â€œApproval needed: Freeze Product Blueprint v1.0 before moving to Phase 6 Design System Engine.â€

Silence is not approval.

---

# 11. What Studio V3 Must Not Do in Phase 5

Do not:

* Generate production frontend
* Generate backend
* Create database schema
* Connect Supabase
* Add authentication
* Export app/PWA
* Deploy publicly
* Touch IdeasForgeAI production
* Expose secrets
* Redesign frozen UI

---

# 12. Success Criteria

Phase 5J is successful when:

* User can submit a product idea
* Product Brain responds with structured intelligence
* One-question-at-a-time flow works
* Preview cards are populated
* Local intelligence mode works without external provider
* Product memory updates safely
* Approval checkpoint is visible
* Studio V3 remains clean and frozen
* No future phase starts without approval
* The experience stays aligned with:

**Less UI. More Intelligence.**

