from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping, Protocol, Sequence

from .contracts import VoiceQualityTier, VoiceRequest, VoiceResponse
from .voice_dna import VoiceDNA

VOICE_GATEWAY_CONTRACT_VERSION = "platform.voice-gateway.v1"


class VoiceProviderMode(str, Enum):
    FORGEVOICE_LOCAL = "forgevoice_local"
    FORGEVOICE_EXTERNAL = "forgevoice_external"
    EXTERNAL_FALLBACK = "external_fallback"


@dataclass(frozen=True)
class VoiceProviderCandidate:
    provider_id: str
    mode: VoiceProviderMode
    capabilities: tuple[str, ...]
    languages: tuple[str, ...] = ()
    available: bool = True
    reliability_score: float = 1.0
    estimated_latency_ms: int = 0
    estimated_cost: float = 0.0


@dataclass(frozen=True)
class VoiceRoutingRequest:
    operation: str
    quality_tier: VoiceQualityTier
    language: str = ""
    voice_id: str = ""
    maximum_cost: float | None = None
    require_realtime: bool = False
    project_policy: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class VoiceRoutingDecision:
    selected_provider_id: str
    selected_mode: VoiceProviderMode
    reason: str
    fallback_provider_ids: tuple[str, ...] = ()
    cache_allowed: bool = True
    retry_budget: int = 1
    estimated_cost: float = 0.0
    contract_version: str = VOICE_GATEWAY_CONTRACT_VERSION


class ForgeVoiceGateway(Protocol):
    async def execute(self, request: VoiceRequest, *, voice_dna: VoiceDNA | None = None) -> VoiceResponse:
        ...
