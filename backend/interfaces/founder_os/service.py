from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from backend.composition.container import PlatformServiceContainer
from backend.composition.registry import (
    PlatformRegistryStatus,
    PlatformRegistryNotConfiguredError,
    get_platform_registry_status,
    get_platform_services,
)

from .models import (
    FounderOSCapabilitiesData,
    FounderOSExecutionBoundary,
    FounderOSHealthData,
    FounderOSRegistryStatusData,
    FounderOSWorkspace,
    FounderOSWorkspaceCatalogueData,
    FounderOSWorkspaceDomain,
)

ContainerResolver = Callable[[], PlatformServiceContainer]
StatusResolver = Callable[[], PlatformRegistryStatus]


@dataclass(frozen=True)
class _WorkspaceDefinition:
    workspace_id: str
    title: str
    domain: FounderOSWorkspaceDomain
    route: str
    provider_capabilities: tuple[tuple[str, str], ...]
    execution_boundary: FounderOSExecutionBoundary
    intrinsic_capabilities: tuple[str, ...] = ()


_WORKSPACE_DEFINITIONS: tuple[_WorkspaceDefinition, ...] = (
    _WorkspaceDefinition(
        "founder-os",
        "Founder OS",
        "system",
        "/dashboard",
        (),
        "read_only",
        (
            "health",
            "capability_discovery",
            "registry_status",
            "workspace_catalogue",
        ),
    ),
    _WorkspaceDefinition(
        "terminal",
        "Terminal",
        "conversation",
        "/terminal",
        (
            ("sessions", "sessions"),
            ("events", "events"),
            ("audit", "audit"),
        ),
        "existing_terminal_policy",
    ),
    _WorkspaceDefinition(
        "forgecode",
        "ForgeCode",
        "engineering",
        "/code",
        (("planning", "planning"),),
        "existing_terminal_policy",
    ),
    _WorkspaceDefinition(
        "worker",
        "Worker",
        "execution",
        "/worker",
        (("approval", "approval"), ("execution", "execution")),
        "existing_worker_policy",
    ),
    _WorkspaceDefinition(
        "convera",
        "Convera",
        "conversation",
        "/convera",
        (("conversation", "conversation"),),
        "unavailable",
    ),
    _WorkspaceDefinition(
        "product",
        "Product",
        "product",
        "/product",
        (("product_intelligence", "product"),),
        "unavailable",
    ),
    _WorkspaceDefinition(
        "studio",
        "Studio",
        "design",
        "/studio",
        (("design", "design"),),
        "unavailable",
    ),
    _WorkspaceDefinition(
        "work",
        "Work",
        "operations",
        "/work",
        (("operations", "operations"),),
        "unavailable",
    ),
    _WorkspaceDefinition(
        "browser",
        "Browser",
        "research",
        "/browser",
        (("research", "research"),),
        "unavailable",
    ),
    _WorkspaceDefinition(
        "mobile",
        "Mobile",
        "mobile",
        "/mobile",
        (("mobile", "mobile"),),
        "unavailable",
    ),
)


class FounderOSReadService:
    """Read-only application service for the initial Founder OS API."""

    def __init__(
        self,
        *,
        container_resolver: ContainerResolver = get_platform_services,
        status_resolver: StatusResolver = get_platform_registry_status,
    ) -> None:
        self._container_resolver = container_resolver
        self._status_resolver = status_resolver

    def health(self) -> FounderOSHealthData:
        status = self._status_resolver()
        return FounderOSHealthData(
            status="ok" if status.configured else "not_configured",
            interface="founder_os",
            read_only=True,
            registry_configured=status.configured,
            registry_initialized=status.initialized,
        )

    def registry_status(self) -> FounderOSRegistryStatusData:
        status = self._status_resolver()
        return FounderOSRegistryStatusData(
            configured=status.configured,
            initialized=status.initialized,
            registry_contract_version=status.contract_version,
        )

    def capabilities(self) -> FounderOSCapabilitiesData:
        container = self._container_resolver()

        service_contracts = {
            "container": container.contract_version,
            "planning": _contract_version(container.planning),
            "approval": _contract_version(container.approval),
            "execution": _contract_version(container.execution),
            "sessions": _contract_version(container.sessions),
            "events": _contract_version(container.events),
            "audit": _contract_version(container.audit),
        }

        return FounderOSCapabilitiesData(
            interface="founder_os",
            read_only=True,
            capabilities={
                "health": True,
                "capability_discovery": True,
                "registry_status": True,
                "task_creation": False,
                "planning": False,
                "approval_issue": False,
                "execution": False,
                "cancellation": False,
                "deployment": False,
                "admin_mutation": False,
            },
            service_contracts=service_contracts,
        )

    def workspaces(self) -> FounderOSWorkspaceCatalogueData:
        """Project registry presence into a deterministic read-only catalogue."""
        try:
            container: object | None = self._container_resolver()
        except PlatformRegistryNotConfiguredError:
            container = None

        workspaces = [
            _workspace_from_definition(definition, container)
            for definition in _WORKSPACE_DEFINITIONS
        ]
        return FounderOSWorkspaceCatalogueData(
            interface="founder_os",
            read_only=True,
            workspaces=workspaces,
        )


def _contract_version(service: object) -> str:
    direct = getattr(service, "contract_version", "")
    if direct:
        return str(direct)

    legacy = getattr(service, "_planner", None)
    if legacy is not None:
        value = getattr(legacy, "CONTRACT_VERSION", "")
        if value:
            return str(value)

    return service.__class__.__name__


def _workspace_from_definition(
    definition: _WorkspaceDefinition,
    container: object | None,
) -> FounderOSWorkspace:
    available_capabilities = list(definition.intrinsic_capabilities)
    provider_count = len(definition.provider_capabilities)

    for capability_id, provider_name in definition.provider_capabilities:
        provider = (
            getattr(container, provider_name, None)
            if container is not None
            else None
        )
        if provider is not None:
            available_capabilities.append(capability_id)

    available_provider_count = (
        len(available_capabilities) - len(definition.intrinsic_capabilities)
    )
    if not provider_count:
        status = "available"
    elif available_provider_count == provider_count:
        status = "available"
    elif available_provider_count:
        status = "degraded"
    else:
        status = "unavailable"

    execution_boundary = (
        definition.execution_boundary
        if status in {"available", "degraded"}
        else "unavailable"
    )
    return FounderOSWorkspace(
        workspace_id=definition.workspace_id,
        title=definition.title,
        domain=definition.domain,
        route=definition.route,
        status=status,
        read_only=True,
        capability_ids=available_capabilities,
        execution_boundary=execution_boundary,
    )
