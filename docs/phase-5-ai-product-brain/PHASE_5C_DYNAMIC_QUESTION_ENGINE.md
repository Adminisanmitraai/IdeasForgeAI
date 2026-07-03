# IdeasForgeAI

## Phase 5C â€” Dynamic Question Engine Specification

### Version 1.0

## Purpose

The Dynamic Question Engine helps IdeasForgeAI understand a product idea without forcing the user into long forms.

The goal is simple:

Ask fewer questions.
Ask smarter questions.
Infer safely.
Move the product forward.

Core mantra:

**Less UI. More Intelligence.**

---

# 1. What This Engine Does

The Dynamic Question Engine decides:

* What is already understood
* What is missing
* What can be safely assumed
* What must be asked before blueprint creation
* What can wait until a later phase
* Which question should be asked next

It should feel like a smart product manager, not a form.

---

# 2. Main Rule

Never ask all questions at once.

IdeasForgeAI should ask:

* One question at a time in Studio V3
* 3 to 5 questions maximum in Guided Mode
* Only critical questions in Fast Mode
* Deeper questions only in Expert Mode

The system should not block progress unless the missing answer is truly important.

---

# 3. Question Modes

## Fast Mode

Use when the user wants speed.

Behavior:

* Ask 1 to 3 questions only
* Make safe assumptions
* Create quick product direction
* Do not go deep into architecture

Best for:

* Quick idea shaping
* Early product exploration
* Small tools
* Personal apps

## Guided Mode

Default mode.

Behavior:

* Ask 3 to 5 important questions
* Infer obvious answers
* Prepare strategy, requirements, and blueprint
* Keep language simple

Best for:

* Serious product planning
* Founder product ideas
* SaaS concepts
* AI tools
* Mobile/web apps

## Expert Mode

Use when the product is complex.

Behavior:

* Ask deeper questions about users, roles, AI, data, security, integrations, monetization, scale, and deployment
* Still avoid unnecessary questions
* Group questions carefully if needed

Best for:

* Public SaaS
* Marketplace products
* Enterprise tools
* AI agent platforms
* Products with payments, roles, databases, or compliance needs

---

# 4. Question Priority Order

The engine should ask questions in this order:

## Priority 1 â€” Product Purpose

Question examples:

* What should this product mainly do?
* What result should the user get from this product?

Why it matters:

Without purpose, the product cannot be shaped.

## Priority 2 â€” Target User

Question examples:

* Who is the primary user?
* Is this for individuals, businesses, teams, clients, or public users?

Why it matters:

User type controls UX, features, data, roles, and pricing.

## Priority 3 â€” Main Workflow

Question examples:

* What should the user do first?
* What should happen after the user gives input?
* What should the final output look like?

Why it matters:

Workflow controls screen map and feature map.

## Priority 4 â€” AI Role

Question examples:

* Should AI only suggest, or should it also generate output?
* Should AI ask questions before creating anything?
* Should AI behave like an assistant, expert, agent, or product team?

Why it matters:

AI behavior defines the intelligence layer.

## Priority 5 â€” Human Approval

Question examples:

* Should the user approve before design or code is generated?
* Should AI wait before making major changes?

Why it matters:

IdeasForgeAI must stay safe by default.

## Priority 6 â€” Data Needs

Question examples:

* Should this product save user data?
* Should it remember previous sessions?
* Should there be product memory, user memory, or project memory?

Why it matters:

Data affects backend, database, privacy, and Supabase Safe Mode later.

## Priority 7 â€” User Roles

Question examples:

* Does this product need roles like user, admin, client, team member, or owner?
* Should different users see different screens?

Why it matters:

Roles affect authentication and permissions in later phases.

## Priority 8 â€” Business Direction

Question examples:

* Is this for personal use, client work, internal use, or public SaaS?
* Should it support paid plans later?

Why it matters:

Business model affects launch strategy and product structure.

## Priority 9 â€” Design Direction

Question examples:

* Should the product feel simple, premium, playful, professional, or enterprise?
* Should it be mobile-first?

Why it matters:

Design belongs to Phase 6, but Phase 5 should capture direction.

## Priority 10 â€” Build Constraints

Question examples:

* Should this be web-first, mobile-first, PWA, or app-store ready later?
* Are there any integrations needed?

Why it matters:

This affects later frontend, backend, export, and deployment phases.

---

# 5. Question Selection Logic

For every user idea, the engine should classify each information area:

* Known
* Probably known
* Safely assumable
* Missing but not blocking
* Missing and blocking

Only ask questions that are:

* Missing and blocking
* Important for product direction
* Needed before blueprint approval

Do not ask questions that can wait for later phases.

---

# 6. Safe Assumption Rules

The engine may safely assume:

* Mobile-first by default
* Clean light-mode UI
* Human approval before code generation
* Design before code
* Visual before technical
* MVP first, advanced features later
* No deployment without approval
* No database changes without safe mode
* No secrets handled in chat

The engine must not assume:

* Payment model
* Legal/compliance needs
* Sensitive data handling
* User identity or private information
* Real deployment target
* Final database schema
* Final authentication roles
* Production readiness

---

# 7. Question Types

## Clarifying Question

Used when the idea is unclear.

Example:

â€œWhat is the main result the user should get from this product?â€

## Choice Question

Used when the user may not know how to explain.

Example:

â€œIs this product mainly for personal use, client work, internal team use, or public SaaS?â€

## Confirmation Question

Used when the AI can infer but needs approval.

Example:

â€œI will assume this should be mobile-first and approval-based. Is that correct?â€

## Expansion Question

Used after the base idea is clear.

Example:

â€œShould this product later support paid users or team accounts?â€

## Risk Question

Used when something may affect safety or architecture.

Example:

â€œWill this product store sensitive user data?â€

---

# 8. One-Question-at-a-Time Behavior

Studio V3 should ask one main question at a time.

Each question card should include:

* Question label
* Short reason if needed
* Answer field
* Continue
* Edit Answer
* Skip
* Save Draft

The question should not feel like a form.

The AI should remember skipped questions as unresolved, not failed.

---

# 9. Question Flow Example

User idea:

â€œI want to create an AI app where a person writes a rough app idea and the system turns it into a product blueprint, screen plan, design direction, and future build plan.â€

## Understanding

The product is an AI product planning and app-building assistant.

## Known

* Product type: AI product factory
* User input: rough idea
* Output: blueprint, screen plan, design direction, build plan
* AI role: product team style assistant

## Missing

* Primary user
* Approval workflow
* Whether output should be saved
* Whether this is personal, client, or SaaS
* Whether it should generate code later

## First Question

Who is the primary user?

Reason:

This decides whether the experience should be founder-friendly, agency-friendly, enterprise-focused, or public SaaS-ready.

## Next Questions

1. Should the system ask approval before design/code?
2. Should it save product memory across sessions?
3. Is this for personal use, client work, or public SaaS?
4. Should it eventually generate installable app/PWA files?

---

# 10. Output Object

The Dynamic Question Engine should produce a structured object:

## question_engine_output

* mode
* known_information
* missing_information
* safe_assumptions
* blocking_questions
* non_blocking_questions
* current_question
* reason_for_question
* answer_status
* next_question
* skipped_questions
* ready_for_strategy
* ready_for_blueprint

---

# 11. Readiness Logic

## Ready for Strategy

The product is ready for strategy when:

* Main purpose is known
* Target user is known or safely assumed
* Main problem is known
* Expected output is known

## Ready for Requirements

The product is ready for requirements when:

* Strategy is clear
* Main workflow is known
* AI role is known or safely assumed
* Screen needs are roughly known

## Ready for Blueprint

The product is ready for blueprint when:

* Product identity is clear
* User journey is clear
* MVP boundary is clear
* Safety and approval assumptions are clear

## Ready for Phase 6

The product is ready for Phase 6 Design System Engine when:

* Blueprint is approved
* Screen map is approved
* Design direction is at least roughly approved
* Human approval is recorded

---

# 12. UX Rules

The question engine must keep Studio V3 clean.

Do not add:

* Long questionnaires
* Multi-step wizard UI
* Heavy admin panels
* Complex forms
* Too many buttons
* Technical settings too early

Use:

* One question at a time
* Short answer input
* Smart assumptions
* Skip option
* Save Draft option
* Clean preview cards

---

# 13. AI Tone

The question engine should sound:

* Calm
* Useful
* Founder-friendly
* Product-minded
* Confident but not pushy
* Simple, not technical

Avoid:

* â€œPlease fill this formâ€
* â€œYou must answer all fieldsâ€
* â€œInsufficient dataâ€
* â€œCannot proceedâ€
* â€œTechnical configuration requiredâ€

Prefer:

* â€œI can move forward with safe assumptions.â€
* â€œThis answer will help shape the product direction.â€
* â€œWe can refine this later.â€
* â€œIâ€™ll keep this simple.â€

---

# 14. Success Criteria

Phase 5C is successful when:

* IdeasForgeAI asks fewer but better questions
* The user does not feel blocked
* The system can infer safe defaults
* One-question-at-a-time flow works
* Missing information is tracked
* Skipped questions are remembered
* Strategy can start before everything is perfect
* Blueprint creation requires only critical clarity
* Studio V3 remains clean
* The product feels intelligent, not form-driven

Final rule:

**Questions should reduce confusion, not create friction.**

