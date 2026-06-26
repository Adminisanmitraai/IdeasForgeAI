# IdeasForgeAI

## Phase 5D — Product Strategy Engine Specification

### Version 1.0

## Purpose

The Product Strategy Engine turns a rough idea into a clear product direction.

It should help IdeasForgeAI understand not only what the user wants to build, but why the product should exist, who it helps, what should be built first, and how it can become valuable.

Core mantra:

**Less UI. More Intelligence.**

---

# 1. Engine Responsibility

The Product Strategy Engine defines:

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

It should make the product feel sharper before design or code begins.

---

# 2. Strategy Input

The engine receives:

* Original user idea
* Refined idea
* User answers from Dynamic Question Engine
* Smart assumptions
* Product memory
* Current phase
* Approval status

The engine should not wait for perfect information.
It should use safe assumptions and clearly mark what is still uncertain.

---

# 3. Strategy Output Object

The engine should produce:

## product_strategy

* product_category
* target_users
* main_problem
* value_promise
* mvp_scope
* key_differentiator
* future_expansion
* risk_level
* complexity_level
* launch_direction
* assumptions
* open_questions

---

# 4. Product Category Logic

The engine should classify the idea into one or more categories:

* AI app builder
* SaaS product
* Marketplace
* Internal business tool
* Personal productivity tool
* Client portal
* Mobile app
* Web app
* AI agent platform
* Automation tool
* Data dashboard
* Creative tool
* Learning product
* Commerce product
* Community product
* Other

The category helps decide future screens, features, data needs, and build phases.

---

# 5. Target User Logic

The engine should identify:

* Primary user
* Secondary user
* Admin or owner
* Future roles

Example user groups:

* Founder
* Creator
* Developer
* Designer
* Business owner
* Agency
* Client
* Customer
* Team member
* Admin
* Public user

If the target user is unclear, the engine should ask one clear question:

“Who is the primary user?”

---

# 6. Problem Logic

The engine should define the problem in simple language.

It should answer:

* What pain is the user facing?
* What is slow, confusing, expensive, or difficult today?
* What manual work does the product reduce?
* What decision does the product make easier?
* What output does the product improve?

The problem should not be generic.

Weak problem:

“Users need an app.”

Strong problem:

“Non-technical founders struggle to turn rough ideas into clear product plans, screen maps, and build-ready specifications.”

---

# 7. Value Promise Logic

The engine should define the promise of the product.

It should answer:

* What result does the user get?
* How does the product save time?
* How does it reduce confusion?
* How does it improve quality?
* Why would someone use it repeatedly?

Value promise format:

“This product helps [target user] achieve [result] by [method].”

Example:

“This product helps founders convert rough ideas into approved product blueprints by using an AI product team workflow before design or code starts.”

---

# 8. MVP Scope Logic

The engine must protect the product from becoming too large too early.

MVP scope should include only what is needed for first usable value.

MVP should define:

* Must-have features
* Must-have screens
* Must-have AI behavior
* Must-have output
* What should wait

The engine should separate:

## MVP Now

Build first.

## Later

Useful but not needed immediately.

## Avoid for Now

Could create risk, delay, or confusion.

---

# 9. Differentiator Logic

The engine should identify what makes the product more valuable than a normal app, template, or generator.

Possible differentiators:

* Chat-first product shaping
* AI team behavior
* Human approval checkpoints
* Design before code
* Product memory
* Safe build planning
* Mobile-first output
* Pixel-matched future conversion
* Full product lifecycle support
* Export and launch readiness later

Differentiator should be practical, not hype.

---

# 10. Future Expansion Logic

The engine should define future growth without overloading MVP.

Expansion examples:

* Design System Engine
* Pixel-Matched Converter
* Frontend Generator
* Backend Generator
* Authentication and roles
* Supabase Safe Mode
* Export / PWA / mobile readiness
* Deployment readiness
* Public SaaS launch
* Team collaboration
* Paid plans
* Templates
* Marketplace

Expansion should follow roadmap order unless user approves a change.

---

# 11. Risk Level Logic

Risk level should be:

* Low
* Medium
* High

Risk should consider:

* Product clarity
* UX complexity
* AI reliability
* Data sensitivity
* Backend complexity
* Role complexity
* Payment or compliance needs
* Deployment risk
* User trust risk

Example:

Low risk: simple personal tool with no saved sensitive data.
Medium risk: SaaS with accounts and saved projects.
High risk: product handling payments, health, finance, legal, or sensitive data.

---

# 12. Complexity Level Logic

Complexity should be:

* Simple
* Moderate
* Advanced
* Complex

Complexity should consider:

* Number of user roles
* Number of screens
* AI decision depth
* Data storage
* Integrations
* Authentication
* Backend logic
* Export/deployment needs

The engine should not confuse ambition with complexity.
A large vision can still have a simple MVP.

---

# 13. Launch Direction Logic

The engine should define where the product is heading:

* Personal tool
* Internal tool
* Client deliverable
* Public web app
* Public SaaS
* PWA
* Mobile app
* Marketplace
* Enterprise platform

Launch direction affects later phases, but should not trigger deployment in Phase 5.

---

# 14. Strategy Response Format

When showing strategy to the user, use:

## Product Strategy

* Product category:
* Target users:
* Main problem:
* Value promise:
* MVP scope:
* Key differentiator:
* Future expansion:
* Risk level:
* Complexity level:
* Launch direction:

## Strategy Note

One short paragraph explaining why this direction is strong.

## Open Questions

Only list questions that truly matter.

---

# 15. Strategy Example

User idea:

“I want to create an AI app where a person writes a rough app idea and the system turns it into a product blueprint, screen plan, design direction, and future build plan.”

## Product Strategy

* Product category: AI Product Factory / AI app builder
* Target users: founders, creators, agencies, non-technical product builders
* Main problem: users have ideas but struggle to convert them into clear product plans before design and code
* Value promise: convert rough ideas into structured blueprints, screen plans, and build-ready direction
* MVP scope: chat-first idea intake, smart questions, strategy, requirements, blueprint, planning, approval checkpoint
* Key differentiator: behaves like an AI product team instead of a simple generator
* Future expansion: design system, pixel converter, frontend/backend generator, auth, database safe mode, export, deployment
* Risk level: medium
* Complexity level: advanced vision with moderate MVP
* Launch direction: public SaaS later, internal product factory first

## Strategy Note

The strongest direction is to make this product think before it builds. That creates trust, reduces failed generation, and makes the product more valuable than a normal app builder.

---

# 16. Safety Rules

The Product Strategy Engine must not:

* Promise instant production-ready apps
* Skip approval steps
* Recommend deployment before readiness
* Assume sensitive data handling is safe
* Assume payment model without confirmation
* Push backend/database generation too early
* Treat strategy as final without approval

---

# 17. Success Criteria

The Product Strategy Engine is successful when:

* The product direction becomes clearer
* MVP scope becomes smaller and stronger
* Future expansion is captured without bloating the first build
* The user understands why the product matters
* Strategy supports later requirements and blueprint generation
* Studio V3 Preview can display the strategy cleanly
* The system stays aligned with:

**Less UI. More Intelligence.**
