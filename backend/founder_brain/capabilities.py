from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from backend.composition.registry import PlatformRegistryStatus

from .models import (
    FounderBrainCapabilityDomain,
    FounderBrainCapabilityEdge,
    FounderBrainCapabilityGraph,
    FounderBrainCapabilityMode,
    FounderBrainCapabilityNode,
    FounderBrainCapabilityStatus,
)


class CapabilityGraphValidationError(ValueError):
    """Raised when capability definitions cannot form a safe graph."""


@dataclass(frozen=True)
class CapabilityDefinition:
    capability_id: str
    title: str
    domain: FounderBrainCapabilityDomain
    provider: str
    mode: FounderBrainCapabilityMode
    workspace_id: str
    provider_slot: str | None = None
    approval_required: bool = False
    execution_boundary: str = "read_only"
    dependencies: tuple[str, ...] = ()
    available_actions: tuple[str, ...] = ("inspect",)
    unsupported_status: FounderBrainCapabilityStatus = "planned"


_DEFINITIONS: tuple[CapabilityDefinition, ...] = (
    CapabilityDefinition(
        "system.health", "System health", "system", "founder-brain",
        "read_only", "founder-os", available_actions=("inspect",),
    ),
    CapabilityDefinition(
        "system.registry.inspect", "Registry inspection", "system",
        "platform-registry", "read_only", "founder-os",
        available_actions=("inspect",), unsupported_status="unavailable",
    ),
    CapabilityDefinition(
        "conversation.intent", "Intent understanding", "conversation",
        "convera", "unavailable", "convera",
    ),
    CapabilityDefinition(
        "conversation.context", "Conversation context", "conversation",
        "convera", "unavailable", "convera",
    ),
    CapabilityDefinition(
        "conversation.memory", "Conversation memory", "memory", "convera",
        "unavailable", "convera",
    ),
    CapabilityDefinition(
        "conversation.quality", "Conversation quality", "conversation",
        "convera", "unavailable", "convera",
    ),
    CapabilityDefinition(
        "engineering.repository.inspect", "Repository inspection",
        "engineering", "forgecode", "unavailable", "forgecode",
    ),
    CapabilityDefinition(
        "engineering.project.context", "Project context", "engineering",
        "forgecode", "unavailable", "forgecode",
        dependencies=("engineering.repository.inspect",),
    ),
    CapabilityDefinition(
        "engineering.architecture.analyze", "Architecture analysis",
        "engineering", "forgecode", "unavailable", "forgecode",
        dependencies=("engineering.project.context",),
    ),
    CapabilityDefinition(
        "engineering.safe_edit.plan", "Safe edit planning", "engineering",
        "platform.planning", "planning", "forgecode",
        provider_slot="planning", execution_boundary="existing_terminal_policy",
        dependencies=("engineering.project.context",),
        available_actions=("describe", "plan"), unsupported_status="unavailable",
    ),
    CapabilityDefinition(
        "engineering.test.discover", "Test discovery", "engineering",
        "forgecode", "unavailable", "forgecode",
        dependencies=("engineering.repository.inspect",),
    ),
    CapabilityDefinition(
        "execution.plan", "Execution planning", "execution",
        "platform.planning", "planning", "worker", provider_slot="planning",
        execution_boundary="existing_terminal_policy",
        available_actions=("describe", "plan"), unsupported_status="unavailable",
    ),
    CapabilityDefinition(
        "execution.approval", "Approval boundary", "execution",
        "platform.approval", "approval_required", "worker",
        provider_slot="approval", approval_required=True,
        execution_boundary="existing_worker_policy",
        dependencies=("execution.plan",), available_actions=("describe",),
        unsupported_status="unavailable",
    ),
    CapabilityDefinition(
        "execution.run", "Controlled execution", "execution",
        "platform.execution", "execution", "worker", provider_slot="execution",
        approval_required=True, execution_boundary="existing_worker_policy",
        dependencies=("execution.approval",), available_actions=("describe",),
        unsupported_status="unavailable",
    ),
    CapabilityDefinition(
        "execution.session", "Execution sessions", "execution",
        "platform.sessions", "read_only", "terminal", provider_slot="sessions",
        execution_boundary="existing_terminal_policy",
        available_actions=("inspect",), unsupported_status="unavailable",
    ),
    CapabilityDefinition(
        "execution.events", "Execution events", "execution",
        "platform.events", "read_only", "terminal", provider_slot="events",
        execution_boundary="existing_terminal_policy",
        dependencies=("execution.session",), available_actions=("inspect",),
        unsupported_status="unavailable",
    ),
    CapabilityDefinition(
        "execution.audit", "Execution audit", "execution",
        "platform.audit", "read_only", "terminal", provider_slot="audit",
        execution_boundary="existing_terminal_policy",
        dependencies=("execution.events",), available_actions=("inspect",),
        unsupported_status="unavailable",
    ),
    CapabilityDefinition(
        "product.requirements", "Product requirements", "product", "product",
        "unavailable", "product",
    ),
    CapabilityDefinition(
        "product.planning", "Product planning", "product", "product",
        "unavailable", "product", dependencies=("product.requirements",),
    ),
    CapabilityDefinition(
        "product.workflow", "Product workflow", "product", "product",
        "unavailable", "product", dependencies=("product.planning",),
    ),
    CapabilityDefinition(
        "design.interface", "Interface design", "design", "studio",
        "unavailable", "studio",
    ),
    CapabilityDefinition(
        "operations.worker", "Worker operations", "operations", "worker",
        "unavailable", "worker", dependencies=("execution.approval",),
    ),
    CapabilityDefinition(
        "research.browser", "Browser research", "research", "browser",
        "unavailable", "browser",
    ),
    CapabilityDefinition(
        "mobile.workspace", "Mobile workspace", "mobile", "mobile",
        "unavailable", "mobile",
    ),
)


def validate_capability_definitions(
    definitions: Sequence[CapabilityDefinition],
) -> tuple[CapabilityDefinition, ...]:
    ordered = tuple(sorted(definitions, key=lambda item: item.capability_id))
    identifiers: set[str] = set()
    for definition in ordered:
        capability_id = definition.capability_id
        if not capability_id or capability_id in identifiers:
            raise CapabilityGraphValidationError(
                f"invalid or duplicate capability id: {capability_id!r}"
            )
        identifiers.add(capability_id)

    for definition in ordered:
        if any(item not in identifiers for item in definition.dependencies):
            raise CapabilityGraphValidationError(
                f"unknown dependency for {definition.capability_id}"
            )

    visiting: set[str] = set()
    visited: set[str] = set()
    by_id = {item.capability_id: item for item in ordered}

    def visit(capability_id: str) -> None:
        if capability_id in visiting:
            raise CapabilityGraphValidationError("cyclic capability dependency")
        if capability_id in visited:
            return
        visiting.add(capability_id)
        for dependency in by_id[capability_id].dependencies:
            visit(dependency)
        visiting.remove(capability_id)
        visited.add(capability_id)

    for capability_id in sorted(identifiers):
        visit(capability_id)
    return ordered


def build_capability_graph(
    *,
    generated_at: str,
    registry_status: PlatformRegistryStatus,
    container: object | None,
    workspace_catalogue: object | None,
    definitions: Sequence[CapabilityDefinition] = _DEFINITIONS,
) -> FounderBrainCapabilityGraph:
    ordered = validate_capability_definitions(definitions)
    workspace_statuses = _workspace_statuses(workspace_catalogue)
    nodes = tuple(
        _node(definition, registry_status, container, workspace_statuses)
        for definition in ordered
    )
    edges = tuple(
        sorted(
            (
                FounderBrainCapabilityEdge(
                    source_capability_id=definition.capability_id,
                    target_capability_id=dependency,
                    relationship="requires",
                )
                for definition in ordered
                for dependency in definition.dependencies
            ),
            key=lambda edge: (
                edge.source_capability_id,
                edge.target_capability_id,
                edge.relationship,
            ),
        )
    )
    summary = {
        domain: sum(node.domain == domain for node in nodes)
        for domain in (
            "system", "conversation", "product", "engineering", "execution",
            "design", "operations", "research", "mobile", "memory",
        )
    }
    return FounderBrainCapabilityGraph(
        generated_at=generated_at,
        nodes=nodes,
        edges=edges,
        domain_summary=summary,
        unavailable_capabilities=tuple(
            node.capability_id for node in nodes if node.status == "unavailable"
        ),
        degraded_capabilities=tuple(
            node.capability_id for node in nodes if node.status == "degraded"
        ),
        planned_capabilities=tuple(
            node.capability_id for node in nodes if node.status == "planned"
        ),
    )


def safe_empty_capability_graph(generated_at: str) -> FounderBrainCapabilityGraph:
    return FounderBrainCapabilityGraph(
        generated_at=generated_at,
        domain_summary={
            domain: 0
            for domain in (
                "system", "conversation", "product", "engineering", "execution",
                "design", "operations", "research", "mobile", "memory",
            )
        },
    )


def _node(
    definition: CapabilityDefinition,
    registry_status: PlatformRegistryStatus,
    container: object | None,
    workspace_statuses: Mapping[str, FounderBrainCapabilityStatus],
) -> FounderBrainCapabilityNode:
    provider_instance = (
        getattr(container, definition.provider_slot, None)
        if container is not None and definition.provider_slot
        else None
    )
    workspace_status = workspace_statuses.get(
        definition.workspace_id, definition.unsupported_status
    )

    if definition.capability_id == "system.health":
        status: FounderBrainCapabilityStatus = "available"
    elif definition.capability_id == "system.registry.inspect":
        status = (
            "available" if registry_status.configured and registry_status.initialized
            else "degraded" if registry_status.configured
            else "unavailable"
        )
    elif definition.provider_slot and provider_instance is not None:
        status = (
            workspace_status
            if workspace_status in {"available", "degraded"}
            else "degraded"
        )
    else:
        status = definition.unsupported_status

    mode: FounderBrainCapabilityMode = (
        definition.mode if status in {"available", "degraded"} else "unavailable"
    )
    actions = (
        tuple(sorted(set(definition.available_actions)))
        if status in {"available", "degraded"}
        else ()
    )
    return FounderBrainCapabilityNode(
        capability_id=definition.capability_id,
        title=definition.title,
        domain=definition.domain,
        provider=definition.provider,
        status=status,
        mode=mode,
        contract_version=_contract_version(provider_instance),
        approval_required=definition.approval_required,
        execution_boundary=definition.execution_boundary,
        dependencies=tuple(sorted(set(definition.dependencies))),
        available_actions=actions,
        metadata={"workspace_id": definition.workspace_id},
    )


def _workspace_statuses(
    catalogue: object | None,
) -> dict[str, FounderBrainCapabilityStatus]:
    workspaces = getattr(catalogue, "workspaces", ())
    if not isinstance(workspaces, (list, tuple)):
        return {}
    values: dict[str, FounderBrainCapabilityStatus] = {}
    for workspace in workspaces:
        workspace_id = getattr(workspace, "workspace_id", None)
        status = getattr(workspace, "status", None)
        if (
            isinstance(workspace_id, str)
            and status in {"available", "degraded", "unavailable", "planned"}
        ):
            values[workspace_id] = status
    return values


def _contract_version(provider: object | None) -> str | None:
    value = getattr(provider, "contract_version", None)
    return value if isinstance(value, str) and value.strip() else None


__all__ = [
    "CapabilityDefinition",
    "CapabilityGraphValidationError",
    "build_capability_graph",
    "safe_empty_capability_graph",
    "validate_capability_definitions",
]
