from __future__ import annotations

from typing import Final, Literal

from pydantic import BaseModel, ConfigDict, Field

FounderBrainChatIntentName = Literal[
    "continue_implementation",
    "start_implementation",
    "inspect_project",
    "audit_project",
    "plan_work",
    "explain_status",
    "review_mission",
    "review_timeline",
    "review_capabilities",
    "general_question",
    "unknown",
]

FounderBrainIntentConfidence = Literal[
    "high",
    "medium",
    "low",
]

FOUNDER_BRAIN_CHAT_INTENT_SCHEMA_VERSION: Final[str] = (
    "founder-brain.chat-intent.v1"
)


class FounderBrainChatIntentValidationError(ValueError):
    """Raised when deterministic chat intent input is invalid."""


class FounderBrainChatIntent(BaseModel):
    """Immutable deterministic interpretation of a founder message."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: str = FOUNDER_BRAIN_CHAT_INTENT_SCHEMA_VERSION
    intent: FounderBrainChatIntentName
    confidence: FounderBrainIntentConfidence
    confidence_score: float = Field(ge=0.0, le=1.0)
    matched_rule: str
    normalized_message: str
    requires_project_context: bool = False
    requires_mission_context: bool = False
    requires_timeline_context: bool = False
    execution_requested: Literal[False] = False
    read_only: Literal[True] = True


def normalize_intent_message(value: object) -> str:
    """Return normalized deterministic intent input."""

    if not isinstance(value, str):
        raise FounderBrainChatIntentValidationError(
            "message must be a string"
        )

    normalized = " ".join(value.strip().lower().split())

    if not normalized:
        raise FounderBrainChatIntentValidationError(
            "message must not be empty"
        )

    if len(normalized) > 4000:
        raise FounderBrainChatIntentValidationError(
            "message must not exceed 4000 characters"
        )

    return normalized


def classify_founder_chat_intent(
    message: object,
) -> FounderBrainChatIntent:
    """Classify a founder message using deterministic local rules."""

    normalized = normalize_intent_message(message)

    rules = (
        (
            "continue_implementation",
            (
                "continue implementation",
                "continue the implementation",
                "continue founder os",
                "resume implementation",
                "next implementation",
            ),
            0.98,
            True,
            True,
            True,
        ),
        (
            "start_implementation",
            (
                "start implementation",
                "begin implementation",
                "implement this",
                "lets start",
                "let us start",
            ),
            0.96,
            True,
            True,
            False,
        ),
        (
            "audit_project",
            (
                "audit project",
                "audit the project",
                "audit code",
                "find issues",
            ),
            0.95,
            True,
            False,
            False,
        ),
        (
            "inspect_project",
            (
                "inspect project",
                "understand project",
                "analyze project",
                "analyse project",
            ),
            0.94,
            True,
            False,
            False,
        ),
        (
            "plan_work",
            (
                "create a plan",
                "make a plan",
                "plan the work",
                "implementation plan",
                "what should we do next",
                "what is next",
                "next steps",
            ),
            0.93,
            True,
            True,
            True,
        ),
        (
            "explain_status",
            (
                "current status",
                "show status",
                "explain status",
                "where are we",
                "what is completed",
                "what have we completed",
                "what is left",
                "progress",
            ),
            0.92,
            False,
            True,
            True,
        ),
        (
            "review_mission",
            (
                "show mission",
                "review mission",
                "current mission",
                "mission status",
            ),
            0.92,
            False,
            True,
            False,
        ),
        (
            "review_timeline",
            (
                "show timeline",
                "review timeline",
                "current timeline",
                "timeline status",
                "milestone timeline",
            ),
            0.92,
            False,
            True,
            True,
        ),
        (
            "review_capabilities",
            (
                "show capabilities",
                "review capabilities",
                "what can founder os do",
                "what can you do",
                "capability status",
            ),
            0.92,
            False,
            False,
            False,
        ),
    )

    for (
        intent,
        phrases,
        score,
        project_context,
        mission_context,
        timeline_context,
    ) in rules:
        for phrase in phrases:
            if phrase in normalized:
                return FounderBrainChatIntent(
                    intent=intent,
                    confidence="high",
                    confidence_score=score,
                    matched_rule=phrase,
                    normalized_message=normalized,
                    requires_project_context=project_context,
                    requires_mission_context=mission_context,
                    requires_timeline_context=timeline_context,
                )

    if normalized.endswith("?"):
        return FounderBrainChatIntent(
            intent="general_question",
            confidence="medium",
            confidence_score=0.70,
            matched_rule="question_shape",
            normalized_message=normalized,
        )

    return FounderBrainChatIntent(
        intent="unknown",
        confidence="low",
        confidence_score=0.25,
        matched_rule="fallback",
        normalized_message=normalized,
    )


__all__ = [
    "FOUNDER_BRAIN_CHAT_INTENT_SCHEMA_VERSION",
    "FounderBrainChatIntent",
    "FounderBrainChatIntentName",
    "FounderBrainChatIntentValidationError",
    "FounderBrainIntentConfidence",
    "classify_founder_chat_intent",
    "normalize_intent_message",
]
