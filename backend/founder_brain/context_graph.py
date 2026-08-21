from __future__ import annotations

from dataclasses import dataclass

from .universal_entities import (
    UniversalEntity,
    UniversalRelationship,
    UniversalRelationshipType,
)

CONTEXT_GRAPH_CONTRACT_VERSION = "founder-brain.context-graph.v1"


@dataclass(frozen=True, slots=True)
class ContextGraph:
    entities: tuple[UniversalEntity, ...] = ()
    relationships: tuple[UniversalRelationship, ...] = ()
    contract_version: str = CONTEXT_GRAPH_CONTRACT_VERSION

    def __post_init__(self) -> None:
        ordered_entities = tuple(sorted(self.entities, key=lambda item: item.entity_id))
        entity_ids = [item.entity_id for item in ordered_entities]
        if len(entity_ids) != len(set(entity_ids)):
            raise ValueError("duplicate universal entity id")
        known = set(entity_ids)
        ordered_relationships = tuple(sorted(
            self.relationships,
            key=lambda item: (
                item.source_entity_id,
                item.target_entity_id,
                item.relationship_type.value,
            ),
        ))
        for relationship in ordered_relationships:
            if relationship.source_entity_id not in known:
                raise ValueError("relationship source references unknown entity")
            if relationship.target_entity_id not in known:
                raise ValueError("relationship target references unknown entity")
        object.__setattr__(self, "entities", ordered_entities)
        object.__setattr__(self, "relationships", ordered_relationships)

    def get(self, entity_id: str) -> UniversalEntity | None:
        return next((item for item in self.entities if item.entity_id == entity_id), None)

    def outgoing(
        self,
        entity_id: str,
        relationship_type: UniversalRelationshipType | None = None,
    ) -> tuple[UniversalRelationship, ...]:
        return tuple(
            item for item in self.relationships
            if item.source_entity_id == entity_id
            and (relationship_type is None or item.relationship_type is relationship_type)
        )
