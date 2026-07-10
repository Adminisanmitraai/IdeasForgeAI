"""Standard-library tests for Convera Audit Agent V2."""

from __future__ import annotations

import unittest
from typing import Any, Mapping

from backend.convera.agents.audit_agent import AuditAgent
from backend.convera.agents.base_agent import (
    AgentMetadata,
    AgentResult,
    BaseConveraAgent,
)
from backend.convera.agents.mention_activation_agent import (
    MentionActivationAgent,
)
from backend.convera.agents.registry import (
    AgentAuditError,
    ConveraAgentRegistry,
)


class UnsafeActionAgent(BaseConveraAgent):
    """Deliberately unsafe agent used to verify audit blocking."""

    metadata = AgentMetadata(
        agent_id="convera.unsafe_test",
        name="Unsafe Test Agent",
        version="1.0.0",
        description=(
            "Unsafe test agent used only to verify that the "
            "Chief Architect Audit Agent blocks unsafe actions."
        ),
        category="test",
        requires_user_approval=False,
        accesses_external_network=False,
        performs_external_actions=True,
    )

    def execute(
        self,
        payload: Mapping[str, Any],
    ) -> AgentResult:
        return AgentResult(
            success=True,
            agent_id=self.metadata.agent_id,
            data={},
        )


class AuditAgentV2Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.auditor = AuditAgent()

    def test_audit_agent_is_production_ready(self) -> None:
        report = self.auditor.audit(AuditAgent)

        self.assertTrue(report["approved"])
        self.assertTrue(report["production_ready"])
        self.assertGreaterEqual(
            report["overall_score"],
            85,
        )

    def test_mention_agent_is_production_ready(self) -> None:
        report = self.auditor.audit(
            MentionActivationAgent
        )

        self.assertTrue(report["approved"])
        self.assertTrue(report["production_ready"])
        self.assertEqual(
            report["blocking_findings"],
            0,
        )

    def test_category_scores_exist(self) -> None:
        report = self.auditor.audit(
            MentionActivationAgent
        )

        expected = {
            "architecture",
            "code_quality",
            "runtime",
            "safety",
            "maintainability",
            "convera_standards",
        }

        self.assertEqual(
            set(report["category_scores"]),
            expected,
        )

    def test_unsafe_action_agent_is_blocked(self) -> None:
        report = self.auditor.audit(
            UnsafeActionAgent
        )

        self.assertFalse(report["approved"])
        self.assertFalse(report["production_ready"])

        codes = {
            finding["code"]
            for finding in report["findings"]
        }

        self.assertIn(
            "ACTION_WITHOUT_APPROVAL",
            codes,
        )

    def test_registry_accepts_approved_agent(self) -> None:
        registry = ConveraAgentRegistry()

        report = registry.register(
            MentionActivationAgent
        )

        self.assertTrue(report["production_ready"])
        self.assertIn(
            "convera.mention_activation",
            registry.registered_agents(),
        )

    def test_registry_rejects_unsafe_agent(self) -> None:
        registry = ConveraAgentRegistry()

        with self.assertRaises(AgentAuditError):
            registry.register(UnsafeActionAgent)


if __name__ == "__main__":
    unittest.main()
