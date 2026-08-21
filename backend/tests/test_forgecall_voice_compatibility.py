import asyncio
import pytest

from backend.platform.contracts.operating import ActionRecord
from backend.platform.voice.client import ForgeVoiceUnavailableError
from backend.platform.voice.contracts import VoiceOperation, VoiceQualityTier
from backend.platform.voice.forgecall_adapter import (
    ForgeCallMigrationMode,
    ForgeCallSessionContext,
    ForgeCallTurn,
    ForgeCallVoiceAdapter,
)
from backend.platform.voice.forgecall_migration import execute_forgecall_migration


def session():
    return ForgeCallSessionContext(
        call_id="call-1",
        project_id="forgecall-core",
        agent_id="priya",
        language="bn",
        voice_id="voice-priya",
        customer_id="customer-1",
        correlation_id="corr-call-1",
    )


def test_adapter_maps_inbound_audio_to_generic_transcribe_request():
    result = ForgeCallVoiceAdapter().map_turn(
        session=session(),
        turn=ForgeCallTurn("turn-1", "inbound", source_asset_id="audio-turn-1"),
        mode=ForgeCallMigrationMode.FOS_PREFERRED,
    )
    assert result.request is not None
    assert result.request.operation is VoiceOperation.TRANSCRIBE
    assert result.request.context.product_id == "forgecall"
    assert result.request.context.session_id == "call-1"
    assert result.request.source_asset_id == "audio-turn-1"
    assert result.request.quality_tier is VoiceQualityTier.REALTIME

def test_adapter_maps_outbound_text_to_generic_generate_request():
    result = ForgeCallVoiceAdapter().map_turn(
        session=session(), turn=ForgeCallTurn("turn-2", "outbound", text="à¦¸à§à¦¬à¦¾à¦—à¦¤à¦®"),
        mode=ForgeCallMigrationMode.FOS_REQUIRED,
    )
    assert result.request is not None
    assert result.request.operation is VoiceOperation.GENERATE
    assert result.request.text == "à¦¸à§à¦¬à¦¾à¦—à¦¤à¦®"
    assert result.request.voice_id == "voice-priya"
    assert result.legacy_fallback_allowed is False


def test_legacy_only_never_creates_founder_os_request():
    result = ForgeCallVoiceAdapter().map_turn(
        session=session(), turn=ForgeCallTurn("turn-3", "inbound", source_asset_id="asset"),
        mode=ForgeCallMigrationMode.LEGACY_ONLY,
    )
    assert result.path == "legacy_realtime"
    assert result.request is None


def test_preferred_mode_falls_back_only_when_forgevoice_unavailable():
    compatibility = ForgeCallVoiceAdapter().map_turn(
        session=session(), turn=ForgeCallTurn("turn-4", "outbound", text="hello"),
        mode=ForgeCallMigrationMode.FOS_PREFERRED,
    )
    async def fos():
        raise ForgeVoiceUnavailableError("offline")
    async def legacy():
        return "legacy-ok"
    outcome = asyncio.run(execute_forgecall_migration(
        compatibility=compatibility, mode=ForgeCallMigrationMode.FOS_PREFERRED,
        founder_os_execute=fos, legacy_execute=legacy,
    ))
    assert outcome.path == "legacy_realtime"
    assert outcome.fallback_used is True
    assert outcome.result == "legacy-ok"


def test_required_mode_does_not_bypass_founder_os_on_outage():
    compatibility = ForgeCallVoiceAdapter().map_turn(
        session=session(), turn=ForgeCallTurn("turn-5", "outbound", text="hello"),
        mode=ForgeCallMigrationMode.FOS_REQUIRED,
    )
    async def fos():
        raise ForgeVoiceUnavailableError("offline")
    async def legacy():
        pytest.fail("legacy must not execute in required mode")
    with pytest.raises(ForgeVoiceUnavailableError):
        asyncio.run(execute_forgecall_migration(
            compatibility=compatibility, mode=ForgeCallMigrationMode.FOS_REQUIRED,
            founder_os_execute=fos, legacy_execute=legacy,
        ))


def test_adapter_satisfies_platform_product_adapter_capability_shape():
    adapter = ForgeCallVoiceAdapter()
    assert adapter.descriptor.product_id == "forgecall"
    assert adapter.can_handle(ActionRecord(action_id="a1", task_id="t1", agent_id="priya", operation="generate", idempotency_key="idem-1", capability="voice.generate"))

