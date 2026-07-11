from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend import coding_agent_terminal_api as api

TOKEN = "founder-secret"

@dataclass
class HydrationChild:
    value: int

@dataclass
class HydrationParent:
    child: HydrationChild
    names: list[str]

class FakeApproval:
    def issue(self, request):
        return SimpleNamespace(token="signed", token_id="t1", expires_at=999)
    def verify(self, token, context, consume=True):
        return SimpleNamespace(ok=token == "signed", code="approval_valid", consumed=consume)
    def revoke(self, token_id, revoked_at, reason=""):
        return SimpleNamespace(ok=token_id == "t1", code="approval_revoked")

class FakeRegistry:
    def __init__(self):
        self.sessions = {}
        self.results = {}
    def submit_session(self, request):
        value = SimpleNamespace(execution_id="e1", status="queued")
        self.sessions["e1"] = value
        return value
    def run_session(self, request):
        value = SimpleNamespace(execution_id="e2", status="succeeded")
        self.sessions["e2"] = value
        self.results["e2"] = SimpleNamespace(exit_code=0)
        return value
    def start_session(self, execution_id):
        return self.sessions.get(execution_id)
    def cancel_session(self, execution_id):
        value = self.sessions.get(execution_id)
        if value:
            value.status = "cancelled"
        return value
    def get_session(self, execution_id):
        return self.sessions.get(execution_id)
    def get_events(self, execution_id, after_sequence=0, limit=None):
        return [SimpleNamespace(sequence=after_sequence + 1, stream="stdout", payload="ok")]
    def get_result(self, execution_id):
        return self.results.get(execution_id)
    def list_sessions(self):
        return list(self.sessions.values())

class FakeAudit:
    def query(self, query=None):
        return SimpleNamespace(records=[], count=0)
    def snapshot(self):
        return SimpleNamespace(records=[], count=0)

@pytest.fixture
def setup(monkeypatch):
    monkeypatch.setenv("IF_FOUNDER_ADMIN_TOKEN", TOKEN)
    monkeypatch.setattr(api, "_construct_dataclass", lambda model, payload: SimpleNamespace(**payload))
    monkeypatch.setattr(api.planner, "build_terminal_execution_plan", lambda request: SimpleNamespace(status="ready"))
    monkeypatch.setattr(api, "_terminal_execution_plan_sha256", lambda result: "p" * 64)
    services = api.TerminalApiServices(FakeRegistry(), FakeAudit(), FakeApproval())
    controller = api.TerminalApiController(
        services,
        api.TerminalApiPolicy(allow_private_host_without_token=False),
    )
    app = FastAPI()
    api.register_terminal_api_routes(app, controller=controller)
    return TestClient(app), services

def headers(token=TOKEN):
    return {"Authorization": f"Bearer {token}"}

def test_contract_and_capabilities():
    assert api.CONTRACT_VERSION == "forgecode.terminal-api.v1"
    caps = api.TerminalApiCapabilities()
    assert caps.planning and caps.approval and caps.session_control
    assert not caps.arbitrary_command_strings and not caps.shell
    assert not caps.direct_subprocess and not caps.file_write and not caps.git_write

def test_auth_required(setup):
    assert setup[0].get(f"{api.ROUTE_PREFIX}/capabilities").status_code == 401

def test_bad_auth(setup):
    assert setup[0].get(f"{api.ROUTE_PREFIX}/capabilities", headers=headers("bad")).status_code == 401

def test_capabilities(setup):
    response = setup[0].get(f"{api.ROUTE_PREFIX}/capabilities", headers=headers())
    assert response.status_code == 200
    assert response.json()["data"]["contracts"]["approval"] == "forgecode.terminal-approval-policy.v1"

def test_plan(setup):
    response = setup[0].post(f"{api.ROUTE_PREFIX}/plan", headers=headers(), json={"x": 1})
    assert response.status_code == 200
    assert response.json()["data"]["plan_sha256"] == "p" * 64

def test_approval_flow(setup):
    assert setup[0].post(f"{api.ROUTE_PREFIX}/approval", headers=headers(), json={"subject": "u"}).status_code == 200
    assert setup[0].post(f"{api.ROUTE_PREFIX}/approval/verify", headers=headers(), json={"token": "signed"}).status_code == 200
    assert setup[0].post(f"{api.ROUTE_PREFIX}/approval/revoke", headers=headers(), json={"token_id": "t1"}).status_code == 200

def test_submit_and_get_session(setup):
    assert setup[0].post(f"{api.ROUTE_PREFIX}/submit", headers=headers(), json={"x": 1}).status_code == 200
    assert setup[0].get(f"{api.ROUTE_PREFIX}/session/e1", headers=headers()).status_code == 200

def test_run_and_result(setup):
    response = setup[0].post(f"{api.ROUTE_PREFIX}/run", headers=headers(), json={"x": 1})
    assert response.status_code == 200
    assert response.json()["data"]["result"]["exit_code"] == 0

def test_start_cancel(setup):
    setup[1].session_registry.submit_session(None)
    assert setup[0].post(f"{api.ROUTE_PREFIX}/session/e1/start", headers=headers()).status_code == 200
    response = setup[0].post(f"{api.ROUTE_PREFIX}/session/e1/cancel", headers=headers())
    assert response.json()["data"]["session"]["status"] == "cancelled"

def test_missing_session(setup):
    assert setup[0].get(f"{api.ROUTE_PREFIX}/session/missing", headers=headers()).status_code == 404

def test_events_bounded(setup):
    response = setup[0].get(f"{api.ROUTE_PREFIX}/session/e1/events?after_sequence=4&limit=999", headers=headers())
    assert response.status_code == 200
    assert response.json()["data"]["limit"] == 100
    assert response.json()["data"]["events"][0]["sequence"] == 5

def test_pending_result(setup):
    setup[1].session_registry.submit_session(None)
    response = setup[0].get(f"{api.ROUTE_PREFIX}/session/e1/result", headers=headers())
    assert response.status_code == 200
    assert response.json()["data"]["result"] is None

def test_missing_result(setup):
    assert setup[0].get(f"{api.ROUTE_PREFIX}/session/missing/result", headers=headers()).status_code == 404

def test_sessions(setup):
    setup[1].session_registry.submit_session(None)
    response = setup[0].get(f"{api.ROUTE_PREFIX}/sessions?limit=999", headers=headers())
    assert response.status_code == 200
    assert response.json()["data"]["limit"] == 100

def test_audit_routes(setup):
    assert setup[0].post(f"{api.ROUTE_PREFIX}/audit/query", headers=headers(), json={}).status_code == 200
    assert setup[0].get(f"{api.ROUTE_PREFIX}/audit", headers=headers()).status_code == 200

def test_body_must_be_object(setup):
    assert setup[0].post(f"{api.ROUTE_PREFIX}/plan", headers=headers(), json=[]).status_code == 400

def test_private_hosts():
    assert api._private_host("localhost")
    assert api._private_host("127.0.0.1:8000")
    assert not api._private_host("example.com")

def test_dataclass_hydration():
    value = api._construct_dataclass(HydrationParent, {"child": {"value": "4"}, "names": ["a"]})
    assert value.child.value == 4

def test_unknown_field_rejected():
    @dataclass
    class Model:
        value: int
    with pytest.raises(api.TerminalApiValidationError):
        api._construct_dataclass(Model, {"value": 1, "extra": 2})

def test_missing_field_rejected():
    @dataclass
    class Model:
        value: int
    with pytest.raises(api.TerminalApiValidationError):
        api._construct_dataclass(Model, {})

def test_no_direct_execution():
    source = open(api.__file__, encoding="utf-8").read()
    assert "import subprocess" not in source
    assert "from subprocess" not in source
    assert "Popen(" not in source
    assert "shell=True" not in source
    assert ".write_text(" not in source
    assert ".write_bytes(" not in source
