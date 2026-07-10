"""Detect whether Convera has been explicitly invited to respond."""

from __future__ import annotations

import re
from typing import Any, Dict, Mapping

from .base_agent import (
    AgentMetadata,
    AgentResult,
    BaseConveraAgent,
)


class MentionActivationAgent(BaseConveraAgent):
    """Keeps Convera silent until an explicit activation is detected."""

    metadata = AgentMetadata(
        agent_id="convera.mention_activation",
        name="Mention Activation Agent",
        version="1.0.0",
        description=(
            "Detects explicit Convera mentions and determines whether "
            "the AI participant is allowed to respond in a conversation."
        ),
        category="conversation_control",
        requires_user_approval=False,
        accesses_external_network=False,
        performs_external_actions=False,
    )

    _EXPLICIT_PATTERNS = (
        re.compile(
            r"(?<![\w])@convera(?![\w])",
            re.IGNORECASE,
        ),
        re.compile(
            r"^\s*convera\s*[,:\-]",
            re.IGNORECASE,
        ),
        re.compile(
            r"\bask\s+convera\b",
            re.IGNORECASE,
        ),
        re.compile(
            r"\bcan\s+convera\b",
            re.IGNORECASE,
        ),
    )

    _MODES = {
        "mention_only",
        "smart_assist",
        "always_active",
        "disabled",
    }

    def execute(self, payload: Mapping[str, Any]) -> AgentResult:
        message = str(payload.get("message") or "")
        mode = str(
            payload.get("activation_mode")
            or "mention_only"
        ).strip().lower()

        sender_is_convera = bool(
            payload.get("sender_is_convera", False)
        )

        if mode not in self._MODES:
            return AgentResult(
                success=False,
                agent_id=self.metadata.agent_id,
                data={
                    "activated": False,
                    "reason": "invalid_activation_mode",
                },
                error=f"Unsupported activation mode: {mode}",
            )

        decision = self.evaluate(
            message=message,
            mode=mode,
            sender_is_convera=sender_is_convera,
        )

        return AgentResult(
            success=True,
            agent_id=self.metadata.agent_id,
            data=decision,
        )

    def evaluate(
        self,
        *,
        message: str,
        mode: str = "mention_only",
        sender_is_convera: bool = False,
    ) -> Dict[str, Any]:
        normalized = message.strip()

        if sender_is_convera:
            return {
                "activated": False,
                "reason": "self_message",
                "activation_mode": mode,
                "matched_trigger": None,
            }

        if mode == "disabled":
            return {
                "activated": False,
                "reason": "agent_disabled",
                "activation_mode": mode,
                "matched_trigger": None,
            }

        if mode == "always_active":
            return {
                "activated": bool(normalized),
                "reason": (
                    "always_active"
                    if normalized
                    else "empty_message"
                ),
                "activation_mode": mode,
                "matched_trigger": "always_active",
            }

        matched_trigger = self._match_trigger(normalized)

        if matched_trigger:
            return {
                "activated": True,
                "reason": "explicit_invocation",
                "activation_mode": mode,
                "matched_trigger": matched_trigger,
            }

        if mode == "smart_assist":
            smart_trigger = self._smart_assist_trigger(normalized)

            if smart_trigger:
                return {
                    "activated": True,
                    "reason": "smart_assist_trigger",
                    "activation_mode": mode,
                    "matched_trigger": smart_trigger,
                }

        return {
            "activated": False,
            "reason": (
                "empty_message"
                if not normalized
                else "no_explicit_invocation"
            ),
            "activation_mode": mode,
            "matched_trigger": None,
        }

    def _match_trigger(self, message: str) -> str | None:
        for pattern in self._EXPLICIT_PATTERNS:
            match = pattern.search(message)

            if match:
                return match.group(0)

        return None

    @staticmethod
    def _smart_assist_trigger(message: str) -> str | None:
        lowered = message.lower()

        triggers = {
            "summarize this conversation": "summary_request",
            "what did i miss": "catch_up_request",
            "create a task": "task_request",
            "turn this into a task": "task_request",
        }

        for phrase, trigger in triggers.items():
            if phrase in lowered:
                return trigger

        return None