import asyncio
import json

from backend.forge_commander.approval_actions import authorize_write_action
from backend.forge_commander.cloud_device_registry import DeviceSession
from backend.forge_commander.cloud_task_channel import build_task_envelope
from backend.forge_commander.production_agent_runtime import _safe_handler


def _message(capability, *, required=True, granted=False, request=None):
    return {
        "task_id": "task-1", "required_capability": capability,
        "approval_required": required, "approval_granted": granted,
        "instruction": json.dumps(request or {}),
    }


def test_write_action_requires_both_required_and_granted():
    missing = authorize_write_action(
        task_id="t1", capability="file.write_text",
        approval_required=True, approval_granted=False,
    )
    bypass = authorize_write_action(
        task_id="t1", capability="file.write_text",
        approval_required=False, approval_granted=True,
    )
    allowed = authorize_write_action(
        task_id="t1", capability="file.write_text",
        approval_required=True, approval_granted=True,
    )
    assert missing.reason == "explicit_approval_required"
    assert bypass.reason == "write_action_must_require_approval"
    assert allowed.allowed is True
    assert allowed.audit_id.startswith("fc-audit-")
    assert missing.audit_id == allowed.audit_id


def test_unapproved_write_is_rejected_without_touching_disk(tmp_path):
    target = tmp_path / "blocked.txt"
    result = asyncio.run(_safe_handler(_message(
        "file.write_text", request={"path": str(target), "content": "blocked"},
    )))
    assert result["succeeded"] is False
    assert result["reason"] == "explicit_approval_required"
    assert not target.exists()
    assert result["output"]["approval_granted"] is False


def test_approved_write_is_bounded_atomic_and_audited(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "backend.forge_commander.approval_actions.allowed_write_roots",
        lambda: (tmp_path.resolve(),),
    )
    target = tmp_path / "approved.txt"
    result = asyncio.run(_safe_handler(_message(
        "file.write_text", granted=True,
        request={"path": str(target), "content": "approved"},
    )))
    assert result["succeeded"] is True
    assert result["reason"] == "approved_action_ok"
    assert target.read_text(encoding="utf-8") == "approved"
    assert result["output"]["audit_id"].startswith("fc-audit-")
    assert result["output"]["data"]["bytes_written"] == 8


def test_sensitive_paths_and_arbitrary_terminal_profiles_are_blocked(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "backend.forge_commander.approval_actions.allowed_write_roots",
        lambda: (tmp_path.resolve(),),
    )
    env_result = asyncio.run(_safe_handler(_message(
        "file.write_text", granted=True,
        request={"path": str(tmp_path / ".env"), "content": "SECRET=x"},
    )))
    terminal_result = asyncio.run(_safe_handler(_message(
        "terminal.execute_profile", granted=True,
        request={"cwd": str(tmp_path), "profile": "powershell_arbitrary"},
    )))
    assert env_result["reason"] == "sensitive_file_blocked"
    assert terminal_result["reason"] == "terminal_profile_not_allowlisted"


def test_git_diff_check_profile_is_allowlisted(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "backend.forge_commander.approval_actions.allowed_write_roots",
        lambda: (tmp_path.resolve(),),
    )
    result = asyncio.run(_safe_handler(_message(
        "terminal.execute_profile", granted=True,
        request={"cwd": str(tmp_path), "profile": "git_diff_check"},
    )))
    assert result["reason"] == "approved_action_ok"
    assert result["output"]["data"]["profile"] == "git_diff_check"
    assert result["output"]["data"]["exit_code"] in {0, 129}


def test_read_only_capability_cannot_receive_write_approval():
    result = asyncio.run(_safe_handler(_message(
        "device.identity", required=True, granted=True,
    )))
    assert result["succeeded"] is False
    assert result["reason"] == "read_only_capability_requires_approval_false"


def test_approval_retry_keeps_task_identity():
    session = DeviceSession(
        session_id="session-1", device_id="device-1", owner_subject="owner-1",
        instance_id="instance-1", connected_at="2026-08-28T00:00:00+00:00",
        heartbeat_at="2026-08-28T00:00:00+00:00",
    )
    pending = build_task_envelope(
        session, instruction='{"path":"C:/temp/cert.txt","content":"ok"}',
        required_capability="file.write_text", approval_required=True,
        approval_granted=False,
    )
    approved = build_task_envelope(
        session, instruction='{"path":"C:/temp/cert.txt","content":"ok"}',
        required_capability="file.write_text", approval_required=True,
        approval_granted=True,
    )
    assert pending.task_id == approved.task_id


def test_mcp_tool_name_alias_reaches_write_handler(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "backend.forge_commander.approval_actions.allowed_write_roots",
        lambda: (tmp_path.resolve(),),
    )
    target = tmp_path / "alias.txt"
    result = asyncio.run(_safe_handler(_message(
        "write_file_text", granted=True,
        request={"path": str(target), "content": "alias-ok"},
    )))
    assert result["succeeded"] is True
    assert target.read_text(encoding="utf-8") == "alias-ok"


def test_approved_delete_is_audited_and_removes_only_file(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "backend.forge_commander.approval_actions.allowed_write_roots",
        lambda: (tmp_path.resolve(),),
    )
    target = tmp_path / "certification.txt"
    target.write_text("temporary", encoding="utf-8")
    result = asyncio.run(_safe_handler(_message(
        "file.delete", granted=True, request={"path": str(target)},
    )))
    assert result["succeeded"] is True
    assert result["output"]["data"]["deleted"] is True
    assert result["output"]["data"]["previous_sha256"]
    assert not target.exists()
