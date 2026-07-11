"""Production HTTP interface for the Convera pipeline."""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.convera.agents.convera_orchestrator_agent import (
    ConveraOrchestratorAgent,
)


router = APIRouter(
    prefix="/api/convera",
    tags=["Convera"],
)


class ConveraMessageRequest(BaseModel):
    """One frontend message submitted to Convera."""

    conversation_id: str
    message: str
    sender_id: str
    actor_id: str | None = None
    actor_role: str = "member"
    chat_type: str = "private"
    activation_mode: str = "mention_only"
    thread_id: str | None = None
    project_id: str | None = None
    request_id: str | None = None
    trace_id: str | None = None
    approval_granted: bool = False
    resource_project_id: str | None = None
    resource_conversation_id: str | None = None
    participants: list[Dict[str, Any]] = Field(
        default_factory=list
    )
    messages: list[Dict[str, Any]] = Field(
        default_factory=list
    )
    memories: list[Dict[str, Any]] = Field(
        default_factory=list
    )
    files: list[Dict[str, Any]] = Field(
        default_factory=list
    )


def _temporary_specialist_output(
    request: ConveraMessageRequest,
) -> Dict[str, Any]:
    """Return relevant test output until CONVERA-12 dispatch exists."""

    cleaned_request = request.message.strip()

    if cleaned_request.lower().startswith("@convera"):
        cleaned_request = cleaned_request[len("@convera"):].strip(
            " ,:-"
        )

    if not cleaned_request:
        cleaned_request = "the current request"

    return {
        "content": (
            f"Convera processed your request about "
            f"{cleaned_request}. The current production "
            "pipeline completed activation, context, intent, "
            "permission, memory, quality validation and "
            "response composition."
        ),
        "metadata": {
            "source": "convera_11c_temporary_specialist",
            "temporary": True,
            "replacement_phase": "CONVERA-12",
        },
    }


@router.get("/health")
def convera_health() -> Dict[str, Any]:
    return {
        "ok": True,
        "service": "convera",
        "pipeline_version": (
            ConveraOrchestratorAgent.PIPELINE_VERSION
        ),
        "specialist_mode": "temporary",
    }


@router.post("/message")
def convera_message(
    request: ConveraMessageRequest,
) -> Dict[str, Any]:
    payload = request.model_dump()

    payload["actor_id"] = (
        request.actor_id
        or request.sender_id
    )

    payload["specialist_result"] = {
        "success": True,
        "agent_id": "convera.temporary_specialist",
        "output": _temporary_specialist_output(request),
    }

    result = ConveraOrchestratorAgent().execute(payload)

    return {
        "success": result.success,
        "agent_id": result.agent_id,
        "data": result.data,
        "error": result.error,
    }
