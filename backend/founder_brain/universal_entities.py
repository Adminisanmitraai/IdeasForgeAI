from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from hashlib import sha256
from types import MappingProxyType
from typing import Any, Mapping

UNIVERSAL_ENTITY_CONTRACT_VERSION = "founder-brain.universal-entities.v1"


class UniversalEntityType(str, Enum):
    COMPANY = "company"
    CLIENT = "client"
    OPPORTUNITY = "opportunity"
    PROJECT = "project"
    OBJECTIVE = "objective"
    REQUIREMENT = "requirement"
    TASK = "task"
    DECISION = "decision"
    BLOCKER = "blocker"
    ARTIFACT = "artifact"
    DEPLOYMENT = "deployment"
    AGENT = "agent"
    CERTIFICATION = "certification"


class UniversalRelationshipType(str, Enum):
    OWNS = "owns"
    SERVES = "serves"
    HAS_OPPORTUNITY = "has_opportunity"
    HAS_PROJECT = "has_project"
    HAS_OBJECTIVE = "has_objective"
    HAS_REQUIREMENT = "has_requirement"
    HAS_TASK = "has_task"
    HAS_DECISION = "has_decision"
    HAS_BLOCKER = "has_blocker"
    PRODUCES = "produces"
    DEPLOYS = "deploys"
    ASSIGNED_TO = "assigned_to"
    CERTIFIES = "certifies"
    DEPENDS_ON = "depends_on"
    RELATED_TO = "related_to"


def _immutable_mapping(value: Mapping[str, Any] | None) -> Mapping[str, Any]:
    return MappingProxyType(dict(value or {}))


def deterministic_entity_id(entity_type: UniversalEntityType, external_key: str) -> str:
    normalized = external_key.strip().lower()
    if not normalized:
        raise ValueError("external_key must not be empty")
    digest = sha256(f"{entity_type.value}:{normalized}".encode("utf-8")).hexdigest()[:16]
    return f"{entity_type.value}:{digest}"


@dataclass(frozen=True, slots=True)
class UniversalEntity:
    entity_id: str
    entity_type: UniversalEntityType
    name: str
    project_id: str = ""
    status: str = "active"
    external_key: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)
    contract_version: str = UNIVERSAL_ENTITY_CONTRACT_VERSION

    def __post_init__(self) -> None:
        if not self.entity_id.strip():
            raise ValueError("entity_id must not be empty")
        if not self.name.strip():
            raise ValueError("entity name must not be empty")
        object.__setattr__(self, "metadata", _immutable_mapping(self.metadata))

    @classmethod
    def create(
        cls,
        entity_type: UniversalEntityType,
        *,
        name: str,
        external_key: str,
        project_id: str = "",
        status: str = "active",
        metadata: Mapping[str, Any] | None = None,
    ) -> "UniversalEntity":
        return cls(
            entity_id=deterministic_entity_id(entity_type, external_key),
            entity_type=entity_type,
            name=name,
            project_id=project_id,
            status=status,
            external_key=external_key,
            metadata=metadata or {},
        )


@dataclass(frozen=True, slots=True)
class UniversalRelationship:
    source_entity_id: str
    target_entity_id: str
    relationship_type: UniversalRelationshipType
    metadata: Mapping[str, Any] = field(default_factory=dict)
    contract_version: str = UNIVERSAL_ENTITY_CONTRACT_VERSION

    def __post_init__(self) -> None:
        if not self.source_entity_id.strip():
            raise ValueError("source_entity_id must not be empty")
        if not self.target_entity_id.strip():
            raise ValueError("target_entity_id must not be empty")
        if self.source_entity_id == self.target_entity_id:
            raise ValueError("relationship cannot target itself")
        object.__setattr__(self, "metadata", _immutable_mapping(self.metadata))


__all__ = [
    "UNIVERSAL_ENTITY_CONTRACT_VERSION",
    "UniversalEntityType",
    "UniversalRelationshipType",
    "UniversalEntity",
    "UniversalRelationship",
    "deterministic_entity_id",
]
