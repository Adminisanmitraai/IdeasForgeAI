import pytest

from backend.founder_brain.universal_entities import (
    UniversalEntity,
    UniversalEntityType,
    UniversalRelationship,
    UniversalRelationshipType,
    deterministic_entity_id,
)


def test_entity_ids_are_deterministic_and_type_scoped():
    a = deterministic_entity_id(UniversalEntityType.PROJECT, "ForgeSocial")
    b = deterministic_entity_id(UniversalEntityType.PROJECT, " forgesocial ")
    c = deterministic_entity_id(UniversalEntityType.CLIENT, "ForgeSocial")
    assert a == b
    assert a != c


def test_all_required_universal_entity_types_exist():
    assert {item.value for item in UniversalEntityType} == {
        "company", "client", "opportunity", "project", "objective",
        "requirement", "task", "decision", "blocker", "artifact",
        "deployment", "agent", "certification",
    }


def test_entity_metadata_is_immutable_and_relationship_rejects_self_reference():
    entity = UniversalEntity.create(
        UniversalEntityType.PROJECT,
        name="ForgeSocial",
        external_key="forgesocial",
        metadata={"channel": "linkedin"},
    )
    with pytest.raises(TypeError):
        entity.metadata["channel"] = "instagram"
    with pytest.raises(ValueError, match="cannot target itself"):
        UniversalRelationship(
            source_entity_id=entity.entity_id,
            target_entity_id=entity.entity_id,
            relationship_type=UniversalRelationshipType.RELATED_TO,
        )


def test_relationship_types_cover_business_and_execution_context():
    values = {item.value for item in UniversalRelationshipType}
    assert {"has_project", "has_objective", "has_requirement", "has_task"} <= values
    assert {"has_decision", "has_blocker", "produces", "deploys", "certifies"} <= values
