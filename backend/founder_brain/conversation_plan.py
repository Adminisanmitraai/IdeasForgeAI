from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict


FounderBrainPlanType = Literal[
    "continue_milestone",
    "start_milestone",
    "inspect_project",
    "audit_project",
    "produce_roadmap",
    "explain_progress",
    "summarize_mission",
    "summarize_timeline",
    "list_capabilities",
    "answer_question",
    "request_clarification",
]


class FounderBrainConversationPlan(BaseModel):
    """Immutable non-executing founder conversation plan."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    plan_id: str
    plan_type: FounderBrainPlanType
    summary: str
    recommended_next_step: str
    requires_project_context: bool
    requires_mission_context: bool
    requires_timeline_context: bool
    operating_mode: Literal["read_only"] = "read_only"
    execution_allowed: Literal[False] = False
    worker_allowed: Literal[False] = False
    filesystem_changes: Literal[False] = False
    network_actions: Literal[False] = False
    tool_execution: Literal[False] = False
    persistence_used: Literal[False] = False
    read_only: Literal[True] = True
    generated_at: str


__all__ = [
    "FounderBrainConversationPlan",
    "FounderBrainPlanType",
]
