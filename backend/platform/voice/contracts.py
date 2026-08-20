from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping

VOICE_CAPABILITY_CONTRACT_VERSION = "platform.voice-capability.v1"


class VoiceQualityTier(str, Enum):
    DRAFT = "DRAFT"
    STANDARD = "STANDARD"
    PREMIUM = "PREMIUM"
    REALTIME = "REALTIME"
    CINEMATIC = "CINEMATIC"


class VoiceOperation(str, Enum):
    TRANSCRIBE = "voice.transcribe"
    GENERATE = "voice.generate"
    STREAM = "voice.stream"
    DETECT_LANGUAGE = "voice.detect_language"
    DESIGN = "voice.design"
    GET_PROFILE = "voice.get_profile"
    LIST_PROFILES = "voice.list_profiles"
    TRANSLATE_SPEECH = "voice.translate_speech"
    CLONE_AUTHORIZED = "voice.clone_authorized"
    HEALTH = "voice.health"
    ESTIMATE_COST = "voice.estimate_cost"


@dataclass(frozen=True)
class VoiceContext:
    project_id: str
    product_id: str = ""
    user_id: str = ""
    agent_id: str = ""
    character_id: str = ""
    session_id: str = ""
    correlation_id: str = ""


@dataclass(frozen=True)
class VoiceRequest:
    operation: VoiceOperation
    context: VoiceContext
    quality_tier: VoiceQualityTier = VoiceQualityTier.STANDARD
    voice_id: str = ""
    language: str = ""
    text: str = ""
    source_asset_id: str = ""
    target_language: str = ""
    maximum_cost: float | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
    contract_version: str = VOICE_CAPABILITY_CONTRACT_VERSION


@dataclass(frozen=True)
class VoiceUsage:
    input_audio_seconds: float = 0.0
    output_audio_seconds: float = 0.0
    input_characters: int = 0
    output_characters: int = 0
    cache_hit: bool = False
    fallback_count: int = 0
    estimated_cost: float = 0.0
    currency: str = "USD"


@dataclass(frozen=True)
class VoiceResponse:
    operation: VoiceOperation
    correlation_id: str
    status: str
    provider_mode: str = ""
    voice_id: str = ""
    language: str = ""
    text: str = ""
    output_asset_id: str = ""
    usage: VoiceUsage = field(default_factory=VoiceUsage)
    metadata: Mapping[str, Any] = field(default_factory=dict)
    contract_version: str = VOICE_CAPABILITY_CONTRACT_VERSION
