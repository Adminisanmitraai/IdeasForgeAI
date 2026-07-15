from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from backend.platform.adapters import (
    TerminalApprovalAdapter,
    TerminalAuditAdapter,
    TerminalEventAdapter,
    TerminalExecutionAdapter,
    TerminalPlanningAdapter,
    TerminalSessionAdapter,
)
from backend.platform.contracts.execution import (
    ApprovalService,
    AuditService,
    EventService,
    ExecutionService,
    PlanningService,
    SessionService,
)

CONTRACT_VERSION = "composition.platform-container.v1"


@dataclass(frozen=True)
class LegacyTerminalDependencies:
    """Concrete legacy dependencies supplied by the application composition root."""

    planner_module: Any
    runtime_module: Any
    approval_module: Any
    audit_module: Any
    session_registry: Any
    approval_authority: Any
    audit_history: Any


@dataclass(frozen=True)
class PlatformServiceContainer:
    """Stable service references consumed by future application layers."""

    planning: PlanningService
    approval: ApprovalService
    execution: ExecutionService
    sessions: SessionService
    events: EventService
    audit: AuditService
    contract_version: str = CONTRACT_VERSION


def build_terminal_platform_container(
    dependencies: LegacyTerminalDependencies,
) -> PlatformServiceContainer:
    """Build one shared adapter graph over the existing Terminal implementation.

    This function does not create legacy runtime state itself. The caller supplies
    the exact session registry, approval authority, and audit history instances so
    existing lifecycle, token, and audit behavior remain authoritative.
    """

    _validate_dependencies(dependencies)

    planning = TerminalPlanningAdapter(dependencies.planner_module)
    approval = TerminalApprovalAdapter(
        dependencies.approval_authority,
        dependencies.approval_module,
    )
    execution = TerminalExecutionAdapter(
        dependencies.session_registry,
        dependencies.runtime_module,
    )
    sessions = TerminalSessionAdapter(
        dependencies.session_registry,
        dependencies.runtime_module,
    )
    events = TerminalEventAdapter(dependencies.session_registry)
    audit = TerminalAuditAdapter(
        dependencies.audit_history,
        dependencies.audit_module,
    )

    return PlatformServiceContainer(
        planning=planning,
        approval=approval,
        execution=execution,
        sessions=sessions,
        events=events,
        audit=audit,
    )


def _validate_dependencies(
    dependencies: LegacyTerminalDependencies,
) -> None:
    if not isinstance(dependencies, LegacyTerminalDependencies):
        raise TypeError(
            "Platform container requires LegacyTerminalDependencies."
        )

    required = {
        "planner_module": dependencies.planner_module,
        "runtime_module": dependencies.runtime_module,
        "approval_module": dependencies.approval_module,
        "audit_module": dependencies.audit_module,
        "session_registry": dependencies.session_registry,
        "approval_authority": dependencies.approval_authority,
        "audit_history": dependencies.audit_history,
    }
    missing = sorted(name for name, value in required.items() if value is None)
    if missing:
        raise ValueError(
            "Missing legacy Terminal dependencies: " + ", ".join(missing)
        )

    registry_methods = {
        "submit_session",
        "start_session",
        "cancel_session",
        "get_session",
        "list_sessions",
        "get_events",
        "get_result",
    }
    missing_registry = sorted(
        name for name in registry_methods
        if not callable(getattr(dependencies.session_registry, name, None))
    )
    if missing_registry:
        raise TypeError(
            "Session registry is missing methods: "
            + ", ".join(missing_registry)
        )

    approval_methods = {"issue", "verify", "revoke"}
    missing_approval = sorted(
        name for name in approval_methods
        if not callable(getattr(dependencies.approval_authority, name, None))
    )
    if missing_approval:
        raise TypeError(
            "Approval authority is missing methods: "
            + ", ".join(missing_approval)
        )

    audit_methods = {"append_session", "query", "verify_integrity"}
    missing_audit = sorted(
        name for name in audit_methods
        if not callable(getattr(dependencies.audit_history, name, None))
    )
    if missing_audit:
        raise TypeError(
            "Audit history is missing methods: "
            + ", ".join(missing_audit)
        )
