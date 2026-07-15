from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

FOUNDER_OS_API_CONTRACT_VERSION = "founder-os.application-api.v1"


class FounderOSResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ok: bool = True
    contract_version: str = FOUNDER_OS_API_CONTRACT_VERSION
    data: dict = Field(default_factory=dict)
    errors: list[dict] = Field(default_factory=list)


class FounderOSHealthData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    interface: str
    read_only: bool
    registry_configured: bool
    registry_initialized: bool


class FounderOSCapabilitiesData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    interface: str
    read_only: bool
    capabilities: dict[str, bool]
    service_contracts: dict[str, str]


class FounderOSRegistryStatusData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    configured: bool
    initialized: bool
    registry_contract_version: str


FounderOSWorkspaceDomain = Literal[
    "system",
    "conversation",
    "product",
    "engineering",
    "execution",
    "design",
    "operations",
    "research",
    "mobile",
]
FounderOSWorkspaceStatus = Literal[
    "available",
    "degraded",
    "unavailable",
    "planned",
]
FounderOSExecutionBoundary = Literal[
    "read_only",
    "existing_terminal_policy",
    "existing_worker_policy",
    "unavailable",
]


class FounderOSWorkspace(BaseModel):
    model_config = ConfigDict(extra="forbid")

    workspace_id: str
    title: str
    domain: FounderOSWorkspaceDomain
    route: str
    status: FounderOSWorkspaceStatus
    read_only: bool = True
    capability_ids: list[str] = Field(default_factory=list)
    execution_boundary: FounderOSExecutionBoundary


class FounderOSWorkspaceCatalogueData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    interface: str
    read_only: bool
    workspaces: list[FounderOSWorkspace] = Field(default_factory=list)
