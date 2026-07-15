from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol, Sequence

from .common import ActorContext

WORKSPACE_TRUST_CONTRACT_VERSION = "platform.workspace-trust.v1"
PROJECT_CONTEXT_CONTRACT_VERSION = "platform.project-context.v1"
TASK_CONTRACT_VERSION = "platform.task.v1"


@dataclass(frozen=True)
class TrustedWorkspace:
    workspace_id: str
    canonical_root: str
    trusted: bool
    read_allowed: bool
    execution_allowed: bool
    trust_source: str
    contract_version: str = WORKSPACE_TRUST_CONTRACT_VERSION
    metadata: Mapping[str, Any] = field(default_factory=dict)


class WorkspaceTrustService(Protocol):
    def resolve_workspace(
        self,
        workspace_ref: str,
        *,
        actor: ActorContext,
    ) -> TrustedWorkspace:
        ...

    def assert_read_allowed(
        self,
        workspace: TrustedWorkspace,
        *,
        actor: ActorContext,
    ) -> None:
        ...

    def assert_execution_allowed(
        self,
        workspace: TrustedWorkspace,
        *,
        actor: ActorContext,
    ) -> None:
        ...


@dataclass(frozen=True)
class ProjectInspectionRequest:
    workspace_id: str
    project_root: str
    refresh: bool = False
    include_git: bool = True
    include_build_test_discovery: bool = True
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ProjectContextSnapshot:
    context_id: str
    workspace_id: str
    project_root: str
    revision: str
    languages: tuple[str, ...] = ()
    frameworks: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()
    architecture_summary: str = ""
    discovered_commands: tuple[Mapping[str, Any], ...] = ()
    contract_version: str = PROJECT_CONTEXT_CONTRACT_VERSION
    metadata: Mapping[str, Any] = field(default_factory=dict)


class ProjectContextService(Protocol):
    def inspect_project(
        self,
        request: ProjectInspectionRequest,
        *,
        actor: ActorContext,
    ) -> ProjectContextSnapshot:
        ...

    def refresh_project_context(
        self,
        context_id: str,
        *,
        actor: ActorContext,
    ) -> ProjectContextSnapshot:
        ...

    def get_project_context(
        self,
        context_id: str,
        *,
        actor: ActorContext,
    ) -> ProjectContextSnapshot | None:
        ...


@dataclass(frozen=True)
class CreateTaskRequest:
    title: str
    intent: str
    workspace_id: str
    project_context_id: str = ""
    requested_capability: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TaskTransition:
    target_status: str
    reason: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TaskQuery:
    workspace_id: str = ""
    status: str = ""
    limit: int = 100


@dataclass(frozen=True)
class TaskRecord:
    task_id: str
    title: str
    intent: str
    status: str
    workspace_id: str
    project_context_id: str = ""
    requested_capability: str = ""
    contract_version: str = TASK_CONTRACT_VERSION
    metadata: Mapping[str, Any] = field(default_factory=dict)


class TaskService(Protocol):
    def create_task(
        self,
        request: CreateTaskRequest,
        *,
        actor: ActorContext,
    ) -> TaskRecord:
        ...

    def get_task(self, task_id: str) -> TaskRecord | None:
        ...

    def transition_task(
        self,
        task_id: str,
        transition: TaskTransition,
        *,
        actor: ActorContext,
    ) -> TaskRecord:
        ...

    def list_tasks(self, query: TaskQuery) -> Sequence[TaskRecord]:
        ...
