from __future__ import annotations

from .project_knowledge_graph import ProjectKnowledgeGraph
from .project_knowledge_graph_builder import ProjectKnowledgeGraphBuilder
from .repository_discovery import FounderBrainRepositoryDiscovery
from .repository_source_adapter import (
    DEFAULT_PER_FILE_BYTE_LIMIT,
    DEFAULT_TOTAL_SNAPSHOT_BYTE_LIMIT,
)
from .repository_source_builder import (
    RepositorySourceBuilderError,
    build_repository_source_snapshot,
)
from .repository_source_understanding_builder import (
    RepositorySourceUnderstandingBuilderError,
    build_repository_understanding_from_source,
)


class ProjectKnowledgeGraphSourceIntegrationError(ValueError):
    """Raised when a project graph cannot be built from repository source."""


def build_project_knowledge_graph_from_discovery(
    discovery: FounderBrainRepositoryDiscovery,
    *,
    per_file_byte_limit: int = DEFAULT_PER_FILE_BYTE_LIMIT,
    total_snapshot_byte_limit: int = DEFAULT_TOTAL_SNAPSHOT_BYTE_LIMIT,
) -> ProjectKnowledgeGraph:
    """Build a project knowledge graph through the repository source pipeline."""

    try:
        snapshot = build_repository_source_snapshot(
            discovery,
            per_file_byte_limit=per_file_byte_limit,
            total_snapshot_byte_limit=total_snapshot_byte_limit,
        )
    except RepositorySourceBuilderError as error:
        raise ProjectKnowledgeGraphSourceIntegrationError(str(error)) from error

    try:
        understanding = build_repository_understanding_from_source(snapshot)
    except RepositorySourceUnderstandingBuilderError as error:
        raise ProjectKnowledgeGraphSourceIntegrationError(str(error)) from error

    try:
        return ProjectKnowledgeGraphBuilder().build(understanding)
    except (ValueError, RuntimeError) as error:
        raise ProjectKnowledgeGraphSourceIntegrationError(str(error)) from error


__all__ = [
    "ProjectKnowledgeGraphSourceIntegrationError",
    "build_project_knowledge_graph_from_discovery",
]
