from backend.platform.voice import (
    VoiceProviderCandidate,
    VoiceProviderMode,
    VoiceRoutingDecision,
    VoiceRoutingRequest,
    VoiceQualityTier,
)


def test_routing_contract_prefers_modes_not_vendor_names():
    request = VoiceRoutingRequest(
        operation="voice.generate",
        quality_tier=VoiceQualityTier.REALTIME,
        language="bn-IN",
        require_realtime=True,
        maximum_cost=0.05,
    )
    assert request.quality_tier is VoiceQualityTier.REALTIME
    assert request.maximum_cost == 0.05


def test_routing_decision_supports_fallback_and_retry_budget():
    decision = VoiceRoutingDecision(
        selected_provider_id="forgevoice-local-primary",
        selected_mode=VoiceProviderMode.FORGEVOICE_LOCAL,
        reason="local meets latency and quality requirements",
        fallback_provider_ids=("forgevoice-external-premium",),
        retry_budget=1,
    )
    assert decision.selected_mode is VoiceProviderMode.FORGEVOICE_LOCAL
    assert decision.fallback_provider_ids == ("forgevoice-external-premium",)
