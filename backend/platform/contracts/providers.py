from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Mapping, Protocol, Sequence

from .common import ActorContext

PROVIDER_GATEWAY_CONTRACT_VERSION = "platform.provider-gateway.v1"


@dataclass(frozen=True)
class ProviderRequest:
    capability: str
    messages: tuple[Mapping[str, Any], ...]
    model: str = ""
    provider: str = ""
    temperature: float | None = None
    maximum_output_tokens: int | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ProviderUsage:
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0


@dataclass(frozen=True)
class ProviderResponse:
    provider: str
    model: str
    output: str
    finish_reason: str = ""
    usage: ProviderUsage = field(default_factory=ProviderUsage)
    contract_version: str = PROVIDER_GATEWAY_CONTRACT_VERSION
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ProviderModel:
    provider: str
    model: str
    capabilities: tuple[str, ...] = ()
    available: bool = True


@dataclass(frozen=True)
class ProviderHealth:
    provider: str
    healthy: bool
    message: str = ""


class ProviderGateway(Protocol):
    async def generate(
        self,
        request: ProviderRequest,
        *,
        actor: ActorContext,
    ) -> ProviderResponse:
        ...

    def list_available_models(self) -> Sequence[ProviderModel]:
        ...

    def get_provider_health(self) -> Sequence[ProviderHealth]:
        ...
