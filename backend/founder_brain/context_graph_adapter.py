from __future__ import annotations

from .context_graph import ContextGraph
from .project_knowledge_graph import ProjectKnowledgeGraph
from .universal_entities import (
    UniversalEntity,
    UniversalEntityType,
    UniversalRelationship,
    UniversalRelationshipType,
)

CONTEXT_GRAPH_ADAPTER_VERSION = "founder-brain.context-graph-adapter.v1"


def adapt_project_knowledge_graph(
    graph: ProjectKnowledgeGraph,
    *,
    project_id: str,
    project_name: str,
) -> ContextGraph:
    project = UniversalEntity.create(
        UniversalEntityType.PROJECT,
        name=project_name,
        external_key=project_id,
        project_id=project_id,
        metadata={"legacy_contract": graph.contract_version},
    )
    entities = [project]
    relationships: list[UniversalRelationship] = []
    legacy_to_universal: dict[str, str] = {}
    for node in graph.nodes:
        entity = UniversalEntity.create(
            UniversalEntityType.ARTIFACT,
            name=node.name,
            external_key=f"{project_id}:{node.id}",
            project_id=project_id,
            metadata={
                "legacy_node_id": node.id,
                "legacy_node_type": node.node_type.value,
                "path": node.path,
                **dict(node.metadata),
            },
        )
        entities.append(entity)
        legacy_to_universal[node.id] = entity.entity_id
        relationships.append(UniversalRelationship(
            source_entity_id=project.entity_id,
            target_entity_id=entity.entity_id,
            relationship_type=UniversalRelationshipType.PRODUCES,
            metadata={"source": "project_knowledge_graph"},
        ))

    for edge in graph.edges:
        source = legacy_to_universal.get(edge.source)
        target = legacy_to_universal.get(edge.target)
        if source is None or target is None:
            continue
        relationships.append(UniversalRelationship(
            source_entity_id=source,
            target_entity_id=target,
            relationship_type=UniversalRelationshipType.RELATED_TO,
            metadata={
                "legacy_edge_type": edge.edge_type.value,
                **dict(edge.metadata),
            },
        ))
    return ContextGraph(
        entities=tuple(entities),
        relationships=tuple(relationships),
    )


__all__ = [
    "CONTEXT_GRAPH_ADAPTER_VERSION",
    "adapt_project_knowledge_graph",
]
