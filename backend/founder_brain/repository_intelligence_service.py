from __future__ import annotations

from .project_knowledge_graph import ProjectKnowledgeGraph
from .project_knowledge_graph_source_integration import (
    ProjectKnowledgeGraphSourceIntegrationError,
    build_project_knowledge_graph_from_discovery,
)
from .repository_discovery import FounderBrainRepositoryDiscovery
from .repository_source_adapter import (
    DEFAULT_PER_FILE_BYTE_LIMIT,
    DEFAULT_TOTAL_SNAPSHOT_BYTE_LIMIT,
)


class RepositoryIntelligenceServiceError(ValueError):
    """Raised when repository intelligence cannot be built."""


class RepositoryIntelligenceService:
    """Read-only orchestration service for repository intelligence."""

    def build_repository_intelligence(
        self,
        discovery: FounderBrainRepositoryDiscovery,
        *,
        per_file_byte_limit: int = DEFAULT_PER_FILE_BYTE_LIMIT,
        total_snapshot_byte_limit: int = DEFAULT_TOTAL_SNAPSHOT_BYTE_LIMIT,
    ) -> ProjectKnowledgeGraph:
        """Build a project graph through the validated source pipeline."""

        if not isinstance(discovery, FounderBrainRepositoryDiscovery):
            raise RepositoryIntelligenceServiceError(
                "discovery must be a FounderBrainRepositoryDiscovery"
            )

        try:
            return build_project_knowledge_graph_from_discovery(
                discovery,
                per_file_byte_limit=per_file_byte_limit,
                total_snapshot_byte_limit=total_snapshot_byte_limit,
            )
        except ProjectKnowledgeGraphSourceIntegrationError as error:
            raise RepositoryIntelligenceServiceError(str(error)) from error


__all__ = [
    "RepositoryIntelligenceService",
    "RepositoryIntelligenceServiceError",
]
