from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from secrets import token_urlsafe

FORGE_COMMANDER_DEVICE_ENROLLMENT_VERSION = "forge-commander.device-enrollment.v1"

@dataclass(frozen=True, slots=True)
class EnrollmentChallenge:
    challenge_id: str
    owner_subject: str
    secret_hash: str
    expires_at: str
    used: bool = False

@dataclass(frozen=True, slots=True)
class EnrollmentResult:
    enrolled: bool
    device_id: str | None
    reason: str


def new_enrollment_secret() -> str:
    return token_urlsafe(24)


def hash_enrollment_secret(secret: str) -> str:
    if not secret.strip():
        raise ValueError("enrollment secret is required")
    return sha256(secret.encode("utf-8")).hexdigest()

def complete_enrollment(
    challenge: EnrollmentChallenge, *, presented_secret: str,
    device_id: str, now: str,
) -> EnrollmentResult:
    if challenge.used:
        return EnrollmentResult(False, None, "challenge_already_used")
    if now > challenge.expires_at:
        return EnrollmentResult(False, None, "challenge_expired")
    if hash_enrollment_secret(presented_secret) != challenge.secret_hash:
        return EnrollmentResult(False, None, "invalid_enrollment_secret")
    if not device_id.strip():
        return EnrollmentResult(False, None, "device_id_required")
    return EnrollmentResult(True, device_id.strip(), "device_enrolled")


__all__ = [
    "FORGE_COMMANDER_DEVICE_ENROLLMENT_VERSION", "EnrollmentChallenge",
    "EnrollmentResult", "new_enrollment_secret", "hash_enrollment_secret",
    "complete_enrollment",
]
