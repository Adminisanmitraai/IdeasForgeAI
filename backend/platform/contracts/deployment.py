from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol, Sequence

from .common import ActorContext

DEPLOYMENT_CONTRACT_VERSION = "platform.deployment.v1"
UPDATE_CONTRACT_VERSION = "platform.update.v1"


@dataclass(frozen=True)
class DeploymentPlanRequest:
    task_id: str
    workspace_id: str
    project_context_id: str
    provider: str
    target: str
    revision: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DeploymentPlan:
    deployment_plan_id: str
    task_id: str
    provider: str
    target: str
    revision: str
    digest: str
    risk: str
    requires_approval: bool
    contract_version: str = DEPLOYMENT_CONTRACT_VERSION
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ApprovedDeploymentRequest:
    deployment_plan_id: str
    plan_digest: str
    approval_token: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ApprovedRollbackRequest:
    deployment_id: str
    rollback_target: str
    approval_token: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DeploymentRecord:
    deployment_id: str
    deployment_plan_id: str
    status: str
    provider: str
    target: str
    revision: str
    rollback_target: str = ""
    contract_version: str = DEPLOYMENT_CONTRACT_VERSION
    metadata: Mapping[str, Any] = field(default_factory=dict)


class DeploymentService(Protocol):
    def create_deployment_plan(
        self,
        request: DeploymentPlanRequest,
        *,
        actor: ActorContext,
    ) -> DeploymentPlan:
        ...

    def deploy(
        self,
        request: ApprovedDeploymentRequest,
        *,
        actor: ActorContext,
    ) -> DeploymentRecord:
        ...

    def rollback(
        self,
        request: ApprovedRollbackRequest,
        *,
        actor: ActorContext,
    ) -> DeploymentRecord:
        ...

    def get_status(self, deployment_id: str) -> DeploymentRecord | None:
        ...


@dataclass(frozen=True)
class UpdateInspectionRequest:
    workspace_id: str
    project_context_id: str
    ecosystems: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class UpdateAssessment:
    assessment_id: str
    updates: tuple[Mapping[str, Any], ...]
    risk: str
    contract_version: str = UPDATE_CONTRACT_VERSION
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class UpdatePlanRequest:
    assessment_id: str
    selected_updates: tuple[str, ...]
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class UpdatePlan:
    update_plan_id: str
    digest: str
    risk: str
    requires_approval: bool
    contract_version: str = UPDATE_CONTRACT_VERSION
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ApprovedUpdateRequest:
    update_plan_id: str
    plan_digest: str
    approval_token: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class UpdateResult:
    update_id: str
    status: str
    changed_components: tuple[str, ...] = ()
    contract_version: str = UPDATE_CONTRACT_VERSION
    metadata: Mapping[str, Any] = field(default_factory=dict)


class UpdateService(Protocol):
    def inspect_updates(
        self,
        request: UpdateInspectionRequest,
        *,
        actor: ActorContext,
    ) -> UpdateAssessment:
        ...

    def create_update_plan(
        self,
        request: UpdatePlanRequest,
        *,
        actor: ActorContext,
    ) -> UpdatePlan:
        ...

    def apply_update(
        self,
        request: ApprovedUpdateRequest,
        *,
        actor: ActorContext,
    ) -> UpdateResult:
        ...
