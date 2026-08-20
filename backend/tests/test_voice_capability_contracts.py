from backend.platform.voice import (
    ConsentStatus,
    VoiceConsent,
    VoiceDNA,
    VoiceOperation,
    VoiceQualityTier,
    VoiceUsageClass,
)


def test_all_generic_voice_operations_are_exposed():
    assert {item.value for item in VoiceOperation} == {
        "voice.transcribe", "voice.generate", "voice.stream",
        "voice.detect_language", "voice.design", "voice.get_profile",
        "voice.list_profiles", "voice.translate_speech",
        "voice.clone_authorized", "voice.health", "voice.estimate_cost",
    }


def test_quality_tiers_are_provider_independent():
    assert [item.value for item in VoiceQualityTier] == [
        "DRAFT", "STANDARD", "PREMIUM", "REALTIME", "CINEMATIC"
    ]


def _voice(**overrides):
    values = dict(
        voice_id="voice-1", name="Asha", owner_id="owner-1",
        project_id="project-1", usage_class=VoiceUsageClass.AUTHORIZED_CLONED,
        allowed_products=("forgecall",),
        reference_asset_ids=("asset-ref-1",),
        consent=VoiceConsent(
            status=ConsentStatus.AUTHORIZED,
            consent_record_id="consent-1",
            cloning_allowed=True,
            reuse_allowed=True,
        ),
    )
    values.update(overrides)
    return VoiceDNA(**values)


def test_authorized_clone_requires_explicit_consent():
    _voice().assert_clone_allowed()
    denied = _voice(consent=VoiceConsent(status=ConsentStatus.PENDING))
    import pytest
    with pytest.raises(PermissionError, match="authorized consent"):
        denied.assert_clone_allowed()


def test_product_scope_and_restricted_export_are_enforced():
    import pytest
    voice = _voice()
    voice.assert_product_allowed("forgecall")
    with pytest.raises(PermissionError, match="not allowed"):
        voice.assert_product_allowed("forgesocial")
    restricted = _voice(usage_class=VoiceUsageClass.RESTRICTED)
    with pytest.raises(PermissionError, match="cannot be exported"):
        restricted.assert_export_allowed()


def test_contract_source_has_no_provider_sdk_keys_or_raw_audio_handling():
    from pathlib import Path
    root = Path("backend/platform/voice")
    text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in root.glob("*.py")
    ).lower()
    forbidden = (
        "openai", "elevenlabs", "api_key", "authorization:",
        "base64", "audio_bytes", "reference_audio",
    )
    assert not [term for term in forbidden if term in text]
