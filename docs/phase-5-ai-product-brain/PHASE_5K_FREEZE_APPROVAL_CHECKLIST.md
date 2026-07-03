# IdeasForgeAI

## Phase 5K â€” Freeze & Approval Checklist

### Version 1.0

## Purpose

This document defines when Phase 5 â€” AI Product Brain is ready to freeze.

Phase 5 should only be frozen when IdeasForgeAI can reliably understand a rough product idea, ask smart questions, generate structured product intelligence, update memory safely, and require human approval before moving to Phase 6.

Core mantra:

**Less UI. More Intelligence.**

---

# 1. Phase 5 Freeze Goal

Phase 5 is ready to freeze when IdeasForgeAI can take a rough idea and produce:

* Understanding
* Intent
* Missing Information
* Smart Assumptions
* Product Strategy
* Requirements
* Product Blueprint
* AI Team View
* Product Memory Summary
* Planning
* Approval Needed
* Next Step

The system must feel like an AI product team, not a simple app generator.

---

# 2. Required Phase 5 Documents

Before freezing Phase 5, the following docs should exist:

* PHASE_5A_MASTER_PROMPT.md
* PHASE_5B_OUTPUT_TEMPLATES.md
* PHASE_5C_DYNAMIC_QUESTION_ENGINE.md
* PHASE_5D_PRODUCT_STRATEGY_ENGINE.md
* PHASE_5E_REQUIREMENTS_ENGINE.md
* PHASE_5F_BLUEPRINT_ENGINE.md
* PHASE_5G_PLANNING_ENGINE.md
* PHASE_5H_AI_TEAM_CONVERSATION_MODEL.md
* PHASE_5I_PRODUCT_MEMORY_STRUCTURE.md
* PHASE_5J_STUDIO_V3_INTERACTION_FLOW.md
* PHASE_5K_FREEZE_APPROVAL_CHECKLIST.md

---

# 3. Studio V3 Freeze Checks

Studio V3 must:

* Open successfully
* Keep frozen layout
* Keep clean light-mode interface
* Keep Create Mode working
* Keep Preview Mode working
* Keep bottom input bar working
* Avoid heavy forms
* Avoid dashboard clutter
* Avoid redesign
* Avoid empty Product Brain cards after idea submission

Studio V3 must not show:

* Raw Product Brain provider failure text
* Old public launch domain text
* IdeasForgeAI production text
* Raw errors
* Secret values
* Deployment actions without approval

---

# 4. Product Brain Output Checks

After a user submits a product idea, the Product Brain should populate:

## Understanding

Should summarize the idea clearly.

## Intent

Should detect intent type, confidence, reason, and next action.

## Missing Information

Should list only important missing details.

## Smart Assumptions

Should show safe assumptions.

## Product Strategy

Should show product category, target user, problem, value, MVP, differentiator, future expansion, risk, and complexity.

## Requirements

Should show functional, screen, AI behavior, data, safety, approval, and future phase requirements.

## Blueprint

Should show product identity, problem, promise, user journey, feature map, screen map, data map, AI behavior, risk map, and build readiness.

## AI Team View

Should show compact views from Product Manager, UX Strategist, Visual Design Thinker, Technical Architect, QA/Risk Reviewer, and Business Strategy Advisor.

## Planning

Should show current phase, recommended next phase, approval needed, risks, do-not-do-yet list, and next step.

## Product Memory

Should update safely with idea, answers, assumptions, strategy, requirements, blueprint, planning, and approval status.

---

# 5. Dynamic Question Checks

The question engine must:

* Ask one question at a time
* Avoid long forms
* Support Continue
* Support Edit Answer
* Support Skip
* Support Save Draft
* Remember skipped questions
* Ask useful questions only
* Allow safe assumptions
* Continue strategy and blueprint drafting without waiting for every answer

Default first question should usually be:

â€œWho is the primary user?â€

---

# 6. Approval Checks

Phase 5 must clearly require approval before Phase 6.

Required approval message:

â€œApprove Product Blueprint v1.0 before moving to Phase 6 Design System Engine.â€

The system must not treat silence as approval.

Approval options should include:

* Approve
* Revise
* Save Draft
* Ask More Questions
* Freeze

---

# 7. Safety Checks

Phase 5 must not:

* Expose secrets
* Add real database writes
* Connect Supabase
* Add authentication
* Generate production backend
* Generate final frontend
* Export PWA/mobile
* Deploy publicly
* Touch IdeasForgeAI production
* Modify unrelated projects
* Skip human approval

---

# 8. Local Intelligence Mode Checks

If external AI provider is missing, local intelligence mode must still work.

It should produce:

* Intent
* Current question
* Smart assumptions
* Product strategy
* Requirements
* Draft blueprint
* AI team view
* Planning
* Approval checkpoint
* Product memory update

It must not show broken error states.

---

# 9. Test Idea

Use this standard test idea:

â€œI want to create an AI app where a person writes a rough app idea and the system turns it into a product blueprint, screen plan, design direction, and future build plan.â€

Expected result:

* Intent: new_product
* Product category: AI Product Factory / AI app builder
* Target users: founders, creators, agencies, non-technical product builders
* Main problem: users have rough ideas but cannot convert them into clear product plans
* MVP: idea input, intent detection, smart questions, strategy, requirements, blueprint, planning, approval
* Differentiator: behaves like an AI product team before building
* Recommended next phase: Phase 6 â€” Design System Engine after blueprint approval

---

# 10. PowerShell Validation

Run:

```powershell
cd D:\APPS\IdeasForgeAI
python -m compileall backend\product_brain
```

Run safety search:

```powershell
Get-ChildItem -Recurse -File -Include *.py,*.js,*.html,*.md |
Where-Object {
  $_.FullName -notmatch "\\.venv\\" -and
  $_.FullName -notmatch "\\__pycache__\\" -and
  $_.FullName -notmatch "\\generated-apps\\"
} |
Select-String -Pattern "raw provider failure text","old public domain text","unapproved launch domain text" -CaseSensitive:$false
```

Studio V3 test URL:

```text
http://127.0.0.1:5173/frontend/pages/studio-v3.html
```

---

# 11. Freeze Decision

Phase 5 can be frozen if:

* All Phase 5 docs exist
* Product Brain syntax check passes
* Studio V3 opens
* AI status is clean
* Product Brain cards populate
* One-question flow works
* Product memory updates
* Approval checkpoint appears
* No secrets are exposed
* No production deployment happens
* No IdeasForgeAI production files are touched
* No frozen Studio V3 redesign happened

---

# 12. Freeze Statement

When all checks pass, record:

â€œPhase 5 â€” AI Product Brain is frozen. IdeasForgeAI can now move to Phase 6 â€” Design System Engine after user approval.â€

---

# 13. If Not Ready

If any check fails, do not freeze Phase 5.

Instead, run:

* Phase 5 Refinement Pass 2
* Fix Studio V3 card population
* Fix Product Brain local intelligence output
* Fix Product Memory update
* Fix approval checkpoint
* Fix safety text
* Re-test

---

# 14. Success Criteria

Phase 5 is successful when IdeasForgeAI thinks before building.

The user should feel:

â€œI explained my idea normally, and IdeasForgeAI shaped it like a real product team.â€

Final rule:

**Freeze the brain only when it is useful, safe, structured, and approval-driven.**

