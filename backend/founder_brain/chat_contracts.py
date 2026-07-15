from __future__ import annotations

from hashlib import sha256
from typing import Final, Literal

from pydantic import BaseModel, ConfigDict, Field

CHAT_MESSAGE_MAX_LENGTH: Final[int] = 4000
DEFAULT_CHAT_SESSION_ID: Final[str] = "founder-brain-default"
NON_EXECUTING_RESPONSE_TEXT: Final[str] = (
    "Founder Brain received the message in non-executing mode."
)


class FounderBrainChatContractValidationError(ValueError):
    """Raised when a Founder Brain chat contract is invalid."""


def normalize_chat_message(value: object) -> str:
    """Return validated and normalized founder chat input."""

    if not isinstance(value, str):
        raise FounderBrainChatContractValidationError(
            "message must be a string"
        )

    normalized = " ".join(value.split())

    if not normalized:
        raise FounderBrainChatContractValidationError(
            "message must not be empty"
        )

    if len(normalized) > CHAT_MESSAGE_MAX_LENGTH:
        raise FounderBrainChatContractValidationError(
            f"message must not exceed {CHAT_MESSAGE_MAX_LENGTH} characters"
        )

    return normalized


def normalize_chat_session_id(value: object) -> str:
    """Return a safe local session identifier."""

    if value is None:
        return DEFAULT_CHAT_SESSION_ID

    if not isinstance(value, str):
        raise FounderBrainChatContractValidationError(
            "session_id must be a string or null"
        )

    normalized = value.strip()

    if not normalized:
        return DEFAULT_CHAT_SESSION_ID

    if len(normalized) > 128:
        raise FounderBrainChatContractValidationError(
            "session_id must not exceed 128 characters"
        )

    return normalized


def deterministic_chat_message_id(
    *,
    session_id: str,
    message: str,
) -> str:
    """Create a deterministic local identifier without persistence."""

    digest = sha256(
        f"{session_id}\n{message}".encode("utf-8")
    ).hexdigest()[:24]

    return f"fbmsg-{digest}"


def build_non_executing_chat_contract(
    *,
    message: object,
    session_id: object = None,
    generated_at: str,
) -> dict[str, object]:
    """Build a deterministic non-executing message result."""

    normalized_message = normalize_chat_message(message)
    normalized_session_id = normalize_chat_session_id(session_id)

    return {
        "message_id": deterministic_chat_message_id(
            session_id=normalized_session_id,
            message=normalized_message,
        ),
        "session_id": normalized_session_id,
        "input": {
            "text": normalized_message,
        },
        "response": {
            "text": NON_EXECUTING_RESPONSE_TEXT,
            "mode": "non_executing",
        },
        "execution": {
            "requested": False,
            "performed": False,
            "approval_required": False,
            "worker_called": False,
        },
        "read_only": True,
        "generated_at": generated_at,
    }



class FounderBrainChatRequest(BaseModel):
    """Validated input accepted by the non-executing chat endpoint."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    message: str = Field(min_length=1, max_length=CHAT_MESSAGE_MAX_LENGTH)
    session_id: str | None = Field(default=None, max_length=128)


class FounderBrainChatInput(BaseModel):
    """Normalized founder message included in the response contract."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    text: str


class FounderBrainChatReply(BaseModel):
    """Deterministic local acknowledgement with no orchestration."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    text: str
    mode: Literal["non_executing"] = "non_executing"


class FounderBrainChatExecutionState(BaseModel):
    """Explicit proof that no execution boundary was crossed."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    requested: Literal[False] = False
    performed: Literal[False] = False
    approval_required: Literal[False] = False
    worker_called: Literal[False] = False


class FounderBrainChatContract(BaseModel):
    """Complete immutable non-executing Founder Brain message result."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    message_id: str
    session_id: str
    input: FounderBrainChatInput
    response: FounderBrainChatReply
    execution: FounderBrainChatExecutionState
    read_only: Literal[True] = True
    generated_at: str


__all__ = [
    "CHAT_MESSAGE_MAX_LENGTH",
    "DEFAULT_CHAT_SESSION_ID",
    "FounderBrainChatContract",
    "FounderBrainChatContractValidationError",
    "FounderBrainChatExecutionState",
    "FounderBrainChatInput",
    "FounderBrainChatReply",
    "FounderBrainChatRequest",
    "NON_EXECUTING_RESPONSE_TEXT",
    "build_non_executing_chat_contract",
    "deterministic_chat_message_id",
    "normalize_chat_message",
    "normalize_chat_session_id",
]
