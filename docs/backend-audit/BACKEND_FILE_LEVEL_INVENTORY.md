# IdeasForgeAI Backend File-Level Inventory

Audit date: 2026-06-25

Scope: backend source, backend architecture docs, Product Brain modules, agent system modules, core orchestration, API routes, generated app backend source folders, generated app local data files, and backend-facing deployment/ops references.

Out of scope: implementation changes, refactoring, dependency installation, deployment, production IdeasForgeAI changes, secrets, pycache files, virtual environments, and Phase 6 feature work.

## 1. Executive Summary

IdeasForgeAI has a working local backend foundation built around FastAPI, an in-process agent pipeline, generated app export folders, and the Phase 5 Product Brain. The backend is useful for local orchestration and placeholder intelligence, but it is not production-ready.

The strongest area is the breadth of local builder agents and Product Brain modules. The weakest area is backend governance: authentication, authorization, route protection, quality gates, persistence boundaries, retries, audit trails, and production-grade validation are not yet present.

Key counts:

| Area | Count |
| --- | ---: |
| Core backend folders inspected | 5 |
| Generated backend folders inspected | 10 |
| Total backend folders inspected | 15 |
| Core backend files inspected | 47 |
| Generated backend files inspected | 27 |
| Total backend files inspected | 74 |
| Core routes found | 13 |
| Generated app routes found | 66 |
| Total routes found | 79 |
| Product Brain implementation modules | 10 |

Biggest backend risk: route and generation endpoints are locally useful but exposed without authentication, authorization, rate limits, request ownership, durable job state, or production-quality guardrails.

## 2. Backend Folder Tree

First-party backend folders inspected:

```text
backend/
  agents/
  api/
  core/
  product_brain/
generated-apps/
  ideasforgeai/backend/
  IdeasForgeAIProduct/backend/
  IdeasForgeAIProduct/backend/data/
  leadflowai/backend/
  persistcrm1/backend/
  persistcrm1/backend/data/
  runtimecrm/backend/
  runtimecrm2/backend/
  runtimecrm3/backend/
  testcrm/backend/
```

Excluded from inspection:

```text
__pycache__/
*.pyc
.venv/
node_modules/
frontend build artifacts
production IdeasForgeAI folders
```

## 3. Backend File Inventory

Core backend files:

| File | Primary purpose | Status |
| --- | --- | --- |
| `backend/.env.example` | Example backend environment variables | Keep |
| `backend/main.py` | FastAPI app, route registration, local orchestration endpoints | Keep, harden |
| `backend/requirements.txt` | Python dependencies | Keep |
| `backend/supabase_schema.sql` | Planned Supabase schema reference | Defer until persistence sprint |
| `backend/__init__.py` | Package marker | Keep |
| `backend/api/health.py` | Health route router | Keep |
| `backend/api/__init__.py` | API package marker | Keep |
| `backend/core/ai_provider.py` | OpenAI provider wrapper with not-configured fallback | Keep, add router interface |
| `backend/core/base_agent.py` | Base agent abstraction and result helpers | Keep |
| `backend/core/models.py` | Shared Pydantic models | Keep, expand |
| `backend/core/pipeline.py` | Sequential in-process agent runner | Keep, upgrade later |
| `backend/core/project_paths.py` | Generated app path helpers | Keep |
| `backend/core/visual_design_provider.py` | Placeholder visual design provider architecture | Keep |
| `backend/core/__init__.py` | Core package marker | Keep |

Agent files:

| File | Primary purpose | Status |
| --- | --- | --- |
| `backend/agents/idea_intake_agent.py` | Normalizes raw idea input | Keep |
| `backend/agents/template_selection_agent.py` | Chooses template direction | Keep |
| `backend/agents/ui_blueprint_agent.py` | Builds UI blueprint | Keep |
| `backend/agents/template_ui_renderer_agent.py` | Renders generated UI templates | Keep |
| `backend/agents/html_builder_agent.py` | Builds static HTML output | Keep |
| `backend/agents/backend_api_agent.py` | Backend API concept output | Keep |
| `backend/agents/backend_code_generator_agent.py` | Generates backend code for apps | Keep, add tests |
| `backend/agents/frontend_api_connector_agent.py` | Frontend/backend wiring for generated apps | Keep, add tests |
| `backend/agents/runtime_config_agent.py` | Runtime config output | Keep |
| `backend/agents/database_persistence_agent.py` | Local persistence generation | Keep |
| `backend/agents/lead_crud_agent.py` | Lead CRUD support | Keep |
| `backend/agents/mobile_packager_agent.py` | Mobile packaging placeholder | Defer |
| `backend/agents/pixel_matched_page_converter_agent.py` | Pixel-matched converter placeholder | Keep for Phase 4/next |
| `backend/agents/visual_design_engine_agent.py` | Visual design placeholder output | Keep |
| `backend/agents/generated_app_export_agent.py` | Exports generated app workspace | Keep |
| `backend/agents/orchestrator_agent.py` | Creates default builder pipeline | Keep, centralize phase flags |
| `backend/agents/deployment_readiness_agent.py` | Dry-run deployment readiness | Keep |
| `backend/agents/git_versioning_agent.py` | Git readiness dry-run | Keep |
| `backend/agents/IdeasForgeAI_landing_template_agent.py` | Product-specific generated template support | Keep isolated |
| `backend/agents/ideasforgeai_product_template_template.py` | IdeasForgeAIProduct generated app template | Keep isolated |
| `backend/agents/IdeasForgeAI_production_sync_agent.py` | Dry-run production sync agent | Keep disabled/dry-run only |
| `backend/agents/__init__.py` | Agents package marker | Keep |

Product Brain files:

| File | Primary purpose | Status |
| --- | --- | --- |
| `backend/product_brain/intent_engine.py` | Detects domain and product intent | Keep |
| `backend/product_brain/conversation_engine.py` | Builds natural local conversation output | Keep |
| `backend/product_brain/product_strategy_engine.py` | Produces strategy sections | Keep |
| `backend/product_brain/requirements_engine.py` | Produces requirements sections | Keep |
| `backend/product_brain/blueprint_engine.py` | Produces product blueprint sections | Keep |
| `backend/product_brain/planning_engine.py` | Produces complexity/timeline/credits/readiness | Keep |
| `backend/product_brain/workflow_engine.py` | Orchestrates Product Brain local workflow | Keep, add schema tests |
| `backend/product_brain/project_memory_engine.py` | Session-only project memory | Keep, add boundary tests |
| `backend/product_brain/dynamic_question_engine.py` | One-question-at-a-time question logic | Keep |
| `backend/product_brain/ai_team_engine.py` | Specialist voice output | Keep |
| `backend/product_brain/__init__.py` | Product Brain package marker | Keep |

Generated app backend files inspected:

| Generated app | Backend files inspected | Notes |
| --- | ---: | --- |
| `ideasforgeai` | 0 | Backend folder exists, no source observed |
| `IdeasForgeAIProduct` | 11 | FastAPI backend plus JSON data files |
| `leadflowai` | 2 | FastAPI backend and requirements |
| `persistcrm1` | 4 | FastAPI backend, requirements, run script, JSON data |
| `runtimecrm` | 2 | FastAPI backend and requirements |
| `runtimecrm2` | 3 | FastAPI backend, requirements, run script |
| `runtimecrm3` | 3 | FastAPI backend, requirements, run script |
| `testcrm` | 2 | FastAPI backend and requirements |

## 4. API / Route Inventory

Core IdeasForgeAI routes:

| Method | Path | Purpose | Status | Auth |
| --- | --- | --- | --- | --- |
| GET | `/health` | Health check | Working | None |
| POST | `/api/generate` | Runs default builder pipeline | Working local | None |
| POST | `/api/pixel-convert` | Pixel converter placeholder | Placeholder | None |
| POST | `/api/visual-design` | Visual design placeholder | Placeholder | None |
| POST | `/api/product-brain/start` | Starts Phase 5 Product Brain | Working local | None |
| POST | `/api/product-brain/answer` | Stores one answer and advances memory | Partial | None |
| POST | `/api/kisan-premium-home` | Product-specific generated output support | Partial | None |
| POST | `/api/production-sync-dry-run` | Production sync dry-run only | Dry-run | None |
| POST | `/api/git-readiness` | Git readiness dry-run | Dry-run | None |
| POST | `/api/deployment-readiness` | Deployment readiness dry-run | Dry-run | None |
| POST | `/api/ai/assistant` | Provider-backed assistant with fallback | Partial | None |
| GET | `/api/projects` | Lists generated apps | Working local | None |

Core route count includes `/health`, for 13 total route handlers.

Generated app route groups:

| Generated app | Route count | Route families |
| --- | ---: | --- |
| `IdeasForgeAIProduct` | 28 | Health, stats, weather, account summary, CRUD for farmers, FPOs, buyers, farms, crops, mandi deals |
| `leadflowai` | 6 | Health, leads, pipeline, followups, stats |
| `persistcrm1` | 8 | Health, lead CRUD, pipeline, followups, stats |
| `runtimecrm` | 6 | Health, leads, pipeline, followups, stats |
| `runtimecrm2` | 6 | Health, leads, pipeline, followups, stats |
| `runtimecrm3` | 6 | Health, leads, pipeline, followups, stats |
| `testcrm` | 6 | Health, leads, pipeline, followups, stats |

Total route count found: 79.

## 5. Product Brain Module Inventory

The Product Brain is present as a clean local architecture layer. It currently behaves as deterministic placeholder intelligence, not a live LLM system.

| Module | Capability found | Current gap |
| --- | --- | --- |
| Intent Engine | Detects common product domains and product type | Needs scoring confidence and typed intent schema |
| Conversation Engine | Creates natural product-team style responses | Needs conversation state contract |
| Product Strategy Engine | Generates problem, users, goals, metrics, monetization, MVP, future features | Needs source attribution and user-decision trace |
| Requirements Engine | Generates functional, non-functional, roles, permissions, modules, dependencies | Needs validation against generated blueprint |
| Blueprint Engine | Generates pages, navigation, tables, APIs, workflows, agents | Needs richer entity modeling |
| Planning Engine | Estimates complexity, timeline, steps, credits, readiness | Needs cost model and phase gates |
| Workflow Engine | Orchestrates start/answer flow and section output | Needs durable job/session state |
| Project Memory Engine | Stores session-only facts and answers | Needs explicit expiry and privacy boundary |
| Dynamic Question Engine | Keeps one-question-at-a-time flow | Needs branching question tests |
| AI Team Engine | Produces specialist team viewpoints | Needs role registry and tone tests |

## 6. Agent System Inventory

Existing implemented or placeholder agents:

| Agent | Current role | Maturity |
| --- | --- | --- |
| Idea Intake | Understand initial idea | Partial |
| Template Selection | Select starting template | Partial |
| UI Blueprint | Draft UI structure | Partial |
| Template UI Renderer | Render template UI | Partial |
| HTML Builder | Build HTML output | Partial |
| Backend API | Draft backend API | Partial |
| Backend Code Generator | Generate backend source | Partial |
| Frontend API Connector | Wire generated frontend to backend | Partial |
| Runtime Config | Generate runtime config | Partial |
| Database Persistence | Add local persistence | Partial |
| Lead CRUD | Add lead CRUD concepts | Partial |
| Mobile Packager | Mobile packaging placeholder | Placeholder |
| Pixel Matched Converter | Phase 4 converter placeholder | Placeholder |
| Visual Design Engine | Phase 3 visual placeholder | Placeholder |
| Generated App Export | Export generated app folder | Partial |
| Deployment Readiness | Dry-run readiness | Partial |
| Git Versioning | Dry-run git readiness | Partial |
| Product-specific IdeasForgeAI agents | Generated product support | Isolated, keep guarded |

Expected product-team roles not yet represented as first-class backend agents:

| Desired role | Current backend status |
| --- | --- |
| CEO / Product Lead | Missing |
| Business Analyst | Partially covered by Product Brain strategy |
| Product Manager | Partially covered by Product Brain workflow |
| UX Designer | Partially covered by blueprint/design placeholders |
| UI Designer | Partially covered by Visual Design Engine placeholder |
| Frontend Engineer | Partially covered by template renderer/connectors |
| Backend Engineer | Partially covered by backend generator |
| Database Architect | Partially covered by persistence agent |
| AI Engineer | Missing as first-class provider/model planner |
| DevOps Engineer | Partially covered by readiness agents |
| QA Engineer | Missing |
| Security Engineer | Missing |
| Marketing Agent | Missing |
| SEO Agent | Missing |
| Documentation Agent | Missing |
| Research Agent | Missing |
| Competitor Analysis Agent | Missing |
| Business Strategy Agent | Partially covered |
| Investor Deck Agent | Missing |

## 7. Pipeline Inventory

`backend/core/pipeline.py` defines a simple sequential `BuilderPipeline`.

Current behavior:

| Capability | Status |
| --- | --- |
| Sequential agent execution | Present |
| Shared mutable context | Present |
| Result stored by agent name | Present |
| Stop on first failure | Present |
| Retry policy | Missing |
| Async job state | Missing |
| Progress events | Missing |
| Approval gates | Missing |
| Rollback | Missing |
| Pipeline persistence | Missing |
| Structured phase contract | Partial |
| Observability | Minimal |

Default builder pipeline order:

```text
IdeaIntakeAgent
TemplateSelectionAgent
UIBlueprintAgent
TemplateUIRendererAgent
HTMLBuilderAgent
BackendAPIAgent
BackendCodeGeneratorAgent
FrontendAPIConnectorAgent
RuntimeConfigAgent
DatabasePersistenceAgent
LeadCRUDAgent
MobilePackagerAgent
PixelMatchedPageConverterAgent
GeneratedAppExportAgent
```

This is enough for local proof-of-concept generation, but it needs a job runner, event timeline, durable logs, typed artifacts, and approval checkpoints before production use.

## 8. AI Provider / Model Router Inventory

Provider architecture found:

| File | Capability |
| --- | --- |
| `backend/core/ai_provider.py` | Direct OpenAI provider wrapper with environment-based key loading and local not-configured fallback |
| `backend/core/visual_design_provider.py` | Placeholder provider abstraction for visual design outputs |

Current provider strengths:

| Strength | Notes |
| --- | --- |
| No frontend secrets | API key loading is backend-side only |
| Missing-key fallback | Assistant can return a not-configured state instead of crashing |
| Local placeholder path | Product Brain and visual design can operate locally |

Current provider gaps:

| Gap | Risk |
| --- | --- |
| No provider registry | Future OpenAI, Anthropic, Google, Azure, and local models are not centrally routed |
| No model selection policy | Cost, latency, reliability, and task suitability are not modeled |
| No retry/failover | Temporary technical failures can surface as failures |
| No streaming/events | UI cannot receive true step-by-step model progress |
| No token/cost tracking | Credits and billing readiness remain estimated only |
| No redaction layer | Prompts and outputs need sanitization before logs |

## 9. Memory / Context Inventory

Memory systems found:

| Area | Current behavior |
| --- | --- |
| Product Brain memory | Session-only local memory for project name, brand, industry, type, previous answers, and decisions |
| Pipeline context | In-memory context dictionary passed across agents |
| Generated app data | Some generated apps use JSON files for local persistence |
| Supabase plan | Schema exists as a future reference, not live backend persistence |

Memory gaps:

| Gap | Impact |
| --- | --- |
| No durable IdeasForgeAI project database | Projects cannot be reliably resumed outside local files |
| No user/session ownership model | Any local caller can access generation endpoints |
| No artifact version history | Generated outputs cannot be compared or rolled back safely |
| No context compaction policy | Future long conversations may lose important decisions |
| No privacy lifecycle | Session-only behavior should be explicitly enforced and tested |

## 10. Generation Engine Inventory

Generation components:

| Component | Purpose | Maturity |
| --- | --- | --- |
| Template selection | Picks starting product template direction | Partial |
| UI blueprint | Produces UI structure | Partial |
| Template renderer | Renders UI templates | Partial |
| HTML builder | Creates HTML output | Partial |
| Backend API agent | Defines backend API concepts | Partial |
| Backend code generator | Produces generated backend source | Partial |
| Frontend API connector | Wires generated frontend to backend | Partial |
| Runtime config | Creates runtime config artifacts | Partial |
| Database persistence | Adds JSON/local persistence to generated apps | Partial |
| Export agent | Writes generated app workspace | Partial |

Generated app backend pattern:

```text
generated-apps/{project}/backend/main.py
generated-apps/{project}/backend/requirements.txt
generated-apps/{project}/backend/run.ps1
generated-apps/{project}/backend/data/*.json
```

Current generation engine is practical for local demos. It is not yet governed by typed build artifacts, schema migrations, automated tests, security checks, dependency scanning, or deploy approvals.

## 11. Integration Inventory

| Integration | Current status | Notes |
| --- | --- | --- |
| FastAPI | Active | Main backend framework |
| Pydantic | Active | Request/response validation, needs more artifact schemas |
| OpenAI | Optional backend provider | Uses environment variable only; no frontend key exposure found in audited backend files |
| Supabase | Planned | Schema file and docs exist, no live writes in IdeasForgeAI backend |
| Git | Dry-run readiness | No commit/push action required for audit |
| Deployment | Dry-run readiness | No deploy action in audit |
| Generated apps | Active local outputs | Backends exist under `generated-apps/` |
| IdeasForgeAIProduct | Active generated app | Isolated local generated app backend |

Missing or deferred:

| Integration | Recommendation |
| --- | --- |
| Authentication provider | Add after Product Brain contracts are stable |
| Queue/job runner | Add before long-running generation |
| Object storage | Add when generated assets become durable |
| Observability/logging | Add before beta usage |
| Security scanning | Add before any publish workflow |

## 12. Security Inventory

Current security posture:

| Area | Status | Risk |
| --- | --- | --- |
| Backend secret placement | Partial | `.env.example` exists; provider reads backend env |
| Frontend secret exposure | No backend evidence found | Continue scanning before release |
| Auth | Missing | High |
| Authorization | Missing | High |
| Route ownership | Missing | High |
| Rate limiting | Missing | Medium/high |
| CORS restrictions | Weak/local | Medium/high |
| Input validation | Partial | Pydantic request models exist, deeper validation needed |
| Output sanitization | Missing | Medium |
| File write boundaries | Partial | Generated app writes need strict project sandboxing |
| Production action guardrails | Partial | Dry-run agents exist, but enforcement should be centralized |
| Audit logging | Missing | Medium |

Immediate security recommendations:

| Priority | Recommendation |
| --- | --- |
| P0 | Add route-level auth before public exposure |
| P0 | Add project ownership/session isolation |
| P0 | Ensure generation writes cannot escape generated workspace |
| P1 | Add centralized deployment/publish approval gates |
| P1 | Add request size limits and rate limits |
| P1 | Add redaction for logs and provider prompts |

## 13. Testing Inventory

Testing state observed from backend inventory:

| Test area | Status |
| --- | --- |
| Unit tests for Product Brain | Not evident |
| Unit tests for route contracts | Not evident |
| Unit tests for pipeline failure behavior | Not evident |
| Generated backend smoke tests | Not evident as formal tests |
| Security tests | Missing |
| Provider fallback tests | Missing |
| File sandbox/path traversal tests | Missing |
| Integration tests | Missing |
| Contract tests for Studio V3 panels | Missing |

Minimum next tests:

| Priority | Test |
| --- | --- |
| P0 | `/api/product-brain/start` returns populated strategy, requirements, blueprint, planning |
| P0 | Missing AI provider never returns visible provider-code failure to Studio V3 |
| P0 | Product Brain asks one question at a time |
| P1 | Pipeline stops on failing agent and reports failure cleanly |
| P1 | Generated app export cannot write outside project folder |
| P1 | Generated app backend health endpoints respond |

## 14. Deployment / Ops Inventory

Ops artifacts and behavior:

| Area | Status |
| --- | --- |
| Core health endpoint | Present |
| Generated app health endpoints | Present in generated backends |
| Deployment readiness endpoint | Dry-run only |
| Git readiness endpoint | Dry-run only |
| Production sync endpoint | Dry-run only |
| Render/Docker/IaC | Not established as live backend path |
| CI/CD | Not evident |
| Logs/metrics/tracing | Minimal/local |
| Background jobs | Missing |
| Rollbacks | Missing |
| Environment validation | Partial |

Ops recommendation: keep all publish/deploy flows dry-run until authentication, ownership, quality gates, tests, and artifact versioning are in place.

## 15. Technical Debt List

| Priority | Debt | Impact |
| --- | --- | --- |
| P0 | Unauthenticated generation and readiness routes | Blocks public use |
| P0 | No durable project/session ownership | Blocks safe multi-user use |
| P0 | No test suite around Product Brain and routes | Makes regressions likely |
| P0 | Generated app writes need stronger path boundaries | File safety risk |
| P1 | Pipeline is synchronous and in-memory | Weak long-running reliability |
| P1 | No typed artifact registry | Hard to evolve phases safely |
| P1 | AI provider logic is not a router | Limits future providers |
| P1 | Product-specific IdeasForgeAI agents remain in generic backend | Needs isolation policy |
| P1 | No centralized approval gate | Publish/generation boundaries can drift |
| P2 | Generated app backends repeat route patterns | Duplication |
| P2 | JSON persistence is useful locally but not scalable | Migration required later |
| P2 | Limited observability | Hard to debug user builds |

## 16. Remove / Keep / Defer List

Keep:

| Item | Reason |
| --- | --- |
| Product Brain modules | Core Phase 5 intelligence layer |
| Default builder pipeline | Useful orchestration baseline |
| Visual Design Engine placeholder | Required for Phase 3 continuity |
| Pixel converter placeholder | Required for Phase 4 continuity |
| Generated app folder model | Useful local artifact boundary |
| Dry-run readiness agents | Good safety posture |
| IdeasForgeAIProduct generated app backend | Existing working generated app |

Defer:

| Item | Reason |
| --- | --- |
| Live AI provider expansion | Architecture should settle first |
| Supabase live writes | Needs auth/project model first |
| Deployment automation | Needs security and quality gates first |
| Background jobs | Add after route contracts are stable |
| Full generated app test harness | Build after artifact schemas stabilize |

Remove or isolate:

| Item | Recommendation |
| --- | --- |
| Product-specific IdeasForgeAI production sync logic inside generic builder surface | Keep dry-run, isolate behind explicit internal/admin flag |
| Repeated generated backend scaffolds | Keep outputs, but move common generator patterns into reusable templates later |
| Any production-domain labels in generic IdeasForgeAI UI/backend docs | Remove or replace with generic readiness wording |

## 17. Recommended Backend Architecture

Recommended next architecture shape:

```text
backend/
  main.py
  api/
    health.py
    product_brain.py
    generation.py
    readiness.py
    projects.py
  core/
    models.py
    pipeline.py
    artifact_registry.py
    provider_router.py
    security.py
    project_paths.py
  product_brain/
    intent_engine.py
    conversation_engine.py
    dynamic_question_engine.py
    product_strategy_engine.py
    requirements_engine.py
    blueprint_engine.py
    planning_engine.py
    ai_team_engine.py
    project_memory_engine.py
    workflow_engine.py
  agents/
    generation/
    design/
    backend/
    frontend/
    readiness/
  tests/
    test_product_brain.py
    test_routes.py
    test_project_paths.py
    test_pipeline.py
```

Architecture principles:

| Principle | Meaning |
| --- | --- |
| Less UI, more intelligence | Studio V3 remains visually frozen while backend intelligence improves |
| Local first, provider ready | Placeholder logic remains useful without AI keys |
| No silent production action | Deploy, publish, git, and sync remain dry-run until explicit approval and security |
| Typed artifacts | Strategy, requirements, blueprint, planning, design, and generation should be versioned objects |
| One phase boundary at a time | Product Brain should complete before frontend/backend generation begins |

## 18. Final File-Level Scorecard

Scores are qualitative backend audit scores from 0 to 100.

| Category | Score | Reason |
| --- | ---: | --- |
| Architecture clarity | 58 | Clear local modules exist, but route boundaries and artifact contracts need separation |
| Product Brain readiness | 66 | Good local Phase 5 modules, needs schemas, tests, and persistence policy |
| Agent system maturity | 54 | Many agents exist, several are placeholders or template-specific |
| API reliability | 42 | Routes exist, but no auth, rate limits, durable jobs, or tests |
| Security posture | 24 | Backend should not be public in current state |
| Generation engine | 50 | Local generation works, production quality gates are missing |
| AI provider extensibility | 45 | Provider wrapper exists, router/failover/cost tracking missing |
| Memory/context | 38 | Session memory exists, durable project memory missing |
| Testing | 18 | Formal backend tests not evident |
| Deployment readiness | 26 | Dry-run readiness exists, live ops path not ready |
| Maintainability | 52 | Files are understandable, but product-specific code needs clearer isolation |

Overall backend score: 43/100.

## 19. Recommended Next Sprint

Recommended next sprint: Backend Intelligence Stabilization Sprint.

Sprint goals:

| Priority | Work item |
| --- | --- |
| P0 | Add typed Product Brain response schemas for understanding, intent, missing information, assumptions, strategy, requirements, blueprint, planning, AI team view, approval, and next step |
| P0 | Add tests proving local Product Brain never fails when external AI is missing |
| P0 | Split Product Brain routes into `backend/api/product_brain.py` without changing Studio V3 visuals |
| P0 | Add route contract tests for populated Strategy, Requirements, Blueprint, and Planning panels |
| P1 | Add artifact registry for generated strategy/requirements/blueprint/planning outputs |
| P1 | Add project/session ownership placeholder middleware before public use |
| P1 | Add safe path tests for generated app exports |
| P1 | Create provider router interface while keeping local mode as default |

Do not start Phase 6 until Phase 5 contracts, tests, and route boundaries are stable.

## 20. Acceptance Criteria

This appendix is complete if:

| Criterion | Status |
| --- | --- |
| One report file was created under `docs/backend-audit/` | Met |
| Backend folders were inventoried | Met |
| Backend files were inventoried | Met |
| Core and generated app routes were counted | Met |
| Product Brain modules were listed | Met |
| Agent system was assessed | Met |
| Pipeline, provider, memory, generation, integration, security, testing, and ops areas were reviewed | Met |
| Technical debt and keep/defer/remove lists were included | Met |
| Recommended backend architecture was provided | Met |
| Final scorecard was included | Met |
| Recommended next sprint was included | Met |
| No feature implementation was performed | Met |
| No deployment was performed | Met |
| No production IdeasForgeAI files were touched | Met |
| No secrets were exposed | Met |

Earlier backend audit update recommendation: yes. Any previous high-level backend audit should be updated to reference this appendix because it provides file-level counts, route totals, Product Brain module inventory, generated backend route inventory, and a more specific next sprint.

