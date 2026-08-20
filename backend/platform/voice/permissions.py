from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .contracts import VoiceOperation, VoiceRequest
from .voice_dna import ConsentStatus, VoiceDNA, VoiceUsageClass

VOICE_PERMISSION_VERSION = "platform.voice-permission.v1"


class VoicePermissionStatus(str, Enum):
    ALLOWED = "allowed"
    DENIED = "denied"
    REQUIRES_APPROVAL = "requires_approval"


@dataclass(frozen=True)
class VoicePermissionDecision:
    status: VoicePermissionStatus
    reason: str
    high_risk: bool = False
    consent_record_id: str = ""
    contract_version: str = VOICE_PERMISSION_VERSION

def evaluate_voice_permission(request: VoiceRequest, voice_dna: VoiceDNA | None) -> VoicePermissionDecision:
    if voice_dna is None:
        return VoicePermissionDecision(VoicePermissionStatus.ALLOWED, "no reusable voice profile requested")
    try:
        voice_dna.assert_product_allowed(request.context.product_id)
    except PermissionError as exc:
        return VoicePermissionDecision(VoicePermissionStatus.DENIED, str(exc))

    if request.operation is VoiceOperation.CLONE_AUTHORIZED:
        if voice_dna.usage_class is not VoiceUsageClass.AUTHORIZED_CLONED:
            return VoicePermissionDecision(VoicePermissionStatus.DENIED, "voice is not classified for authorized cloning", True)
        if voice_dna.consent.status is not ConsentStatus.AUTHORIZED or not voice_dna.consent.cloning_allowed:
            return VoicePermissionDecision(VoicePermissionStatus.DENIED, "authorized cloning consent is required", True)
        return VoicePermissionDecision(
            VoicePermissionStatus.REQUIRES_APPROVAL,
            "authorized clone request requires explicit high-risk approval",
            True,
            voice_dna.consent.consent_record_id,
        )

    if voice_dna.usage_class is VoiceUsageClass.RESTRICTED:
        if request.operation in {VoiceOperation.DESIGN, VoiceOperation.TRANSLATE_SPEECH}:
            return VoicePermissionDecision(VoicePermissionStatus.DENIED, "restricted voice cannot be transformed or reused")
    return VoicePermissionDecision(
        VoicePermissionStatus.ALLOWED,
        "voice use permitted by profile policy",
        False,
        voice_dna.consent.consent_record_id,
    )


__all__ = ["VOICE_PERMISSION_VERSION", "VoicePermissionStatus", "VoicePermissionDecision", "evaluate_voice_permission"]
