from __future__ import annotations

from dataclasses import dataclass, field as dc_field
from typing import Any, Literal, Mapping

CONTRACT_VERSION = "platform.common.v1"

ActorRole = Literal[
    "viewer",
    "developer",
    "maintainer",
    "admin",
    "founder",
    "founder_admin",
    "system",
]


@dataclass(frozen=True)
class ContractMetadata:
    contract_version: str
    correlation_id: str
    causation_id: str = ""
    source: str = ""
    metadata: Mapping[str, Any] = dc_field(default_factory=dict)


@dataclass(frozen=True)
class ActorContext:
    actor_id: str
    role: ActorRole
    authenticated: bool
    session_id: str = ""
    interface: str = ""
    correlation_id: str = ""
    permission_scopes: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = dc_field(default_factory=dict)


@dataclass(frozen=True)
class ErrorDetail:
    code: str
    message: str
    field: str = ""
    metadata: Mapping[str, Any] = dc_field(default_factory=dict)


@dataclass(frozen=True)
class OperationReceipt:
    ok: bool
    operation_id: str
    contract_version: str
    errors: tuple[ErrorDetail, ...] = ()
    warnings: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = dc_field(default_factory=dict)
