from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

FORGE_COMMANDER_GATEWAY_AUTH_VERSION = "forge-commander.gateway-auth.v1"

@dataclass(frozen=True, slots=True)
class GatewayPrincipal:
    subject: str
    token_fingerprint: str
    authenticated: bool


def fingerprint_token(token: str) -> str:
    cleaned = token.strip()
    if not cleaned:
        raise ValueError("token is required")
    return "fc-auth-" + sha256(cleaned.encode("utf-8")).hexdigest()[:24]


def authenticate_bearer(token: str, *, expected_subject: str) -> GatewayPrincipal:
    cleaned_subject = expected_subject.strip()
    if not cleaned_subject:
        raise ValueError("expected_subject is required")
    return GatewayPrincipal(cleaned_subject, fingerprint_token(token), True)


def _b64url(data: bytes) -> str:
    import base64
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def issue_gateway_token(subject: str, *, signing_key: str, expires_at: int) -> str:
    import hmac
    cleaned = subject.strip()
    if not cleaned or not signing_key:
        raise ValueError("subject and signing_key are required")
    payload = _b64url(f"{cleaned}\n{int(expires_at)}".encode("utf-8"))
    signature = hmac.new(signing_key.encode("utf-8"), payload.encode("ascii"), sha256).digest()
    return f"{payload}.{_b64url(signature)}"


def parse_bearer_principal(authorization: str, *, signing_key: str | None = None,
                           now_epoch: int | None = None) -> GatewayPrincipal | None:
    import base64, hmac, os, time
    if not authorization.startswith("Bearer "):
        return None
    token = authorization[7:].strip()
    key = signing_key or os.getenv("FORGE_COMMANDER_GATEWAY_SIGNING_KEY", "")
    if not token or not key or "." not in token:
        return None
    payload, provided = token.split(".", 1)
    expected = _b64url(hmac.new(key.encode("utf-8"), payload.encode("ascii"), sha256).digest())
    if not hmac.compare_digest(provided, expected):
        return None
    try:
        padded = payload + "=" * (-len(payload) % 4)
        decoded = base64.urlsafe_b64decode(padded.encode("ascii")).decode("utf-8")
        subject, expires_text = decoded.split("\n", 1)
        expires_at = int(expires_text)
    except Exception:
        return None
    now = int(time.time()) if now_epoch is None else int(now_epoch)
    if expires_at <= now or not subject.strip():
        return None
    return GatewayPrincipal(subject.strip(), fingerprint_token(token), True)

GatewayPrincipal.owner_subject = property(lambda self: self.subject)

__all__ = [
    "FORGE_COMMANDER_GATEWAY_AUTH_VERSION", "GatewayPrincipal",
    "fingerprint_token", "authenticate_bearer",
    "issue_gateway_token", "parse_bearer_principal",
]
