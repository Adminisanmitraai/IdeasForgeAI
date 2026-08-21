from backend.founder_brain.context_graph_adapter import adapt_project_knowledge_graph
from backend.founder_brain.project_knowledge_graph import (
    ProjectGraphEdge,
    ProjectGraphEdgeType,
    ProjectGraphNode,
    ProjectGraphNodeType,
    ProjectKnowledgeGraph,
)
from backend.founder_brain.universal_entities import UniversalEntityType, UniversalRelationshipType


def test_legacy_project_graph_adapts_without_losing_node_or_edge_lineage():
    repo = ProjectGraphNode(
        id="repository:root",
        name="root",
        node_type=ProjectGraphNodeType.REPOSITORY,
        path=".",
    )
    file_node = ProjectGraphNode(
        id="file:a.py",
        name="a.py",
        node_type=ProjectGraphNodeType.FILE,
        path="a.py",
    )
    graph = ProjectKnowledgeGraph(
        nodes=(repo, file_node),
        edges=(ProjectGraphEdge("repository:root", "file:a.py", ProjectGraphEdgeType.CONTAINS),),
    )
    adapted = adapt_project_knowledge_graph(
        graph,
        project_id="ideasforgeai",
        project_name="IdeasForgeAI",
    )
    project_entities = [item for item in adapted.entities if item.entity_type is UniversalEntityType.PROJECT]
    artifact_entities = [item for item in adapted.entities if item.entity_type is UniversalEntityType.ARTIFACT]
    assert len(project_entities) == 1
    assert len(artifact_entities) == 2
    assert {item.metadata["legacy_node_id"] for item in artifact_entities} == {"repository:root", "file:a.py"}

    project_links = [item for item in adapted.relationships if item.relationship_type is UniversalRelationshipType.PRODUCES]
    legacy_links = [item for item in adapted.relationships if item.relationship_type is UniversalRelationshipType.RELATED_TO]
    assert len(project_links) == 2
    assert len(legacy_links) == 1
    assert legacy_links[0].metadata["legacy_edge_type"] == "contains"
