from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from backend.core.models import AgentResult


class BaseAgent(ABC):
    name: str = "base_agent"

    @abstractmethod
    def run(self, context: Dict[str, Any]) -> AgentResult:
        raise NotImplementedError

    def success(self, summary: str, data: Optional[Dict[str, Any]] = None) -> AgentResult:
        return AgentResult(
            agent_name=self.name,
            status="success",
            summary=summary,
            data=data or {},
        )

    def failed(self, summary: str, data: Optional[Dict[str, Any]] = None) -> AgentResult:
        return AgentResult(
            agent_name=self.name,
            status="failed",
            summary=summary,
            data=data or {},
        )
