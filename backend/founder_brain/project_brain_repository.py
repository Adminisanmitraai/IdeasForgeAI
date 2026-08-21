from __future__ import annotations

import json
from dataclasses import dataclass
from hashlib import sha256
from typing import Any, Mapping

from .context_graph import CONTEXT_GRAPH_CONTRACT_VERSION, ContextGraph
from .universal_entities import (
    UniversalEntity,
    UniversalEntityType,
    UniversalRelationship,
    UniversalRelationshipType,
)

PROJECT_BRAIN_REPOSITORY_VERSION = "founder-brain.project-repository.v1"


class ProjectBrainRepositoryError(RuntimeError):
    pass


class ProjectBrainCorruptionError(ProjectBrainRepositoryError):
    pass


def canonical_project_brain_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":"))
def _sha256_json(value: Any) -> str:
    return sha256(canonical_project_brain_json(value).encode("utf-8")).hexdigest()


def entity_payload(entity: UniversalEntity) -> dict[str, Any]:
    return {
        "entity_id": entity.entity_id,
        "entity_type": entity.entity_type.value,
        "name": entity.name,
        "project_id": entity.project_id,
        "status": entity.status,
        "external_key": entity.external_key,
        "metadata": dict(entity.metadata),
        "contract_version": entity.contract_version,
    }


def relationship_payload(item: UniversalRelationship) -> dict[str, Any]:
    return {
        "source_entity_id": item.source_entity_id,
        "target_entity_id": item.target_entity_id,
        "relationship_type": item.relationship_type.value,
        "metadata": dict(item.metadata),
        "contract_version": item.contract_version,
    }
def graph_payload(graph: ContextGraph) -> dict[str, Any]:
    return {
        "contract_version": graph.contract_version,
        "entities": [entity_payload(item) for item in graph.entities],
        "relationships": [relationship_payload(item) for item in graph.relationships],
    }


def hydrate_graph(payload: Mapping[str, Any]) -> ContextGraph:
    entities = tuple(
        UniversalEntity(
            entity_id=str(item["entity_id"]),
            entity_type=UniversalEntityType(str(item["entity_type"])),
            name=str(item["name"]),
            project_id=str(item.get("project_id", "")),
            status=str(item.get("status", "active")),
            external_key=str(item.get("external_key", "")),
            metadata=item.get("metadata", {}),
            contract_version=str(item.get("contract_version", "founder-brain.universal-entities.v1")),
        )
        for item in payload.get("entities", [])
    )
    relationships = tuple(
        UniversalRelationship(
            source_entity_id=str(item["source_entity_id"]),
            target_entity_id=str(item["target_entity_id"]),
            relationship_type=UniversalRelationshipType(str(item["relationship_type"])),
            metadata=item.get("metadata", {}),
            contract_version=str(item.get("contract_version", "founder-brain.universal-entities.v1")),
        )
        for item in payload.get("relationships", [])
    )
    return ContextGraph(
        entities,
        relationships,
        str(payload.get("contract_version", CONTEXT_GRAPH_CONTRACT_VERSION)),
    )


@dataclass(frozen=True, slots=True)
class ProjectBrainSnapshot:
    project_id: str
    project_name: str
    version: int
    stored_at: str
    graph: ContextGraph
    graph_sha256: str
    snapshot_sha256: str
    schema_version: str = PROJECT_BRAIN_REPOSITORY_VERSION
    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "project_id": self.project_id,
            "project_name": self.project_name,
            "version": self.version,
            "stored_at": self.stored_at,
            "graph": graph_payload(self.graph),
            "graph_sha256": self.graph_sha256,
            "snapshot_sha256": self.snapshot_sha256,
        }


def build_project_brain_snapshot(
    project_id: str,
    project_name: str,
    version: int,
    stored_at: str,
    graph: ContextGraph,
) -> ProjectBrainSnapshot:
    graph_data = graph_payload(graph)
    base = {
        "schema_version": PROJECT_BRAIN_REPOSITORY_VERSION,
        "project_id": project_id,
        "project_name": project_name,
        "version": version,
        "stored_at": stored_at,
        "graph": graph_data,
        "graph_sha256": _sha256_json(graph_data),
    }
    return ProjectBrainSnapshot(
        project_id=project_id,
        project_name=project_name,
        version=version,
        stored_at=stored_at,
        graph=graph,
        graph_sha256=str(base["graph_sha256"]),
        snapshot_sha256=_sha256_json(base),
    )
def restore_project_brain_snapshot(raw: str | bytes) -> ProjectBrainSnapshot:
    try:
        payload = json.loads(raw)
        graph = hydrate_graph(payload["graph"])
        snapshot = ProjectBrainSnapshot(
            project_id=str(payload["project_id"]),
            project_name=str(payload["project_name"]),
            version=int(payload["version"]),
            stored_at=str(payload["stored_at"]),
            graph=graph,
            graph_sha256=str(payload["graph_sha256"]),
            snapshot_sha256=str(payload["snapshot_sha256"]),
            schema_version=str(payload["schema_version"]),
        )
    except Exception as error:
        raise ProjectBrainCorruptionError("invalid project brain snapshot") from error
    expected = build_project_brain_snapshot(
        snapshot.project_id,
        snapshot.project_name,
        snapshot.version,
        snapshot.stored_at,
        snapshot.graph,
    )
    if snapshot != expected:
        raise ProjectBrainCorruptionError("project brain snapshot integrity mismatch")
    return snapshot


__all__ = [
    "PROJECT_BRAIN_REPOSITORY_VERSION",
    "ProjectBrainSnapshot",
    "ProjectBrainRepositoryError",
    "ProjectBrainCorruptionError",
    "canonical_project_brain_json",
    "build_project_brain_snapshot",
    "restore_project_brain_snapshot",
    "graph_payload",
]
