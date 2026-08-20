# FOS-BE-1 — Platform Contracts & Composition Boundary

## Objective
Establish the canonical Founder OS backend contract layer used by all IdeasForgeAI products and specialist agents.

## Certified baseline
- Overall Founder OS progress: 60%
- Progress must remain 60% until all FOS-BE-1 verification gates pass.
- Target after PASS: 63%.

## Core domain chain
Product -> Project -> Objective -> Plan -> Task -> Agent -> Action -> Result -> Verification -> Memory

## Canonical contracts

### ProductRef
- id: string
- slug: string
- name: string
- kind: product | platform | internal
- status: active | paused | archived

### ProjectRef
- id: string
- productId: string
- slug: string
- name: string
- repositoryRefs: RepositoryRef[]
- environmentRefs: EnvironmentRef[]
- status: active | blocked | completed | archived

### Objective
- id: string
- projectId: string
- requestedBy: ActorRef
- intent: string
- constraints: Constraint[]
- riskLevel: low | medium | high | critical
- approvalPolicy: ApprovalPolicy
- status: proposed | approved | planning | executing | verifying | completed | failed | cancelled

### Plan
- id: string
- objectiveId: string
- version: number
- tasks: Task[]
- generatedBy: AgentRef
- requiresApproval: boolean
- status: draft | proposed | approved | executing | completed | failed | superseded

### Task
- id: string
- planId: string
- type: inspect | reason | read | write | test | build | deploy | rollback | notify | remember
- title: string
- description: string
- dependsOn: string[]
- assignedAgent?: AgentRef
- requiredCapabilities: string[]
- executionPolicy: ExecutionPolicy
- status: pending | ready | running | blocked | succeeded | failed | cancelled | skipped

### AgentRef
- id: string
- name: string
- role: founder_brain | orchestrator | specialist | validator | memory | system
- capabilities: string[]
- trustTier: read_only | controlled_write | privileged

### Action
- id: string
- taskId: string
- agentId: string
- capability: string
- operation: string
- target: ResourceRef
- inputSummary: string
- riskLevel: low | medium | high | critical
- requiresConfirmation: boolean
- confirmationId?: string
- idempotencyKey: string
- status: proposed | authorized | running | succeeded | failed | rejected | cancelled

### Result
- id: string
- actionId: string
- success: boolean
- summary: string
- artifacts: ArtifactRef[]
- diagnostics: Diagnostic[]
- startedAt: string
- completedAt: string

### Verification
- id: string
- objectiveId: string
- taskId?: string
- checks: VerificationCheck[]
- verdict: pass | fail | partial | inconclusive
- verifiedBy: AgentRef
- evidence: EvidenceRef[]

### MemoryRecord
- id: string
- scope: founder | company | product | project | objective | agent
- scopeId: string
- type: decision | fact | preference | outcome | failure | lesson | deployment | relationship
- content: string
- sourceRefs: ResourceRef[]
- confidence: number
- createdAt: string
- supersedes?: string

## Composition boundary
Founder Brain may interpret intent and create plans, but may not directly perform privileged writes.

Orchestrator may select agents, sequence tasks, enforce dependencies, and route approvals, but may not bypass policy.

Specialist agents may operate only within declared capability and trust tier.

Validators must be logically independent from the action that produced the change wherever practical.

Memory writes occur only after a meaningful result, decision, or verified state transition.

## Approval policy
- Read-only inspection: no explicit confirmation required unless sensitive data policy requires it.
- Reversible low-risk writes: governed by product policy.
- External communication, deployment, billing, permission changes, destructive writes, user/account changes: explicit authorization required unless a pre-authorized policy exists.
- Critical actions: explicit confirmation plus verification requirement.

## Idempotency and replay safety
Every write Action must carry an idempotencyKey.
Repeated worker delivery must not duplicate side effects.
Completed actions are immutable; retries create attempt records linked to the original action.

## Audit event contract
Every state transition emits an immutable event:
- eventId
- eventType
- actor
- entityType
- entityId
- previousState
- newState
- timestamp
- correlationId
- causationId
- metadata

## Error contract
Errors use stable categories:
- VALIDATION_ERROR
- PERMISSION_DENIED
- APPROVAL_REQUIRED
- CAPABILITY_UNAVAILABLE
- DEPENDENCY_FAILED
- EXECUTION_FAILED
- VERIFICATION_FAILED
- TIMEOUT
- CANCELLED
- CONFLICT
- EXTERNAL_SERVICE_ERROR
- INTERNAL_ERROR

Each error includes code, message, retryable, correlationId, and safe diagnostics.

## Required boundaries
1. No product-specific business logic in core contracts.
2. ForgeCall, ForgeHR, ForgeStudio integrate through adapters.
3. No direct UI -> specialist-agent privileged write path.
4. All privileged execution flows through policy + action authorization.
5. Every successful objective has verification evidence before completion.
6. Every execution has correlation IDs and audit events.
7. Contracts are versioned and backward-compatible within a major version.

## Verification gates

### Gate A — Contract integrity
- Schema/type validation passes.
- Required identifiers and state enums are enforced.
- Invalid state transitions are rejected.

### Gate B — Composition boundary
- Founder Brain cannot invoke privileged writes directly.
- Specialist agents cannot exceed capabilities.
- Orchestrator cannot bypass approval policy.

### Gate C — Replay safety
- Duplicate action delivery does not duplicate side effects.
- Retry attempts are traceable.

### Gate D — Auditability
- Every state transition generates an audit event.
- Objective -> Plan -> Task -> Action -> Result -> Verification can be traced by correlationId.

### Gate E — Compatibility
- Existing Founder UI/read APIs continue to work.
- No visible milestone/progress change before PASS.

### Gate F — Build and tests
- Existing test suite passes.
- New FOS-BE-1 contract tests pass.
- Production build passes.

## Certification rule
Only after Gates A-F PASS:
- overallProgress: 60 -> 63
- milestone: FOS-BE-1 — Platform Contracts & Composition Boundary
- produce FOS-BE-1-RESULT.txt with evidence

## Next phase after certification
FOS-BE-2 — Worker Lifecycle & Durable Job Execution.
