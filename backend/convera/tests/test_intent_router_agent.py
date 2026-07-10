"""Tests for the Convera Intent Router Agent."""

from __future__ import annotations

import unittest

from backend.convera.agents.audit_agent import AuditAgent
from backend.convera.agents.intent_router_agent import (
    IntentRouterAgent,
)
from backend.convera.agents.registry import (
    ConveraAgentRegistry,
)


class IntentRouterAgentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.agent = IntentRouterAgent()

    def test_agent_passes_chief_architect_audit(self) -> None:
        report = AuditAgent().audit(IntentRouterAgent)

        self.assertTrue(report["approved"])
        self.assertTrue(report["production_ready"])
        self.assertGreaterEqual(
            report["overall_score"],
            85,
        )

    def test_routes_summary_request(self) -> None:
        result = self.agent.execute(
            {
                "message": (
                    "@Convera summarize the last 30 messages"
                ),
                "activated": True,
            }
        )

        self.assertTrue(result.success)
        self.assertEqual(
            result.data["primary_intent"],
            "summarize",
        )
        self.assertEqual(
            result.data["target_agent_id"],
            "convera.summarization",
        )

    def test_routes_task_creation(self) -> None:
        result = self.agent.execute(
            {
                "message": (
                    "@Convera create a task for Ranjan"
                ),
                "activated": True,
            }
        )

        self.assertEqual(
            result.data["primary_intent"],
            "create_task",
        )
        self.assertTrue(
            result.data["requires_approval"]
        )

    def test_routes_presentation_creation(self) -> None:
        result = self.agent.execute(
            {
                "message": (
                    "Create a presentation from this discussion"
                ),
                "activated": True,
            }
        )

        self.assertEqual(
            result.data["primary_intent"],
            "create_presentation",
        )
        self.assertEqual(
            result.data["target_agent_id"],
            "convera.presentation",
        )

    def test_plain_question_uses_general_intent(self) -> None:
        result = self.agent.execute(
            {
                "message": (
                    "@Convera why is the mobile menu failing?"
                ),
                "activated": True,
            }
        )

        self.assertEqual(
            result.data["primary_intent"],
            "general_question",
        )
        self.assertEqual(
            result.data["confidence"],
            0.55,
        )

    def test_does_not_route_when_not_activated(self) -> None:
        result = self.agent.execute(
            {
                "message": "Please send the file.",
                "activated": False,
            }
        )

        self.assertTrue(result.success)
        self.assertFalse(
            result.data["should_route"]
        )
        self.assertIsNone(
            result.data["primary_intent"]
        )

    def test_empty_message_fails(self) -> None:
        result = self.agent.execute(
            {
                "message": "",
                "activated": True,
            }
        )

        self.assertFalse(result.success)
        self.assertEqual(
            result.error,
            "message is required.",
        )

    def test_multiple_intents_are_preserved(self) -> None:
        result = self.agent.execute(
            {
                "message": (
                    "@Convera summarize this conversation "
                    "and create a task"
                ),
                "activated": True,
            }
        )

        intents = {
            result.data["primary_intent"],
            *result.data["secondary_intents"],
        }

        self.assertIn("summarize", intents)
        self.assertIn("create_task", intents)

    def test_registry_accepts_intent_router(self) -> None:
        registry = ConveraAgentRegistry()
        report = registry.register(
            IntentRouterAgent
        )

        self.assertTrue(report["production_ready"])

        created = registry.create(
            "convera.intent_router"
        )

        self.assertIsInstance(
            created,
            IntentRouterAgent,
        )


if __name__ == "__main__":
    unittest.main()
