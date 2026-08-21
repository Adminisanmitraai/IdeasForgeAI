"""Founder Brain operating-state and universal context contracts."""

from .models import FOUNDER_BRAIN_API_CONTRACT_VERSION, FOUNDER_BRAIN_STATE_SCHEMA_VERSION
from .router import ROUTE_PREFIX, create_founder_brain_router
from .service import FounderBrainReadService
from .universal_entities import (
    UNIVERSAL_ENTITY_CONTRACT_VERSION,
    UniversalEntity,
    UniversalEntityType,
    UniversalRelationship,
    UniversalRelationshipType,
    deterministic_entity_id,
)
from .context_graph import CONTEXT_GRAPH_CONTRACT_VERSION, ContextGraph
from .context_graph_adapter import CONTEXT_GRAPH_ADAPTER_VERSION, adapt_project_knowledge_graph
from .project_brain_repository import (
    PROJECT_BRAIN_REPOSITORY_VERSION,
    ProjectBrainCorruptionError,
    ProjectBrainRepositoryError,
    ProjectBrainSnapshot,
    build_project_brain_snapshot,
    canonical_project_brain_json,
    restore_project_brain_snapshot,
)
__all__ = [
    "FOUNDER_BRAIN_API_CONTRACT_VERSION",
    "FOUNDER_BRAIN_STATE_SCHEMA_VERSION",
    "FounderBrainReadService",
    "ROUTE_PREFIX",
    "create_founder_brain_router",
    "UNIVERSAL_ENTITY_CONTRACT_VERSION",
    "UniversalEntity",
    "UniversalEntityType",
    "UniversalRelationship",
    "UniversalRelationshipType",
    "deterministic_entity_id",
    "CONTEXT_GRAPH_CONTRACT_VERSION",
    "ContextGraph",
    "CONTEXT_GRAPH_ADAPTER_VERSION",
    "adapt_project_knowledge_graph",
    "PROJECT_BRAIN_REPOSITORY_VERSION",
    "ProjectBrainSnapshot",
    "ProjectBrainRepositoryError",
    "ProjectBrainCorruptionError",
    "build_project_brain_snapshot",
    "canonical_project_brain_json",
    "restore_project_brain_snapshot",
]

from .command_resolver import (
    FOUNDER_COMMAND_RESOLVER_VERSION,
    FounderCommandKind,
    FounderCommandResolution,
    resolve_founder_command,
)

__all__ += (
    "FOUNDER_COMMAND_RESOLVER_VERSION",
    "FounderCommandKind",
    "FounderCommandResolution",
    "resolve_founder_command",
)
