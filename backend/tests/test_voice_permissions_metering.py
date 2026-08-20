from backend.platform.voice.contracts import VoiceContext, VoiceOperation, VoiceRequest, VoiceResponse, VoiceUsage
from backend.platform.voice.metering import VoiceRateCard, build_cost_record, estimate_voice_cost
from backend.platform.voice.permissions import VoicePermissionStatus, evaluate_voice_permission
from backend.platform.voice.voice_dna import ConsentStatus, VoiceConsent, VoiceDNA, VoiceUsageClass


def req(operation=VoiceOperation.GENERATE, product='forgecall'):
    return VoiceRequest(
        operation=operation,
        context=VoiceContext(project_id='p1', product_id=product, session_id='s1', correlation_id='c1'),
        voice_id='v1', language='en', text='hello',
    )


def dna(usage=VoiceUsageClass.STANDARD_SYNTHETIC, consent=None, products=('forgecall',)):
    return VoiceDNA(
        voice_id='v1', name='Voice One', owner_id='o1', project_id='p1', usage_class=usage,
        allowed_products=products,
        consent=consent or VoiceConsent(ConsentStatus.NOT_REQUIRED),
        reference_asset_ids=('opaque-ref-1',),
    )


def test_product_scope_is_enforced():
    decision = evaluate_voice_permission(req(product='forgehr'), dna())
    assert decision.status is VoicePermissionStatus.DENIED


def test_clone_requires_authorized_consent_and_approval():
    denied = evaluate_voice_permission(req(VoiceOperation.CLONE_AUTHORIZED), dna(VoiceUsageClass.AUTHORIZED_CLONED))
    assert denied.status is VoicePermissionStatus.DENIED
    consent = VoiceConsent(
        ConsentStatus.AUTHORIZED,
        consent_record_id='consent-1',
        cloning_allowed=True,
        reuse_allowed=True,
    )
    allowed = evaluate_voice_permission(
        req(VoiceOperation.CLONE_AUTHORIZED),
        dna(VoiceUsageClass.AUTHORIZED_CLONED, consent),
    )
    assert allowed.status is VoicePermissionStatus.REQUIRES_APPROVAL
    assert allowed.high_risk is True
    assert allowed.consent_record_id == 'consent-1'


def test_restricted_voice_transform_is_denied():
    decision = evaluate_voice_permission(
        req(VoiceOperation.TRANSLATE_SPEECH),
        dna(VoiceUsageClass.RESTRICTED),
    )
    assert decision.status is VoicePermissionStatus.DENIED


def test_duration_cost_and_cache_zero_cost():
    usage = VoiceUsage(
        input_audio_seconds=60,
        output_audio_seconds=30,
        output_characters=100,
    )
    rate = VoiceRateCard('premium', stt_per_minute=0.10, tts_per_minute=0.20, character_rate=0.001)
    assert estimate_voice_cost(usage, rate) == 0.30
    response = VoiceResponse(
        operation=VoiceOperation.GENERATE,
        correlation_id='c1', status='ok', language='en',
        usage=VoiceUsage(input_audio_seconds=60, cache_hit=True),
    )
    record = build_cost_record(req(), response, provider_id='premium', rate=rate)
    assert record.estimated_cost == 0.0
    assert record.cache_hit is True
