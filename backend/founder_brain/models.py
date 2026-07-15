from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

FOUNDER_BRAIN_API_CONTRACT_VERSION = "founder-brain.read-api.v1"
FOUNDER_BRAIN_STATE_SCHEMA_VERSION = "founder-brain.operating-state.v1"

FounderBrainOperatingStateName = Literal[
    "booting",
    "loading",
    "ready",
    "understanding",
    "planning",
    "awaiting_approval",
    "executing",
    "validating",
    "completed",
    "blocked",
    "failed",
]
FounderBrainOperatingMode = Literal["read_only"]
FounderBrainCapabilityStatus = Literal[
    "available",
    "degraded",
    "unavailable",
    "planned",
]
FounderBrainCapabilityDomain = Literal[
    "system",
    "conversation",
    "product",
    "engineering",
    "execution",
    "design",
    "operations",
    "research",
    "mobile",
    "memory",
]
FounderBrainCapabilityMode = Literal[
    "read_only",
    "planning",
    "approval_required",
    "execution",
    "unavailable",
]
FounderBrainCapabilityRelationship = Literal[
    "requires",
    "provided_by",
    "validates",
    "produces",
    "precedes",
]

FOUNDER_BRAIN_CAPABILITY_GRAPH_SCHEMA_VERSION = (
    "founder-brain.capability-graph.v1"
)
FOUNDER_BRAIN_MISSION_GRAPH_SCHEMA_VERSION = "founder-brain.mission-graph.v1"
FOUNDER_BRAIN_TIMELINE_SCHEMA_VERSION = "founder-brain.timeline.v1"

FounderBrainWorkStatus = Literal[
    "planned",
    "active",
    "blocked",
    "completed",
    "cancelled",
]
FounderBrainPriority = Literal["low", "normal", "high", "critical"]
FounderBrainRiskLevel = Literal["low", "medium", "high", "critical"]
FounderBrainValidationState = Literal[
    "not_started",
    "pending",
    "passed",
    "failed",
    "blocked",
]
FounderBrainTimelineSeverity = Literal[
    "informational",
    "attention",
    "approval",
    "warning",
    "critical",
]


class FounderBrainResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    ok: bool = True
    contract_version: str = FOUNDER_BRAIN_API_CONTRACT_VERSION
    data: dict[str, object] = Field(default_factory=dict)
    errors: tuple[dict[str, str], ...] = ()


class FounderBrainCapabilitySummary(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    registry_status: FounderBrainCapabilityStatus
    registry_configured: bool
    registry_initialized: bool
    available_capability_ids: tuple[str, ...] = ()
    unavailable_capability_ids: tuple[str, ...] = ()


class FounderBrainCapabilityNode(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    capability_id: str
    title: str
    domain: FounderBrainCapabilityDomain
    provider: str
    status: FounderBrainCapabilityStatus
    mode: FounderBrainCapabilityMode
    contract_version: str | None
    approval_required: bool
    execution_boundary: str
    dependencies: tuple[str, ...] = ()
    available_actions: tuple[str, ...] = ()
    read_only: bool = True
    metadata: dict[str, object] = Field(default_factory=dict)


class FounderBrainCapabilityEdge(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    source_capability_id: str
    target_capability_id: str
    relationship: FounderBrainCapabilityRelationship


class FounderBrainCapabilityGraph(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: str = FOUNDER_BRAIN_CAPABILITY_GRAPH_SCHEMA_VERSION
    generated_at: str
    read_only: bool = True
    nodes: tuple[FounderBrainCapabilityNode, ...] = ()
    edges: tuple[FounderBrainCapabilityEdge, ...] = ()
    domain_summary: dict[str, int] = Field(default_factory=dict)
    unavailable_capabilities: tuple[str, ...] = ()
    degraded_capabilities: tuple[str, ...] = ()
    planned_capabilities: tuple[str, ...] = ()


class FounderBrainMissionNode(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    mission_id: str
    title: str
    description: str
    status: FounderBrainWorkStatus
    priority: FounderBrainPriority
    project_ids: tuple[str, ...] = ()
    active_project_id: str | None
    created_at: str
    updated_at: str
    metadata: dict[str, object] = Field(default_factory=dict)


class FounderBrainProjectNode(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    project_id: str
    title: str
    description: str
    status: FounderBrainWorkStatus
    active_milestone_id: str | None
    workspace_id: str
    repository_reference: str | None
    metadata: dict[str, object] = Field(default_factory=dict)


class FounderBrainMilestoneNode(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    milestone_id: str
    project_id: str
    title: str
    description: str
    status: FounderBrainWorkStatus
    sequence: int
    task_ids: tuple[str, ...] = ()
    completed_task_count: int
    total_task_count: int
    started_at: str | None
    completed_at: str | None
    next_action: str | None
    metadata: dict[str, object] = Field(default_factory=dict)


class FounderBrainTaskNode(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    task_id: str
    milestone_id: str
    title: str
    description: str
    status: FounderBrainWorkStatus
    sequence: int
    risk_level: FounderBrainRiskLevel
    capability_ids: tuple[str, ...] = ()
    dependency_ids: tuple[str, ...] = ()
    approval_required: bool
    validation_state: FounderBrainValidationState
    result_reference: str | None
    metadata: dict[str, object] = Field(default_factory=dict)


class FounderBrainDecisionNode(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    decision_id: str
    title: str
    summary: str
    status: FounderBrainWorkStatus
    scope: str
    related_project_id: str | None
    related_milestone_id: str | None
    related_task_id: str | None
    created_at: str
    supersedes: tuple[str, ...] = ()
    metadata: dict[str, object] = Field(default_factory=dict)


class FounderBrainMissionGraph(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: str = FOUNDER_BRAIN_MISSION_GRAPH_SCHEMA_VERSION
    generated_at: str
    read_only: bool = True
    mission: FounderBrainMissionNode
    projects: tuple[FounderBrainProjectNode, ...] = ()
    milestones: tuple[FounderBrainMilestoneNode, ...] = ()
    tasks: tuple[FounderBrainTaskNode, ...] = ()
    decisions: tuple[FounderBrainDecisionNode, ...] = ()
    active_project_id: str | None
    active_milestone_id: str | None
    active_task_id: str | None
    recommended_next_action: str


class FounderBrainTimelineEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    event_id: str
    occurred_at: str
    event_type: str
    title: str
    summary: str
    project_id: str | None
    milestone_id: str | None
    task_id: str | None
    severity: FounderBrainTimelineSeverity
    source: str
    reference_ids: tuple[str, ...] = ()
    metadata: dict[str, object] = Field(default_factory=dict)


class FounderBrainTimelineResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: str = FOUNDER_BRAIN_TIMELINE_SCHEMA_VERSION
    generated_at: str
    read_only: bool = True
    events: tuple[FounderBrainTimelineEvent, ...] = ()
    latest_event_id: str | None
    total_events: int
    next_cursor: str | None
    previous_cursor: str | None


class FounderBrainOperatingState(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: str = FOUNDER_BRAIN_STATE_SCHEMA_VERSION
    session_id: str
    mission: str
    project: str
    milestone: str | None
    task: str | None
    workspace: str
    operating_state: FounderBrainOperatingStateName
    operating_mode: FounderBrainOperatingMode = "read_only"
    active_jobs: tuple[str, ...] = ()
    pending_approvals: tuple[str, ...] = ()
    capability_summary: FounderBrainCapabilitySummary
    recommended_next_action: str
    read_only: bool = True
    generated_at: str


class FounderBrainSessionData(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: str = FOUNDER_BRAIN_STATE_SCHEMA_VERSION
    session_id: str
    workspace: str
    operating_state: FounderBrainOperatingStateName
    operating_mode: FounderBrainOperatingMode = "read_only"
    active_jobs: tuple[str, ...] = ()
    pending_approvals: tuple[str, ...] = ()
    read_only: bool = True
    generated_at: str


class FounderBrainMissionData(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: str = FOUNDER_BRAIN_STATE_SCHEMA_VERSION
    mission: str
    project: str
    milestone: str | None
    task: str | None
    recommended_next_action: str
    read_only: bool = True
    generated_at: str
