from __future__ import annotations

import json
from dataclasses import dataclass
from hashlib import sha256
from typing import Any

from .cognitive_memory import (
    FOUNDER_COGNITIVE_MEMORY_SCHEMA_VERSION,
    FounderCognitiveProfile,
    validate_cognitive_profile,
)

FOUNDER_COGNITIVE_REPOSITORY_VERSION = "forgebrain.cognitive-repository.v1"


class CognitiveMemoryRepositoryError(RuntimeError):
    pass


class CognitiveMemoryCorruptionError(CognitiveMemoryRepositoryError):
    pass


def canonical_cognitive_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":"))


def _sha256_json(value: Any) -> str:
    return sha256(canonical_cognitive_json(value).encode("utf-8")).hexdigest()


def cognitive_profile_payload(profile: FounderCognitiveProfile) -> dict[str, Any]:
    return profile.model_dump(mode="json")


@dataclass(frozen=True, slots=True)
class CognitiveMemorySnapshot:
    founder_id: str
    version: int
    stored_at: str
    profile: FounderCognitiveProfile
    profile_sha256: str
    snapshot_sha256: str
    previous_snapshot_sha256: str | None = None
    schema_version: str = FOUNDER_COGNITIVE_REPOSITORY_VERSION

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "founder_id": self.founder_id,
            "version": self.version,
            "stored_at": self.stored_at,
            "profile": cognitive_profile_payload(self.profile),
            "profile_sha256": self.profile_sha256,
            "previous_snapshot_sha256": self.previous_snapshot_sha256,
            "snapshot_sha256": self.snapshot_sha256,
        }


def build_cognitive_memory_snapshot(
    profile: FounderCognitiveProfile,
    *,
    version: int,
    stored_at: str,
    previous_snapshot_sha256: str | None = None,
) -> CognitiveMemorySnapshot:
    validate_cognitive_profile(profile)
    if version < 1:
        raise ValueError("cognitive snapshot version must be positive")
    profile_data = cognitive_profile_payload(profile)
    profile_sha256 = _sha256_json(profile_data)
    base = {
        "schema_version": FOUNDER_COGNITIVE_REPOSITORY_VERSION,
        "founder_id": profile.founder_id,
        "version": version,
        "stored_at": stored_at,
        "profile": profile_data,
        "profile_sha256": profile_sha256,
        "previous_snapshot_sha256": previous_snapshot_sha256,
    }
    return CognitiveMemorySnapshot(
        founder_id=profile.founder_id,
        version=version,
        stored_at=stored_at,
        profile=profile,
        profile_sha256=profile_sha256,
        previous_snapshot_sha256=previous_snapshot_sha256,
        snapshot_sha256=_sha256_json(base),
    )


def restore_cognitive_memory_snapshot(raw: str | bytes) -> CognitiveMemorySnapshot:
    try:
        payload = json.loads(raw)
        profile = FounderCognitiveProfile.model_validate(payload["profile"])
        snapshot = CognitiveMemorySnapshot(
            founder_id=str(payload["founder_id"]),
            version=int(payload["version"]),
            stored_at=str(payload["stored_at"]),
            profile=profile,
            profile_sha256=str(payload["profile_sha256"]),
            previous_snapshot_sha256=payload.get("previous_snapshot_sha256"),
            snapshot_sha256=str(payload["snapshot_sha256"]),
            schema_version=str(payload["schema_version"]),
        )
    except Exception as error:
        raise CognitiveMemoryCorruptionError("invalid cognitive memory snapshot") from error
    expected = build_cognitive_memory_snapshot(
        snapshot.profile,
        version=snapshot.version,
        stored_at=snapshot.stored_at,
        previous_snapshot_sha256=snapshot.previous_snapshot_sha256,
    )
    if snapshot != expected:
        raise CognitiveMemoryCorruptionError("cognitive memory snapshot integrity mismatch")
    return snapshot


def validate_snapshot_chain(snapshots: tuple[CognitiveMemorySnapshot, ...]) -> None:
    if not snapshots:
        return
    founder_id = snapshots[0].founder_id
    for index, snapshot in enumerate(snapshots):
        if snapshot.founder_id != founder_id:
            raise CognitiveMemoryRepositoryError("snapshot chain mixes founders")
        expected_version = index + 1
        if snapshot.version != expected_version:
            raise CognitiveMemoryRepositoryError("snapshot chain version gap")
        expected_previous = None if index == 0 else snapshots[index - 1].snapshot_sha256
        if snapshot.previous_snapshot_sha256 != expected_previous:
            raise CognitiveMemoryRepositoryError("snapshot chain integrity mismatch")


__all__ = [
    "FOUNDER_COGNITIVE_REPOSITORY_VERSION",
    "CognitiveMemorySnapshot",
    "CognitiveMemoryRepositoryError",
    "CognitiveMemoryCorruptionError",
    "canonical_cognitive_json",
    "cognitive_profile_payload",
    "build_cognitive_memory_snapshot",
    "restore_cognitive_memory_snapshot",
    "validate_snapshot_chain",
]
