from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Mapping, Protocol, Sequence

from .common import ActorContext

OPERATING_MODEL_CONTRACT_VERSION = "platform.operating-model.v1"

ObjectiveStatus = Literal[
    "proposed", "approved", "planning", "executing", "verifying",
    "completed", "failed", "cancelled",
]
ActionStatus = Literal[
    "proposed", "authorized", "running", "succeeded", "failed",
    "rejected", "cancelled",
]
TrustTier = Literal["read_only", "controlled_write", "privileged"]
AgentRole = Literal[
    "founder_brain", "orchestrator", "specialist", "validator",
    "memory", "system",
]


@dataclass(frozen=True)
class ProductRecord:
    product_id: str
    name: str
    status: str = "active"
    contract_version: str = OPERATING_MODEL_CONTRACT_VERSION
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ProjectRecord:
    project_id: str
    product_id: str
    name: str
    workspace_id: str
    status: str = "active"
    contract_version: str = OPERATING_MODEL_CONTRACT_VERSION
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ObjectiveRecord:
    objective_id: str
    project_id: str
    title: str
    desired_outcome: str
    status: ObjectiveStatus = "proposed"
    risk_level: str = "low"
    correlation_id: str = ""
    contract_version: str = OPERATING_MODEL_CONTRACT_VERSION
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AgentAssignment:
    agent_id: str
    task_id: str
    capability: str
    trust_tier: TrustTier
    role: AgentRole = "specialist"
    status: str = "assigned"
    contract_version: str = OPERATING_MODEL_CONTRACT_VERSION
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ActionRecord:
    action_id: str
    task_id: str
    agent_id: str
    operation: str
    idempotency_key: str
    capability: str = ""
    target: str = ""
    input_summary: str = ""
    risk: str = "low"
    requires_approval: bool = False
    correlation_id: str = ""
    status: ActionStatus = "proposed"
    contract_version: str = OPERATING_MODEL_CONTRACT_VERSION
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ResultRecord:
    result_id: str
    action_id: str
    ok: bool
    status: str
    summary: str = ""
    output_digest: str = ""
    correlation_id: str = ""
    contract_version: str = OPERATING_MODEL_CONTRACT_VERSION
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class VerificationRecord:
    verification_id: str
    result_id: str
    ok: bool
    status: str
    objective_id: str = ""
    task_id: str = ""
    correlation_id: str = ""
    checks: tuple[Mapping[str, Any], ...] = ()
    contract_version: str = OPERATING_MODEL_CONTRACT_VERSION
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ProductAdapterDescriptor:
    product_id: str
    adapter_id: str
    capabilities: tuple[str, ...]
    contract_version: str = OPERATING_MODEL_CONTRACT_VERSION
    metadata: Mapping[str, Any] = field(default_factory=dict)


class ProductAdapter(Protocol):
    descriptor: ProductAdapterDescriptor

    def can_handle(self, action: ActionRecord) -> bool:
        ...


class OperatingModelService(Protocol):
    """Canonical Founder OS hierarchy without owning execution behavior."""

    def get_product(self, product_id: str) -> ProductRecord | None:
        ...

    def get_project(self, project_id: str) -> ProjectRecord | None:
        ...

    def get_objective(self, objective_id: str) -> ObjectiveRecord | None:
        ...

    def list_projects(
        self,
        product_id: str,
        *,
        actor: ActorContext,
    ) -> Sequence[ProjectRecord]:
        ...

    def list_objectives(
        self,
        project_id: str,
        *,
        actor: ActorContext,
    ) -> Sequence[ObjectiveRecord]:
        ...
