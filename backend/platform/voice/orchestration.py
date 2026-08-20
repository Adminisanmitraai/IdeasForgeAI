from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Sequence

from backend.platform.platform_event_model import PlatformEvent, build_event

from .client import ForgeVoiceServiceClient, ForgeVoiceUnavailableError
from .contracts import VoiceRequest, VoiceResponse
from .gateway import VoiceProviderCandidate, VoiceRoutingDecision, VoiceRoutingRequest
from .routing import decide_voice_route
from .voice_dna import VoiceDNA

VOICE_ORCHESTRATION_VERSION = "platform.voice-orchestration.v1"


@dataclass(frozen=True)
class VoiceOrchestrationResult:
    response: VoiceResponse
    decision: VoiceRoutingDecision
    events: tuple[PlatformEvent, ...]
    fallback_used: bool = False
    contract_version: str = VOICE_ORCHESTRATION_VERSION


def _event(
    request: VoiceRequest,
    event_type: str,
    payload: dict[str, object],
    sequence: int,
) -> PlatformEvent:
    return build_event(
        event_type=event_type,
        source="founder-os.voice",
        occurred_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        correlation_id=request.context.correlation_id,
        sequence=sequence,
        subject_id=request.voice_id or request.context.agent_id or request.context.project_id,
        payload=payload,
    )


async def orchestrate_voice(
    *,
    request: VoiceRequest,
    routing_request: VoiceRoutingRequest,
    candidates: Sequence[VoiceProviderCandidate],
    clients: dict[str, ForgeVoiceServiceClient],
    voice_dna: VoiceDNA | None = None,
) -> VoiceOrchestrationResult:
    decision = decide_voice_route(routing_request, candidates)
    events = [
        _event(
            request,
            "voice.route_selected",
            {
                "provider_id": decision.selected_provider_id,
                "mode": decision.selected_mode.value,
                "fallbacks": list(decision.fallback_provider_ids),
            },
            1,
        )
    ]
    ordered_ids = (decision.selected_provider_id,) + decision.fallback_provider_ids
    last_error = ""
    for index, provider_id in enumerate(ordered_ids):
        client = clients.get(provider_id)
        if client is None:
            last_error = f"client unavailable: {provider_id}"
            events.append(_event(request, "voice.provider_unavailable", {"provider_id": provider_id}, index + 2))
            continue
        try:
            candidate = next(item for item in candidates if item.provider_id == provider_id)
            attempt_decision = VoiceRoutingDecision(
                selected_provider_id=provider_id,
                selected_mode=candidate.mode,
                reason=decision.reason if index == 0 else f"fallback after provider failure: {provider_id}",
                fallback_provider_ids=tuple(ordered_ids[index + 1:]),
                cache_allowed=decision.cache_allowed,
                retry_budget=max(0, decision.retry_budget - index),
                estimated_cost=candidate.estimated_cost,
            )
            result = await client.execute(request, attempt_decision, voice_dna=voice_dna)
            fallback_used = index > 0
            events.append(
                _event(
                    request,
                    "voice.completed",
                    {"provider_id": provider_id, "fallback_used": fallback_used},
                    index + 2,
                )
            )
            return VoiceOrchestrationResult(result.response, decision, tuple(events), fallback_used)
        except ForgeVoiceUnavailableError as exc:
            last_error = str(exc)
            events.append(
                _event(
                    request,
                    "voice.provider_failed",
                    {"provider_id": provider_id, "error": type(exc).__name__},
                    index + 2,
                )
            )
    raise ForgeVoiceUnavailableError(last_error or "all voice providers unavailable")


__all__ = ["VOICE_ORCHESTRATION_VERSION", "VoiceOrchestrationResult", "orchestrate_voice"]
