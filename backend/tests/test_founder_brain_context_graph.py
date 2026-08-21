import pytest

from backend.founder_brain.context_graph import ContextGraph
from backend.founder_brain.universal_entities import (
    UniversalEntity,
    UniversalEntityType,
    UniversalRelationship,
    UniversalRelationshipType,
)


def entity(kind, key):
    return UniversalEntity.create(kind, name=key, external_key=key)


def test_context_graph_orders_entities_and_supports_outgoing_queries():
    project = entity(UniversalEntityType.PROJECT, "project-1")
    task = entity(UniversalEntityType.TASK, "task-1")
    relationship = UniversalRelationship(
        project.entity_id,
        task.entity_id,
        UniversalRelationshipType.HAS_TASK,
    )
    graph = ContextGraph((task, project), (relationship,))
    assert [item.entity_id for item in graph.entities] == sorted([project.entity_id, task.entity_id])
    assert graph.get(project.entity_id) == project
    assert graph.outgoing(project.entity_id) == (relationship,)


def test_context_graph_rejects_unknown_relationship_targets():
    project = entity(UniversalEntityType.PROJECT, "project-1")
    relationship = UniversalRelationship(
        project.entity_id,
        "task:missing",
        UniversalRelationshipType.HAS_TASK,
    )
    with pytest.raises(ValueError, match="target references unknown entity"):
        ContextGraph((project,), (relationship,))


def test_context_graph_filters_relationship_type():
    project = entity(UniversalEntityType.PROJECT, "project-1")
    task = entity(UniversalEntityType.TASK, "task-1")
    artifact = entity(UniversalEntityType.ARTIFACT, "artifact-1")
    graph = ContextGraph(
        (project, task, artifact),
        (
            UniversalRelationship(project.entity_id, task.entity_id, UniversalRelationshipType.HAS_TASK),
            UniversalRelationship(project.entity_id, artifact.entity_id, UniversalRelationshipType.PRODUCES),
        ),
    )
    assert len(graph.outgoing(project.entity_id, UniversalRelationshipType.HAS_TASK)) == 1
