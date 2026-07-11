from __future__ import annotations

import inspect
import json
import os
import threading
from pathlib import Path

import pytest

import backend.coding_agent_terminal_execution_runtime as rt
import backend.coding_agent_terminal_execution_planner as tp


def discovered(
    command_id: str,
    code: str,
    *,
    category: str = "syntax_check",
    risk: str = "low",
    requires_approval: bool = False,
    mutates_files: bool = False,
    requires_network: bool = False,
    installs_dependencies: bool = False,
    starts_long_running_process: bool = False,
    required_files: list[str] | None = None,
):
    return {
        "id": command_id,
        "category": category,
        "label": f"Run {command_id}",
        "argv": ["python", "-c", code],
        "working_directory": ".",
        "ecosystem": "python",
        "package_manager": None,
        "framework": "python",
        "confidence": "high",
        "risk": risk,
        "requires_approval": requires_approval,
        "read_only": not mutates_files,
        "mutates_files": mutates_files,
        "installs_dependencies": installs_dependencies,
        "starts_long_running_process": starts_long_running_process,
        "requires_network": requires_network,
        "expected_outputs": [],
        "required_files": required_files or ["marker.txt"],
        "evidence": [],
        "warnings": [],
        "metadata": {},
    }


def make_plan(
    root: Path,
    commands: list[dict] | None = None,
    *,
    approved: list[str] | None = None,
    environment: list[tp.TerminalEnvironmentVariable] | None = None,
    timeout: int = 5,
    output_limit: int = 256_000,
    error_limit: int = 128_000,
    planner_policy: tp.TerminalExecutionPolicy | None = None,
):
    root.mkdir(parents=True, exist_ok=True)
    marker = root / "marker.txt"
    if not marker.exists():
        marker.write_text("stable\n", encoding="utf-8")
    records = commands or [discovered("cmd-1", "print('ok')")]
    request = tp.TerminalExecutionPlanRequest(
        project_id="project-1",
        project_root=str(root),
        approved_root=str(root.parent),
        command_ids=[item["id"] for item in records],
        discovered_commands=records,
        policy=planner_policy or tp.TerminalExecutionPolicy(),
        environment=environment or [],
        approved_command_ids=approved or [],
        timeout_seconds=timeout,
        maximum_output_bytes=output_limit,
        maximum_error_bytes=error_limit,
    )
    plan = tp.build_terminal_execution_plan(request)
    assert plan.ok, plan.errors
    return request, plan


def runtime_request(
    root: Path,
    commands: list[dict] | None = None,
    *,
    approved: list[str] | None = None,
    environment: list[tp.TerminalEnvironmentVariable] | None = None,
    timeout: int = 5,
    output_limit: int = 256_000,
    error_limit: int = 128_000,
    planner_policy: tp.TerminalExecutionPolicy | None = None,
    runtime_policy: rt.TerminalRuntimePolicy | None = None,
    snapshot: bool = True,
    continue_on_error: bool = False,
    total_timeout: int = 30,
):
    plan_request, plan = make_plan(
        root,
        commands,
        approved=approved,
        environment=environment,
        timeout=timeout,
        output_limit=output_limit,
        error_limit=error_limit,
        planner_policy=planner_policy,
    )
    policy = runtime_policy or rt.TerminalRuntimePolicy()
    snap = rt.build_terminal_execution_snapshot(plan_request, policy) if snapshot else None
    bindings = rt.build_terminal_executable_bindings(plan, policy)
    return rt.TerminalExecutionRuntimeRequest(
        "execution-1",
        plan_request,
        plan,
        snap,
        bindings,
        policy,
        total_timeout,
        continue_on_error,
    )


def error_code(result):
    return result.errors[0]["code"] if result.errors else None


def test_contract_and_capabilities(tmp_path):
    request = runtime_request(tmp_path / "project")
    result = rt.execute_terminal_execution_plan(request)
    data = rt.serialize_terminal_execution_runtime(result)
    assert result.ok and result.status == "succeeded"
    assert data["contract_version"] == "forgecode.terminal-runtime.v1"
    assert data["capabilities"] == {
        "repository_read": True,
        "command_planning": False,
        "command_execution": True,
        "shell": False,
        "subprocess": True,
        "cancellation": True,
        "output_capture": True,
        "file_write": False,
        "git_read": False,
        "git_write": False,
        "network": False,
        "deployment": False,
    }


def test_success_captures_stdout_and_resolved_executable(tmp_path):
    result = rt.execute_terminal_execution_plan(runtime_request(tmp_path / "project"))
    assert result.steps[0].stdout.strip() == "ok"
    assert Path(result.steps[0].resolved_executable).is_file()
    assert result.steps[0].exit_code == 0


def test_stderr_capture_and_nonzero_exit(tmp_path):
    command = discovered(
        "fail",
        "(print('bad',file=__import__('sys').stderr),__import__('sys').exit(3))",
    )
    result = rt.execute_terminal_execution_plan(runtime_request(tmp_path / "project", [command]))
    assert not result.ok and result.status == "failed"
    assert result.steps[0].exit_code == 3 and "bad" in result.steps[0].stderr


def test_timeout_terminates_process(tmp_path):
    command = discovered("slow", "__import__('time').sleep(5)")
    result = rt.execute_terminal_execution_plan(
        runtime_request(tmp_path / "project", [command], timeout=1, total_timeout=3)
    )
    assert result.status == "timed_out"
    assert result.steps[0].status == "timed_out"


def test_cancellation_before_execution(tmp_path):
    token = rt.TerminalCancellationToken()
    token.cancel()
    result = rt.execute_terminal_execution_plan(runtime_request(tmp_path / "project"), token)
    assert result.status == "cancelled"
    assert result.steps[0].status == "not_run"
    assert "cancelled_before_step" in result.steps[0].warnings


def test_cancellation_during_execution(tmp_path):
    command = discovered("slow", "__import__('time').sleep(5)")
    request = runtime_request(tmp_path / "project", [command], timeout=5)
    token = rt.TerminalCancellationToken()
    timer = threading.Timer(0.15, token.cancel)
    timer.start()
    try:
        result = rt.execute_terminal_execution_plan(request, token)
    finally:
        timer.cancel()
    assert result.status == "cancelled"
    assert result.steps[0].status == "cancelled"


def test_output_truncation_is_bounded(tmp_path):
    command = discovered("large", "print('x'*5000)")
    result = rt.execute_terminal_execution_plan(
        runtime_request(tmp_path / "project", [command], output_limit=64)
    )
    step = result.steps[0]
    assert result.ok and step.stdout_truncated and len(step.stdout.encode("utf-8")) <= 64
    assert step.stdout_bytes > 64 and "stdout_truncated" in step.warnings


def test_stderr_truncation_is_bounded(tmp_path):
    command = discovered("large-error", "print('x'*5000,file=__import__('sys').stderr)")
    result = rt.execute_terminal_execution_plan(
        runtime_request(tmp_path / "project", [command], error_limit=64)
    )
    step = result.steps[0]
    assert result.ok and step.stderr_truncated and len(step.stderr.encode("utf-8")) <= 64


def test_environment_value_is_redacted_from_output(tmp_path):
    environment = [tp.TerminalEnvironmentVariable("CI", "supersecret")]
    command = discovered("env", "print(__import__('os').environ['CI'])")
    result = rt.execute_terminal_execution_plan(
        runtime_request(tmp_path / "project", [command], environment=environment)
    )
    assert "supersecret" not in result.steps[0].stdout
    assert "[REDACTED_ENV]" in result.steps[0].stdout


def test_ansi_and_control_output_are_sanitized(tmp_path):
    command = discovered("ansi", "print(chr(27)+'[31mred'+chr(27)+'[0m'+chr(1))")
    result = rt.execute_terminal_execution_plan(runtime_request(tmp_path / "project", [command]))
    assert result.steps[0].stdout.strip() == "red"


def test_snapshot_is_deterministic(tmp_path):
    plan_request, _ = make_plan(tmp_path / "project")
    one = rt.build_terminal_execution_snapshot(plan_request)
    two = rt.build_terminal_execution_snapshot(plan_request)
    assert rt.serialize_terminal_execution_runtime  # public import smoke check
    assert one == two and len(one.digest) == 64


def test_snapshot_detects_required_file_change(tmp_path):
    root = tmp_path / "project"
    request = runtime_request(root)
    (root / "marker.txt").write_text("changed\n", encoding="utf-8")
    result = rt.execute_terminal_execution_plan(request)
    assert result.status == "rejected" and error_code(result) == "repository_snapshot_changed"


def test_snapshot_rejects_missing_required_file(tmp_path):
    root = tmp_path / "project"
    plan_request, _ = make_plan(root)
    (root / "marker.txt").unlink()
    with pytest.raises(rt.TerminalRuntimeValidationError, match="missing"):
        rt.build_terminal_execution_snapshot(plan_request)


def test_snapshot_rejects_required_file_traversal(tmp_path):
    root = tmp_path / "project"
    command = discovered("bad", "print('x')", required_files=["../outside.txt"])
    (tmp_path / "outside.txt").write_text("x", encoding="utf-8")
    plan_request, _ = make_plan(root, [command])
    with pytest.raises(rt.TerminalRuntimeValidationError) as caught:
        rt.build_terminal_execution_snapshot(plan_request)
    assert caught.value.code == "invalid_required_file"


def test_snapshot_file_limit(tmp_path):
    root = tmp_path / "project"
    files = [f"f{i}.txt" for i in range(2)]
    root.mkdir(parents=True)
    for name in files:
        (root / name).write_text(name, encoding="utf-8")
    command = discovered("many", "print('x')", required_files=files)
    plan_request, _ = make_plan(root, [command])
    policy = rt.TerminalRuntimePolicy(maximum_snapshot_files=1)
    with pytest.raises(rt.TerminalRuntimeValidationError) as caught:
        rt.build_terminal_execution_snapshot(plan_request, policy)
    assert caught.value.code == "snapshot_file_limit_exceeded"


def test_snapshot_file_size_limit(tmp_path):
    root = tmp_path / "project"
    root.mkdir(parents=True)
    (root / "marker.txt").write_text("0123456789", encoding="utf-8")
    plan_request, _ = make_plan(root)
    policy = rt.TerminalRuntimePolicy(maximum_snapshot_file_bytes=2)
    with pytest.raises(rt.TerminalRuntimeValidationError) as caught:
        rt.build_terminal_execution_snapshot(plan_request, policy)
    assert caught.value.code == "snapshot_file_too_large"


def test_plan_hash_is_stable(tmp_path):
    _, plan = make_plan(tmp_path / "project")
    assert rt.terminal_execution_plan_sha256(plan) == rt.terminal_execution_plan_sha256(plan)


def test_plan_contract_mismatch_rejected(tmp_path):
    request = runtime_request(tmp_path / "project")
    request.plan.contract_version = "wrong"
    result = rt.execute_terminal_execution_plan(request)
    assert error_code(result) == "plan_contract_mismatch"


def test_plan_tampering_rejected(tmp_path):
    request = runtime_request(tmp_path / "project")
    request.plan.steps[0].label = "tampered"
    result = rt.execute_terminal_execution_plan(request)
    assert error_code(result) == "plan_mismatch"


def test_rejected_plan_cannot_execute(tmp_path):
    request = runtime_request(tmp_path / "project")
    request.plan.ok = False
    result = rt.execute_terminal_execution_plan(request)
    assert error_code(result) == "invalid_plan"


def test_missing_approval_rejected(tmp_path):
    command = discovered("test", "print('test')", category="unit_test", risk="medium")
    request = runtime_request(tmp_path / "project", [command])
    result = rt.execute_terminal_execution_plan(request)
    assert error_code(result) == "approval_required"


def test_approved_medium_risk_command_executes(tmp_path):
    command = discovered("test", "print('test')", category="unit_test", risk="medium")
    result = rt.execute_terminal_execution_plan(
        runtime_request(tmp_path / "project", [command], approved=["test"])
    )
    assert result.ok and result.steps[0].stdout.strip() == "test"


def test_runtime_file_mutation_gate_is_independent(tmp_path):
    command = discovered(
        "mutating",
        "print('planned')",
        risk="high",
        requires_approval=True,
        mutates_files=True,
    )
    planner_policy = tp.TerminalExecutionPolicy(allow_file_mutation=True)
    request = runtime_request(
        tmp_path / "project",
        [command],
        approved=["mutating"],
        planner_policy=planner_policy,
    )
    result = rt.execute_terminal_execution_plan(request)
    assert error_code(result) == "file_mutation_not_allowed"


def test_runtime_network_gate_is_independent(tmp_path):
    command = discovered(
        "network",
        "print('planned')",
        risk="high",
        requires_approval=True,
        requires_network=True,
    )
    planner_policy = tp.TerminalExecutionPolicy(allow_network=True)
    request = runtime_request(
        tmp_path / "project",
        [command],
        approved=["network"],
        planner_policy=planner_policy,
    )
    result = rt.execute_terminal_execution_plan(request)
    assert error_code(result) == "network_not_allowed"


def test_snapshot_required_by_default(tmp_path):
    request = runtime_request(tmp_path / "project", snapshot=False)
    result = rt.execute_terminal_execution_plan(request)
    assert error_code(result) == "snapshot_required"


def test_snapshot_can_be_disabled_explicitly(tmp_path):
    policy = rt.TerminalRuntimePolicy(require_snapshot=False)
    request = runtime_request(tmp_path / "project", runtime_policy=policy, snapshot=False)
    result = rt.execute_terminal_execution_plan(request)
    assert result.ok


def test_executable_binding_hash_is_verified(tmp_path):
    request = runtime_request(tmp_path / "project")
    binding = request.executable_bindings[0]
    request.executable_bindings = [
        rt.TerminalExecutableBinding(binding.executable, binding.resolved_path, binding.size_bytes, "0" * 64)
    ]
    result = rt.execute_terminal_execution_plan(request)
    assert error_code(result) == "executable_binding_changed"


def test_executable_binding_scope_must_be_exact(tmp_path):
    request = runtime_request(tmp_path / "project")
    request.executable_bindings = []
    result = rt.execute_terminal_execution_plan(request)
    assert error_code(result) == "executable_binding_scope_mismatch"


def test_missing_executable_is_rejected(tmp_path, monkeypatch):
    _, plan = make_plan(tmp_path / "project")
    monkeypatch.setattr(rt.shutil, "which", lambda *args, **kwargs: None)
    with pytest.raises(rt.TerminalRuntimeValidationError) as caught:
        rt.build_terminal_executable_bindings(plan)
    assert caught.value.code == "executable_not_found"


def test_shell_wrapper_executable_is_rejected(tmp_path, monkeypatch):
    wrapper = tmp_path / "python.sh"
    wrapper.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    wrapper.chmod(0o755)
    _, plan = make_plan(tmp_path / "project")
    monkeypatch.setattr(rt.shutil, "which", lambda *args, **kwargs: str(wrapper))
    with pytest.raises(rt.TerminalRuntimeValidationError) as caught:
        rt.build_terminal_executable_bindings(plan)
    assert caught.value.code == "shell_wrapper_rejected"


def test_invalid_execution_id_rejected(tmp_path):
    request = runtime_request(tmp_path / "project")
    request.execution_id = "bad id"
    result = rt.execute_terminal_execution_plan(request)
    assert error_code(result) == "invalid_execution_id"


def test_invalid_runtime_policy_rejected(tmp_path):
    policy = rt.TerminalRuntimePolicy(maximum_steps=0)
    plan_request, plan = make_plan(tmp_path / "project")
    request = rt.TerminalExecutionRuntimeRequest("execution-1", plan_request, plan, None, [], policy)
    result = rt.execute_terminal_execution_plan(request)
    assert error_code(result) == "invalid_runtime_policy"


def test_continue_on_error_runs_remaining_steps(tmp_path):
    commands = [
        discovered("fail", "__import__('sys').exit(2)"),
        discovered("pass", "print('second')"),
    ]
    result = rt.execute_terminal_execution_plan(
        runtime_request(tmp_path / "project", commands, continue_on_error=True)
    )
    assert [step.status for step in result.steps] == ["failed", "succeeded"]
    assert result.status == "failed" and result.steps[1].stdout.strip() == "second"


def test_default_failure_stops_remaining_steps(tmp_path):
    commands = [
        discovered("fail", "__import__('sys').exit(2)"),
        discovered("pass", "print('second')"),
    ]
    result = rt.execute_terminal_execution_plan(runtime_request(tmp_path / "project", commands))
    assert [step.status for step in result.steps] == ["failed", "not_run"]
    assert "stopped_after_failed" in result.steps[1].warnings


def test_continue_on_error_can_be_disabled_by_policy(tmp_path):
    commands = [discovered("fail", "__import__('sys').exit(2)")]
    policy = rt.TerminalRuntimePolicy(allow_continue_on_error=False)
    request = runtime_request(
        tmp_path / "project",
        commands,
        runtime_policy=policy,
        continue_on_error=True,
    )
    result = rt.execute_terminal_execution_plan(request)
    assert error_code(result) == "continue_on_error_not_allowed"


def test_launch_failure_is_auditable(tmp_path):
    request = runtime_request(tmp_path / "project")

    def fail_runner(*args, **kwargs):
        return rt._RawProcessOutcome(
            "launch_failed", None, b"", b"", 0, 0, False, False, 1,
            "process_launch_failed", "synthetic launch failure"
        )

    result = rt.execute_terminal_execution_plan(request, _runner=fail_runner)
    assert result.status == "failed"
    assert result.steps[0].errors[0]["code"] == "process_launch_failed"


def test_json_contract_is_valid_and_complete(tmp_path):
    result = rt.execute_terminal_execution_plan(runtime_request(tmp_path / "project"))
    data = json.loads(rt.terminal_execution_runtime_json(result))
    assert set(data) == {
        "ok", "execution_id", "project_id", "project_root", "status",
        "plan_sha256", "snapshot_sha256", "steps", "warnings", "errors",
        "statistics", "capabilities", "contract_version",
    }
    assert data == rt.serialize_terminal_execution_runtime(result)


def test_runtime_source_has_no_shell_or_arbitrary_command_api():
    source = inspect.getsource(rt)
    assert "shell=True" not in source
    assert "os.system" not in source
    assert "os.popen" not in source
    fields = {field.name for field in rt.TerminalExecutionRuntimeRequest.__dataclass_fields__.values()}
    assert not {"command", "command_text", "shell_command"} & fields


def test_runtime_does_not_write_repository_files(tmp_path):
    root = tmp_path / "project"
    request = runtime_request(root)
    before = (root / "marker.txt").read_bytes()
    result = rt.execute_terminal_execution_plan(request)
    assert result.ok and (root / "marker.txt").read_bytes() == before


def test_scoped_statistics(tmp_path):
    result = rt.execute_terminal_execution_plan(runtime_request(tmp_path / "project"))
    assert result.statistics["planned_steps"] == 1
    assert result.statistics["attempted_steps"] == 1
    assert result.statistics["succeeded_steps"] == 1
    assert result.statistics["not_run_steps"] == 0
