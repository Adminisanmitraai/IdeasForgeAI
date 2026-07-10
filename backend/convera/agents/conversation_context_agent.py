"""Conversation working-memory builder for Convera."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Mapping, Sequence

from .base_agent import (
    AgentMetadata,
    AgentResult,
    BaseConveraAgent,
)


class ConversationContextAgent(BaseConveraAgent):
    """Build a bounded, isolated context snapshot for one chat thread."""

    metadata = AgentMetadata(
        agent_id="convera.conversation_context",
        name="Conversation Context Agent",
        version="1.0.0",
        description=(
            "Builds a safe and bounded working-memory snapshot from "
            "messages, participants, files, decisions, tasks and pending "
            "questions while preserving conversation and project isolation."
        ),
        category="conversation_intelligence",
        requires_user_approval=False,
        accesses_external_network=False,
        performs_external_actions=False,
    )

    DEFAULT_MESSAGE_LIMIT = 20
    MAX_MESSAGE_LIMIT = 100
    MAX_MESSAGE_LENGTH = 8000
    MAX_PARTICIPANTS = 100
    MAX_FILES = 50

    _DECISION_PATTERNS = (
        re.compile(
            r"\b(?:approved|confirmed|final decision)\b[:\s-]*(.+)",
            re.IGNORECASE,
        ),
        re.compile(
            r"\bwe(?:'ll| will)\s+(?:use|choose|launch|ship)\s+(.+)",
            re.IGNORECASE,
        ),
        re.compile(
            r"\blet(?:'s| us)\s+(?:use|choose|go with)\s+(.+)",
            re.IGNORECASE,
        ),
    )

    _TASK_PATTERN = re.compile(
        r"\b(?:please|need to|must|should)\s+(.+?)(?:[.!?]|$)",
        re.IGNORECASE,
    )

    def execute(self, payload: Mapping[str, Any]) -> AgentResult:
        validation_error = self._validate_payload(payload)

        if validation_error:
            return AgentResult(
                success=False,
                agent_id=self.metadata.agent_id,
                data={},
                error=validation_error,
            )

        context = self.build_context(payload)

        return AgentResult(
            success=True,
            agent_id=self.metadata.agent_id,
            data={
                "conversation_state": context,
            },
        )

    def build_context(
        self,
        payload: Mapping[str, Any],
    ) -> Dict[str, Any]:
        conversation_id = str(
            payload["conversation_id"]
        ).strip()

        project_id = self._optional_text(
            payload.get("project_id")
        )

        thread_id = self._optional_text(
            payload.get("thread_id")
        ) or conversation_id

        chat_type = str(
            payload.get("chat_type") or "private"
        ).strip().lower()

        message_limit = self._normalize_limit(
            payload.get("message_limit")
        )

        participants = self._normalize_participants(
            payload.get("participants")
        )

        messages = self._normalize_messages(
            payload.get("messages"),
            conversation_id=conversation_id,
            project_id=project_id,
            thread_id=thread_id,
            limit=message_limit,
        )

        current_message = self._normalize_current_message(
            payload,
            conversation_id=conversation_id,
            project_id=project_id,
            thread_id=thread_id,
        )

        if current_message:
            messages.append(current_message)
            messages = messages[-message_limit:]

        files = self._normalize_files(
            payload.get("files")
        )

        decisions = self._extract_decisions(messages)
        pending_questions = self._extract_questions(messages)
        task_candidates = self._extract_task_candidates(messages)

        topic = self._derive_topic(
            messages,
            fallback=payload.get("topic"),
        )

        token_estimate = self._estimate_tokens(messages)

        return {
            "conversation_id": conversation_id,
            "thread_id": thread_id,
            "project_id": project_id,
            "chat_type": chat_type,
            "participants": participants,
            "recent_messages": messages,
            "message_count": len(messages),
            "message_limit": message_limit,
            "token_estimate": token_estimate,
            "topic": topic,
            "decisions": decisions,
            "pending_questions": pending_questions,
            "task_candidates": task_candidates,
            "files": files,
            "isolation": {
                "conversation_id": conversation_id,
                "thread_id": thread_id,
                "project_id": project_id,
                "cross_thread_messages_rejected": True,
                "cross_project_messages_rejected": True,
            },
            "generated_at": datetime.now(
                timezone.utc
            ).isoformat(),
        }

    def _validate_payload(
        self,
        payload: Mapping[str, Any],
    ) -> str | None:
        conversation_id = str(
            payload.get("conversation_id") or ""
        ).strip()

        if not conversation_id:
            return "conversation_id is required."

        chat_type = str(
            payload.get("chat_type") or "private"
        ).strip().lower()

        if chat_type not in {"private", "group", "project"}:
            return (
                "chat_type must be private, group or project."
            )

        participants = payload.get("participants")

        if participants is not None and not isinstance(
            participants,
            Sequence,
        ):
            return "participants must be a sequence."

        messages = payload.get("messages")

        if messages is not None and not isinstance(
            messages,
            Sequence,
        ):
            return "messages must be a sequence."

        return None

    def _normalize_messages(
        self,
        raw_messages: Any,
        *,
        conversation_id: str,
        project_id: str | None,
        thread_id: str,
        limit: int,
    ) -> List[Dict[str, Any]]:
        if not isinstance(raw_messages, Sequence):
            return []

        normalized: List[Dict[str, Any]] = []

        for index, item in enumerate(raw_messages):
            if not isinstance(item, Mapping):
                continue

            item_conversation = self._optional_text(
                item.get("conversation_id")
            )

            if (
                item_conversation
                and item_conversation != conversation_id
            ):
                continue

            item_thread = self._optional_text(
                item.get("thread_id")
            )

            if item_thread and item_thread != thread_id:
                continue

            item_project = self._optional_text(
                item.get("project_id")
            )

            if item_project and item_project != project_id:
                continue

            text = self._clean_text(
                item.get("text") or item.get("message")
            )

            if not text:
                continue

            normalized.append(
                {
                    "message_id": self._optional_text(
                        item.get("message_id")
                    ) or f"history-{index + 1}",
                    "sender_id": self._optional_text(
                        item.get("sender_id")
                        or item.get("sender")
                    ) or "unknown",
                    "text": text,
                    "timestamp": self._optional_text(
                        item.get("timestamp")
                    ),
                    "conversation_id": conversation_id,
                    "thread_id": thread_id,
                    "project_id": project_id,
                }
            )

        return normalized[-limit:]

    def _normalize_current_message(
        self,
        payload: Mapping[str, Any],
        *,
        conversation_id: str,
        project_id: str | None,
        thread_id: str,
    ) -> Dict[str, Any] | None:
        text = self._clean_text(
            payload.get("message")
        )

        if not text:
            return None

        return {
            "message_id": self._optional_text(
                payload.get("message_id")
            ) or "current",
            "sender_id": self._optional_text(
                payload.get("sender_id")
                or payload.get("sender")
            ) or "unknown",
            "text": text,
            "timestamp": self._optional_text(
                payload.get("timestamp")
            ),
            "conversation_id": conversation_id,
            "thread_id": thread_id,
            "project_id": project_id,
        }

    def _normalize_participants(
        self,
        raw_participants: Any,
    ) -> List[Dict[str, Any]]:
        if not isinstance(raw_participants, Sequence):
            return []

        normalized: List[Dict[str, Any]] = []
        seen: set[str] = set()

        for item in raw_participants[:self.MAX_PARTICIPANTS]:
            if isinstance(item, str):
                participant_id = item.strip()

                if not participant_id:
                    continue

                participant = {
                    "participant_id": participant_id,
                    "display_name": participant_id,
                    "role": "member",
                }

            elif isinstance(item, Mapping):
                participant_id = self._optional_text(
                    item.get("participant_id")
                    or item.get("user_id")
                    or item.get("id")
                )

                if not participant_id:
                    continue

                participant = {
                    "participant_id": participant_id,
                    "display_name": self._optional_text(
                        item.get("display_name")
                        or item.get("name")
                    ) or participant_id,
                    "role": self._optional_text(
                        item.get("role")
                    ) or "member",
                }

            else:
                continue

            if participant_id in seen:
                continue

            seen.add(participant_id)
            normalized.append(participant)

        return normalized

    def _normalize_files(
        self,
        raw_files: Any,
    ) -> List[Dict[str, Any]]:
        if not isinstance(raw_files, Sequence):
            return []

        normalized: List[Dict[str, Any]] = []

        for index, item in enumerate(
            raw_files[:self.MAX_FILES]
        ):
            if isinstance(item, str):
                normalized.append(
                    {
                        "file_id": f"file-{index + 1}",
                        "name": item.strip(),
                        "mime_type": None,
                    }
                )

            elif isinstance(item, Mapping):
                name = self._optional_text(
                    item.get("name")
                    or item.get("filename")
                )

                if not name:
                    continue

                normalized.append(
                    {
                        "file_id": self._optional_text(
                            item.get("file_id")
                            or item.get("id")
                        ) or f"file-{index + 1}",
                        "name": name,
                        "mime_type": self._optional_text(
                            item.get("mime_type")
                        ),
                    }
                )

        return normalized

    def _extract_decisions(
        self,
        messages: Sequence[Mapping[str, Any]],
    ) -> List[Dict[str, Any]]:
        decisions: List[Dict[str, Any]] = []

        for message in messages:
            text = str(message.get("text") or "")

            for pattern in self._DECISION_PATTERNS:
                match = pattern.search(text)

                if not match:
                    continue

                decision_text = (
                    match.group(1).strip()
                    if match.lastindex
                    else match.group(0).strip()
                )

                decisions.append(
                    {
                        "text": decision_text,
                        "source_message_id": message.get(
                            "message_id"
                        ),
                        "sender_id": message.get("sender_id"),
                    }
                )
                break

        return decisions[-10:]

    def _extract_questions(
        self,
        messages: Sequence[Mapping[str, Any]],
    ) -> List[Dict[str, Any]]:
        questions: List[Dict[str, Any]] = []

        for message in messages:
            text = str(message.get("text") or "").strip()

            if not text.endswith("?"):
                continue

            questions.append(
                {
                    "text": text,
                    "source_message_id": message.get(
                        "message_id"
                    ),
                    "sender_id": message.get("sender_id"),
                }
            )

        return questions[-10:]

    def _extract_task_candidates(
        self,
        messages: Sequence[Mapping[str, Any]],
    ) -> List[Dict[str, Any]]:
        tasks: List[Dict[str, Any]] = []

        for message in messages:
            text = str(message.get("text") or "")
            match = self._TASK_PATTERN.search(text)

            if not match:
                continue

            tasks.append(
                {
                    "text": match.group(1).strip(),
                    "source_message_id": message.get(
                        "message_id"
                    ),
                    "suggested_owner": message.get(
                        "sender_id"
                    ),
                    "status": "candidate",
                }
            )

        return tasks[-10:]

    def _derive_topic(
        self,
        messages: Sequence[Mapping[str, Any]],
        *,
        fallback: Any,
    ) -> str | None:
        explicit = self._optional_text(fallback)

        if explicit:
            return explicit

        if not messages:
            return None

        latest = str(messages[-1].get("text") or "")
        words = latest.split()

        if not words:
            return None

        return " ".join(words[:12])

    def _estimate_tokens(
        self,
        messages: Sequence[Mapping[str, Any]],
    ) -> int:
        character_count = sum(
            len(str(message.get("text") or ""))
            for message in messages
        )

        return max(0, round(character_count / 4))

    def _normalize_limit(self, value: Any) -> int:
        try:
            limit = int(value)
        except (TypeError, ValueError):
            limit = self.DEFAULT_MESSAGE_LIMIT

        return max(
            1,
            min(limit, self.MAX_MESSAGE_LIMIT),
        )

    def _clean_text(self, value: Any) -> str:
        text = str(value or "").strip()
        return text[:self.MAX_MESSAGE_LENGTH]

    @staticmethod
    def _optional_text(value: Any) -> str | None:
        text = str(value or "").strip()
        return text or None
