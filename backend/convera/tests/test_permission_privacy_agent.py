"""Tests for the Convera Permission and Privacy Agent."""

from __future__ import annotations

import unittest

from backend.convera.agents.audit_agent import AuditAgent
from backend.convera.agents.permission_privacy_agent import (
    PermissionPrivacyAgent,
)
from backend.convera.agents.registry import (
    ConveraAgentRegistry,
)


class PermissionPrivacyAgentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.agent = PermissionPrivacyAgent()

    def test_agent_passes_chief_architect_audit(self) -> None:
        report = AuditAgent().audit(
            PermissionPrivacyAgent
        )

        self.assertTrue(report["approved"])
        self.assertTrue(report["production_ready"])
        self.assertGreaterEqual(
            report["overall_score"],
            85,
        )

    def test_member_can_read_own_conversation(self) -> None:
        result = self.agent.execute(
            {
                "actor_id": "ranjan",
                "actor_role": "member",
                "action": "summarize",
                "resource_type": "conversation",
                "actor_conversation_id": "chat-1",
                "resource_conversation_id": "chat-1",
                "participants": [
                    "ranjan",
                    "user-2",
                ],
            }
        )

        self.assertTrue(result.success)
        self.assertTrue(result.data["allowed"])

    def test_cross_conversation_access_is_denied(self) -> None:
        result = self.agent.execute(
            {
                "actor_id": "ranjan",
                "actor_role": "member",
                "action": "read",
                "resource_type": "private_conversation",
                "actor_conversation_id": "chat-1",
                "resource_conversation_id": "chat-2",
                "participants": ["ranjan"],
            }
        )

        self.assertFalse(result.data["allowed"])
        self.assertIn(
            "cross_conversation_access_denied",
            result.data["reasons"],
        )

    def test_cross_project_access_is_denied(self) -> None:
        result = self.agent.execute(
            {
                "actor_id": "ranjan",
                "actor_role": "member",
                "action": "analyze",
                "resource_type": "project_file",
                "actor_project_id": "project-a",
                "resource_project_id": "project-b",
                "participants": ["ranjan"],
            }
        )

        self.assertFalse(result.data["allowed"])
        self.assertIn(
            "cross_project_access_denied",
            result.data["reasons"],
        )

    def test_non_participant_is_denied(self) -> None:
        result = self.agent.execute(
            {
                "actor_id": "outsider",
                "actor_role": "member",
                "action": "read",
                "resource_type": "conversation",
                "participants": [
                    "ranjan",
                    "user-2",
                ],
            }
        )

        self.assertFalse(result.data["allowed"])
        self.assertIn(
            "actor_not_conversation_participant",
            result.data["reasons"],
        )

    def test_convera_requires_activation(self) -> None:
        result = self.agent.execute(
            {
                "actor_id": "convera",
                "actor_role": "convera",
                "action": "summarize",
                "resource_type": "conversation",
                "participants": [
                    "ranjan",
                    "convera",
                ],
                "convera_invoked": False,
            }
        )

        self.assertFalse(result.data["allowed"])
        self.assertIn(
            "convera_not_invoked",
            result.data["reasons"],
        )

    def test_convera_can_read_after_activation(self) -> None:
        result = self.agent.execute(
            {
                "actor_id": "convera",
                "actor_role": "convera",
                "action": "summarize",
                "resource_type": "conversation",
                "participants": [
                    "ranjan",
                    "convera",
                ],
                "convera_invoked": True,
            }
        )

        self.assertTrue(result.data["allowed"])

    def test_write_action_requires_approval(self) -> None:
        result = self.agent.execute(
            {
                "actor_id": "ranjan",
                "actor_role": "member",
                "action": "create_task",
                "resource_type": "conversation",
                "participants": ["ranjan"],
                "approval_granted": False,
            }
        )

        self.assertFalse(result.data["allowed"])
        self.assertTrue(
            result.data["requires_approval"]
        )
        self.assertIn(
            "explicit_approval_required",
            result.data["reasons"],
        )

    def test_write_action_allowed_after_approval(self) -> None:
        result = self.agent.execute(
            {
                "actor_id": "ranjan",
                "actor_role": "member",
                "action": "create_task",
                "resource_type": "conversation",
                "participants": ["ranjan"],
                "approval_granted": True,
            }
        )

        self.assertTrue(result.data["allowed"])

    def test_guest_cannot_write(self) -> None:
        result = self.agent.execute(
            {
                "actor_id": "guest-1",
                "actor_role": "guest",
                "action": "send_message",
                "resource_type": "conversation",
                "participants": ["guest-1"],
                "approval_granted": True,
            }
        )

        self.assertFalse(result.data["allowed"])
        self.assertIn(
            "guest_write_access_denied",
            result.data["reasons"],
        )

    def test_sensitive_resource_acl_is_enforced(self) -> None:
        result = self.agent.execute(
            {
                "actor_id": "user-2",
                "actor_role": "member",
                "action": "read",
                "resource_type": "private_file",
                "allowed_users": ["ranjan"],
                "resource_owner_id": "ranjan",
            }
        )

        self.assertFalse(result.data["allowed"])
        self.assertIn(
            "actor_not_in_resource_acl",
            result.data["reasons"],
        )

    def test_registry_accepts_permission_agent(self) -> None:
        registry = ConveraAgentRegistry()

        report = registry.register(
            PermissionPrivacyAgent
        )

        self.assertTrue(report["production_ready"])

        created = registry.create(
            "convera.permission_privacy"
        )

        self.assertIsInstance(
            created,
            PermissionPrivacyAgent,
        )

    def test_missing_actor_id_fails(self) -> None:
        result = self.agent.execute(
            {
                "actor_role": "member",
                "action": "read",
                "resource_type": "conversation",
            }
        )

        self.assertFalse(result.success)
        self.assertEqual(
            result.error,
            "actor_id is required.",
        )


if __name__ == "__main__":
    unittest.main()
