"""Tests for the Convera Orchestrator Agent."""

from __future__ import annotations

import unittest

from backend.convera.agents.audit_agent import AuditAgent
from backend.convera.agents.convera_orchestrator_agent import (
    ConveraOrchestratorAgent,
)
from backend.convera.agents.registry import (
    ConveraAgentRegistry,
)


class ConveraOrchestratorAgentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.agent = ConveraOrchestratorAgent()

    def base_payload(self) -> dict:
        return {
            "conversation_id": "chat-1",
            "thread_id": "thread-1",
            "project_id": "convera-project",
            "chat_type": "group",
            "sender_id": "ranjan",
            "actor_id": "ranjan",
            "actor_role": "member",
            "participants": [
                {
                    "participant_id": "ranjan",
                    "display_name": "Ranjan",
                },
                {
                    "participant_id": "user-2",
                    "display_name": "User Two",
                },
                {
                    "participant_id": "convera",
                    "display_name": "Convera",
                    "role": "assistant",
                },
            ],
            "messages": [],
            "memories": [],
        }

    def test_passes_chief_architect_audit(self) -> None:
        report = AuditAgent().audit(
            ConveraOrchestratorAgent
        )

        self.assertTrue(report["approved"])
        self.assertTrue(report["production_ready"])
        self.assertGreaterEqual(
            report["overall_score"],
            85,
        )

    def test_stays_silent_without_activation(self) -> None:
        payload = self.base_payload()
        payload["message"] = "Please send the file."

        result = self.agent.execute(payload)

        self.assertTrue(result.success)
        self.assertEqual(
            result.data["status"],
            "silent",
        )
        self.assertFalse(
            result.data["should_respond"]
        )

    def test_routes_summary_request(self) -> None:
        payload = self.base_payload()
        payload["message"] = (
            "@Convera summarize this conversation"
        )

        result = self.agent.execute(payload)

        self.assertTrue(result.success)
        self.assertEqual(
            result.data["status"],
            "ready",
        )
        self.assertEqual(
            result.data["execution_plan"][
                "primary_intent"
            ],
            "summarize",
        )
        self.assertEqual(
            result.data["execution_plan"][
                "target_agent_id"
            ],
            "convera.summarization",
        )

    def test_task_request_waits_for_approval(self) -> None:
        payload = self.base_payload()
        payload["message"] = (
            "@Convera create a task for Ranjan"
        )
        payload["approval_granted"] = False

        result = self.agent.execute(payload)

        self.assertEqual(
            result.data["status"],
            "blocked",
        )
        self.assertIn(
            "explicit_approval_required",
            result.data["permission"]["reasons"],
        )

    def test_task_request_is_ready_after_approval(self) -> None:
        payload = self.base_payload()
        payload["message"] = (
            "@Convera create a task for Ranjan"
        )
        payload["approval_granted"] = True

        result = self.agent.execute(payload)

        self.assertEqual(
            result.data["status"],
            "ready",
        )
        self.assertTrue(
            result.data["execution_plan"][
                "can_execute"
            ]
        )

    def test_cross_project_access_is_blocked(self) -> None:
        payload = self.base_payload()
        payload["message"] = (
            "@Convera summarize this project"
        )
        payload["resource_project_id"] = "other-project"

        result = self.agent.execute(payload)

        self.assertEqual(
            result.data["status"],
            "blocked",
        )
        self.assertIn(
            "cross_project_access_denied",
            result.data["permission"]["reasons"],
        )

    def test_memory_is_project_isolated(self) -> None:
        payload = self.base_payload()
        payload["message"] = (
            "@Convera what is our project status?"
        )
        payload["memories"] = [
            {
                "memory_id": "allowed",
                "key": "status",
                "value": "Active",
                "memory_type": "project_context",
                "conversation_id": "chat-1",
                "project_id": "convera-project",
                "user_id": "ranjan",
            },
            {
                "memory_id": "blocked",
                "key": "status",
                "value": "Secret",
                "memory_type": "project_context",
                "conversation_id": "chat-1",
                "project_id": "other-project",
                "user_id": "ranjan",
            },
        ]

        result = self.agent.execute(payload)

        matches = result.data["memory"]["matches"]

        self.assertEqual(len(matches), 1)
        self.assertEqual(
            matches[0]["memory_id"],
            "allowed",
        )

    def test_trace_contains_all_pipeline_stages(self) -> None:
        payload = self.base_payload()
        payload["message"] = (
            "@Convera summarize the discussion"
        )

        result = self.agent.execute(payload)

        stages = [
            item["stage"]
            for item in result.data["trace"]
        ]

        self.assertEqual(
            stages,
            [
                "mention_activation",
                "conversation_context",
                "intent_router",
                "permission_privacy",
                "conversation_memory",
            ],
        )

    def test_registry_accepts_orchestrator(self) -> None:
        registry = ConveraAgentRegistry()

        report = registry.register(
            ConveraOrchestratorAgent
        )

        self.assertTrue(report["production_ready"])

        created = registry.create(
            "convera.orchestrator"
        )

        self.assertIsInstance(
            created,
            ConveraOrchestratorAgent,
        )

    def test_missing_message_fails(self) -> None:
        payload = self.base_payload()
        payload["message"] = ""

        result = self.agent.execute(payload)

        self.assertFalse(result.success)
        self.assertEqual(
            result.error,
            "message is required.",
        )

    def test_validates_specialist_result_after_dispatch(self) -> None:
        payload = self.base_payload()
        payload["message"] = (
            "@Convera summarize the project discussion"
        )
        payload["specialist_result"] = {
            "success": True,
            "agent_id": "convera.summarization",
            "output": (
                "The project discussion focused on the "
                "mobile interface and deployment plan."
            ),
        }

        result = self.agent.execute(payload)

        self.assertEqual(
            result.data["status"],
            "validated",
        )
        self.assertEqual(
            result.data["execution_plan"]["next_step"],
            "compose_response",
        )

        stages = [
            item["stage"]
            for item in result.data["trace"]
        ]

        self.assertEqual(
            stages[-2:],
            [
                "specialist_agent",
                "quality_validator",
            ],
        )

    def test_rejects_invalid_specialist_output(self) -> None:
        payload = self.base_payload()
        payload["message"] = (
            "@Convera summarize the project discussion"
        )
        payload["specialist_result"] = {
            "success": True,
            "agent_id": "convera.summarization",
            "output": "",
        }

        result = self.agent.execute(payload)

        self.assertEqual(
            result.data["status"],
            "validation_rejected",
        )
        self.assertFalse(
            result.data["should_respond"]
        )
        self.assertEqual(
            result.data["execution_plan"]["next_step"],
            "return_to_specialist",
        )

    def test_structured_specialist_output_is_preserved(
        self,
    ) -> None:
        payload = self.base_payload()
        payload["message"] = (
            "@Convera create a project summary"
        )
        payload["specialist_result"] = {
            "success": True,
            "agent_id": "convera.summarization",
            "output": {
                "content": (
                    "The project summary covers mobile "
                    "interface work and deployment."
                ),
                "artifact": {
                    "type": "document",
                    "artifact_id": "doc-1",
                },
            },
        }

        result = self.agent.execute(payload)

        self.assertEqual(
            result.data["status"],
            "validated",
        )
        self.assertEqual(
            result.data["validated_response"][
                "artifact"
            ]["artifact_id"],
            "doc-1",
        )

    def test_silent_flow_never_reaches_validator(self) -> None:
        payload = self.base_payload()
        payload["message"] = "Summarize the discussion"
        payload["specialist_result"] = {
            "success": True,
            "output": "This must not be validated.",
        }

        result = self.agent.execute(payload)

        stages = [
            item["stage"]
            for item in result.data["trace"]
        ]

        self.assertNotIn(
            "quality_validator",
            stages,
        )
        self.assertEqual(
            result.data["status"],
            "silent",
        )

    def test_blocked_flow_never_reaches_validator(self) -> None:
        payload = self.base_payload()
        payload["message"] = (
            "@Convera summarize this project"
        )
        payload["resource_project_id"] = "other-project"
        payload["specialist_result"] = {
            "success": True,
            "output": "This must not be validated.",
        }

        result = self.agent.execute(payload)

        stages = [
            item["stage"]
            for item in result.data["trace"]
        ]

        self.assertNotIn(
            "quality_validator",
            stages,
        )
        self.assertEqual(
            result.data["status"],
            "blocked",
        )

    def test_validator_exception_fails_safely(self) -> None:
        class ExplodingValidator:
            def execute(self, payload: dict) -> object:
                raise RuntimeError("validator exploded")

        self.agent._quality_agent = ExplodingValidator()

        payload = self.base_payload()
        payload["message"] = (
            "@Convera summarize the project discussion"
        )
        payload["specialist_result"] = {
            "success": True,
            "agent_id": "convera.summarization",
            "output": (
                "The project discussion covers the "
                "mobile interface."
            ),
        }

        result = self.agent.execute(payload)

        self.assertEqual(
            result.data["status"],
            "validation_failed",
        )
        self.assertFalse(
            result.data["should_respond"]
        )
        self.assertIn(
            "failed safely",
            result.data["error"],
        )



if __name__ == "__main__":
    unittest.main()
