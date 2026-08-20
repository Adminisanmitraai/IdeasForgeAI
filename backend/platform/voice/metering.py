from __future__ import annotations

from dataclasses import dataclass

from .contracts import VoiceRequest, VoiceResponse, VoiceUsage

VOICE_METERING_VERSION = "platform.voice-metering.v1"


@dataclass(frozen=True)
class VoiceRateCard:
    provider_id: str
    stt_per_minute: float = 0.0
    tts_per_minute: float = 0.0
    character_rate: float = 0.0
    local_compute_per_minute: float = 0.0
    currency: str = "USD"


@dataclass(frozen=True)
class VoiceCostRecord:
    provider_id: str
    project_id: str
    product_id: str
    agent_id: str
    voice_id: str
    language: str
    session_id: str
    input_audio_seconds: float
    output_audio_seconds: float
    cache_hit: bool
    fallback_count: int
    estimated_cost: float
    currency: str
    contract_version: str = VOICE_METERING_VERSION

def estimate_voice_cost(usage: VoiceUsage, rate: VoiceRateCard, *, local_mode: bool = False) -> float:
    input_minutes = max(0.0, usage.input_audio_seconds) / 60.0
    output_minutes = max(0.0, usage.output_audio_seconds) / 60.0
    if local_mode:
        return round((input_minutes + output_minutes) * rate.local_compute_per_minute, 8)
    cost = input_minutes * rate.stt_per_minute + output_minutes * rate.tts_per_minute
    if rate.character_rate:
        cost += max(0, usage.output_characters) * rate.character_rate
    return round(cost, 8)


def build_cost_record(
    request: VoiceRequest,
    response: VoiceResponse,
    *,
    provider_id: str,
    rate: VoiceRateCard,
    local_mode: bool = False,
) -> VoiceCostRecord:
    usage = response.usage
    cost = 0.0 if usage.cache_hit else estimate_voice_cost(usage, rate, local_mode=local_mode)
    return VoiceCostRecord(
        provider_id=provider_id,
        project_id=request.context.project_id,
        product_id=request.context.product_id,
        agent_id=request.context.agent_id,
        voice_id=request.voice_id or response.voice_id,
        language=response.language or request.language,
        session_id=request.context.session_id,
        input_audio_seconds=usage.input_audio_seconds,
        output_audio_seconds=usage.output_audio_seconds,
        cache_hit=usage.cache_hit,
        fallback_count=usage.fallback_count,
        estimated_cost=cost,
        currency=rate.currency,
    )


__all__ = ["VOICE_METERING_VERSION", "VoiceRateCard", "VoiceCostRecord", "estimate_voice_cost", "build_cost_record"]
