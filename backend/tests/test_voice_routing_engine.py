import pytest

from backend.platform.voice.contracts import VoiceQualityTier
from backend.platform.voice.gateway import (
    VoiceProviderCandidate, VoiceProviderMode, VoiceRoutingRequest,
)
from backend.platform.voice.routing import VoiceRoutingError, decide_voice_route


def candidate(provider_id, mode, *, cost=0.0, latency=100, reliability=1.0, languages=('en',)):
    return VoiceProviderCandidate(
        provider_id=provider_id,
        mode=mode,
        capabilities=('voice.generate', 'voice.transcribe'),
        languages=languages,
        available=True,
        reliability_score=reliability,
        estimated_latency_ms=latency,
        estimated_cost=cost,
    )


def test_standard_prefers_local_first():
    request = VoiceRoutingRequest('voice.generate', VoiceQualityTier.STANDARD, language='en')
    decision = decide_voice_route(request, [
        candidate('premium', VoiceProviderMode.FORGEVOICE_EXTERNAL, cost=0.3),
        candidate('local', VoiceProviderMode.FORGEVOICE_LOCAL, cost=0.01),
    ])
    assert decision.selected_provider_id == 'local'


def test_cinematic_prefers_forgevoice_external():
    request = VoiceRoutingRequest('voice.generate', VoiceQualityTier.CINEMATIC, language='en')
    decision = decide_voice_route(request, [
        candidate('local', VoiceProviderMode.FORGEVOICE_LOCAL, cost=0.01),
        candidate('premium', VoiceProviderMode.FORGEVOICE_EXTERNAL, cost=0.3),
    ])
    assert decision.selected_provider_id == 'premium'


def test_language_and_cost_filters_are_enforced():
    request = VoiceRoutingRequest(
        'voice.generate', VoiceQualityTier.STANDARD,
        language='bn', maximum_cost=0.05,
    )
    decision = decide_voice_route(request, [
        candidate('english-local', VoiceProviderMode.FORGEVOICE_LOCAL, languages=('en',)),
        candidate('bangla-premium', VoiceProviderMode.FORGEVOICE_EXTERNAL, cost=0.2, languages=('bn',)),
        candidate('bangla-local', VoiceProviderMode.FORGEVOICE_LOCAL, cost=0.02, languages=('bn',)),
    ])
    assert decision.selected_provider_id == 'bangla-local'


def test_no_eligible_candidate_fails_closed():
    request = VoiceRoutingRequest('voice.stream', VoiceQualityTier.REALTIME, language='en')
    with pytest.raises(VoiceRoutingError):
        decide_voice_route(request, [candidate('x', VoiceProviderMode.FORGEVOICE_LOCAL)])
