"""Controlled orchestration pipeline for Convera."""

from __future__ import annotations

from typing import Any, Dict, Mapping

from .base_agent import (
    AgentMetadata,
    AgentResult,
    BaseConveraAgent,
)
from .conversation_context_agent import (
    ConversationContextAgent,
)
from .conversation_memory_agent import (
    ConversationMemoryAgent,
)
from .intent_router_agent import IntentRouterAgent
from .mention_activation_agent import (
    MentionActivationAgent,
)
from .permission_privacy_agent import (
    PermissionPrivacyAgent,
)
from .quality_validator_agent import (
    QualityValidatorAgent,
)


class ConveraOrchestratorAgent(BaseConveraAgent):
    """Coordinate Convera's foundational agents through one safe pipeline."""

    metadata = AgentMetadata(
        agent_id="convera.orchestrator",
        name="Convera Orchestrator Agent",
        version="1.0.0",
        description=(
            "Coordinates mention activation, conversation context, "
            "intent routing, privacy authorization and approved memory "
            "retrieval to produce a safe specialist execution plan."
        ),
        category="orchestration",
        requires_user_approval=False,
        accesses_external_network=False,
        performs_external_actions=False,
    )

    PIPELINE_VERSION = "1.1.0"

    def __init__(self) -> None:
        self._mention_agent = MentionActivationAgent()
        self._context_agent = ConversationContextAgent()
        self._intent_agent = IntentRouterAgent()
        self._permission_agent = PermissionPrivacyAgent()
        self._memory_agent = ConversationMemoryAgent()
        self._quality_agent = QualityValidatorAgent()

    def execute(self, payload: Mapping[str, Any]) -> AgentResult:
        validation_error = self._validate(payload)

        if validation_error:
            return AgentResult(
                success=False,
                agent_id=self.metadata.agent_id,
                data={
                    "status": "rejected",
                    "pipeline_version": self.PIPELINE_VERSION,
                },
                error=validation_error,
            )

        try:
            plan = self.orchestrate(payload)
        except Exception as error:
            return AgentResult(
                success=False,
                agent_id=self.metadata.agent_id,
                data={
                    "status": "failed",
                    "pipeline_version": self.PIPELINE_VERSION,
                },
                error=f"Orchestration failed: {error}",
            )

        return AgentResult(
            success=True,
            agent_id=self.metadata.agent_id,
            data=plan,
        )

    def orchestrate(
        self,
        payload: Mapping[str, Any],
    ) -> Dict[str, Any]:
        trace: list[Dict[str, Any]] = []

        activation = self._mention_agent.execute(
            {
                "message": payload.get("message"),
                "activation_mode": payload.get(
                    "activation_mode",
                    "mention_only",
                ),
                "sender_is_convera": payload.get(
                    "sender_is_convera",
                    False,
                ),
            }
        )

        trace.append(
            self._trace_entry(
                "mention_activation",
                activation,
            )
        )

        if not activation.success:
            return self._stop_plan(
                reason="activation_agent_failed",
                trace=trace,
                error=activation.error,
            )

        if not activation.data.get("activated", False):
            return {
                "status": "silent",
                "should_respond": False,
                "reason": activation.data.get(
                    "reason",
                    "not_activated",
                ),
                "pipeline_version": self.PIPELINE_VERSION,
                "trace": trace,
            }

        context = self._context_agent.execute(
            {
                "conversation_id": payload.get(
                    "conversation_id"
                ),
                "thread_id": payload.get("thread_id"),
                "project_id": payload.get("project_id"),
                "chat_type": payload.get(
                    "chat_type",
                    "private",
                ),
                "sender_id": payload.get("sender_id"),
                "message_id": payload.get("message_id"),
                "message": payload.get("message"),
                "timestamp": payload.get("timestamp"),
                "participants": payload.get(
                    "participants",
                    [],
                ),
                "messages": payload.get("messages", []),
                "files": payload.get("files", []),
                "message_limit": payload.get(
                    "message_limit",
                    20,
                ),
                "topic": payload.get("topic"),
            }
        )

        trace.append(
            self._trace_entry(
                "conversation_context",
                context,
            )
        )

        if not context.success:
            return self._stop_plan(
                reason="context_agent_failed",
                trace=trace,
                error=context.error,
            )

        conversation_state = context.data[
            "conversation_state"
        ]

        intent = self._intent_agent.execute(
            {
                "message": payload.get("message"),
                "activated": True,
                "context": conversation_state,
            }
        )

        trace.append(
            self._trace_entry(
                "intent_router",
                intent,
            )
        )

        if not intent.success:
            return self._stop_plan(
                reason="intent_agent_failed",
                trace=trace,
                error=intent.error,
            )

        primary_intent = intent.data.get(
            "primary_intent"
        )

        permission_action = self._permission_action(
            primary_intent
        )

        permission = self._permission_agent.execute(
            {
                "actor_id": payload.get("actor_id")
                or payload.get("sender_id"),
                "actor_role": payload.get(
                    "actor_role",
                    "member",
                ),
                "action": permission_action,
                "resource_type": payload.get(
                    "resource_type",
                    "conversation",
                ),
                "actor_conversation_id": payload.get(
                    "conversation_id"
                ),
                "resource_conversation_id": payload.get(
                    "resource_conversation_id"
                )
                or payload.get("conversation_id"),
                "actor_project_id": payload.get(
                    "project_id"
                ),
                "resource_project_id": payload.get(
                    "resource_project_id"
                )
                or payload.get("project_id"),
                "participants": self._participant_ids(
                    conversation_state.get(
                        "participants",
                        []
                    )
                ),
                "allowed_users": payload.get(
                    "allowed_users",
                    [],
                ),
                "resource_owner_id": payload.get(
                    "resource_owner_id"
                ),
                "convera_invoked": True,
                "approval_granted": payload.get(
                    "approval_granted",
                    False,
                ),
            }
        )

        trace.append(
            self._trace_entry(
                "permission_privacy",
                permission,
            )
        )

        if not permission.success:
            return self._stop_plan(
                reason="permission_agent_failed",
                trace=trace,
                error=permission.error,
            )

        if not permission.data.get("allowed", False):
            return {
                "status": "blocked",
                "should_respond": True,
                "reason": permission.data.get(
                    "reason",
                    "permission_denied",
                ),
                "permission": permission.data,
                "intent": intent.data,
                "pipeline_version": self.PIPELINE_VERSION,
                "trace": trace,
            }

        memory = self._memory_agent.execute(
            {
                "operation": "retrieve",
                "conversation_id": payload.get(
                    "conversation_id"
                ),
                "project_id": payload.get("project_id"),
                "user_id": payload.get("actor_id")
                or payload.get("sender_id"),
                "permission_granted": True,
                "memories": payload.get("memories", []),
                "key": payload.get("memory_key"),
                "memory_type": payload.get(
                    "memory_type"
                ),
            }
        )

        trace.append(
            self._trace_entry(
                "conversation_memory",
                memory,
            )
        )

        if not memory.success:
            return self._stop_plan(
                reason="memory_agent_failed",
                trace=trace,
                error=memory.error,
            )

        approval_required = bool(
            intent.data.get("requires_approval", False)
        )

        approval_granted = bool(
            payload.get("approval_granted", False)
        )

        execution_status = (
            "awaiting_approval"
            if approval_required and not approval_granted
            else "ready"
        )

        plan = {
            "status": execution_status,
            "should_respond": True,
            "pipeline_version": self.PIPELINE_VERSION,
            "activation": activation.data,
            "conversation_context": conversation_state,
            "intent": intent.data,
            "permission": permission.data,
            "memory": memory.data,
            "execution_plan": {
                "primary_intent": primary_intent,
                "secondary_intents": intent.data.get(
                    "secondary_intents",
                    [],
                ),
                "target_agent_id": intent.data.get(
                    "target_agent_id"
                ),
                "requires_approval": approval_required,
                "approval_granted": approval_granted,
                "can_execute": (
                    execution_status == "ready"
                ),
                "next_step": (
                    "request_user_approval"
                    if execution_status
                    == "awaiting_approval"
                    else "dispatch_specialist_agent"
                ),
            },
            "trace": trace,
        }

        if execution_status != "ready":
            return plan

        if payload.get("specialist_result") is None:
            return plan

        return self._validate_specialist_result(
            payload=payload,
            plan=plan,
            trace=trace,
        )

    def _validate_specialist_result(
        self,
        *,
        payload: Mapping[str, Any],
        plan: Dict[str, Any],
        trace: list[Dict[str, Any]],
    ) -> Dict[str, Any]:
        specialist_result = payload.get("specialist_result")

        if isinstance(specialist_result, AgentResult):
            specialist_success = specialist_result.success
            specialist_agent_id = specialist_result.agent_id
            specialist_data: Any = specialist_result.data
            specialist_error = specialist_result.error
        elif isinstance(specialist_result, Mapping):
            specialist_success = bool(
                specialist_result.get("success", True)
            )
            specialist_agent_id = self._text(
                specialist_result.get("agent_id")
            ) or self._text(
                plan["execution_plan"].get("target_agent_id")
            ) or "convera.specialist"
            specialist_data = specialist_result.get(
                "data",
                specialist_result.get(
                    "output",
                    specialist_result,
                ),
            )
            specialist_error = specialist_result.get("error")
        else:
            specialist_success = False
            specialist_agent_id = self._text(
                plan["execution_plan"].get("target_agent_id")
            ) or "convera.specialist"
            specialist_data = specialist_result
            specialist_error = (
                "specialist_result must be an AgentResult "
                "or mapping."
            )

        trace.append(
            {
                "stage": "specialist_agent",
                "agent_id": specialist_agent_id,
                "success": specialist_success,
                "error": specialist_error,
            }
        )

        output = specialist_data

        if isinstance(specialist_data, Mapping):
            output = specialist_data.get(
                "output",
                specialist_data,
            )

        validator_payload = {
            "request": payload.get("message"),
            "output": output,
            "conversation_id": payload.get(
                "conversation_id"
            ),
            "source_conversation_id": (
                payload.get("source_conversation_id")
                or payload.get("conversation_id")
            ),
            "project_id": payload.get("project_id"),
            "source_project_id": (
                payload.get("source_project_id")
                or payload.get("project_id")
            ),
            "activated": True,
            "specialist_success": specialist_success,
            "specialist_error": specialist_error,
            "approval_required": plan[
                "execution_plan"
            ].get("requires_approval", False),
            "approval_granted": plan[
                "execution_plan"
            ].get("approval_granted", False),
            "external_action_completed": bool(
                payload.get(
                    "external_action_completed",
                    False,
                )
            ),
            "research_used": bool(
                payload.get("research_used", False)
            ),
            "citations": payload.get("citations", []),
            "contains_factual_claims": bool(
                payload.get(
                    "contains_factual_claims",
                    False,
                )
            ),
        }

        try:
            quality = self._quality_agent.execute(
                validator_payload
            )
        except Exception as error:
            quality = AgentResult(
                success=False,
                agent_id=(
                    QualityValidatorAgent.metadata.agent_id
                ),
                data={
                    "approved": False,
                    "next_action": "return_to_specialist",
                },
                error=(
                    "Quality validation failed safely: "
                    f"{error}"
                ),
            )

        trace.append(
            self._trace_entry(
                "quality_validator",
                quality,
            )
        )

        result = dict(plan)
        result["trace"] = trace
        result["specialist_result"] = specialist_result
        result["quality_validation"] = quality.data

        if not quality.success:
            result["status"] = "validation_failed"
            result["should_respond"] = False
            result["error"] = quality.error
            result["execution_plan"] = dict(
                plan["execution_plan"]
            )
            result["execution_plan"]["can_execute"] = False
            result["execution_plan"][
                "next_step"
            ] = "handle_validation_failure"
            return result

        if quality.data.get("approved", False):
            result["status"] = "validated"
            result["should_respond"] = True
            result["validated_response"] = quality.data.get(
                "validated_response"
            )
            result["execution_plan"] = dict(
                plan["execution_plan"]
            )
            result["execution_plan"][
                "next_step"
            ] = "compose_response"
            return result

        result["status"] = "validation_rejected"
        result["should_respond"] = False
        result["execution_plan"] = dict(
            plan["execution_plan"]
        )
        result["execution_plan"]["can_execute"] = False
        result["execution_plan"]["next_step"] = (
            quality.data.get(
                "next_action",
                "return_to_specialist",
            )
        )
        return result

    def _validate(
        self,
        payload: Mapping[str, Any],
    ) -> str | None:
        if not self._text(payload.get("conversation_id")):
            return "conversation_id is required."

        if not self._text(payload.get("message")):
            return "message is required."

        sender_id = self._text(
            payload.get("sender_id")
            or payload.get("actor_id")
        )

        if not sender_id:
            return "sender_id or actor_id is required."

        return None

    @staticmethod
    def _permission_action(
        intent: str | None,
    ) -> str:
        action_map = {
            "create_task": "create_task",
            "create_reminder": "create_reminder",
            "schedule_meeting": "schedule_meeting",
            "summarize": "summarize",
            "analyze_file": "analyze",
            "research_web": "read",
            "create_document": "read",
            "create_presentation": "read",
            "create_logo": "read",
            "create_image": "read",
            "translate": "read",
            "draft_reply": "reply",
            "project_update": "read",
            "extract_decisions": "read",
            "find_information": "search",
            "general_question": "read",
        }

        return action_map.get(intent or "", "read")

    @staticmethod
    def _participant_ids(
        participants: Any,
    ) -> list[str]:
        if not isinstance(participants, list):
            return []

        result: list[str] = []

        for participant in participants:
            if not isinstance(participant, Mapping):
                continue

            participant_id = str(
                participant.get("participant_id")
                or ""
            ).strip()

            if participant_id:
                result.append(participant_id)

        return result

    @staticmethod
    def _trace_entry(
        stage: str,
        result: AgentResult,
    ) -> Dict[str, Any]:
        return {
            "stage": stage,
            "agent_id": result.agent_id,
            "success": result.success,
            "error": result.error,
        }

    def _stop_plan(
        self,
        *,
        reason: str,
        trace: list[Dict[str, Any]],
        error: str | None,
    ) -> Dict[str, Any]:
        return {
            "status": "failed",
            "should_respond": False,
            "reason": reason,
            "error": error,
            "pipeline_version": self.PIPELINE_VERSION,
            "trace": trace,
        }

    @staticmethod
    def _text(value: Any) -> str:
        return str(value or "").strip()
