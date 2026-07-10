"""Compose validated Convera output into a final reply."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Mapping, Sequence

from .base_agent import (
    AgentMetadata,
    AgentResult,
    BaseConveraAgent,
)


class ResponseComposerAgent(BaseConveraAgent):
    """Create safe channel-aware replies from validated output."""

    metadata = AgentMetadata(
        agent_id="convera.response_composer",
        name="Response Composer Agent",
        version="1.0.0",
        description=(
            "Transforms approved specialist output into a stable "
            "user-facing Convera reply while preserving artifacts, "
            "citations, attachments and conversation boundaries."
        ),
        category="response_generation",
        requires_user_approval=False,
        accesses_external_network=False,
        performs_external_actions=False,
    )

    SUPPORTED_CHAT_TYPES = {
        "private",
        "direct",
        "group",
        "project",
        "project_thread",
        "task",
    }

    INTERNAL_KEYS = {
        "findings",
        "issues",
        "warnings",
        "blocking_findings",
        "validation_summary",
        "quality_score",
        "score",
        "production_ready",
        "corrected_output",
        "next_action",
        "required_action",
    }

    def execute(self, payload: Mapping[str, Any]) -> AgentResult:
        validation_error = self._validate_payload(payload)

        if validation_error:
            return AgentResult(
                success=False,
                agent_id=self.metadata.agent_id,
                data={
                    "status": "composition_failed",
                    "should_send": False,
                    "reply": None,
                },
                error=validation_error,
            )

        try:
            composed = self.compose_response(payload)
        except Exception as error:
            return AgentResult(
                success=False,
                agent_id=self.metadata.agent_id,
                data={
                    "status": "composition_failed",
                    "should_send": False,
                    "reply": None,
                },
                error=f"Response composition failed: {error}",
            )

        return AgentResult(
            success=True,
            agent_id=self.metadata.agent_id,
            data=composed,
        )

    def compose_response(
        self,
        payload: Mapping[str, Any],
    ) -> Dict[str, Any]:
        activated = bool(payload.get("activated", False))

        if not activated:
            return {
                "status": "silent",
                "should_send": False,
                "reply": None,
                "reason": "convera_not_activated",
            }

        permission_allowed = bool(
            payload.get("permission_allowed", True)
        )

        if not permission_allowed:
            return self._blocked_response(payload)

        validation_approved = bool(
            payload.get("validation_approved", False)
        )

        if not validation_approved:
            return self._validation_failure_response(
                payload
            )

        validated_response = deepcopy(
            payload.get("validated_response")
        )

        reply = self._build_reply(
            validated_response,
            payload,
        )

        return {
            "status": "ready_to_send",
            "should_send": True,
            "reply": reply,
            "conversation_id": self._text(
                payload.get("conversation_id")
            ),
            "thread_id": self._optional_text(
                payload.get("thread_id")
            ),
            "project_id": self._optional_text(
                payload.get("project_id")
            ),
            "request_id": self._optional_text(
                payload.get("request_id")
            ),
            "trace_id": self._optional_text(
                payload.get("trace_id")
            ),
        }

    def _build_reply(
        self,
        validated_response: Any,
        payload: Mapping[str, Any],
    ) -> Dict[str, Any]:
        chat_type = self._normalized_chat_type(
            payload.get("chat_type")
        )

        content = self._extract_content(
            validated_response
        )

        structured = self._structured_payload(
            validated_response
        )

        artifacts = self._collect_items(
            payload.get("artifacts"),
            structured.get("artifacts"),
            structured.get("artifact"),
        )

        attachments = self._collect_items(
            payload.get("attachments"),
            structured.get("attachments"),
            structured.get("files"),
        )

        citations = self._collect_items(
            payload.get("citations"),
            structured.get("citations"),
        )

        reply_type = self._reply_type(
            structured=structured,
            artifacts=artifacts,
            attachments=attachments,
        )

        metadata = self._safe_metadata(
            structured.get("metadata")
        )

        return {
            "type": reply_type,
            "content": content,
            "chat_type": chat_type,
            "sender": {
                "id": "convera",
                "name": "Convera",
                "role": "assistant",
            },
            "artifacts": artifacts,
            "attachments": attachments,
            "citations": citations,
            "metadata": metadata,
            "reply_to_message_id": self._optional_text(
                payload.get("reply_to_message_id")
            ),
            "mentions": self._normalize_sequence(
                payload.get("mentions")
            ),
        }

    def _blocked_response(
        self,
        payload: Mapping[str, Any],
    ) -> Dict[str, Any]:
        reason = self._text(
            payload.get("permission_reason")
        ) or "permission_denied"

        return {
            "status": "blocked",
            "should_send": True,
            "reply": {
                "type": "system_notice",
                "content": (
                    "I can’t complete that request because "
                    "the required permission is not available."
                ),
                "chat_type": self._normalized_chat_type(
                    payload.get("chat_type")
                ),
                "sender": {
                    "id": "convera",
                    "name": "Convera",
                    "role": "assistant",
                },
                "artifacts": [],
                "attachments": [],
                "citations": [],
                "metadata": {
                    "reason": reason,
                },
                "reply_to_message_id": None,
                "mentions": [],
            },
            "reason": reason,
        }

    def _validation_failure_response(
        self,
        payload: Mapping[str, Any],
    ) -> Dict[str, Any]:
        action = self._text(
            payload.get("required_action")
        ) or "return_to_specialist"

        message = (
            "I couldn’t prepare a reliable response yet. "
            "Please try again."
        )

        if action == "request_user_approval":
            message = (
                "I need your approval before I can continue "
                "with that request."
            )
        elif action == "block_output":
            message = (
                "I can’t provide that response because it "
                "did not pass Convera’s safety checks."
            )

        return {
            "status": "not_ready",
            "should_send": True,
            "reply": {
                "type": "system_notice",
                "content": message,
                "chat_type": self._normalized_chat_type(
                    payload.get("chat_type")
                ),
                "sender": {
                    "id": "convera",
                    "name": "Convera",
                    "role": "assistant",
                },
                "artifacts": [],
                "attachments": [],
                "citations": [],
                "metadata": {
                    "required_action": action,
                },
                "reply_to_message_id": None,
                "mentions": [],
            },
            "required_action": action,
        }

    def _validate_payload(
        self,
        payload: Mapping[str, Any],
    ) -> str | None:
        if not self._text(payload.get("conversation_id")):
            return "conversation_id is required."

        if payload.get("activated") is None:
            return "activated is required."

        if bool(payload.get("validation_approved", False)):
            if payload.get("validated_response") is None:
                return (
                    "validated_response is required when "
                    "validation_approved is true."
                )

        return None

    def _extract_content(self, value: Any) -> str:
        if isinstance(value, str):
            return value.strip()

        if isinstance(value, Mapping):
            for key in (
                "content",
                "text",
                "message",
                "answer",
                "summary",
            ):
                candidate = value.get(key)

                if isinstance(candidate, str):
                    return candidate.strip()

            return ""

        if isinstance(value, Sequence) and not isinstance(
            value,
            (str, bytes),
        ):
            return "\n".join(
                self._text(item)
                for item in value
                if self._text(item)
            )

        return self._text(value)

    @staticmethod
    def _structured_payload(
        value: Any,
    ) -> Dict[str, Any]:
        if not isinstance(value, Mapping):
            return {}

        return {
            key: deepcopy(item)
            for key, item in value.items()
            if key not in ResponseComposerAgent.INTERNAL_KEYS
        }

    def _safe_metadata(
        self,
        value: Any,
    ) -> Dict[str, Any]:
        if not isinstance(value, Mapping):
            return {}

        return {
            str(key): deepcopy(item)
            for key, item in value.items()
            if str(key) not in self.INTERNAL_KEYS
        }

    def _collect_items(
        self,
        *values: Any,
    ) -> list[Any]:
        result: list[Any] = []

        for value in values:
            if value is None:
                continue

            if isinstance(value, Sequence) and not isinstance(
                value,
                (str, bytes),
            ):
                result.extend(deepcopy(list(value)))
                continue

            result.append(deepcopy(value))

        return result

    @staticmethod
    def _reply_type(
        *,
        structured: Mapping[str, Any],
        artifacts: Sequence[Any],
        attachments: Sequence[Any],
    ) -> str:
        declared_type = str(
            structured.get("type")
            or structured.get("output_type")
            or ""
        ).strip()

        if declared_type:
            return declared_type

        if artifacts:
            return "artifact"

        if attachments:
            return "attachment"

        return "message"

    def _normalized_chat_type(
        self,
        value: Any,
    ) -> str:
        chat_type = self._text(value).lower()

        if chat_type in self.SUPPORTED_CHAT_TYPES:
            return chat_type

        return "private"

    @staticmethod
    def _normalize_sequence(value: Any) -> list[Any]:
        if (
            isinstance(value, Sequence)
            and not isinstance(value, (str, bytes))
        ):
            return deepcopy(list(value))

        return []

    @staticmethod
    def _text(value: Any) -> str:
        return str(value or "").strip()

    @staticmethod
    def _optional_text(value: Any) -> str | None:
        text = str(value or "").strip()
        return text or None
