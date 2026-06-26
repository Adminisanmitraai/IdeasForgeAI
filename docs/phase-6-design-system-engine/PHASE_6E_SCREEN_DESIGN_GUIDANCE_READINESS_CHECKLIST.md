# IdeasForgeAI

## Phase 6E — Screen Design Guidance & Readiness Checklist

### Version 1.0

## Purpose

This document defines how the Design System Engine should create screen-level design guidance and decide when a product is ready to move from design planning into Pixel-Matched Conversion or Frontend Generation.

Phase 6 must design before code.

Core mantra:

**Less UI. More Intelligence.**

---

# 1. Screen Guidance Role

Screen guidance converts the approved product blueprint into screen-by-screen design direction.

It does not generate final frontend code.

It defines:

* Screen purpose
* Main user action
* Content hierarchy
* Required components
* Visual tone
* Mobile behavior
* Empty state
* Error state
* Approval state
* Do-not-do rules

---

# 2. Required Screen Guidance Format

Every screen should use this format:

## Screen Design Guidance

### Screen Name

Name of the screen.

### Screen Purpose

What this screen helps the user do.

### Primary User Action

The main action the user should take.

### Secondary Actions

Helpful but non-primary actions.

### Content Hierarchy

What appears first, second, third.

### Required Components

Which components are needed.

### Visual Tone

How this screen should feel.

### Mobile Behavior

How the screen should behave on small screens.

### Empty State

What appears before content exists.

### Loading State

What appears while AI is working.

### Error / Safe Fallback State

What appears if AI/provider/build step is unavailable.

### Approval State

What must be approved before moving forward.

### Do Not Do

What the screen must avoid.

---

# 3. IdeasForgeAI Core Screens

For IdeasForgeAI itself, Phase 6 should define design guidance for:

1. Create Mode
2. Product Preview Mode
3. Question Flow
4. Product Strategy View
5. Requirements View
6. Blueprint View
7. Planning View
8. AI Team View
9. Product Memory Summary
10. Approval Checkpoint
11. Design Direction Preview
12. Public SaaS Readiness View
13. Pixel-Matched Converter Placeholder

---

# 4. Create Mode Guidance

## Screen Name

Create Mode

## Screen Purpose

Let the user describe a product idea naturally.

## Primary User Action

Type a rough product idea.

## Required Components

* Chat input
* AI response card
* User message card
* Bottom input bar
* Send button
* Mic placeholder
* Attachment placeholder

## Visual Tone

Calm, intelligent, founder-friendly.

## Mobile Behavior

* Full-width stacked chat cards
* Bottom input remains easy to reach
* Buttons stay thumb-friendly
* No dense panels

## Empty State

“Tell me your product idea, and I will shape it like a product team.”

## Do Not Do

* Do not show long forms
* Do not ask technical setup questions first
* Do not generate code immediately
* Do not ask for secrets

---

# 5. Product Preview Mode Guidance

## Screen Name

Product Preview Mode

## Screen Purpose

Show the product idea becoming structured before design or code.

## Primary User Action

Review product strategy, requirements, blueprint, planning, and approval status.

## Required Components

* Product Strategy card
* Requirements card
* Blueprint card
* Planning card
* AI Team View card
* Product Memory summary
* Approval checkpoint

## Visual Tone

Structured, calm, reviewable.

## Mobile Behavior

Cards stack vertically.

## Empty State

“Submit a product idea to generate product strategy, requirements, blueprint, and planning.”

## Do Not Do

* Do not show empty cards after idea submission
* Do not show raw JSON
* Do not show internal booleans
* Do not trigger build automatically

---

# 6. Question Flow Guidance

## Screen Name

Question Flow

## Screen Purpose

Ask one important missing question at a time.

## Primary User Action

Answer the current question.

## Required Components

* Question label
* Main question
* Answer input
* Continue button
* Edit Answer button
* Skip button
* Save Draft button

## Visual Tone

Simple, guided, non-blocking.

## Default First Question

“Who is the primary user?”

## Do Not Do

* Do not ask all questions at once
* Do not make it feel like a form
* Do not treat skipped questions as failure

---

# 7. Product Strategy View Guidance

## Screen Name

Product Strategy View

## Screen Purpose

Show product direction clearly.

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

## Do Not Do

* Do not duplicate fields
* Do not use hype language
* Do not mix MVP and future expansion

---

# 8. Requirements View Guidance

## Screen Name

Requirements View

## Screen Purpose

Show what the product must do.

## Required Groups

* Functional requirements
* Screen requirements
* AI behavior requirements
* Data requirements
* Safety requirements
* Approval requirements
* Future phase requirements

## Do Not Do

* Do not create database schema
* Do not generate frontend/backend
* Do not mix all requirements into one long list

---

# 9. Blueprint View Guidance

## Screen Name

Blueprint View

## Screen Purpose

Show the product source of truth before design/build.

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

## Do Not Do

* Do not treat blueprint as frozen without approval
* Do not hide risks
* Do not start Phase 6 automatically

---

# 10. Planning View Guidance

## Screen Name

Planning View

## Screen Purpose

Show what should happen next.

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

## Do Not Do

* Do not show raw booleans
* Do not show technical internal values
* Do not recommend skipping approval

---

# 11. AI Team View Guidance

## Screen Name

AI Team View

## Screen Purpose

Show compact product-team guidance.

## Required Roles

* Product Manager
* UX Strategist
* Visual Design Thinker
* Technical Architect
* QA / Risk Reviewer
* Business Strategy Advisor

## Do Not Do

* Do not show long internal debate
* Do not overload user
* Do not reveal hidden reasoning

---

# 12. Product Memory Summary Guidance

## Screen Name

Product Memory Summary

## Screen Purpose

Show what IdeasForgeAI remembers safely.

## Required Fields

* Product name
* Current phase
* Current status
* Last saved idea
* Pending approval
* Next step
* Memory safety note

## Do Not Do

* Do not show raw memory JSON
* Do not store or show secrets
* Do not expose private credentials

---

# 13. Approval Checkpoint Guidance

## Screen Name

Approval Checkpoint

## Screen Purpose

Stop premature generation and require human approval.

## Required Message

“Approve Product Blueprint v1.0 before moving to Phase 6 Design System Engine.”

For Phase 6:

“Approve Design System v1.0 before moving to Pixel-Matched Conversion or Frontend Generation.”

## Required Actions

* Approve
* Revise
* Save Draft
* Ask More Questions
* Freeze

## Do Not Do

* Do not treat silence as approval
* Do not unlock future generation too early

---

# 14. Design Direction Preview Guidance

## Screen Name

Design Direction Preview

## Screen Purpose

Show the approved or draft design system direction.

## Required Sections

* Design positioning
* Brand personality
* Visual style
* Typography rules
* Color rules
* Component rules
* Layout rules
* Mobile-first rules
* Accessibility rules
* Approval needed

## Do Not Do

* Do not generate final frontend code
* Do not redesign Studio V3
* Do not move to Phase 8 without approval

---

# 15. Design Readiness Checklist

A product is ready for Design System approval when:

* Product Blueprint v1.0 exists
* Blueprint is approved or explicitly allowed for draft design
* Target user is clear
* Product category is clear
* Screen map is clear
* Brand personality is defined
* Visual style is defined
* Component rules are defined
* Layout rules are defined
* Mobile-first rules are defined
* Accessibility rules are defined
* Do-not-do rules are defined
* Approval checkpoint is visible

---

# 16. Ready for Phase 7 Checklist

Ready for Phase 7 — Pixel-Matched Converter when:

* Design System v1.0 is approved
* Reference image or visual target is available
* Pixel-matching rules are approved
* Text replacement rules are clear
* Layout preservation rules are clear
* Human approval is recorded

---

# 17. Ready for Phase 8 Checklist

Ready for Phase 8 — Frontend Generator when:

* Product Blueprint v1.0 is approved
* Design System v1.0 is approved
* Screen map is approved
* Component rules are approved
* Layout rules are approved
* Mobile-first rules are approved
* Interaction behavior is approved

---

# 18. Not Ready Conditions

Do not move forward when:

* Blueprint is missing
* Design direction is unclear
* User has not approved design system
* Screen map is unclear
* Mobile behavior is undefined
* Component rules are missing
* User is asking for code too early
* Safety rules are missing
* Studio V3 would need redesign
* Secrets, deployment, database, or auth are involved too early

---

# 19. Success Criteria

Phase 6E is successful when:

* Every major screen has clear design guidance
* Design readiness can be checked
* Phase 7 receives clean pixel-matching inputs
* Phase 8 receives clean frontend design inputs
* Human approval remains required
* Studio V3 remains protected
* The product stays aligned with:

**Less UI. More Intelligence.**
