"""Tests for the Convera Quality Validator Agent."""

from __future__ import annotations

import unittest

from backend.convera.agents.audit_agent import AuditAgent
from backend.convera.agents.quality_validator_agent import (
    QualityValidatorAgent,
)
from backend.convera.agents.registry import (
    ConveraAgentRegistry,
)


class QualityValidatorAgentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.agent = QualityValidatorAgent()

    def base_payload(self) -> dict:
        return {
            "request": "Summarize the project discussion",
            "output": (
                "The project discussion focused on the mobile "
                "interface, drawer behavior and deployment plan."
            ),
            "conversation_id": "chat-1",
            "source_conversation_id": "chat-1",
            "project_id": "convera",
            "source_project_id": "convera",
            "specialist_success": True,
            "approval_required": False,
            "approval_granted": False,
            "research_used": False,
            "citations": [],
        }

    def test_passes_chief_architect_audit(self) -> None:
        report = AuditAgent().audit(
            QualityValidatorAgent
        )

        self.assertTrue(report["approved"])
        self.assertTrue(report["production_ready"])
        self.assertGreaterEqual(
            report["overall_score"],
            85,
        )

    def test_approves_good_output(self) -> None:
        result = self.agent.execute(
            self.base_payload()
        )

        self.assertTrue(result.success)
        self.assertTrue(result.data["approved"])
        self.assertEqual(
            result.data["next_action"],
            "send_response",
        )

    def test_blocks_empty_output(self) -> None:
        payload = self.base_payload()
        payload["output"] = ""

        result = self.agent.execute(payload)

        self.assertFalse(result.data["approved"])
        self.assertEqual(
            result.data["next_action"],
            "return_to_specialist",
        )

        codes = {
            item["code"]
            for item in result.data["findings"]
        }

        self.assertIn("EMPTY_OUTPUT", codes)

    def test_blocks_sensitive_data(self) -> None:
        payload = self.base_payload()
        payload["output"] = (
            "Use api_key=super-secret-value "
            "for the integration."
        )

        result = self.agent.execute(payload)

        self.assertFalse(result.data["approved"])
        self.assertEqual(
            result.data["next_action"],
            "block_output",
        )

    def test_blocks_cross_conversation_leakage(self) -> None:
        payload = self.base_payload()
        payload["source_conversation_id"] = "chat-2"

        result = self.agent.execute(payload)

        codes = {
            item["code"]
            for item in result.data["findings"]
        }

        self.assertIn(
            "CROSS_CONVERSATION_LEAKAGE",
            codes,
        )
        self.assertEqual(
            result.data["next_action"],
            "block_output",
        )

    def test_blocks_cross_project_leakage(self) -> None:
        payload = self.base_payload()
        payload["source_project_id"] = "secret-project"

        result = self.agent.execute(payload)

        codes = {
            item["code"]
            for item in result.data["findings"]
        }

        self.assertIn(
            "CROSS_PROJECT_LEAKAGE",
            codes,
        )

    def test_requires_approval_before_finalizing(self) -> None:
        payload = self.base_payload()
        payload["approval_required"] = True
        payload["approval_granted"] = False

        result = self.agent.execute(payload)

        self.assertFalse(result.data["approved"])
        self.assertEqual(
            result.data["next_action"],
            "request_user_approval",
        )

    def test_allows_approved_action_output(self) -> None:
        payload = self.base_payload()
        payload["approval_required"] = True
        payload["approval_granted"] = True

        result = self.agent.execute(payload)

        self.assertTrue(result.data["approved"])

    def test_research_requires_citations(self) -> None:
        payload = self.base_payload()
        payload["research_used"] = True
        payload["citations"] = []

        result = self.agent.execute(payload)

        codes = {
            item["code"]
            for item in result.data["findings"]
        }

        self.assertIn(
            "MISSING_RESEARCH_CITATIONS",
            codes,
        )
        self.assertFalse(result.data["approved"])

    def test_research_with_citations_can_pass(self) -> None:
        payload = self.base_payload()
        payload["research_used"] = True
        payload["citations"] = [
            {
                "title": "Source",
                "url": "https://example.com",
            }
        ]

        result = self.agent.execute(payload)

        self.assertTrue(result.data["approved"])

    def test_specialist_failure_is_blocked(self) -> None:
        payload = self.base_payload()
        payload["specialist_success"] = False

        result = self.agent.execute(payload)

        codes = {
            item["code"]
            for item in result.data["findings"]
        }

        self.assertIn(
            "SPECIALIST_REPORTED_FAILURE",
            codes,
        )
        self.assertFalse(result.data["approved"])

    def test_registry_accepts_quality_validator(self) -> None:
        registry = ConveraAgentRegistry()

        report = registry.register(
            QualityValidatorAgent
        )

        self.assertTrue(report["production_ready"])

        created = registry.create(
            "convera.quality_validator"
        )

        self.assertIsInstance(
            created,
            QualityValidatorAgent,
        )

    def test_missing_request_fails(self) -> None:
        payload = self.base_payload()
        payload["request"] = ""

        result = self.agent.execute(payload)

        self.assertFalse(result.success)
        self.assertEqual(
            result.error,
            "request is required.",
        )

    def test_whitespace_output_is_blocked(self) -> None:
        payload = self.base_payload()
        payload["output"] = "   \n  "

        result = self.agent.execute(payload)

        self.assertFalse(result.data["approved"])

        codes = {
            item["code"]
            for item in result.data["findings"]
        }

        self.assertIn("EMPTY_OUTPUT", codes)

    def test_structured_output_is_preserved(self) -> None:
        payload = self.base_payload()
        payload["output"] = {
            "content": (
                "The project discussion covers the mobile "
                "interface and deployment plan."
            ),
            "artifact": {
                "type": "document",
                "artifact_id": "doc-1",
            },
        }

        result = self.agent.execute(payload)

        self.assertTrue(result.data["approved"])
        self.assertEqual(
            result.data["validated_response"],
            payload["output"],
        )
        self.assertIsNot(
            result.data["validated_response"],
            payload["output"],
        )

    def test_non_activated_output_is_blocked(self) -> None:
        payload = self.base_payload()
        payload["activated"] = False

        result = self.agent.execute(payload)

        codes = {
            item["code"]
            for item in result.data["findings"]
        }

        self.assertIn(
            "CONVERA_NOT_ACTIVATED",
            codes,
        )
        self.assertFalse(result.data["approved"])

    def test_does_not_mutate_original_output(self) -> None:
        payload = self.base_payload()
        payload["output"] = {
            "content": (
                "Summarize the project discussion and "
                "deployment plan."
            ),
            "metadata": {
                "type": "summary",
                "items": ["mobile", "deployment"],
            },
        }

        original = {
            "content": payload["output"]["content"],
            "metadata": {
                "type": "summary",
                "items": ["mobile", "deployment"],
            },
        }

        self.agent.execute(payload)

        self.assertEqual(payload["output"], original)



if __name__ == "__main__":
    unittest.main()
