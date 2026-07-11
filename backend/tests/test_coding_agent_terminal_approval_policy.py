from __future__ import annotations

import dataclasses
import json
import threading

import pytest

import backend.coding_agent_terminal_approval_policy as ap

KEY = b"k" * 32
PLAN = "a" * 64

def request(**overrides):
    values = dict(
        subject="user-1",
        role="admin",
        project_id="project-1",
        plan_sha256=PLAN,
        command_id="unit_test-1",
        session_id="session-1",
        risk="high",
        requested_at=100,
    )
    values.update(overrides)
    return ap.TerminalApprovalRequest(**values)

def context(**overrides):
    values = dict(
        now=101,
        subject="user-1",
        role="admin",
        project_id="project-1",
        plan_sha256=PLAN,
        command_id="unit_test-1",
        session_id="session-1",
        risk="high",
    )
    values.update(overrides)
    return ap.TerminalApprovalContext(**values)

def authority(**policy_overrides):
    policy = ap.TerminalApprovalPolicy(**policy_overrides)
    return ap.build_terminal_approval_authority(KEY, policy)

def test_contract_and_capabilities():
    assert ap.CONTRACT_VERSION == "forgecode.terminal-approval-policy.v1"
    caps = ap.TerminalApprovalCapabilities()
    assert caps.approval_issue and caps.approval_verify and caps.replay_protection
    assert not caps.command_execution and not caps.shell and not caps.file_write
    assert not caps.database and not caps.git_write and not caps.network and not caps.deployment and not caps.api_routes

def test_issue_and_verify_consumes():
    auth = authority()
    token = auth.issue(request())
    decision = auth.verify(token.token, context())
    assert decision.ok and decision.state == "approved" and decision.consumed
    assert token.token_id in auth.consumed_token_ids()
    assert token.token_id not in auth.active_token_ids()

def test_replay_rejected():
    auth = authority()
    token = auth.issue(request())
    assert auth.verify(token.token, context()).ok
    decision = auth.verify(token.token, context(now=102))
    assert not decision.ok and decision.code == "approval_replayed"

def test_verify_without_consume():
    auth = authority()
    token = auth.issue(request())
    decision = auth.verify(token.token, context(), consume=False)
    assert decision.ok and not decision.consumed
    assert token.token_id in auth.active_token_ids()

@pytest.mark.parametrize("field,value,code", [
    ("subject", "other", "subject_mismatch"),
    ("role", "founder", "role_mismatch"),
    ("project_id", "other", "project_id_mismatch"),
    ("plan_sha256", "b"*64, "plan_sha256_mismatch"),
    ("command_id", "other", "command_id_mismatch"),
    ("session_id", "other", "session_id_mismatch"),
    ("risk", "medium", "risk_mismatch"),
])
def test_binding_mismatch(field, value, code):
    auth = authority()
    token = auth.issue(request())
    decision = auth.verify(token.token, context(**{field: value}))
    assert not decision.ok and decision.code == code

def test_tamper_rejected():
    auth = authority()
    token = auth.issue(request())
    raw = token.token[:-1] + ("A" if token.token[-1] != "A" else "B")
    decision = auth.verify(raw, context())
    assert not decision.ok and decision.code == "invalid_signature"

def test_bad_format_rejected():
    decision = authority().verify("bad", context())
    assert not decision.ok and decision.code == "invalid_token"

def test_expired_rejected():
    auth = authority(clock_skew_seconds=0)
    token = auth.issue(request(expires_at=101))
    decision = auth.verify(token.token, context(now=101))
    assert not decision.ok and decision.state == "expired"

def test_not_yet_valid_rejected():
    auth = authority(clock_skew_seconds=0)
    token = auth.issue(request(requested_at=100))
    decision = auth.verify(token.token, context(now=99))
    assert not decision.ok and decision.code == "approval_not_yet_valid"

def test_revoke_active():
    auth = authority()
    token = auth.issue(request())
    revoked = auth.revoke(token.token_id, revoked_at=101, reason="operator")
    assert revoked.ok and token.token_id in auth.revoked_token_ids()
    decision = auth.verify(token.token, context())
    assert not decision.ok and decision.state == "revoked"

def test_revoke_missing():
    decision = authority().revoke("missing", revoked_at=1)
    assert not decision.ok and decision.code == "approval_not_found"

def test_consumed_cannot_revoke():
    auth = authority()
    token = auth.issue(request())
    auth.verify(token.token, context())
    decision = auth.revoke(token.token_id, revoked_at=2)
    assert not decision.ok and decision.state == "consumed"

@pytest.mark.parametrize("risk,role,allowed", [
    ("low", "viewer", False),
    ("low", "developer", True),
    ("medium", "developer", False),
    ("medium", "maintainer", True),
    ("high", "maintainer", False),
    ("high", "admin", True),
])
def test_role_matrix(risk, role, allowed):
    auth = authority()
    if allowed:
        assert auth.issue(request(risk=risk, role=role))
    else:
        with pytest.raises(ap.TerminalApprovalValidationError):
            auth.issue(request(risk=risk, role=role))

def test_critical_disabled():
    with pytest.raises(ap.TerminalApprovalValidationError, match="disabled"):
        authority().issue(request(risk="critical", role="founder"))

def test_critical_enabled():
    token = authority(allow_critical=True).issue(request(risk="critical", role="founder"))
    assert token.token

@pytest.mark.parametrize("bad", ["", "x", "G"*64, "a"*63, "a"*65])
def test_bad_plan_hash(bad):
    with pytest.raises(ap.TerminalApprovalValidationError):
        authority().issue(request(plan_sha256=bad))

@pytest.mark.parametrize("risk", ["unknown", "", "HIGHER"])
def test_bad_risk(risk):
    with pytest.raises(ap.TerminalApprovalValidationError):
        authority().issue(request(risk=risk))

def test_bad_ttl():
    auth = authority(default_ttl_seconds=5, maximum_ttl_seconds=10)
    with pytest.raises(ap.TerminalApprovalValidationError):
        auth.issue(request(expires_at=111))

def test_default_ttl():
    token = authority(default_ttl_seconds=7, maximum_ttl_seconds=10).issue(request())
    assert token.expires_at == 107

def test_short_signing_key():
    with pytest.raises(ap.TerminalApprovalValidationError):
        ap.TerminalApprovalAuthority(b"short")

def test_capacity():
    auth = authority(max_active_tokens=1)
    auth.issue(request())
    with pytest.raises(ap.TerminalApprovalValidationError, match="capacity"):
        auth.issue(request(session_id="s2"))

def test_metadata_sanitized():
    token = authority().issue(request(metadata={"z": object(), "a": "x"*1000}))
    assert token.token

def test_deterministic_request_hash():
    one = ap.terminal_approval_request_sha256(request(metadata={"b": 2, "a": 1}))
    two = ap.terminal_approval_request_sha256(request(metadata={"a": 1, "b": 2}))
    assert one == two and len(one) == 64

def test_deterministic_decision_serialization():
    decision = ap._decision(True, "approved", "ok", "ok", warnings=["b", "a", "a"])
    data = ap.serialize_terminal_approval_decision(decision)
    assert data["warnings"] == ["a", "b"]
    assert ap.terminal_approval_decision_json(decision) == ap.terminal_approval_decision_json(decision)
    assert len(decision.decision_sha256) == 64

def test_policy_json_deterministic():
    policy = ap.TerminalApprovalPolicy()
    assert ap.terminal_approval_policy_json(policy) == ap.terminal_approval_policy_json(policy)

def test_decision_retention():
    auth = authority(max_decisions=2)
    for _ in range(3):
        auth.verify("bad", context())
    assert len(auth.list_decisions(limit=10)) == 2

def test_list_decisions_by_token():
    auth = authority()
    token = auth.issue(request())
    auth.verify(token.token, context(), consume=False)
    assert len(auth.list_decisions(token_id=token.token_id)) == 1

def test_revoked_retention():
    auth = authority(max_revoked_tokens=2)
    for i in range(3):
        token = auth.issue(request(session_id=f"s{i}"))
        auth.revoke(token.token_id, revoked_at=i)
    assert len(auth.revoked_token_ids()) == 2

def test_consumed_retention():
    auth = authority(max_consumed_tokens=2)
    for i in range(3):
        token = auth.issue(request(session_id=f"s{i}"))
        auth.verify(token.token, context(session_id=f"s{i}", now=101+i))
    assert len(auth.consumed_token_ids()) == 2

def test_non_one_time_policy():
    auth = authority(require_one_time_use=False)
    token = auth.issue(request())
    assert auth.verify(token.token, context()).ok
    assert auth.verify(token.token, context(now=102)).ok

def test_binding_can_be_disabled():
    auth = authority(require_session_binding=False, require_project_binding=False, require_command_binding=False)
    token = auth.issue(request())
    decision = auth.verify(token.token, context(
        session_id="other",
        project_id="other",
        plan_sha256="b"*64,
        command_id="other",
    ))
    assert decision.ok

def test_thread_safe_single_consume():
    auth = authority()
    token = auth.issue(request())
    results = []
    lock = threading.Lock()
    def run():
        value = auth.verify(token.token, context())
        with lock:
            results.append(value)
    threads = [threading.Thread(target=run) for _ in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert sum(item.ok for item in results) == 1
    assert sum(item.code == "approval_replayed" for item in results) == 7

def test_public_contract_shapes():
    assert dataclasses.is_dataclass(ap.TerminalApprovalPolicy)
    assert dataclasses.is_dataclass(ap.TerminalApprovalRequest)
    assert dataclasses.is_dataclass(ap.TerminalApprovalClaims)
    assert dataclasses.is_dataclass(ap.TerminalApprovalDecision)
    assert callable(ap.build_terminal_approval_authority)

def test_no_execution_imports():
    source = open(ap.__file__, encoding="utf-8").read()
    assert "subprocess" not in source
    assert "Popen(" not in source
    assert "socket" not in source
    assert "requests" not in source
    assert ".write_text(" not in source
    assert ".write_bytes(" not in source
