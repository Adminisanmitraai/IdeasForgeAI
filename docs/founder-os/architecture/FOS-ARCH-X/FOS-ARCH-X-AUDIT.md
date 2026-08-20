# FOS-ARCH-X — Founder OS Expansion Architecture Audit

Status: ARCHITECTURE AUDIT ONLY — NO IMPLEMENTATION AUTHORIZED
Certified baseline: 75%
Certified milestone: FOS-BE-4 — ForgeCode Capability Facade
Current development branch observed: fos-be-5-platform-event-model
Progress/milestone change during audit: NONE

## 1. Current Founder OS Architecture

The current system is not a blank slate. It already contains a mature Founder Brain, execution-policy/safety stack, repository intelligence, agent/worker orchestration, ForgeCode terminal/runtime controls, project/task/provider contracts, Founder Terminal frontend, certification/progress governance, and emerging platform abstractions.

Primary architectural layers observed:
- Founder Terminal / chat interfaces.
- Founder Brain: mission, planning, task, timeline, milestone and progress intelligence.
- Project/repository intelligence and project knowledge graph.
- Execution policy, approval, sandbox, worker and audit controls.
- Platform layer: durable jobs, orchestration, supervision, ForgeCode facade, contracts and adapters.
- ForgeCode specialist modules for repository analysis, editing, validation, terminal planning/runtime/session/audit.
- Existing product/Forge modules and frontend generator/pixel mapping subsystems.

## 2. Existing Capabilities

EXISTING: Founder Progress + milestone/certification discipline; Founder Terminal; repository discovery/intelligence; code knowledge graph; execution boundary; approval engines; execution policy; immutable audit ledger; agent orchestration; worker coordination; durable jobs; execution supervision; ForgeCode capability facade; project/task/workspace contracts; provider gateway contract; chat streaming; Terminal event polling; frontend generator; Pixel Mapping components.

PARTIAL: persistent project brain, universal context graph, provider gateway implementation, agent capability registry, execution ledger lifecycle, artifact intelligence, cross-app orchestration, command-mode resolution, activity feed/event model.

MISSING: canonical universal business/project entity store; provider registry/router with cost/latency/reliability policy; secure credential-reference service; unified artifact/provenance model; cost intelligence; business/opportunity intelligence; decision objects; risk/blocker aggregation; daily founder briefing; MCP gateway; generic ForgeBuilder orchestration layer.

FUTURE: cinema-specific orchestration, Character DNA, World DNA, advanced rights/royalty systems, broad external provider fleet, autonomous commercial execution.
## 3. Current Milestone and Verified Progress

Certified progress remains 75% at FOS-BE-4. FOS-BE-5 Platform Event Model has begun but is not certified; its uncommitted event-model work must be treated as in-progress and cannot increase Founder Progress.

## 4. Reusable Components

High-value reusable components include platform.agent_orchestration, agent_job_coordination, durable_jobs/runtime, objective_execution_supervisor, forgecode_capability_facade, platform contracts for project/task/provider/workspace trust, Founder Brain project_knowledge_graph, execution_audit_ledger, execution policy/approval/sandbox stack, Coding Agent runtime/audit/session modules, existing chat/Terminal transports, frontend generator and Pixel Mapping subsystems.

## 5. Missing Capabilities

The most important missing architectural capability is a canonical Universal Project Brain entity model that can represent business and production context—not only repository/code structure. It needs stable IDs and relationships for companies, clients, opportunities, projects, objectives, requirements, tasks, decisions, blockers, artifacts, deployments, agents, costs and certifications.

The second major gap is a real multi-provider gateway implementation. A ProviderGateway protocol exists, but the active core provider remains OpenAI-specific and the registry/routing/cost/reliability logic requested by the expansion does not yet exist.

## 6. Architectural Conflicts

1. Two architectural generations coexist: extensive Founder Brain contracts and the newer backend/platform abstraction layer. They must be consolidated by adapters, not replaced.
2. The current Project Knowledge Graph is code/repository-centric; naming it the universal Context Graph without extending node semantics would be misleading.
3. Existing execution audit ledger is audit-only/in-memory and does not yet implement the full REQUESTED→PLANNED→APPROVAL→EXECUTING→VERIFYING→COMPLETED lifecycle.
4. Product-specific persistence/schema should not become the Founder OS universal database by accident.
5. Direct OpenAI-specific code paths must remain operational while a provider gateway is introduced incrementally.

## 7. Security Implications

Preserve the existing Founder OS policy boundary. Provider secrets must stay server-side and only opaque credential references may enter project/entity records. Existing approval, workspace trust, runtime plan revalidation, snapshot integrity, executable binding, sandbox and audit controls should become shared platform services rather than be bypassed by new agents or Forge applications.

External interfaces, including future MCP, must expose bounded capabilities only; unrestricted shell, raw database access, credential access, deployment primitives and infrastructure control remain internal.
## 8. Database / Schema Implications

The observed Supabase schema is not a Founder OS canonical schema; it is largely product/domain-specific JSON payload storage. Do not migrate all Founder OS state into it during this expansion audit.

Recommended future persistence boundary:
- projects / entities / relationships
- decisions / blockers / approvals
- artifacts / versions / provenance
- execution ledger / evidence
- provider usage / costs
- agent capability/reliability metrics

Introduce persistence only behind versioned repository interfaces and migrations. Keep current in-memory contracts working until parity tests pass.

## 9. Agent Implications

Do not create the full proposed ForgeBuilder agent list immediately. The current orchestration model already selects agents by capability and trust tier. Extend its descriptor over time with cost, reliability, workload, model/tool support and project permissions. Prefer deterministic workers for scanning, compilation, file transforms and validation; reserve reasoning agents for planning, architecture, design, research, diagnosis and review.

## 10. Infrastructure Implications

No new cloud platform is required for the first expansion phases. Current GitHub, Render/Cloudflare, Supabase and existing API infrastructure can remain. New infrastructure becomes justified only when durable universal entities, provider telemetry, artifact storage or cross-app event retention requires it.

## 11. Recommended Target Architecture

Founder interfaces (ChatGPT / Founder Terminal / Voice / apps)
→ Founder Command Resolver
→ Universal Project Brain + Context Graph
→ Founder Intelligence / Decision / Risk layer
→ Agent & Capability Orchestrator
→ Forge capability facades (ForgeCode, ForgeStudio, ForgeSocial, ForgeHR, ForgeCall, etc.)
→ Multi-AI Provider Gateway
→ Governed Execution Infrastructure
→ Event Model + Execution Ledger + Evidence
→ Persistent Entity / Artifact / Cost stores.

The current platform layer should become the stable integration spine. Existing Founder Brain modules remain intelligence providers behind adapters until gradually consolidated.
## 12. Recommended Phase Order

1. Complete/certify current FOS-BE-5 Platform Event Model if compatibility review passes. Estimated +4% (75→79).
2. FOS-BRAIN-1 Universal Entity Contracts + Context Graph Extension. Estimated +3%.
3. FOS-BRAIN-2 Persistent Project Brain Repository + migration-safe storage. Estimated +3%.
4. FOS-X-1 Founder Command Resolver using canonical project state. Estimated +2%.
5. FOS-EXEC-1 Unified Execution Ledger lifecycle + evidence linking. Estimated +2%.
6. FOS-AI-1 Provider Registry + capability routing core. Estimated +3%.
7. FOS-AI-2 Usage/cost/reliability telemetry + fallback policy. Estimated +2%.
8. FOS-BUILD-1 ForgeBuilder planning/orchestration facade reusing ForgeCode/frontend generator/Pixel Mapping. Estimated +3%.
9. FOS-BIZ-1 Opportunity + decision + blocker intelligence. Estimated +3%.
10. FOS-MCP-1 Read-only authenticated external capability gateway. Estimated +2%.

These estimates are roadmap contribution estimates only; they do not authorize Founder Progress increases.

## 13. Build Now vs Deferred

BUILD NOW: finish the platform event backbone; universal entity contracts; Context Graph extension; persistence repository interfaces; command resolver; execution-ledger unification; provider registry core.

DEFER: dozens of new specialist agents, cinema-specific systems, Character/World DNA, royalties, broad external provider integrations, autonomous financial/commercial actions, full MCP write capabilities.

## 14. Migration Plan

- Freeze certified FOS-BE-4 as rollback baseline.
- Review FOS-BE-5 against the expansion architecture; extend rather than discard if compatible.
- Add universal contracts beside existing Founder Brain/code graph models.
- Build adapters from legacy project/repository models into universal entities.
- Add repository interfaces before selecting physical persistence.
- Dual-read/compare legacy and new projections during migration.
- Route one capability at a time through provider/capability registries.
- Preserve existing public APIs until contract tests prove compatibility.
- Only retire legacy paths after parity, regression, build and production verification.

## 15. Roadmap Absorption

Do not reset FOS-BE numbering or Founder Progress. FOS-X, FOS-BRAIN, FOS-AI, FOS-BUILD, FOS-CREATIVE, FOS-EXEC, FOS-BIZ and FOS-MCP become expansion tracks layered after/around the existing certified roadmap. Existing FOS-BE phases remain historical and authoritative.
## 16. Verification Criteria by Proposed Phase

Every implementation phase must have: versioned contracts; backward-compatibility tests; focused unit/integration tests; security/policy boundary tests; full backend regression; frontend production build where affected; persistence migration/rollback test where applicable; live/runtime verification where applicable; certification record; only then a progress/milestone update.

Additional gates:
- Context Graph: deterministic entity IDs, relationship traversal, legacy adapter parity.
- Persistence: migration + rollback + tenant/project isolation + no secret leakage.
- Provider gateway: capability routing, policy routing, fallback, usage accounting, provider-failure tests.
- Execution ledger: legal state transitions, evidence links, approval enforcement, immutable history.
- ForgeBuilder: existing-project detection, plan/preview before write, tests + visual QA before deployment.
- MCP: authentication, capability allowlist, audit logging, no unrestricted infrastructure primitives.

## 17. Smallest High-Leverage Next Implementation Phase

Recommendation: DO NOT abandon FOS-BE-5. First perform a compatibility hardening pass on the existing Platform Event Model and then complete/certify FOS-BE-5.

Reason: the expansion requires cross-app orchestration, execution ledger, activity feeds, provider telemetry, cost intelligence, risk signals and daily founder intelligence. All of those benefit from one stable internal event envelope. FOS-BE-5 is already started and directly supports the new target without creating a parallel architecture.

After FOS-BE-5 certification, the first new expansion-track phase should be:

FOS-BRAIN-1 — Universal Entity Contracts + Context Graph Extension

Scope should be contracts and in-memory graph semantics only: generic Entity, Relationship, Project, Company, Client, Opportunity, Objective, Requirement, Task, Decision, Blocker, Artifact, Deployment, Agent and Certification references; adapters from the existing repository ProjectKnowledgeGraph; traversal/query tests. Do not add database persistence in the same phase.

Estimated contribution: +3% after full certification, not before.

## Audit Decision

COMPATIBLE WITH EXTENSION. The proposed Founder OS expansion should proceed by extending and connecting the existing architecture, not rebuilding it. FOS-BE-5 remains the correct immediate engineering phase, followed by FOS-BRAIN-1. Founder Progress remains 75% and the certified milestone remains FOS-BE-4 during this audit.