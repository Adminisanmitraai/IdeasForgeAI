from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

PROJECT_KNOWLEDGE_GRAPH_CONTRACT_VERSION = "1.0"


class ProjectGraphNodeType(str, Enum):
    REPOSITORY = "repository"
    DIRECTORY = "directory"
    FILE = "file"
    MODULE = "module"
    PACKAGE = "package"
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    API_ROUTE = "api_route"
    SERVICE = "service"
    MODEL = "model"
    CONFIGURATION = "configuration"
    FRONTEND_PAGE = "frontend_page"
    COMPONENT = "component"
    DATABASE_MODEL = "database_model"


class ProjectGraphEdgeType(str, Enum):
    CONTAINS = "contains"
    IMPORTS = "imports"
    DEFINES = "defines"
    DEPENDS_ON = "depends_on"
    CALLS = "calls"
    IMPLEMENTS = "implements"
    REFERENCES = "references"
    EXPOSES = "exposes"
    USES = "uses"


def _immutable_mapping(value: Mapping[str, Any] | None) -> Mapping[str, Any]:
    return MappingProxyType(dict(value or {}))


@dataclass(frozen=True, slots=True)
class ProjectGraphNode:
    id: str
    name: str
    node_type: ProjectGraphNodeType
    path: str
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("node id must not be empty")
        if not self.name.strip():
            raise ValueError("node name must not be empty")
        object.__setattr__(self, "metadata", _immutable_mapping(self.metadata))

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "node_type": self.node_type.value,
            "path": self.path,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "ProjectGraphNode":
        return cls(
            id=str(payload["id"]),
            name=str(payload["name"]),
            node_type=ProjectGraphNodeType(payload["node_type"]),
            path=str(payload["path"]),
            metadata=payload.get("metadata", {}),
        )


@dataclass(frozen=True, slots=True)
class ProjectGraphEdge:
    source: str
    target: str
    edge_type: ProjectGraphEdgeType
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.source.strip():
            raise ValueError("edge source must not be empty")
        if not self.target.strip():
            raise ValueError("edge target must not be empty")
        object.__setattr__(self, "metadata", _immutable_mapping(self.metadata))

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "edge_type": self.edge_type.value,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "ProjectGraphEdge":
        return cls(
            source=str(payload["source"]),
            target=str(payload["target"]),
            edge_type=ProjectGraphEdgeType(payload["edge_type"]),
            metadata=payload.get("metadata", {}),
        )


@dataclass(frozen=True, slots=True)
class ProjectKnowledgeGraph:
    contract_version: str = PROJECT_KNOWLEDGE_GRAPH_CONTRACT_VERSION
    nodes: tuple[ProjectGraphNode, ...] = ()
    edges: tuple[ProjectGraphEdge, ...] = ()

    def __post_init__(self) -> None:
        ordered_nodes = tuple(sorted(self.nodes, key=lambda node: node.id))
        node_ids = [node.id for node in ordered_nodes]

        if len(node_ids) != len(set(node_ids)):
            raise ValueError("duplicate project graph node id")

        ordered_edges = tuple(
            sorted(
                self.edges,
                key=lambda edge: (
                    edge.source,
                    edge.target,
                    edge.edge_type.value,
                    repr(sorted(dict(edge.metadata).items())),
                ),
            )
        )

        edge_keys = [
            (
                edge.source,
                edge.target,
                edge.edge_type.value,
                repr(sorted(dict(edge.metadata).items())),
            )
            for edge in ordered_edges
        ]

        if len(edge_keys) != len(set(edge_keys)):
            raise ValueError("duplicate project graph edge")

        object.__setattr__(self, "nodes", ordered_nodes)
        object.__setattr__(self, "edges", ordered_edges)

    def node_count(self) -> int:
        return len(self.nodes)

    def edge_count(self) -> int:
        return len(self.edges)

    def get_node(self, node_id: str) -> ProjectGraphNode | None:
        return next((node for node in self.nodes if node.id == node_id), None)

    def to_dict(self) -> dict[str, Any]:
        return {
            "contract_version": self.contract_version,
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "ProjectKnowledgeGraph":
        return cls(
            contract_version=str(
                payload.get(
                    "contract_version",
                    PROJECT_KNOWLEDGE_GRAPH_CONTRACT_VERSION,
                )
            ),
            nodes=tuple(
                ProjectGraphNode.from_dict(item)
                for item in payload.get("nodes", [])
            ),
            edges=tuple(
                ProjectGraphEdge.from_dict(item)
                for item in payload.get("edges", [])
            ),
        )
