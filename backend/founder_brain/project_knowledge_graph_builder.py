from __future__ import annotations

from copy import deepcopy
from typing import Iterable

from .project_knowledge_graph import (
    ProjectGraphEdge,
    ProjectGraphEdgeType,
    ProjectGraphNode,
    ProjectGraphNodeType,
    ProjectKnowledgeGraph,
)
from .repository_understanding import FounderBrainRepositoryUnderstanding


class ProjectKnowledgeGraphBuilder:
    REPOSITORY_NODE_ID = "repository:root"

    def build(
        self,
        understanding: FounderBrainRepositoryUnderstanding,
    ) -> ProjectKnowledgeGraph:
        original_payload = deepcopy(understanding.model_dump())

        nodes: list[ProjectGraphNode] = [
            ProjectGraphNode(
                id=self.REPOSITORY_NODE_ID,
                name="Repository",
                node_type=ProjectGraphNodeType.REPOSITORY,
                path=".",
                metadata={
                    "understanding_version": understanding.understanding_version,
                    "read_only": understanding.read_only,
                },
            )
        ]
        edges: list[ProjectGraphEdge] = []

        self._append_nodes(
            nodes=nodes,
            edges=edges,
            values=understanding.languages,
            category="language",
            node_type=ProjectGraphNodeType.CONFIGURATION,
        )
        self._append_nodes(
            nodes=nodes,
            edges=edges,
            values=understanding.frameworks,
            category="framework",
            node_type=ProjectGraphNodeType.CONFIGURATION,
        )
        self._append_nodes(
            nodes=nodes,
            edges=edges,
            values=understanding.services,
            category="service",
            node_type=ProjectGraphNodeType.SERVICE,
        )
        self._append_nodes(
            nodes=nodes,
            edges=edges,
            values=understanding.modules,
            category="module",
            node_type=ProjectGraphNodeType.MODULE,
        )

        if understanding.model_dump() != original_payload:
            raise RuntimeError(
                "repository understanding was mutated during graph generation"
            )

        return ProjectKnowledgeGraph(
            nodes=tuple(nodes),
            edges=tuple(edges),
        )

    def _append_nodes(
        self,
        *,
        nodes: list[ProjectGraphNode],
        edges: list[ProjectGraphEdge],
        values: Iterable[str],
        category: str,
        node_type: ProjectGraphNodeType,
    ) -> None:
        for value in sorted(set(values), key=lambda item: item.casefold()):
            node_id = f"{category}:{self._slug(value)}"

            nodes.append(
                ProjectGraphNode(
                    id=node_id,
                    name=value,
                    node_type=node_type,
                    path="",
                    metadata={"category": category},
                )
            )
            edges.append(
                ProjectGraphEdge(
                    source=self.REPOSITORY_NODE_ID,
                    target=node_id,
                    edge_type=ProjectGraphEdgeType.CONTAINS,
                    metadata={"category": category},
                )
            )

    @staticmethod
    def _slug(value: str) -> str:
        normalized = value.strip().casefold()
        return "-".join(normalized.split())
