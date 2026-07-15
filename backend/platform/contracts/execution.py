from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol, Sequence

from .common import ActorContext, OperationReceipt

PLANNING_CONTRACT_VERSION = "platform.plan.v1"
CHANGE_PREVIEW_CONTRACT_VERSION = "platform.change-preview.v1"
APPROVAL_CONTRACT_VERSION = "platform.approval.v1"
EXECUTION_POLICY_CONTRACT_VERSION = "platform.execution-policy.v1"
EXECUTION_CONTRACT_VERSION = "platform.execution.v1"
SESSION_CONTRACT_VERSION = "platform.session.v1"
VALIDATION_CONTRACT_VERSION = "platform.validation.v1"
AUDIT_CONTRACT_VERSION = "platform.audit.v1"
EVENT_CONTRACT_VERSION = "platform.event.v1"
MEMORY_CONTRACT_VERSION = "platform.memory.v1"


@dataclass(frozen=True)
class PlanRequest:
    task_id: str
    workspace_id: str
    project_context_id: str
    requested_operations: tuple[str, ...]
    approved_root: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PlanResult:
    plan_id: str
    task_id: str
    workspace_id: str
    digest: str
    risk: str
    requires_approval: bool
    steps: tuple[Mapping[str, Any], ...] = ()
    contract_version: str = PLANNING_CONTRACT_VERSION
    metadata: Mapping[str, Any] = field(default_factory=dict)


class PlanningService(Protocol):
    def create_plan(
        self,
        request: PlanRequest,
        *,
        actor: ActorContext,
    ) -> PlanResult:
        ...

    def get_plan(self, plan_id: str) -> PlanResult | None:
        ...

    def calculate_plan_digest(self, plan: PlanResult) -> str:
        ...


@dataclass(frozen=True)
class ChangePreviewRequest:
    task_id: str
    plan_id: str
    workspace_id: str
    proposed_changes: tuple[Mapping[str, Any], ...]
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ChangePreview:
    preview_id: str
    task_id: str
    plan_id: str
    digest: str
    affected_files: tuple[str, ...] = ()
    changes: tuple[Mapping[str, Any], ...] = ()
    contract_version: str = CHANGE_PREVIEW_CONTRACT_VERSION
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PreviewIntegrityResult:
    ok: bool
    preview_id: str
    calculated_digest: str
    expected_digest: str
    errors: tuple[str, ...] = ()


class ChangePreviewService(Protocol):
    def create_preview(
        self,
        request: ChangePreviewRequest,
        *,
        actor: ActorContext,
    ) -> ChangePreview:
        ...

    def get_preview(self, preview_id: str) -> ChangePreview | None:
        ...

    def validate_preview_integrity(
        self,
        preview: ChangePreview,
    ) -> PreviewIntegrityResult:
        ...


@dataclass(frozen=True)
class ApprovalRequest:
    subject: str
    role: str
    project_id: str
    plan_digest: str
    command_id: str
    session_id: str
    risk: str
    requested_at: int
    expires_at: int | None = None
    reason: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ApprovalVerificationContext:
    now: int
    subject: str
    role: str
    project_id: str
    plan_digest: str
    command_id: str
    session_id: str
    risk: str


@dataclass(frozen=True)
class ApprovalGrant:
    token: str
    approval_id: str
    expires_at: int
    claims_digest: str = ""
    contract_version: str = APPROVAL_CONTRACT_VERSION


@dataclass(frozen=True)
class ApprovalDecision:
    ok: bool
    state: str
    code: str
    message: str
    approval_id: str = ""
    consumed: bool = False
    contract_version: str = APPROVAL_CONTRACT_VERSION
    metadata: Mapping[str, Any] = field(default_factory=dict)


class ApprovalService(Protocol):
    def issue(
        self,
        request: ApprovalRequest,
        *,
        actor: ActorContext,
    ) -> ApprovalGrant:
        ...

    def verify(
        self,
        token: str,
        context: ApprovalVerificationContext,
        *,
        consume: bool = True,
    ) -> ApprovalDecision:
        ...

    def revoke(
        self,
        approval_id: str,
        *,
        actor: ActorContext,
        reason: str,
    ) -> ApprovalDecision:
        ...


@dataclass(frozen=True)
class ExecutionPolicyRequest:
    workspace_id: str
    plan_id: str
    risk: str
    requested_operation: str
    approval_present: bool
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ExecutionPolicyDecision:
    allowed: bool
    code: str
    message: str
    requires_approval: bool
    contract_version: str = EXECUTION_POLICY_CONTRACT_VERSION
    metadata: Mapping[str, Any] = field(default_factory=dict)


class ExecutionPolicyService(Protocol):
    def evaluate_plan(
        self,
        request: ExecutionPolicyRequest,
        *,
        actor: ActorContext,
    ) -> ExecutionPolicyDecision:
        ...

    def evaluate_step(
        self,
        request: ExecutionPolicyRequest,
        *,
        actor: ActorContext,
    ) -> ExecutionPolicyDecision:
        ...


@dataclass(frozen=True)
class ExecutionRequest:
    execution_id: str
    task_id: str
    plan_id: str
    plan_digest: str
    workspace_id: str
    approval_token: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ExecutionRecord:
    execution_id: str
    task_id: str
    status: str
    session_id: str = ""
    contract_version: str = EXECUTION_CONTRACT_VERSION
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ExecutionResult:
    execution_id: str
    status: str
    ok: bool
    exit_code: int | None = None
    output_digest: str = ""
    contract_version: str = EXECUTION_CONTRACT_VERSION
    metadata: Mapping[str, Any] = field(default_factory=dict)


class ExecutionService(Protocol):
    def submit(
        self,
        request: ExecutionRequest,
        *,
        actor: ActorContext,
    ) -> ExecutionRecord:
        ...

    def start(
        self,
        execution_id: str,
        *,
        actor: ActorContext,
    ) -> ExecutionRecord:
        ...

    def cancel(
        self,
        execution_id: str,
        *,
        actor: ActorContext,
    ) -> ExecutionRecord:
        ...

    def get_result(
        self,
        execution_id: str,
        *,
        actor: ActorContext,
    ) -> ExecutionResult | None:
        ...


@dataclass(frozen=True)
class SessionRequest:
    execution_id: str
    workspace_id: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SessionQuery:
    status: str = ""
    limit: int = 100


@dataclass(frozen=True)
class SessionRecord:
    session_id: str
    execution_id: str
    status: str
    cancellation_requested: bool = False
    contract_version: str = SESSION_CONTRACT_VERSION
    metadata: Mapping[str, Any] = field(default_factory=dict)


class SessionService(Protocol):
    def create_session(
        self,
        request: SessionRequest,
        *,
        actor: ActorContext,
    ) -> SessionRecord:
        ...

    def get_session(self, session_id: str) -> SessionRecord | None:
        ...

    def list_sessions(self, query: SessionQuery) -> Sequence[SessionRecord]:
        ...

    def request_cancellation(
        self,
        session_id: str,
        *,
        actor: ActorContext,
    ) -> SessionRecord:
        ...


@dataclass(frozen=True)
class ValidationRequest:
    task_id: str
    execution_id: str
    checks: tuple[str, ...]
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ValidationResult:
    validation_id: str
    execution_id: str
    ok: bool
    status: str
    checks: tuple[Mapping[str, Any], ...] = ()
    contract_version: str = VALIDATION_CONTRACT_VERSION
    metadata: Mapping[str, Any] = field(default_factory=dict)


class ValidationService(Protocol):
    def validate(
        self,
        request: ValidationRequest,
        *,
        actor: ActorContext,
    ) -> ValidationResult:
        ...

    def validate_execution_result(
        self,
        execution_id: str,
        *,
        actor: ActorContext,
    ) -> ValidationResult:
        ...


@dataclass(frozen=True)
class AuditEvent:
    event_id: str
    occurred_at: int
    category: str
    operation: str
    decision: str
    actor_id: str
    actor_role: str
    source_interface: str
    correlation_id: str = ""
    task_id: str = ""
    session_id: str = ""
    execution_id: str = ""
    workspace_id: str = ""
    project_id: str = ""
    approval_id: str = ""
    request_digest: str = ""
    result_digest: str = ""
    previous_event_digest: str = ""
    contract_version: str = AUDIT_CONTRACT_VERSION
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AuditQuery:
    category: str = ""
    task_id: str = ""
    execution_id: str = ""
    limit: int = 100


@dataclass(frozen=True)
class AuditScope:
    category: str = ""
    workspace_id: str = ""
    execution_id: str = ""


@dataclass(frozen=True)
class AuditIntegrityResult:
    ok: bool
    checked_events: int
    broken_event_id: str = ""
    message: str = ""


class AuditService(Protocol):
    def append(
        self,
        event: AuditEvent,
        *,
        actor: ActorContext,
    ) -> OperationReceipt:
        ...

    def query(self, query: AuditQuery) -> Sequence[AuditEvent]:
        ...

    def verify_chain(
        self,
        scope: AuditScope,
    ) -> AuditIntegrityResult:
        ...


@dataclass(frozen=True)
class PlatformEvent:
    stream_id: str
    sequence: int
    event_type: str
    occurred_at: int
    payload: Mapping[str, Any] = field(default_factory=dict)
    contract_version: str = EVENT_CONTRACT_VERSION


@dataclass(frozen=True)
class EventSubscriptionRequest:
    stream_id: str
    after_sequence: int = 0
    event_types: tuple[str, ...] = ()


@dataclass(frozen=True)
class EventSubscription:
    subscription_id: str
    stream_id: str
    after_sequence: int


class EventService(Protocol):
    def publish(self, event: PlatformEvent) -> OperationReceipt:
        ...

    def read(
        self,
        stream_id: str,
        *,
        after_sequence: int = 0,
        limit: int = 100,
    ) -> Sequence[PlatformEvent]:
        ...

    def subscribe(
        self,
        request: EventSubscriptionRequest,
    ) -> EventSubscription:
        ...


@dataclass(frozen=True)
class MemoryEntry:
    memory_id: str
    domain: str
    owner_id: str
    content: Mapping[str, Any]
    contract_version: str = MEMORY_CONTRACT_VERSION
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class MemoryQuery:
    domain: str
    owner_id: str = ""
    limit: int = 20


@dataclass(frozen=True)
class ForgetMemoryRequest:
    memory_id: str
    reason: str = ""


class MemoryService(Protocol):
    def store(
        self,
        entry: MemoryEntry,
        *,
        actor: ActorContext,
    ) -> OperationReceipt:
        ...

    def retrieve(
        self,
        query: MemoryQuery,
        *,
        actor: ActorContext,
    ) -> Sequence[MemoryEntry]:
        ...

    def forget(
        self,
        request: ForgetMemoryRequest,
        *,
        actor: ActorContext,
    ) -> OperationReceipt:
        ...
