import asyncio
import pytest

from backend.platform.voice.client import ForgeVoiceServiceClient, ForgeVoiceUnavailableError
from backend.platform.voice.contracts import (
    VoiceContext, VoiceOperation, VoiceQualityTier, VoiceRequest,
)
from backend.platform.voice.gateway import (
    VoiceProviderCandidate, VoiceProviderMode, VoiceRoutingRequest,
)
from backend.platform.voice.orchestration import orchestrate_voice


def request():
    return VoiceRequest(
        operation=VoiceOperation.GENERATE,
        context=VoiceContext(project_id='p1', product_id='forgecall', correlation_id='corr-1'),
        quality_tier=VoiceQualityTier.STANDARD,
        voice_id='voice-1', language='en', text='hello',
    )


def candidate(provider_id, mode):
    return VoiceProviderCandidate(
        provider_id=provider_id, mode=mode,
        capabilities=('voice.generate',), languages=('en',),
        estimated_latency_ms=100, estimated_cost=0.01,
    )


def test_gateway_client_preserves_controlled_payload_and_response():
    captured = {}
    async def transport(payload):
        captured.update(payload)
        return {'status': 'ok', 'provider_mode': 'forgevoice_local', 'text': 'audio-ready', 'output_asset_id': 'asset-1'}
    client = ForgeVoiceServiceClient(transport)
    decision = type('D', (), {
        'selected_provider_id': 'local', 'selected_mode': VoiceProviderMode.FORGEVOICE_LOCAL,
    })()
    result = asyncio.run(client.execute(request(), decision))
    assert captured['operation'] == 'voice.generate'
    assert captured['context']['product_id'] == 'forgecall'
    assert 'api_key' not in captured
    assert result.response.output_asset_id == 'asset-1'


def test_gateway_unavailable_is_normalized():
    async def transport(payload):
        raise ConnectionError('offline')
    client = ForgeVoiceServiceClient(transport)
    decision = type('D', (), {
        'selected_provider_id': 'local', 'selected_mode': VoiceProviderMode.FORGEVOICE_LOCAL,
    })()
    with pytest.raises(ForgeVoiceUnavailableError):
        asyncio.run(client.execute(request(), decision))


def test_orchestration_falls_back_in_order_and_emits_events():
    calls = []
    async def local_transport(payload):
        calls.append(payload['selected_provider_id'])
        raise ConnectionError('local down')
    async def premium_transport(payload):
        calls.append(payload['selected_provider_id'])
        return {'status': 'ok', 'provider_mode': 'forgevoice_external', 'output_asset_id': 'asset-premium'}
    result = asyncio.run(orchestrate_voice(
        request=request(),
        routing_request=VoiceRoutingRequest('voice.generate', VoiceQualityTier.STANDARD, language='en'),
        candidates=[
            candidate('local', VoiceProviderMode.FORGEVOICE_LOCAL),
            candidate('premium', VoiceProviderMode.FORGEVOICE_EXTERNAL),
        ],
        clients={
            'local': ForgeVoiceServiceClient(local_transport),
            'premium': ForgeVoiceServiceClient(premium_transport),
        },
    ))
    assert calls == ['local', 'premium']
    assert result.fallback_used is True
    assert result.response.output_asset_id == 'asset-premium'
    assert [event.event_type for event in result.events] == [
        'voice.route_selected', 'voice.provider_failed', 'voice.completed'
    ]
