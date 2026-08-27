from __future__ import annotations

import base64
import hmac
import os
import time
from dataclasses import dataclass
from hashlib import sha256

FORGE_COMMANDER_DEVICE_AUTH_VERSION = "forge-commander.device-auth.v1"

@dataclass(frozen=True, slots=True)
class DevicePrincipal:
    owner_subject: str
    device_id: str
    expires_at: int


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def issue_device_token(owner_subject: str, device_id: str, *, signing_key: str, expires_at: int) -> str:
    owner = owner_subject.strip()
    device = device_id.strip()
    if not owner or not device or not signing_key:
        raise ValueError("owner_subject, device_id and signing_key are required")
    payload = _b64url(f"{owner}\n{device}\n{int(expires_at)}".encode("utf-8"))
    sig = hmac.new(signing_key.encode("utf-8"), payload.encode("ascii"), sha256).digest()
    return f"{payload}.{_b64url(sig)}"

def parse_device_token(token: str, *, expected_device_id: str, signing_key: str | None = None,
                       now_epoch: int | None = None) -> DevicePrincipal | None:
    key = signing_key or os.getenv("FORGE_COMMANDER_GATEWAY_SIGNING_KEY", "")
    if not token or not key or "." not in token:
        return None
    payload, provided = token.split(".", 1)
    expected = _b64url(hmac.new(key.encode("utf-8"), payload.encode("ascii"), sha256).digest())
    if not hmac.compare_digest(provided, expected):
        return None
    try:
        padded = payload + "=" * (-len(payload) % 4)
        owner, device, expires_text = base64.urlsafe_b64decode(padded).decode("utf-8").split("\n", 2)
        expires_at = int(expires_text)
    except Exception:
        return None
    now = int(time.time()) if now_epoch is None else int(now_epoch)
    if expires_at <= now or device != expected_device_id or not owner.strip():
        return None
    return DevicePrincipal(owner.strip(), device, expires_at)


__all__ = ["FORGE_COMMANDER_DEVICE_AUTH_VERSION", "DevicePrincipal",
           "issue_device_token", "parse_device_token"]
