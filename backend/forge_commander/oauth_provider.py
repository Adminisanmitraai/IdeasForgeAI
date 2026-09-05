from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from typing import Any
from urllib.parse import urlencode, urlparse

from mcp.server.auth.provider import (
    AccessToken, AuthorizationCode, AuthorizationParams,
    OAuthAuthorizationServerProvider, RefreshToken,
)
from mcp.shared.auth import OAuthClientInformationFull, OAuthToken

FORGE_COMMANDER_OAUTH_VERSION = "forge-commander.oauth.v1"


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _unb64(value: str) -> bytes:
    return base64.urlsafe_b64decode((value + "=" * (-len(value) % 4)).encode("ascii"))


def _key() -> bytes:
    root = os.getenv("FORGE_COMMANDER_GATEWAY_SIGNING_KEY", "").encode("utf-8")
    if not root:
        raise RuntimeError("gateway signing key is required")
    epoch = os.getenv("FORGE_COMMANDER_OAUTH_SIGNING_EPOCH", "v1").encode("utf-8")
    return hmac.new(root, b"forgecommander-oauth\n" + epoch, hashlib.sha256).digest()


def _seal(kind: str, payload: dict[str, Any], ttl: int) -> str:
    body = dict(payload)
    body.update({"k": kind, "exp": int(time.time()) + ttl, "jti": secrets.token_urlsafe(18)})
    raw = _b64(json.dumps(body, separators=(",", ":"), sort_keys=True).encode("utf-8"))
    sig = _b64(hmac.new(_key(), raw.encode("ascii"), hashlib.sha256).digest())
    return f"{raw}.{sig}"


def _open(token: str, kind: str) -> dict[str, Any] | None:
    try:
        raw, provided = token.split(".", 1)
        expected = _b64(hmac.new(_key(), raw.encode("ascii"), hashlib.sha256).digest())
        if not hmac.compare_digest(provided, expected):
            return None
        data = json.loads(_unb64(raw))
        if data.get("k") != kind or int(data.get("exp", 0)) <= int(time.time()):
            return None
        return data
    except Exception:
        return None


def _client_payload(info: OAuthClientInformationFull) -> dict[str, Any]:
    data = info.model_dump(mode="json", exclude_none=True)
    for key in ("client_id", "client_secret", "client_id_issued_at", "client_secret_expires_at"):
        data.pop(key, None)
    return data


def _client_secret(client_id: str) -> str:
    return _b64(hmac.new(_key(), ("client-secret\n" + client_id).encode(), hashlib.sha256).digest())


class ForgeCommanderOAuthProvider(
    OAuthAuthorizationServerProvider[AuthorizationCode, RefreshToken, AccessToken]
):
    def __init__(self, issuer_url: str):
        self.issuer_url = issuer_url.rstrip("/")
        self._used_codes: set[str] = set()

    async def register_client(self, client_info: OAuthClientInformationFull) -> None:
        allowed_hosts = {"chatgpt.com", "openai.com"}
        for redirect_uri in client_info.redirect_uris or []:
            parsed = urlparse(str(redirect_uri))
            host = (parsed.hostname or "").lower()
            if parsed.scheme != "https" or not any(host == h or host.endswith("." + h) for h in allowed_hosts):
                raise ValueError("untrusted OAuth redirect URI")
        payload = _client_payload(client_info)
        client_id = "fc-client." + _seal("client", payload, 365 * 24 * 3600)
        client_info.client_id = client_id
        client_info.client_id_issued_at = int(time.time())
        if client_info.token_endpoint_auth_method != "none":
            client_info.client_secret = _client_secret(client_id)
            client_info.client_secret_expires_at = int(time.time()) + 365 * 24 * 3600

    async def get_client(self, client_id: str) -> OAuthClientInformationFull | None:
        if not client_id.startswith("fc-client."):
            return None
        data = _open(client_id[len("fc-client."):], "client")
        if data is None:
            return None
        data.pop("k", None); data.pop("exp", None); data.pop("jti", None)
        data["client_id"] = client_id
        try:
            info = OAuthClientInformationFull.model_validate(data)
        except Exception as exc:
            print(f"[forge-oauth] get_client reject reason=model_validation error={type(exc).__name__}")
            return None
        info.client_id_issued_at = int(time.time())
        if info.token_endpoint_auth_method != "none":
            info.client_secret = _client_secret(client_id)
            info.client_secret_expires_at = int(time.time()) + 24 * 3600
        return info

    async def authorize(self, client: OAuthClientInformationFull, params: AuthorizationParams) -> str:
        pending = _seal("pending", {
            "client_id": client.client_id,
            "state": params.state,
            "scopes": params.scopes or [],
            "code_challenge": params.code_challenge,
            "redirect_uri": str(params.redirect_uri),
            "redirect_explicit": params.redirect_uri_provided_explicitly,
            "resource": params.resource,
        }, 300)
        return f"{self.issuer_url}/oauth/approve?{urlencode({'request': pending})}"

    def approve_request(self, pending_token: str, owner_secret: str) -> str | None:
        data = _open(pending_token, "pending")
        expected_hash = os.getenv("FORGE_COMMANDER_OAUTH_OWNER_SECRET_SHA256", "")
        owner_subject = os.getenv("FORGE_COMMANDER_OAUTH_OWNER_SUBJECT", "").strip()
        presented_hash = hashlib.sha256(owner_secret.encode("utf-8")).hexdigest()
        if data is None or not expected_hash or not owner_subject:
            return None
        if not hmac.compare_digest(presented_hash, expected_hash):
            return None
        code = _seal("code", {
            "client_id": data["client_id"], "scopes": data.get("scopes", []),
            "code_challenge": data["code_challenge"], "redirect_uri": data["redirect_uri"],
            "redirect_explicit": bool(data.get("redirect_explicit")),
            "resource": data.get("resource"), "subject": owner_subject,
        }, 120)
        query = {"code": code}
        if data.get("state") is not None:
            query["state"] = data["state"]
        sep = "&" if "?" in data["redirect_uri"] else "?"
        return data["redirect_uri"] + sep + urlencode(query)

    async def load_authorization_code(self, client, authorization_code: str):
        if authorization_code in self._used_codes:
            return None
        data = _open(authorization_code, "code")
        if data is None or data.get("client_id") != client.client_id:
            return None
        return AuthorizationCode(
            code=authorization_code, scopes=list(data.get("scopes", [])),
            expires_at=float(data["exp"]), client_id=data["client_id"],
            code_challenge=data["code_challenge"], redirect_uri=data["redirect_uri"],
            redirect_uri_provided_explicitly=bool(data.get("redirect_explicit")),
            resource=data.get("resource"), subject=data.get("subject"),
        )

    async def exchange_authorization_code(self, client, authorization_code: AuthorizationCode) -> OAuthToken:
        if authorization_code.code in self._used_codes:
            raise ValueError("authorization code already used")
        self._used_codes.add(authorization_code.code)
        access = _seal("access", {
            "client_id": client.client_id, "scopes": authorization_code.scopes,
            "resource": authorization_code.resource, "subject": authorization_code.subject,
        }, 3600)
        refresh = _seal("refresh", {
            "client_id": client.client_id, "scopes": authorization_code.scopes,
            "subject": authorization_code.subject,
        }, 30 * 24 * 3600)
        return OAuthToken(
            access_token=access, expires_in=3600,
            refresh_token=refresh, scope=" ".join(authorization_code.scopes),
        )

    async def load_refresh_token(self, client, refresh_token: str):
        data = _open(refresh_token, "refresh")
        if data is None or data.get("client_id") != client.client_id:
            return None
        return RefreshToken(
            token=refresh_token, client_id=client.client_id,
            scopes=list(data.get("scopes", [])), expires_at=int(data["exp"]),
            subject=data.get("subject"),
        )

    async def exchange_refresh_token(self, client, refresh_token: RefreshToken, scopes: list[str]) -> OAuthToken:
        requested = scopes or refresh_token.scopes
        if not set(requested).issubset(set(refresh_token.scopes)):
            raise ValueError("invalid refresh scope")
        access = _seal("access", {
            "client_id": client.client_id, "scopes": requested,
            "resource": None, "subject": refresh_token.subject,
        }, 3600)
        refresh = _seal("refresh", {
            "client_id": client.client_id, "scopes": requested,
            "subject": refresh_token.subject,
        }, 30 * 24 * 3600)
        return OAuthToken(
            access_token=access, expires_in=3600,
            refresh_token=refresh, scope=" ".join(requested),
        )

    async def load_access_token(self, token: str):
        data = _open(token, "access")
        if data is None:
            return None
        return AccessToken(
            token=token, client_id=data["client_id"], scopes=list(data.get("scopes", [])),
            expires_at=int(data["exp"]), resource=data.get("resource"),
            subject=data.get("subject"), claims={"iss": self.issuer_url},
        )

    async def revoke_token(self, token: AccessToken | RefreshToken) -> None:
        return None


__all__ = ["FORGE_COMMANDER_OAUTH_VERSION", "ForgeCommanderOAuthProvider"]
