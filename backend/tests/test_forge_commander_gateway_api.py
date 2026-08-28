import os, time
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.forge_commander.gateway_api import router, session_manager
from backend.forge_commander.device_auth import issue_device_token
from backend.forge_commander.gateway_auth import issue_gateway_token

KEY = "test-signing-key"

def _client():
    os.environ["FORGE_COMMANDER_GATEWAY_SIGNING_KEY"] = KEY
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)

def _token(subject="owner-1"):
    return issue_gateway_token(subject, signing_key=KEY, expires_at=int(time.time()) + 300)

def test_health_and_tool_auth():
    client = _client()
    assert client.get("/forge-commander/health").status_code == 200
    assert client.get("/forge-commander/mcp/tools").status_code == 401
    r = client.get("/forge-commander/mcp/tools", headers={"Authorization": f"Bearer {_token()}"})
    assert r.status_code == 200
    assert r.json()["owner_subject"] == "owner-1"

def test_websocket_attach_heartbeat_disconnect():
    client = _client()
    token = issue_device_token(
        "owner-1", "dev-1", signing_key=KEY, expires_at=int(time.time()) + 300
    )
    path = "/forge-commander/device/ws/dev-1?session_id=s1&instance_id=i1"
    with client.websocket_connect(
        path, headers={"Authorization": f"Bearer {token}"}
    ) as ws:
        live = session_manager.get("dev-1")
        assert live is not None
        assert live.session.owner_subject == "owner-1"
        ws.send_json({"type": "heartbeat", "at": "2026-08-27T04:00:00+00:00"})
        assert ws.receive_json() == {
            "type": "heartbeat_ack", "at": "2026-08-27T04:00:00+00:00"
        }
        assert session_manager.get("dev-1").last_heartbeat_at == "2026-08-27T04:00:00+00:00"
    assert session_manager.get("dev-1") is None
