from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

from .chat_intent import FounderBrainChatIntent


class FounderBrainChatContext(BaseModel):
    """Immutable read-only context attached to founder intent."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    session_id: str
    workspace: str
    mission: str
    project: str
    milestone: str | None = None
    task: str | None = None
    recommended_next_action: str
    intent: FounderBrainChatIntent
    operating_mode: Literal["read_only"] = "read_only"
    execution_allowed: Literal[False] = False
    worker_available: Literal[False] = False
    persistence_used: Literal[False] = False
    read_only: Literal[True] = True
    generated_at: str


def build_founder_chat_context(
    *,
    state: object,
    intent: FounderBrainChatIntent,
) -> FounderBrainChatContext:
    """Build immutable read-only context from Founder Brain state."""

    return FounderBrainChatContext(
        session_id=str(
            getattr(state, "session_id", "founder-brain-default")
        ),
        workspace=str(
            getattr(state, "workspace", "founder-os")
        ),
        mission=str(
            getattr(state, "mission", "Build IdeasForgeAI")
        ),
        project=str(
            getattr(state, "project", "IdeasForgeAI")
        ),
        milestone=getattr(state, "milestone", None),
        task=getattr(state, "task", None),
        recommended_next_action=str(
            getattr(
                state,
                "recommended_next_action",
                "Review the current Founder OS state.",
            )
        ),
        intent=intent,
        generated_at=str(
            getattr(state, "generated_at", "")
        ),
    )


__all__ = [
    "FounderBrainChatContext",
    "build_founder_chat_context",
]
