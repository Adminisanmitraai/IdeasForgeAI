"""Run Chief Architect audits for all Convera agents."""

from __future__ import annotations

import json
import sys

from backend.convera.agents.audit_agent import AuditAgent
from backend.convera.agents.mention_activation_agent import (
    MentionActivationAgent,
)
from backend.convera.agents.conversation_context_agent import (
    ConversationContextAgent,
)
from backend.convera.agents.intent_router_agent import (
    IntentRouterAgent,
)
from backend.convera.agents.permission_privacy_agent import (
    PermissionPrivacyAgent,
)
from backend.convera.agents.conversation_memory_agent import (
    ConversationMemoryAgent,
)
from backend.convera.agents.convera_orchestrator_agent import (
    ConveraOrchestratorAgent,
)
from backend.convera.agents.quality_validator_agent import (
    QualityValidatorAgent,
)


AGENT_CLASSES = [
    AuditAgent,
    MentionActivationAgent,
    ConversationContextAgent,
    IntentRouterAgent,
    PermissionPrivacyAgent,
    ConversationMemoryAgent,
    ConveraOrchestratorAgent,
    QualityValidatorAgent,
]


def main() -> int:
    auditor = AuditAgent()

    reports = {
        agent_class.metadata.agent_id:
            auditor.audit(agent_class)
        for agent_class in AGENT_CLASSES
    }

    print(json.dumps(reports, indent=2))

    failed = [
        agent_id
        for agent_id, report in reports.items()
        if not report["approved"]
        or not report["production_ready"]
    ]

    print("\nCONVERA AGENT AUDIT SUMMARY")

    for agent_id, report in reports.items():
        status = (
            "PRODUCTION READY"
            if report["production_ready"]
            else "FAILED"
        )

        print(
            f"- {agent_id}: "
            f"{report['overall_score']}% | {status}"
        )

        for category, score in (
            report["category_scores"].items()
        ):
            print(f"    {category}: {score}%")

    if failed:
        print(
            "\nAUDIT FAILED: " + ", ".join(failed),
            file=sys.stderr,
        )
        return 1

    print("\nAUDIT PASSED: all Convera agents approved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
