"""Tests for the Convera Conversation Context Agent."""

from __future__ import annotations

import unittest

from backend.convera.agents.audit_agent import AuditAgent
from backend.convera.agents.conversation_context_agent import (
    ConversationContextAgent,
)
from backend.convera.agents.registry import (
    ConveraAgentRegistry,
)


class ConversationContextAgentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.agent = ConversationContextAgent()

    def test_agent_passes_chief_architect_audit(self) -> None:
        report = AuditAgent().audit(
            ConversationContextAgent
        )

        self.assertTrue(report["approved"])
        self.assertTrue(report["production_ready"])
        self.assertGreaterEqual(
            report["overall_score"],
            85,
        )

    def test_builds_private_chat_context(self) -> None:
        result = self.agent.execute(
            {
                "conversation_id": "chat-101",
                "chat_type": "private",
                "sender_id": "ranjan",
                "message": "@Convera summarize this.",
                "participants": [
                    {
                        "participant_id": "ranjan",
                        "display_name": "Ranjan",
                    },
                    {
                        "participant_id": "user-2",
                        "display_name": "User Two",
                    },
                ],
            }
        )

        self.assertTrue(result.success)

        state = result.data["conversation_state"]

        self.assertEqual(
            state["conversation_id"],
            "chat-101",
        )
        self.assertEqual(state["chat_type"], "private")
        self.assertEqual(len(state["participants"]), 2)
        self.assertEqual(state["message_count"], 1)

    def test_prunes_old_messages(self) -> None:
        messages = [
            {
                "message_id": f"m-{index}",
                "conversation_id": "chat-1",
                "text": f"Message {index}",
                "sender_id": "user-1",
            }
            for index in range(30)
        ]

        result = self.agent.execute(
            {
                "conversation_id": "chat-1",
                "messages": messages,
                "message_limit": 5,
            }
        )

        recent = result.data[
            "conversation_state"
        ]["recent_messages"]

        self.assertEqual(len(recent), 5)
        self.assertEqual(
            recent[0]["message_id"],
            "m-25",
        )

    def test_rejects_cross_conversation_messages(self) -> None:
        result = self.agent.execute(
            {
                "conversation_id": "chat-a",
                "messages": [
                    {
                        "message_id": "safe",
                        "conversation_id": "chat-a",
                        "text": "Correct chat",
                    },
                    {
                        "message_id": "leak",
                        "conversation_id": "chat-b",
                        "text": "Private information",
                    },
                ],
            }
        )

        messages = result.data[
            "conversation_state"
        ]["recent_messages"]

        ids = {
            message["message_id"]
            for message in messages
        }

        self.assertIn("safe", ids)
        self.assertNotIn("leak", ids)

    def test_rejects_cross_project_messages(self) -> None:
        result = self.agent.execute(
            {
                "conversation_id": "chat-a",
                "project_id": "project-one",
                "messages": [
                    {
                        "message_id": "same-project",
                        "conversation_id": "chat-a",
                        "project_id": "project-one",
                        "text": "Allowed",
                    },
                    {
                        "message_id": "other-project",
                        "conversation_id": "chat-a",
                        "project_id": "project-two",
                        "text": "Must not leak",
                    },
                ],
            }
        )

        messages = result.data[
            "conversation_state"
        ]["recent_messages"]

        ids = {
            message["message_id"]
            for message in messages
        }

        self.assertIn("same-project", ids)
        self.assertNotIn("other-project", ids)

    def test_extracts_decision_question_and_task(self) -> None:
        result = self.agent.execute(
            {
                "conversation_id": "chat-2",
                "messages": [
                    {
                        "message_id": "m1",
                        "text": (
                            "Let's use the blue logo."
                        ),
                        "sender_id": "ranjan",
                    },
                    {
                        "message_id": "m2",
                        "text": (
                            "Please prepare the presentation."
                        ),
                        "sender_id": "ranjan",
                    },
                    {
                        "message_id": "m3",
                        "text": (
                            "When will it be ready?"
                        ),
                        "sender_id": "user-2",
                    },
                ],
            }
        )

        state = result.data["conversation_state"]

        self.assertEqual(len(state["decisions"]), 1)
        self.assertEqual(
            len(state["task_candidates"]),
            1,
        )
        self.assertEqual(
            len(state["pending_questions"]),
            1,
        )

    def test_registry_accepts_context_agent(self) -> None:
        registry = ConveraAgentRegistry()
        report = registry.register(
            ConversationContextAgent
        )

        self.assertTrue(report["production_ready"])

        created = registry.create(
            "convera.conversation_context"
        )

        self.assertIsInstance(
            created,
            ConversationContextAgent,
        )

    def test_missing_conversation_id_fails(self) -> None:
        result = self.agent.execute(
            {
                "message": "Hello",
            }
        )

        self.assertFalse(result.success)
        self.assertEqual(
            result.error,
            "conversation_id is required.",
        )


if __name__ == "__main__":
    unittest.main()
