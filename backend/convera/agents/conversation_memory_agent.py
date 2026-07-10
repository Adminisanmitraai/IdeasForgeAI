"""Permission-aware conversation memory for Convera."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Mapping, Sequence

from .base_agent import (
    AgentMetadata,
    AgentResult,
    BaseConveraAgent,
)


class ConversationMemoryAgent(BaseConveraAgent):
    """Manage bounded memories without crossing chat or project boundaries."""

    metadata = AgentMetadata(
        agent_id="convera.conversation_memory",
        name="Conversation Memory Agent",
        version="1.0.0",
        description=(
            "Creates, retrieves and removes permission-approved memories "
            "while enforcing conversation isolation, project isolation, "
            "bounded retention and sensitive-data protection."
        ),
        category="conversation_intelligence",
        requires_user_approval=False,
        accesses_external_network=False,
        performs_external_actions=False,
    )

    VALID_OPERATIONS = {
        "remember",
        "retrieve",
        "forget",
        "list",
    }

    VALID_MEMORY_TYPES = {
        "preference",
        "decision",
        "fact",
        "task_context",
        "project_context",
        "participant_preference",
    }

    SENSITIVE_KEYS = {
        "password",
        "passcode",
        "api_key",
        "secret",
        "token",
        "access_token",
        "refresh_token",
        "credit_card",
        "cvv",
        "private_key",
        "credential",
    }

    MAX_MEMORIES = 200
    MAX_VALUE_LENGTH = 4000

    def execute(self, payload: Mapping[str, Any]) -> AgentResult:
        validation_error = self._validate(payload)

        if validation_error:
            return AgentResult(
                success=False,
                agent_id=self.metadata.agent_id,
                data={},
                error=validation_error,
            )

        operation = str(payload["operation"]).strip().lower()

        if not bool(payload.get("permission_granted", False)):
            return AgentResult(
                success=True,
                agent_id=self.metadata.agent_id,
                data={
                    "allowed": False,
                    "operation": operation,
                    "reason": "permission_required",
                    "memories": self._normalize_memories(
                        payload.get("memories")
                    ),
                },
            )

        if operation == "remember":
            result = self._remember(payload)
        elif operation == "retrieve":
            result = self._retrieve(payload)
        elif operation == "forget":
            result = self._forget(payload)
        else:
            result = self._list(payload)

        return AgentResult(
            success=True,
            agent_id=self.metadata.agent_id,
            data=result,
        )

    def _remember(
        self,
        payload: Mapping[str, Any],
    ) -> Dict[str, Any]:
        memories = self._normalize_memories(
            payload.get("memories")
        )

        key = self._text(payload.get("key"))
        value = self._text(payload.get("value"))
        memory_type = self._text(
            payload.get("memory_type")
        ).lower()

        if self._contains_sensitive_key(key):
            return {
                "allowed": False,
                "operation": "remember",
                "reason": "sensitive_memory_rejected",
                "memories": memories,
            }

        if not bool(payload.get("retention_approved", False)):
            return {
                "allowed": False,
                "operation": "remember",
                "reason": "retention_approval_required",
                "memories": memories,
            }

        scope = self._scope(payload)

        filtered = [
            item
            for item in memories
            if not (
                item["key"] == key
                and self._same_scope(item, scope)
            )
        ]

        memory = {
            "memory_id": self._text(
                payload.get("memory_id")
            ) or self._memory_id(scope, key),
            "key": key,
            "value": value[:self.MAX_VALUE_LENGTH],
            "memory_type": memory_type,
            "conversation_id": scope["conversation_id"],
            "project_id": scope["project_id"],
            "user_id": scope["user_id"],
            "created_at": self._text(
                payload.get("created_at")
            ) or datetime.now(timezone.utc).isoformat(),
            "source_message_id": self._optional_text(
                payload.get("source_message_id")
            ),
        }

        filtered.append(memory)
        filtered = filtered[-self.MAX_MEMORIES:]

        return {
            "allowed": True,
            "operation": "remember",
            "reason": "memory_saved",
            "memory": memory,
            "memories": filtered,
            "count": len(filtered),
        }

    def _retrieve(
        self,
        payload: Mapping[str, Any],
    ) -> Dict[str, Any]:
        memories = self._normalize_memories(
            payload.get("memories")
        )
        scope = self._scope(payload)
        key = self._optional_text(payload.get("key"))
        memory_type = self._optional_text(
            payload.get("memory_type")
        )

        matches = [
            item
            for item in memories
            if self._same_scope(item, scope)
            and (not key or item["key"] == key)
            and (
                not memory_type
                or item["memory_type"] == memory_type
            )
        ]

        return {
            "allowed": True,
            "operation": "retrieve",
            "reason": "memory_retrieved",
            "matches": matches,
            "count": len(matches),
            "memories": memories,
        }

    def _forget(
        self,
        payload: Mapping[str, Any],
    ) -> Dict[str, Any]:
        memories = self._normalize_memories(
            payload.get("memories")
        )
        scope = self._scope(payload)
        memory_id = self._optional_text(
            payload.get("memory_id")
        )
        key = self._optional_text(payload.get("key"))

        if not memory_id and not key:
            return {
                "allowed": False,
                "operation": "forget",
                "reason": "memory_id_or_key_required",
                "memories": memories,
            }

        removed: List[Dict[str, Any]] = []
        retained: List[Dict[str, Any]] = []

        for item in memories:
            target = (
                self._same_scope(item, scope)
                and (
                    (memory_id and item["memory_id"] == memory_id)
                    or (key and item["key"] == key)
                )
            )

            if target:
                removed.append(item)
            else:
                retained.append(item)

        return {
            "allowed": True,
            "operation": "forget",
            "reason": "memory_removed",
            "removed": removed,
            "removed_count": len(removed),
            "memories": retained,
        }

    def _list(
        self,
        payload: Mapping[str, Any],
    ) -> Dict[str, Any]:
        memories = self._normalize_memories(
            payload.get("memories")
        )
        scope = self._scope(payload)

        scoped = [
            item
            for item in memories
            if self._same_scope(item, scope)
        ]

        return {
            "allowed": True,
            "operation": "list",
            "reason": "memory_listed",
            "matches": scoped,
            "count": len(scoped),
            "memories": memories,
        }

    def _validate(
        self,
        payload: Mapping[str, Any],
    ) -> str | None:
        operation = self._text(
            payload.get("operation")
        ).lower()

        if operation not in self.VALID_OPERATIONS:
            return (
                "operation must be remember, retrieve, "
                "forget or list."
            )

        if not self._text(payload.get("conversation_id")):
            return "conversation_id is required."

        if not self._text(payload.get("user_id")):
            return "user_id is required."

        if operation == "remember":
            if not self._text(payload.get("key")):
                return "key is required for remember."

            if not self._text(payload.get("value")):
                return "value is required for remember."

            memory_type = self._text(
                payload.get("memory_type")
            ).lower()

            if memory_type not in self.VALID_MEMORY_TYPES:
                return "memory_type is invalid."

        return None

    def _normalize_memories(
        self,
        raw: Any,
    ) -> List[Dict[str, Any]]:
        if (
            not isinstance(raw, Sequence)
            or isinstance(raw, (str, bytes))
        ):
            return []

        normalized: List[Dict[str, Any]] = []

        for item in raw[-self.MAX_MEMORIES:]:
            if not isinstance(item, Mapping):
                continue

            key = self._text(item.get("key"))
            value = self._text(item.get("value"))

            if not key or not value:
                continue

            if self._contains_sensitive_key(key):
                continue

            normalized.append(
                {
                    "memory_id": self._text(
                        item.get("memory_id")
                    ),
                    "key": key,
                    "value": value[:self.MAX_VALUE_LENGTH],
                    "memory_type": self._text(
                        item.get("memory_type")
                    ).lower(),
                    "conversation_id": self._text(
                        item.get("conversation_id")
                    ),
                    "project_id": self._optional_text(
                        item.get("project_id")
                    ),
                    "user_id": self._text(
                        item.get("user_id")
                    ),
                    "created_at": self._optional_text(
                        item.get("created_at")
                    ),
                    "source_message_id": self._optional_text(
                        item.get("source_message_id")
                    ),
                }
            )

        return normalized

    def _scope(
        self,
        payload: Mapping[str, Any],
    ) -> Dict[str, str | None]:
        return {
            "conversation_id": self._text(
                payload.get("conversation_id")
            ),
            "project_id": self._optional_text(
                payload.get("project_id")
            ),
            "user_id": self._text(
                payload.get("user_id")
            ),
        }

    @staticmethod
    def _same_scope(
        memory: Mapping[str, Any],
        scope: Mapping[str, Any],
    ) -> bool:
        return (
            memory.get("conversation_id")
            == scope.get("conversation_id")
            and memory.get("project_id")
            == scope.get("project_id")
            and memory.get("user_id")
            == scope.get("user_id")
        )

    def _contains_sensitive_key(self, key: str) -> bool:
        normalized = key.lower().replace("-", "_").replace(" ", "_")

        return any(
            sensitive in normalized
            for sensitive in self.SENSITIVE_KEYS
        )

    @staticmethod
    def _memory_id(
        scope: Mapping[str, Any],
        key: str,
    ) -> str:
        project = scope.get("project_id") or "none"

        return (
            f"{scope['conversation_id']}::"
            f"{project}::{scope['user_id']}::{key}"
        )

    @staticmethod
    def _text(value: Any) -> str:
        return str(value or "").strip()

    @staticmethod
    def _optional_text(value: Any) -> str | None:
        text = str(value or "").strip()
        return text or None
