from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping

VOICE_DNA_CONTRACT_VERSION = "platform.voice-dna.v1"


class VoiceUsageClass(str, Enum):
    STANDARD_SYNTHETIC = "standard_synthetic"
    DESIGNED_FICTIONAL = "designed_fictional"
    AUTHORIZED_CLONED = "authorized_cloned"
    RESTRICTED = "restricted"


class ConsentStatus(str, Enum):
    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    AUTHORIZED = "authorized"
    REVOKED = "revoked"
    EXPIRED = "expired"


@dataclass(frozen=True)
class VoiceConsent:
    status: ConsentStatus
    consent_record_id: str = ""
    cloning_allowed: bool = False
    export_allowed: bool = False
    reuse_allowed: bool = False
    expires_at: str = ""


@dataclass(frozen=True)
class VoiceDNA:
    voice_id: str
    name: str
    owner_id: str
    project_id: str
    usage_class: VoiceUsageClass
    gender_presentation: str = ""
    age_impression: str = ""
    languages: tuple[str, ...] = ()
    accent: str = ""
    pitch: str = ""
    timbre: str = ""
    speaking_rate: str = ""
    energy: str = ""
    emotion_profile: Mapping[str, float] = field(default_factory=dict)
    authority: float = 0.0
    warmth: float = 0.0
    breathiness: float = 0.0
    pronunciation_profile_id: str = ""
    style_presets: tuple[str, ...] = ()
    reference_asset_ids: tuple[str, ...] = ()
    consent: VoiceConsent = field(default_factory=lambda: VoiceConsent(ConsentStatus.NOT_REQUIRED))
    allowed_products: tuple[str, ...] = ()
    provider_preferences: tuple[str, ...] = ()
    fallback_voice_id: str = ""
    version: int = 1
    contract_version: str = VOICE_DNA_CONTRACT_VERSION

    def assert_clone_allowed(self) -> None:
        if self.usage_class is not VoiceUsageClass.AUTHORIZED_CLONED:
            raise PermissionError("voice is not classified for authorized cloning")
        if self.consent.status is not ConsentStatus.AUTHORIZED:
            raise PermissionError("authorized consent is required for cloning")
        if not self.consent.cloning_allowed:
            raise PermissionError("cloning permission is not granted")

    def assert_product_allowed(self, product_id: str) -> None:
        if self.allowed_products and product_id not in self.allowed_products:
            raise PermissionError(f"voice is not allowed for product: {product_id}")

    def assert_export_allowed(self) -> None:
        if self.usage_class is VoiceUsageClass.RESTRICTED:
            raise PermissionError("restricted voice cannot be exported")
        if self.usage_class is VoiceUsageClass.AUTHORIZED_CLONED and not self.consent.export_allowed:
            raise PermissionError("voice export permission is not granted")
