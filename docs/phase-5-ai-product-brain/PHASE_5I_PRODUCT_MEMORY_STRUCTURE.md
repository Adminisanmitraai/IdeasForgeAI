# IdeasForgeAI

## Phase 5I — Product Memory Structure

### Version 1.0

## Purpose

The Product Memory Structure defines what IdeasForgeAI should remember about each product idea.

Product memory allows IdeasForgeAI to continue working intelligently across phases without losing product direction, user answers, approvals, risks, or roadmap status.

Core mantra:

**Less UI. More Intelligence.**

---

# 1. Memory Responsibility

Product Memory should store:

* Original product idea
* Refined product direction
* User answers
* Smart assumptions
* Product strategy
* Requirements
* Blueprint
* Planning
* AI team view
* Approval status
* Revision history
* Current roadmap phase
* Next recommended step

Product Memory should not store secrets.

Product Memory should not store production credentials.

Product Memory should not modify real databases in Phase 5.

---

# 2. Phase 5 Memory Rule

In Phase 5, memory should be local and safe.

It can exist as:

* Local object
* Local JSON
* Session memory
* Draft memory file
* Preview state

It should not require Supabase yet.

Supabase Safe Mode belongs to Phase 11.

---

# 3. Main Memory Objects

Product Memory should include these main objects:

1. Product Profile
2. Idea Record
3. Question Record
4. Strategy Record
5. Requirements Record
6. Blueprint Record
7. AI Team Record
8. Planning Record
9. Approval Record
10. Revision Record
11. Safety Record

---

# 4. Product Profile

Stores the main identity and status of the product.

## Fields

* product_id
* product_name
* product_category
* current_phase
* current_status
* owner_intent
* target_users
* last_approved_direction
* created_at
* updated_at

## Status Values

* draft
* needs_clarification
* ready_for_approval
* approved
* frozen
* superseded
* blocked

## Example

* product_name: IdeasForgeAI
* product_category: AI Product Factory
* current_phase: Phase 5 — AI Product Brain
* current_status: draft
* owner_intent: Build a product factory that turns rough ideas into approved product plans and future build outputs

---

# 5. Idea Record

Stores the raw and refined idea.

## Fields

* original_idea
* refined_idea
* main_problem
* desired_outcome
* target_users
* product_type
* idea_confidence
* open_clarifications

## Purpose

This lets the system remember what the user actually asked for before strategy or requirements changed the wording.

---

# 6. Question Record

Stores question engine activity.

## Fields

* question_mode
* questions_asked
* user_answers
* skipped_questions
* unanswered_questions
* safe_assumptions
* blocking_questions
* non_blocking_questions
* current_question
* ready_for_strategy
* ready_for_blueprint

## Purpose

This prevents IdeasForgeAI from asking the same questions repeatedly.

Skipped questions should remain visible as unresolved, not treated as failure.

---

# 7. Strategy Record

Stores product strategy output.

## Fields

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
* strategy_status

## Purpose

This becomes the strategy foundation for requirements and blueprint generation.

---

# 8. Requirements Record

Stores grouped requirements.

## Fields

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

## Purpose

This helps Codex later implement features safely without guessing product direction.

---

# 9. Blueprint Record

Stores the central product blueprint.

## Fields

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

## Purpose

The blueprint is the source of truth before moving to design or build.

No major future phase should start before blueprint approval.

---

# 10. AI Team Record

Stores the compact AI team review.

## Fields

* product_manager_view
* ux_strategist_view
* visual_design_view
* technical_architect_view
* qa_risk_view
* business_strategy_view
* team_summary_status

## Purpose

This keeps IdeasForgeAI behaving like a product team without showing long internal debate.

---

# 11. Planning Record

Stores next-step planning.

## Fields

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

## Purpose

This keeps the roadmap controlled and prevents premature building.

---

# 12. Approval Record

Stores human approvals.

## Fields

* approved_item
* approval_scope
* approval_status
* approval_time
* frozen_items
* pending_approval_items
* approval_notes

## Approval Status Values

* not_requested
* requested
* approved
* revise_requested
* frozen
* rejected
* blocked

## Purpose

This ensures IdeasForgeAI does not move from one major phase to another without explicit approval.

---

# 13. Revision Record

Stores product changes over time.

## Fields

* revision_id
* changed_item
* previous_value
* new_value
* reason_for_change
* changed_by
* changed_at
* revision_status

## Purpose

This helps the user track how the product evolved.

It is especially important before freezing blueprint, design direction, or build plans.

---

# 14. Safety Record

Stores safety boundaries.

## Fields

* secrets_detected
* production_touch_risk
* unrelated_project_risk
* deployment_risk
* database_risk
* auth_risk
* approval_missing_risk
* safety_notes
* safety_status

## Purpose

This keeps IdeasForgeAI safe by default.

Safety Record must flag:

* Secret exposure risk
* Production deployment risk
* KisanMitraAI separation risk
* Database write risk
* Auth and role risk
* Public launch risk

---

# 15. Memory Status Rules

Each memory object should have a status.

Allowed statuses:

* draft
* needs_clarification
* ready_for_approval
* approved
* frozen
* superseded
* blocked

## Draft

The object is being created.

## Needs Clarification

Important information is missing.

## Ready for Approval

The object is ready for user review.

## Approved

The user approved the object.

## Frozen

The user finalized the object.

## Superseded

A newer version replaced it.

## Blocked

Progress cannot continue safely.

---

# 16. Memory Update Rules

Product Memory should update when:

* User submits a new idea
* User answers a question
* User skips a question
* Strategy is generated
* Requirements are generated
* Blueprint is generated
* User approves something
* User asks to revise something
* Next phase is recommended
* Codex prompt is prepared
* Risk is detected

---

# 17. Memory Should Not Store

Do not store:

* API keys
* Passwords
* Tokens
* Private credentials
* Production secrets
* Payment card information
* Sensitive personal data unless explicitly required and approved
* Hidden reasoning
* Unrelated project data

---

# 18. Product Memory Example

## Product Profile

* Product name: IdeasForgeAI
* Category: AI Product Factory
* Current phase: Phase 5 — AI Product Brain
* Status: draft

## Idea Record

* Original idea: User wants an AI app that turns rough product ideas into blueprints, screen plans, design direction, and build plans.
* Refined idea: Chat-first AI product factory that thinks before building.
* Target users: founders, creators, agencies, non-technical product builders.
* Desired outcome: approved product blueprint and future build plan.

## Strategy Record

* Positioning: AI Product Factory
* MVP: idea intake, questions, strategy, requirements, blueprint, planning, approval
* Differentiator: behaves like a product team
* Risk level: medium
* Complexity: advanced vision with moderate MVP

## Requirements Record

* Functional: idea input, intent detection, smart questions, strategy, requirements, blueprint, planning
* Screens: Create Mode, Preview Mode, Product Brain cards
* AI behavior: ask smarter questions, avoid premature code, wait for approval
* Safety: no secrets, no production touch, no deployment

## Blueprint Record

* Version: v1.0 draft
* Status: ready_for_approval after user review
* Next phase: Phase 6 Design System Engine

## Planning Record

* Next step: approve blueprint before Phase 6
* ChatGPT responsibility: design system architecture and Codex prompt
* Codex responsibility: implementation only after approval

---

# 19. Studio V3 Memory Display Rule

Studio V3 should not show raw memory objects.

It should show simple summaries:

* Current phase
* Current status
* Last approved item
* Pending approval
* Next step
* Saved draft status

The memory should power intelligence in the background, not clutter the interface.

---

# 20. Future Supabase Mapping

In Phase 11, Product Memory may later map to Supabase tables.

Possible future tables:

* products
* product_ideas
* product_questions
* product_strategy
* product_requirements
* product_blueprints
* product_plans
* product_approvals
* product_revisions
* product_safety_logs

Do not create these tables in Phase 5.

This is future planning only.

---

# 21. Success Criteria

Product Memory is successful when:

* IdeasForgeAI remembers product direction
* It avoids asking the same questions repeatedly
* It tracks assumptions and approvals
* It supports future roadmap phases
* It separates ChatGPT and Codex responsibility
* It prevents premature code, database, auth, or deployment
* It keeps Studio V3 clean
* It stays aligned with:

**Less UI. More Intelligence.**
