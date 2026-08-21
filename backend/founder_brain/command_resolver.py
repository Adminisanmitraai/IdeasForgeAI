from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re

from .context_graph import ContextGraph
from .universal_entities import UniversalEntity, UniversalEntityType

FOUNDER_COMMAND_RESOLVER_VERSION = "founder-brain.command-resolver.v1"


class FounderCommandKind(str, Enum):
    CONTINUE = "continue"
    START_NEXT = "start_next"
    STATUS = "status"
    BLOCKERS = "blockers"
    AUDIT = "audit"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class FounderCommandResolution:
    command: FounderCommandKind
    project: UniversalEntity | None
    milestone: str
    next_action: str
    blockers: tuple[UniversalEntity, ...] = ()
    confidence: float = 0.0
    execution_requested: bool = False
    contract_version: str = FOUNDER_COMMAND_RESOLVER_VERSION
def _normalize(value: object) -> str:
    return " ".join(str(value or "").strip().lower().split())


def _command_kind(message: str) -> FounderCommandKind:
    if re.search(r"\b(block|blocking|blocker|blocked)\b", message):
        return FounderCommandKind.BLOCKERS
    if re.search(r"\b(status|progress|where are we|what.*left)\b", message):
        return FounderCommandKind.STATUS
    if re.search(r"\b(audit|review|inspect)\b", message):
        return FounderCommandKind.AUDIT
    if re.search(r"\b(start|begin)\b.*\b(next|phase|action)\b", message):
        return FounderCommandKind.START_NEXT
    if re.search(r"\b(continue|resume|proceed)\b", message):
        return FounderCommandKind.CONTINUE
    return FounderCommandKind.UNKNOWN


def _projects(graph: ContextGraph) -> tuple[UniversalEntity, ...]:
    return tuple(item for item in graph.entities if item.entity_type is UniversalEntityType.PROJECT)


def _match_project(message: str, graph: ContextGraph, active_project_id: str) -> UniversalEntity | None:
    projects = _projects(graph)
    ranked = sorted(
        (item for item in projects if _normalize(item.name) and _normalize(item.name) in message),
        key=lambda item: (-len(_normalize(item.name)), item.entity_id),
    )
    if ranked:
        return ranked[0]
    if active_project_id:
        return next((item for item in projects if item.entity_id == active_project_id or item.project_id == active_project_id or _normalize(item.name) == _normalize(active_project_id)), None)
    return projects[0] if len(projects) == 1 else None
def resolve_founder_command(
    message: object,
    *,
    graph: ContextGraph,
    active_project_id: str = "",
    milestone: str = "",
    recommended_next_action: str = "",
) -> FounderCommandResolution:
    normalized = _normalize(message)
    if not normalized:
        raise ValueError("founder command must not be empty")
    command = _command_kind(normalized)
    project = _match_project(normalized, graph, active_project_id)
    project_key = project.project_id if project is not None else active_project_id
    blockers = tuple(
        item for item in graph.entities
        if item.entity_type is UniversalEntityType.BLOCKER
        and (not project_key or item.project_id == project_key)
        and item.status.lower() not in {"closed", "resolved", "done"}
    )
    confidence = 0.95 if command is not FounderCommandKind.UNKNOWN and project is not None else 0.75 if command is not FounderCommandKind.UNKNOWN else 0.25
    next_action = recommended_next_action.strip()
    if command is FounderCommandKind.BLOCKERS and blockers:
        next_action = f"Resolve blocker: {blockers[0].name}"
    return FounderCommandResolution(
        command=command,
        project=project,
        milestone=milestone.strip(),
        next_action=next_action,
        blockers=tuple(sorted(blockers, key=lambda item: item.entity_id)),
        confidence=confidence,
        execution_requested=False,
    )


__all__ = ["FOUNDER_COMMAND_RESOLVER_VERSION", "FounderCommandKind", "FounderCommandResolution", "resolve_founder_command"]
