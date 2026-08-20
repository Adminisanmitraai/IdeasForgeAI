import asyncio
import pytest

from backend.platform.voice.audit import build_voice_audit_event
from backend.platform.voice.client import ForgeVoiceServiceClient
from backend.platform.voice.contracts import VoiceContext, VoiceOperation, VoiceQualityTier, VoiceRequest
from backend.platform.voice.gateway import VoiceProviderCandidate, VoiceProviderMode, VoiceRoutingRequest
from backend.platform.voice.governance import VoiceGovernanceError, orchestrate_governed_voice
from backend.platform.voice.metering import VoiceRateCard
from backend.platform.voice.permissions import evaluate_voice_permission
from backend.platform.voice.voice_dna import ConsentStatus, VoiceConsent, VoiceDNA, VoiceUsageClass


def request(operation=VoiceOperation.GENERATE):
    return VoiceRequest(
        operation=operation,
        context=VoiceContext(project_id='p1', product_id='forgecall', agent_id='a1', session_id='s1', correlation_id='c1'),
        quality_tier=VoiceQualityTier.STANDARD,
        voice_id='v1', language='en', text='hello',
    )


def cloned_dna():
    return VoiceDNA(
        voice_id='v1', name='Authorized Voice', owner_id='o1', project_id='p1',
        usage_class=VoiceUsageClass.AUTHORIZED_CLONED,
        allowed_products=('forgecall',), reference_asset_ids=('opaque-ref-1',),
        consent=VoiceConsent(ConsentStatus.AUTHORIZED, consent_record_id='consent-1', cloning_allowed=True),
    )

def candidate(provider_id='local', mode=VoiceProviderMode.FORGEVOICE_LOCAL):
    return VoiceProviderCandidate(
        provider_id=provider_id,
        mode=mode,
        capabilities=('voice.generate', 'voice.clone_authorized'),
        languages=('en',),
        estimated_cost=0.02,
    )


def test_clone_is_blocked_without_explicit_approval():
    async def transport(payload):
        raise AssertionError('transport must not be called before approval')
    with pytest.raises(VoiceGovernanceError, match='explicit approval required'):
        asyncio.run(orchestrate_governed_voice(
            request=request(VoiceOperation.CLONE_AUTHORIZED),
            routing_request=VoiceRoutingRequest('voice.clone_authorized', VoiceQualityTier.STANDARD, language='en'),
            candidates=[candidate()],
            clients={'local': ForgeVoiceServiceClient(transport)},
            rate_cards={'local': VoiceRateCard('local')},
            voice_dna=cloned_dna(),
            approval_granted=False,
        ))


def test_governed_execution_records_cost_and_safe_audit():
    async def transport(payload):
        return {
            'status': 'ok',
            'provider_mode': 'forgevoice_local',
            'voice_id': 'v1',
            'language': 'en',
            'output_asset_id': 'asset-out',
            'usage': {
                'input_audio_seconds': 30,
                'output_audio_seconds': 30,
                'fallback_count': 0,
            },
        }
    result = asyncio.run(orchestrate_governed_voice(
        request=request(),
        routing_request=VoiceRoutingRequest('voice.generate', VoiceQualityTier.STANDARD, language='en'),
        candidates=[candidate()],
        clients={'local': ForgeVoiceServiceClient(transport)},
        rate_cards={'local': VoiceRateCard('local', local_compute_per_minute=0.02)},
        voice_dna=cloned_dna(),
        approval_granted=True,
    ))
    assert result.cost.estimated_cost == 0.02
    assert len(result.audit_records) == 2
    serialized = str(result.audit_records)
    assert 'opaque-ref-1' not in serialized
