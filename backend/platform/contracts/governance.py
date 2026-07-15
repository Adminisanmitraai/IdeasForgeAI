from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol

from .common import ActorContext, OperationReceipt

GOVERNANCE_CONTRACT_VERSION = "platform.admin-governance.v1"


@dataclass(frozen=True)
class PermissionEvaluationRequest:
    actor: ActorContext
    capability: str
    resource_type: str
    resource_id: str = ""
    operation: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PermissionDecision:
    allowed: bool
    code: str
    message: str
    required_role: str = ""
    contract_version: str = GOVERNANCE_CONTRACT_VERSION
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class GovernancePolicyRequest:
    policy_name: str
    operation: str
    risk: str
    actor: ActorContext
    resource_id: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class GovernanceEvent:
    event_type: str
    actor_id: str
    decision: str
    occurred_at: int
    correlation_id: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class GovernanceStatusQuery:
    capability: str = ""
    policy_name: str = ""


@dataclass(frozen=True)
class GovernanceStatus:
    healthy: bool
    policy_version: str
    approval_available: bool
    audit_available: bool
    contract_version: str = GOVERNANCE_CONTRACT_VERSION
    metadata: Mapping[str, Any] = field(default_factory=dict)


class AdminGovernanceInterface(Protocol):
    def evaluate_permission(
        self,
        request: PermissionEvaluationRequest,
    ) -> PermissionDecision:
        ...

    def evaluate_governance_policy(
        self,
        request: GovernancePolicyRequest,
    ) -> PermissionDecision:
        ...

    def record_governance_event(
        self,
        event: GovernanceEvent,
    ) -> OperationReceipt:
        ...

    def get_governance_status(
        self,
        query: GovernanceStatusQuery,
    ) -> GovernanceStatus:
        ...
