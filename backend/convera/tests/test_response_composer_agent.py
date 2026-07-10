"""Tests for the Convera Response Composer Agent."""

from __future__ import annotations

import copy
import unittest

from backend.convera.agents.audit_agent import AuditAgent
from backend.convera.agents.registry import (
    ConveraAgentRegistry,
)
from backend.convera.agents.response_composer_agent import (
    ResponseComposerAgent,
)


class ResponseComposerAgentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.agent = ResponseComposerAgent()

    def base_payload(self) -> dict:
        return {
            "conversation_id": "chat-1",
            "thread_id": "thread-1",
            "project_id": "project-1",
            "chat_type": "group",
            "activated": True,
            "permission_allowed": True,
            "validation_approved": True,
            "validated_response": (
                "The discussion focused on the mobile "
                "interface and deployment plan."
            ),
            "artifacts": [],
            "attachments": [],
            "citations": [],
        }

    def test_passes_chief_architect_audit(self) -> None:
        report = AuditAgent().audit(
            ResponseComposerAgent
        )

        self.assertTrue(report["approved"])
        self.assertTrue(report["production_ready"])
        self.assertGreaterEqual(
            report["overall_score"],
            85,
        )

    def test_composes_normal_message(self) -> None:
        result = self.agent.execute(
            self.base_payload()
        )

        self.assertTrue(result.success)
        self.assertEqual(
            result.data["status"],
            "ready_to_send",
        )
        self.assertTrue(result.data["should_send"])
        self.assertEqual(
            result.data["reply"]["type"],
            "message",
        )

    def test_stays_silent_without_activation(self) -> None:
        payload = self.base_payload()
        payload["activated"] = False

        result = self.agent.execute(payload)

        self.assertTrue(result.success)
        self.assertEqual(
            result.data["status"],
            "silent",
        )
        self.assertFalse(result.data["should_send"])
        self.assertIsNone(result.data["reply"])

    def test_preserves_structured_artifact(self) -> None:
        payload = self.base_payload()
        payload["validated_response"] = {
            "type": "document",
            "content": "Project summary document.",
            "artifact": {
                "artifact_id": "doc-1",
                "format": "docx",
            },
            "metadata": {
                "title": "Project Summary",
            },
        }

        result = self.agent.execute(payload)

        self.assertEqual(
            result.data["reply"]["type"],
            "document",
        )
        self.assertEqual(
            result.data["reply"]["artifacts"][0][
                "artifact_id"
            ],
            "doc-1",
        )

    def test_preserves_citations(self) -> None:
        payload = self.base_payload()
        payload["citations"] = [
            {
                "title": "Source One",
                "url": "https://example.com",
            }
        ]

        result = self.agent.execute(payload)

        self.assertEqual(
            len(result.data["reply"]["citations"]),
            1,
        )

    def test_permission_denial_is_preserved(self) -> None:
        payload = self.base_payload()
        payload["permission_allowed"] = False
        payload["permission_reason"] = (
            "cross_project_access_denied"
        )

        result = self.agent.execute(payload)

        self.assertEqual(
            result.data["status"],
            "blocked",
        )
        self.assertEqual(
            result.data["reply"]["type"],
            "system_notice",
        )
        self.assertEqual(
            result.data["reason"],
            "cross_project_access_denied",
        )

    def test_validation_failure_is_not_exposed(self) -> None:
        payload = self.base_payload()
        payload["validation_approved"] = False
        payload["validated_response"] = None
        payload["required_action"] = (
            "return_to_specialist"
        )
        payload["findings"] = [
            {
                "code": "INTERNAL_PRIVATE_FINDING",
                "message": "Secret internal detail",
            }
        ]

        result = self.agent.execute(payload)

        reply_text = result.data["reply"]["content"]

        self.assertNotIn(
            "INTERNAL_PRIVATE_FINDING",
            reply_text,
        )
        self.assertNotIn(
            "Secret internal detail",
            reply_text,
        )

    def test_requests_approval_safely(self) -> None:
        payload = self.base_payload()
        payload["validation_approved"] = False
        payload["validated_response"] = None
        payload["required_action"] = (
            "request_user_approval"
        )

        result = self.agent.execute(payload)

        self.assertIn(
            "approval",
            result.data["reply"]["content"].lower(),
        )

    def test_does_not_mutate_original_payload(self) -> None:
        payload = self.base_payload()
        payload["validated_response"] = {
            "content": "Project summary.",
            "metadata": {
                "sections": ["overview", "status"],
            },
        }

        original = copy.deepcopy(payload)

        self.agent.execute(payload)

        self.assertEqual(payload, original)

    def test_missing_conversation_id_fails(self) -> None:
        payload = self.base_payload()
        payload["conversation_id"] = ""

        result = self.agent.execute(payload)

        self.assertFalse(result.success)
        self.assertEqual(
            result.error,
            "conversation_id is required.",
        )

    def test_missing_validated_response_fails(self) -> None:
        payload = self.base_payload()
        payload["validated_response"] = None

        result = self.agent.execute(payload)

        self.assertFalse(result.success)
        self.assertIn(
            "validated_response is required",
            result.error,
        )

    def test_registry_accepts_response_composer(self) -> None:
        registry = ConveraAgentRegistry()

        report = registry.register(
            ResponseComposerAgent
        )

        self.assertTrue(report["production_ready"])

        created = registry.create(
            "convera.response_composer"
        )

        self.assertIsInstance(
            created,
            ResponseComposerAgent,
        )


if __name__ == "__main__":
    unittest.main()
