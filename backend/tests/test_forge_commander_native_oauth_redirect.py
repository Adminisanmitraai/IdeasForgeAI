import asyncio
import pytest
from mcp.shared.auth import OAuthClientInformationFull
from backend.forge_commander.oauth_provider import ForgeCommanderOAuthProvider

ISSUER = "https://commander.ideasforgeai.com/forge-commander"
GOOD_NATIVE = "http://127.0.0.1:49152/forgepc/oauth/callback"

def client(uri):
    return OAuthClientInformationFull(
        redirect_uris=[uri], token_endpoint_auth_method="none",
        grant_types=["authorization_code", "refresh_token"], response_types=["code"],
    )

async def register(uri):
    provider = ForgeCommanderOAuthProvider(ISSUER)
    info = client(uri)
    await provider.register_client(info)
    return info


def test_allows_exact_forgepc_loopback_callback(monkeypatch):
    monkeypatch.setenv("FORGE_COMMANDER_GATEWAY_SIGNING_KEY", "test-key")
    info = asyncio.run(register(GOOD_NATIVE))
    assert info.client_id.startswith("fc-client.")
    assert info.client_secret is None

@pytest.mark.parametrize("uri", [
    "http://localhost:49152/forgepc/oauth/callback",
    "http://127.0.0.2:49152/forgepc/oauth/callback",
    "http://192.168.1.10:49152/forgepc/oauth/callback",
    "https://127.0.0.1:49152/forgepc/oauth/callback",
    "http://127.0.0.1:49152/other",
    "http://127.0.0.1:49152/forgepc/oauth/callback?next=x",
    "http://127.0.0.1:49152/forgepc/oauth/callback#fragment",
    "http://127.0.0.1:80/forgepc/oauth/callback",
])
def test_rejects_non_exact_native_redirects(monkeypatch, uri):
    monkeypatch.setenv("FORGE_COMMANDER_GATEWAY_SIGNING_KEY", "test-key")
    with pytest.raises(ValueError, match="untrusted OAuth redirect URI"):
        asyncio.run(register(uri))

def test_existing_chatgpt_https_redirect_remains_allowed(monkeypatch):
    monkeypatch.setenv("FORGE_COMMANDER_GATEWAY_SIGNING_KEY", "test-key")
    info = asyncio.run(register("https://chatgpt.com/connector/oauth/callback"))
    assert info.client_id.startswith("fc-client.")

def test_lookalike_web_host_remains_rejected(monkeypatch):
    monkeypatch.setenv("FORGE_COMMANDER_GATEWAY_SIGNING_KEY", "test-key")
    with pytest.raises(ValueError, match="untrusted OAuth redirect URI"):
        asyncio.run(register("https://chatgpt.com.evil.example/connector/oauth/callback"))
