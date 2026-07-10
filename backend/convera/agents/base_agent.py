"""Shared contracts for all Convera agents."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Any, ClassVar, Dict, Mapping


@dataclass(frozen=True)
class AgentMetadata:
    """Machine-readable declaration required from every Convera agent."""

    agent_id: str
    name: str
    version: str
    description: str
    category: str
    requires_user_approval: bool
    accesses_external_network: bool
    performs_external_actions: bool


@dataclass
class AgentResult:
    """Standard result returned by every Convera agent."""

    success: bool
    agent_id: str
    data: Dict[str, Any]
    error: str | None = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class BaseConveraAgent(ABC):
    """Base class enforcing the minimum Convera agent interface."""

    metadata: ClassVar[AgentMetadata]

    @abstractmethod
    def execute(self, payload: Mapping[str, Any]) -> AgentResult:
        """Run the agent against a validated input payload."""

    def health_check(self) -> AgentResult:
        """Return a deterministic local health result."""

        metadata = getattr(self, "metadata", None)

        if not isinstance(metadata, AgentMetadata):
            return AgentResult(
                success=False,
                agent_id=self.__class__.__name__,
                data={},
                error="Agent metadata is missing or invalid.",
            )

        return AgentResult(
            success=True,
            agent_id=metadata.agent_id,
            data={
                "status": "healthy",
                "version": metadata.version,
            },
        )

    @classmethod
    def metadata_dict(cls) -> Dict[str, Any]:
        metadata = getattr(cls, "metadata", None)

        if not isinstance(metadata, AgentMetadata):
            return {}

        return asdict(metadata)