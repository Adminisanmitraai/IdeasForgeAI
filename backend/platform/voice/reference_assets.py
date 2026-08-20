from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

REFERENCE_ASSET_CONTRACT_VERSION = "platform.voice-reference-asset.v1"


@dataclass(frozen=True)
class VoiceReferenceAsset:
    asset_id: str
    owner_id: str
    project_id: str
    media_type: str
    purpose: str = "voice_reference"
    consent_record_id: str = ""
    contract_version: str = REFERENCE_ASSET_CONTRACT_VERSION


class VoiceReferenceAssetResolver(Protocol):
    """Least-privilege resolver implemented outside Founder OS voice metadata storage."""

    def metadata(self, asset_id: str) -> VoiceReferenceAsset: ...

    def authorize_use(self, asset_id: str, *, project_id: str, purpose: str) -> bool: ...


__all__ = ["REFERENCE_ASSET_CONTRACT_VERSION", "VoiceReferenceAsset", "VoiceReferenceAssetResolver"]
