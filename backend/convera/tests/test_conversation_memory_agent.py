"""Tests for the Convera Conversation Memory Agent."""

from __future__ import annotations

import unittest

from backend.convera.agents.audit_agent import AuditAgent
from backend.convera.agents.conversation_memory_agent import (
    ConversationMemoryAgent,
)
from backend.convera.agents.registry import ConveraAgentRegistry


class ConversationMemoryAgentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.agent = ConversationMemoryAgent()

    def base_payload(self) -> dict:
        return {
            "conversation_id": "chat-1",
            "project_id": "project-a",
            "user_id": "ranjan",
            "permission_granted": True,
            "memories": [],
        }

    def test_passes_audit(self) -> None:
        report = AuditAgent().audit(
            ConversationMemoryAgent
        )

        self.assertTrue(report["approved"])
        self.assertTrue(report["production_ready"])

    def test_remember_requires_permission(self) -> None:
        payload = self.base_payload()
        payload.update(
            {
                "operation": "remember",
                "permission_granted": False,
                "retention_approved": True,
                "key": "preferred_language",
                "value": "English",
                "memory_type": "preference",
            }
        )

        result = self.agent.execute(payload)

        self.assertFalse(result.data["allowed"])
        self.assertEqual(
            result.data["reason"],
            "permission_required",
        )

    def test_remember_requires_retention_approval(self) -> None:
        payload = self.base_payload()
        payload.update(
            {
                "operation": "remember",
                "retention_approved": False,
                "key": "preferred_language",
                "value": "English",
                "memory_type": "preference",
            }
        )

        result = self.agent.execute(payload)

        self.assertFalse(result.data["allowed"])
        self.assertEqual(
            result.data["reason"],
            "retention_approval_required",
        )

    def test_saves_safe_memory(self) -> None:
        payload = self.base_payload()
        payload.update(
            {
                "operation": "remember",
                "retention_approved": True,
                "key": "preferred_language",
                "value": "English",
                "memory_type": "preference",
            }
        )

        result = self.agent.execute(payload)

        self.assertTrue(result.data["allowed"])
        self.assertEqual(result.data["count"], 1)

    def test_rejects_sensitive_memory(self) -> None:
        payload = self.base_payload()
        payload.update(
            {
                "operation": "remember",
                "retention_approved": True,
                "key": "api_key",
                "value": "secret-value",
                "memory_type": "fact",
            }
        )

        result = self.agent.execute(payload)

        self.assertFalse(result.data["allowed"])
        self.assertEqual(
            result.data["reason"],
            "sensitive_memory_rejected",
        )

    def test_retrieval_is_conversation_isolated(self) -> None:
        memories = [
            {
                "memory_id": "one",
                "key": "theme",
                "value": "dark",
                "memory_type": "preference",
                "conversation_id": "chat-1",
                "project_id": "project-a",
                "user_id": "ranjan",
            },
            {
                "memory_id": "two",
                "key": "theme",
                "value": "light",
                "memory_type": "preference",
                "conversation_id": "chat-2",
                "project_id": "project-a",
                "user_id": "ranjan",
            },
        ]

        payload = self.base_payload()
        payload.update(
            {
                "operation": "retrieve",
                "key": "theme",
                "memories": memories,
            }
        )

        result = self.agent.execute(payload)

        self.assertEqual(result.data["count"], 1)
        self.assertEqual(
            result.data["matches"][0]["value"],
            "dark",
        )

    def test_retrieval_is_project_isolated(self) -> None:
        memories = [
            {
                "memory_id": "one",
                "key": "status",
                "value": "active",
                "memory_type": "project_context",
                "conversation_id": "chat-1",
                "project_id": "project-a",
                "user_id": "ranjan",
            },
            {
                "memory_id": "two",
                "key": "status",
                "value": "private",
                "memory_type": "project_context",
                "conversation_id": "chat-1",
                "project_id": "project-b",
                "user_id": "ranjan",
            },
        ]

        payload = self.base_payload()
        payload.update(
            {
                "operation": "retrieve",
                "key": "status",
                "memories": memories,
            }
        )

        result = self.agent.execute(payload)

        self.assertEqual(result.data["count"], 1)
        self.assertEqual(
            result.data["matches"][0]["value"],
            "active",
        )

    def test_forget_removes_only_scoped_memory(self) -> None:
        memories = [
            {
                "memory_id": "remove-me",
                "key": "theme",
                "value": "dark",
                "memory_type": "preference",
                "conversation_id": "chat-1",
                "project_id": "project-a",
                "user_id": "ranjan",
            },
            {
                "memory_id": "keep-me",
                "key": "theme",
                "value": "light",
                "memory_type": "preference",
                "conversation_id": "chat-2",
                "project_id": "project-a",
                "user_id": "ranjan",
            },
        ]

        payload = self.base_payload()
        payload.update(
            {
                "operation": "forget",
                "memory_id": "remove-me",
                "memories": memories,
            }
        )

        result = self.agent.execute(payload)

        self.assertEqual(
            result.data["removed_count"],
            1,
        )
        self.assertEqual(
            len(result.data["memories"]),
            1,
        )
        self.assertEqual(
            result.data["memories"][0]["memory_id"],
            "keep-me",
        )

    def test_registry_accepts_memory_agent(self) -> None:
        registry = ConveraAgentRegistry()
        report = registry.register(
            ConversationMemoryAgent
        )

        self.assertTrue(report["production_ready"])
        self.assertIsInstance(
            registry.create(
                "convera.conversation_memory"
            ),
            ConversationMemoryAgent,
        )


if __name__ == "__main__":
    unittest.main()
