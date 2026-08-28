import asyncio
import json

from backend.forge_commander.approval_actions import authorize_write_action
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


def test_read_only_capability_cannot_receive_write_approval():
    result = asyncio.run(_safe_handler(_message(
        "device.identity", required=True, granted=True,
    )))
    assert result["succeeded"] is False
    assert result["reason"] == "read_only_capability_requires_approval_false"
