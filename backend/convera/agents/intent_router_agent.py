"""Intent classification and specialist routing for Convera."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Mapping, Sequence, Tuple

from .base_agent import (
    AgentMetadata,
    AgentResult,
    BaseConveraAgent,
)


class IntentRouterAgent(BaseConveraAgent):
    """Classify a message and select the appropriate Convera capability."""

    metadata = AgentMetadata(
        agent_id="convera.intent_router",
        name="Intent Router Agent",
        version="1.0.0",
        description=(
            "Classifies activated Convera requests into safe structured "
            "intents and selects the appropriate specialist capability "
            "without executing external actions."
        ),
        category="conversation_intelligence",
        requires_user_approval=False,
        accesses_external_network=False,
        performs_external_actions=False,
    )

    DEFAULT_INTENT = "general_question"

    INTENT_AGENT_MAP = {
        "general_question": "convera.response_composer",
        "summarize": "convera.summarization",
        "create_task": "convera.task_extraction",
        "create_reminder": "convera.reminder",
        "schedule_meeting": "convera.scheduling",
        "create_document": "convera.document_creation",
        "create_presentation": "convera.presentation",
        "create_logo": "convera.visual_design",
        "create_image": "convera.image_generation",
        "analyze_file": "convera.file_intelligence",
        "research_web": "convera.web_research",
        "translate": "convera.translation",
        "draft_reply": "convera.smart_reply",
        "project_update": "convera.project_workspace",
        "extract_decisions": "convera.decision_extraction",
        "find_information": "convera.knowledge_search",
    }

    _RULES: Tuple[Tuple[str, Tuple[str, ...]], ...] = (
        (
            "summarize",
            (
                r"\bsummari[sz]e\b",
                r"\bsummary\b",
                r"\bwhat did i miss\b",
                r"\bcatch me up\b",
                r"\brecap\b",
            ),
        ),
        (
            "create_task",
            (
                r"\bcreate (?:a )?task\b",
                r"\badd (?:a )?task\b",
                r"\bturn .* into (?:a )?task\b",
                r"\bassign .* task\b",
                r"\baction item\b",
            ),
        ),
        (
            "create_reminder",
            (
                r"\bremind me\b",
                r"\bset (?:a )?reminder\b",
                r"\bremind us\b",
                r"\bfollow up (?:on|at|in)\b",
            ),
        ),
        (
            "schedule_meeting",
            (
                r"\bschedule (?:a )?meeting\b",
                r"\bbook (?:a )?meeting\b",
                r"\bset up (?:a )?(?:call|meeting)\b",
                r"\bfind (?:a )?time\b",
            ),
        ),
        (
            "create_presentation",
            (
                r"\bcreate (?:a )?(?:presentation|deck|ppt)\b",
                r"\bmake (?:a )?(?:presentation|deck|ppt)\b",
                r"\bslides?\b",
            ),
        ),
        (
            "create_document",
            (
                r"\bcreate (?:a )?(?:document|report|proposal|letter)\b",
                r"\bmake (?:a )?(?:document|report|proposal)\b",
                r"\bturn .* into (?:a )?(?:document|report)\b",
            ),
        ),
        (
            "create_logo",
            (
                r"\bcreate (?:a )?logo\b",
                r"\bdesign (?:a )?logo\b",
                r"\blogo concept\b",
            ),
        ),
        (
            "create_image",
            (
                r"\bcreate (?:an? )?image\b",
                r"\bgenerate (?:an? )?image\b",
                r"\bedit (?:this |the )?image\b",
                r"\bremove (?:the )?background\b",
            ),
        ),
        (
            "analyze_file",
            (
                r"\banaly[sz]e (?:this |the )?(?:file|pdf|document)\b",
                r"\bread (?:this |the )?(?:file|pdf|document)\b",
                r"\bcompare (?:these |the )?(?:files|documents)\b",
            ),
        ),
        (
            "research_web",
            (
                r"\bresearch\b",
                r"\bsearch the web\b",
                r"\blook up\b",
                r"\bfind current\b",
                r"\blatest information\b",
            ),
        ),
        (
            "translate",
            (
                r"\btranslate\b",
                r"\bin (?:english|hindi|bengali|bangla|spanish|french)\b",
            ),
        ),
        (
            "draft_reply",
            (
                r"\bdraft (?:a )?reply\b",
                r"\bwrite (?:a )?reply\b",
                r"\brespond to\b",
                r"\bmake this (?:friendlier|shorter|professional)\b",
            ),
        ),
        (
            "project_update",
            (
                r"\bproject update\b",
                r"\bproject status\b",
                r"\bwhat changed in .* project\b",
                r"\bupdate the project\b",
            ),
        ),
        (
            "extract_decisions",
            (
                r"\bwhat did we decide\b",
                r"\bextract (?:the )?decisions\b",
                r"\blist (?:the )?decisions\b",
                r"\bfinal decisions?\b",
            ),
        ),
        (
            "find_information",
            (
                r"\bfind (?:the )?(?:message|file|decision|task)\b",
                r"\bsearch (?:this |the )?(?:chat|project)\b",
                r"\bwhere did we discuss\b",
            ),
        ),
    )

    _COMPILED_RULES = tuple(
        (
            intent,
            tuple(
                re.compile(pattern, re.IGNORECASE)
                for pattern in patterns
            ),
        )
        for intent, patterns in _RULES
    )

    def execute(self, payload: Mapping[str, Any]) -> AgentResult:
        message = str(payload.get("message") or "").strip()

        if not message:
            return AgentResult(
                success=False,
                agent_id=self.metadata.agent_id,
                data={},
                error="message is required.",
            )

        activated = payload.get("activated")

        if activated is False:
            return AgentResult(
                success=True,
                agent_id=self.metadata.agent_id,
                data={
                    "should_route": False,
                    "reason": "convera_not_activated",
                    "primary_intent": None,
                    "secondary_intents": [],
                    "target_agent_id": None,
                    "confidence": 0.0,
                },
            )

        result = self.classify(
            message=message,
            context=payload.get("context"),
        )

        return AgentResult(
            success=True,
            agent_id=self.metadata.agent_id,
            data=result,
        )

    def classify(
        self,
        *,
        message: str,
        context: Any = None,
    ) -> Dict[str, Any]:
        normalized = self._strip_activation_phrase(message)
        matches = self._score_intents(normalized)

        if not matches:
            primary_intent = self.DEFAULT_INTENT
            secondary_intents: List[str] = []
            confidence = 0.55
            evidence: List[str] = []
        else:
            ordered = sorted(
                matches.items(),
                key=lambda item: (-item[1]["score"], item[0]),
            )

            primary_intent = ordered[0][0]
            secondary_intents = [
                intent
                for intent, details in ordered[1:]
                if details["score"] > 0
            ][:3]

            strongest_score = ordered[0][1]["score"]
            confidence = min(
                0.99,
                0.65 + (strongest_score * 0.1),
            )

            evidence = ordered[0][1]["evidence"]

        return {
            "should_route": True,
            "reason": "intent_classified",
            "primary_intent": primary_intent,
            "secondary_intents": secondary_intents,
            "target_agent_id": self.INTENT_AGENT_MAP[
                primary_intent
            ],
            "confidence": round(confidence, 2),
            "evidence": evidence,
            "normalized_request": normalized,
            "requires_approval": self._requires_approval(
                primary_intent
            ),
            "context_available": isinstance(context, Mapping),
        }

    def _score_intents(
        self,
        message: str,
    ) -> Dict[str, Dict[str, Any]]:
        matches: Dict[str, Dict[str, Any]] = {}

        for intent, patterns in self._COMPILED_RULES:
            evidence: List[str] = []

            for pattern in patterns:
                match = pattern.search(message)

                if match:
                    evidence.append(match.group(0))

            if evidence:
                matches[intent] = {
                    "score": len(evidence),
                    "evidence": evidence[:3],
                }

        return matches

    @staticmethod
    def _strip_activation_phrase(message: str) -> str:
        cleaned = re.sub(
            r"^\s*@convera\s*[,:\-]?\s*",
            "",
            message,
            flags=re.IGNORECASE,
        )

        cleaned = re.sub(
            r"^\s*convera\s*[,:\-]\s*",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )

        return cleaned.strip()

    @staticmethod
    def _requires_approval(intent: str) -> bool:
        return intent in {
            "create_task",
            "create_reminder",
            "schedule_meeting",
        }
