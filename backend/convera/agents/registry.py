"""Audited registry for Convera agents."""

from __future__ import annotations

from typing import Dict, Type

from .audit_agent import AuditAgent
from .base_agent import BaseConveraAgent


class AgentAuditError(RuntimeError):
    """Raised when an agent fails registration audit."""


class ConveraAgentRegistry:
    """Stores only production-ready agents approved by Audit Agent."""

    def __init__(self) -> None:
        self._audit_agent = AuditAgent()
        self._agents: Dict[
            str,
            Type[BaseConveraAgent],
        ] = {}
        self._audit_reports: Dict[str, dict] = {}

    def register(
        self,
        agent_class: Type[BaseConveraAgent],
    ) -> dict:
        report = self._audit_agent.audit(agent_class)

        if not report["approved"]:
            raise AgentAuditError(
                f"{agent_class.__name__} failed audit: "
                f"{report['findings']}"
            )

        if not report["production_ready"]:
            raise AgentAuditError(
                f"{agent_class.__name__} is not production ready: "
                f"score={report['overall_score']}"
            )

        agent_id = agent_class.metadata.agent_id

        if agent_id in self._agents:
            raise ValueError(
                f"Agent already registered: {agent_id}"
            )

        self._agents[agent_id] = agent_class
        self._audit_reports[agent_id] = report

        return report

    def create(
        self,
        agent_id: str,
    ) -> BaseConveraAgent:
        agent_class = self._agents.get(agent_id)

        if agent_class is None:
            raise KeyError(
                f"Unknown or unaudited agent: {agent_id}"
            )

        return agent_class()

    def registered_agents(self) -> list[str]:
        return sorted(self._agents)

    def audit_report(self, agent_id: str) -> dict:
        if agent_id not in self._audit_reports:
            raise KeyError(
                f"No audit report for agent: {agent_id}"
            )

        return dict(self._audit_reports[agent_id])

    def audit_registered_agents(self) -> dict:
        reports = {
            agent_id: self._audit_agent.audit(agent_class)
            for agent_id, agent_class in self._agents.items()
        }

        self._audit_reports.update(reports)

        return reports
