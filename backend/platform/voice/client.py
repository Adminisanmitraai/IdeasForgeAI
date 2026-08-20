from __future__ import annotations

from dataclasses import dataclass
from typing import Awaitable, Callable, Mapping

from backend.platform.platform_event_model import build_event

from .contracts import VoiceRequest, VoiceResponse
from .gateway import VoiceProviderMode, VoiceRoutingDecision
from .voice_dna import VoiceDNA

FORGEVOICE_CLIENT_VERSION = "platform.forgevoice-client.v1"
Transport = Callable[[Mapping[str, object]], Awaitable[Mapping[str, object]]]


class ForgeVoiceUnavailableError(RuntimeError):
    pass


@dataclass(frozen=True)
class ForgeVoiceClientResult:
    response: VoiceResponse
    selected_provider_id: str
    fallback_used: bool = False
    contract_version: str = FORGEVOICE_CLIENT_VERSION


def _payload(
    request: VoiceRequest,
    decision: VoiceRoutingDecision,
    voice_dna: VoiceDNA | None,
) -> dict[str, object]:
    return {
        "contract_version": FORGEVOICE_CLIENT_VERSION,
        "operation": request.operation.value,
        "context": {
            "project_id": request.context.project_id,
            "product_id": request.context.product_id,
            "user_id": request.context.user_id,
            "agent_id": request.context.agent_id,
            "character_id": request.context.character_id,
            "session_id": request.context.session_id,
            "correlation_id": request.context.correlation_id,
        },
        "quality_tier": request.quality_tier.value,
        "voice_id": request.voice_id,
        "language": request.language,
        "text": request.text,
        "source_asset_id": request.source_asset_id,
        "target_language": request.target_language,
        "selected_provider_id": decision.selected_provider_id,
        "selected_mode": decision.selected_mode.value,
        "voice_dna_version": voice_dna.version if voice_dna else "",
    }


class ForgeVoiceServiceClient:
    def __init__(self, transport: Transport) -> None:
        self._transport = transport

    async def execute(
        self,
        request: VoiceRequest,
        decision: VoiceRoutingDecision,
        *,
        voice_dna: VoiceDNA | None = None,
    ) -> ForgeVoiceClientResult:
        try:
            raw = await self._transport(_payload(request, decision, voice_dna))
        except Exception as exc:
            raise ForgeVoiceUnavailableError(str(exc)) from exc
        response = VoiceResponse(
            operation=request.operation,
            correlation_id=request.context.correlation_id,
            status=str(raw.get("status", "error")),
            provider_mode=str(raw.get("provider_mode", decision.selected_mode.value)),
            voice_id=str(raw.get("voice_id", request.voice_id)),
            language=str(raw.get("language", request.language)),
            text=str(raw.get("text", "")),
            output_asset_id=str(raw.get("output_asset_id", "")),
            metadata=dict(raw.get("metadata", {}) or {}),
        )
        return ForgeVoiceClientResult(response, decision.selected_provider_id)
