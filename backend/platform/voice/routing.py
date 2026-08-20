from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .contracts import VoiceQualityTier
from .gateway import (
    VoiceProviderCandidate,
    VoiceProviderMode,
    VoiceRoutingDecision,
    VoiceRoutingRequest,
)


class VoiceRoutingError(RuntimeError):
    pass


def _supports(candidate: VoiceProviderCandidate, request: VoiceRoutingRequest) -> bool:
    if not candidate.available:
        return False
    if request.operation not in candidate.capabilities:
        return False
    if request.language and candidate.languages and request.language not in candidate.languages:
        return False
    if request.maximum_cost is not None and candidate.estimated_cost > request.maximum_cost:
        return False
    if request.require_realtime and candidate.estimated_latency_ms > 1000:
        return False
    return True

def _priority(candidate: VoiceProviderCandidate, request: VoiceRoutingRequest) -> tuple:
    premium = request.quality_tier in {VoiceQualityTier.PREMIUM, VoiceQualityTier.CINEMATIC}
    mode_rank = {
        VoiceProviderMode.FORGEVOICE_LOCAL: 0 if not premium else 1,
        VoiceProviderMode.FORGEVOICE_EXTERNAL: 1 if not premium else 0,
        VoiceProviderMode.EXTERNAL_FALLBACK: 2,
    }[candidate.mode]
    return (
        mode_rank,
        candidate.estimated_cost,
        candidate.estimated_latency_ms,
        -candidate.reliability_score,
        candidate.provider_id,
    )


def decide_voice_route(
    request: VoiceRoutingRequest,
    candidates: Sequence[VoiceProviderCandidate],
) -> VoiceRoutingDecision:
    eligible = [candidate for candidate in candidates if _supports(candidate, request)]
    if not eligible:
        raise VoiceRoutingError("no eligible voice provider candidate")
    ordered = sorted(eligible, key=lambda candidate: _priority(candidate, request))
    selected = ordered[0]
    return VoiceRoutingDecision(
        selected_provider_id=selected.provider_id,
        selected_mode=selected.mode,
        reason=f"selected {selected.provider_id} for {request.quality_tier.value}",
        fallback_provider_ids=tuple(item.provider_id for item in ordered[1:]),
        retry_budget=1 if request.require_realtime else 2,
        estimated_cost=selected.estimated_cost,
    )


__all__ = ["VoiceRoutingError", "decide_voice_route"]
