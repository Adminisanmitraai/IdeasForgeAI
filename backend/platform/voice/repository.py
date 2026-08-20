from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Iterable

from .voice_dna import ConsentStatus, VoiceConsent, VoiceDNA, VoiceUsageClass

VOICE_DNA_REPOSITORY_VERSION = "platform.voice-dna-repository.v1"


class VoiceDNARepositoryError(RuntimeError):
    pass


class VoiceDNANotFoundError(VoiceDNARepositoryError):
    pass


class VoiceDNAVersionConflictError(VoiceDNARepositoryError):
    pass


class VoiceDNAAccessError(PermissionError):
    pass
def _safe_record(voice: VoiceDNA) -> dict[str, object]:
    data = asdict(voice)
    data["usage_class"] = voice.usage_class.value
    data["consent"]["status"] = voice.consent.status.value
    # Reference assets remain opaque IDs; repository never dereferences or embeds bytes.
    data["reference_asset_ids"] = list(voice.reference_asset_ids)
    return data


def _hydrate(data: dict[str, object]) -> VoiceDNA:
    consent_data = dict(data.get("consent", {}) or {})
    consent = VoiceConsent(
        status=ConsentStatus(str(consent_data.get("status", ConsentStatus.NOT_REQUIRED.value))),
        consent_record_id=str(consent_data.get("consent_record_id", "")),
        cloning_allowed=bool(consent_data.get("cloning_allowed", False)),
        export_allowed=bool(consent_data.get("export_allowed", False)),
        reuse_allowed=bool(consent_data.get("reuse_allowed", False)),
        expires_at=str(consent_data.get("expires_at", "")),
    )
    allowed = {field.name for field in VoiceDNA.__dataclass_fields__.values()}
    payload = {key: value for key, value in data.items() if key in allowed}
    payload["usage_class"] = VoiceUsageClass(str(data["usage_class"]))
    payload["consent"] = consent
    for key in ("languages", "style_presets", "reference_asset_ids", "allowed_products", "provider_preferences"):
        payload[key] = tuple(payload.get(key, ()) or ())
    return VoiceDNA(**payload)
class VoiceDNARepository:
    """File-backed, versioned Voice DNA metadata store. No raw audio is persisted."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _voice_dir(self, voice_id: str) -> Path:
        safe = voice_id.strip()
        if not safe or any(ch in safe for ch in ("/", "\\", "..")):
            raise VoiceDNARepositoryError("invalid voice_id")
        return self.root / safe

    def _versions(self, voice_id: str) -> tuple[Path, ...]:
        directory = self._voice_dir(voice_id)
        if not directory.exists():
            return ()
        return tuple(sorted(directory.glob("v*.json"), key=lambda p: int(p.stem[1:])))

    def save(self, voice: VoiceDNA) -> VoiceDNA:
        directory = self._voice_dir(voice.voice_id)
        directory.mkdir(parents=True, exist_ok=True)
        versions = self._versions(voice.voice_id)
        expected = 1 if not versions else int(versions[-1].stem[1:]) + 1
        if voice.version != expected:
            raise VoiceDNAVersionConflictError(f"expected version {expected}, got {voice.version}")
        target = directory / f"v{voice.version}.json"
        target.write_text(json.dumps(_safe_record(voice), sort_keys=True, indent=2), encoding="utf-8")
        return voice
    def get(self, voice_id: str, *, version: int | None = None) -> VoiceDNA:
        versions = self._versions(voice_id)
        if not versions:
            raise VoiceDNANotFoundError(voice_id)
        selected = versions[-1] if version is None else self._voice_dir(voice_id) / f"v{version}.json"
        if not selected.exists():
            raise VoiceDNANotFoundError(f"{voice_id}@{version}")
        return _hydrate(json.loads(selected.read_text(encoding="utf-8")))

    def history(self, voice_id: str) -> tuple[VoiceDNA, ...]:
        return tuple(_hydrate(json.loads(path.read_text(encoding="utf-8"))) for path in self._versions(voice_id))

    def list_for_product(self, product_id: str, *, project_id: str = "") -> tuple[VoiceDNA, ...]:
        voices: list[VoiceDNA] = []
        for directory in sorted((path for path in self.root.iterdir() if path.is_dir()), key=lambda p: p.name):
            voice = self.get(directory.name)
            if project_id and voice.project_id and voice.project_id != project_id:
                continue
            if voice.allowed_products and product_id not in voice.allowed_products:
                continue
            voices.append(voice)
        return tuple(voices)

    def get_authorized(self, voice_id: str, *, product_id: str, project_id: str = "") -> VoiceDNA:
        voice = self.get(voice_id)
        if project_id and voice.project_id and voice.project_id != project_id:
            raise VoiceDNAAccessError("voice belongs to another project")
        voice.assert_product_allowed(product_id)
        return voice


__all__ = ["VOICE_DNA_REPOSITORY_VERSION", "VoiceDNARepository", "VoiceDNARepositoryError", "VoiceDNANotFoundError", "VoiceDNAVersionConflictError", "VoiceDNAAccessError"]
