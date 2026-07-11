from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest

import backend.coding_agent_terminal_execution_planner as tp


def command(command_id="cmd-1", **changes):
    value = {
        "id": command_id,
        "category": "syntax_check",
        "label": "Compile Python",
        "argv": ["python", "-m", "compileall", "."],
        "working_directory": ".",
        "risk": "low",
        "requires_approval": False,
        "read_only": True,
        "mutates_files": False,
        "installs_dependencies": False,
        "starts_long_running_process": False,
        "requires_network": False,
        "expected_outputs": [],
        "warnings": [],
        "metadata": {},
    }
    value.update(changes)
    return value


def request(root: Path, commands=None, command_ids=None, **changes):
    values = {
        "project_id": "project-1",
        "project_root": str(root),
        "approved_root": str(root.parent),
        "command_ids": command_ids or ["cmd-1"],
        "discovered_commands": commands or [command()],
    }
    values.update(changes)
    return tp.TerminalExecutionPlanRequest(**values)


def error(result):
    assert not result.ok and result.errors
    return result.errors[0]["code"]


def test_public_api_and_contract(tmp_path):
    result = tp.build_terminal_execution_plan(request(tmp_path))
    data = tp.serialize_terminal_execution_plan(result)
    assert result.ok and data["contract_version"] == "forgecode.terminal-plan.v1"
    assert set(data) == {
        "ok",
        "project_id",
        "project_root",
        "steps",
        "risk",
        "requires_approval",
        "approval_reasons",
        "warnings",
        "errors",
        "statistics",
        "capabilities",
        "contract_version",
    }
    assert data["capabilities"] == {
        "repository_read": True,
        "command_planning": True,
        "command_execution": False,
        "shell": False,
        "subprocess": False,
        "file_write": False,
        "git_read": False,
        "git_write": False,
        "network": False,
        "deployment": False,
    }


def test_source_has_no_execution_or_write_primitives():
    source = inspect.getsource(tp)
    for forbidden in (
        "import subprocess",
        "from subprocess",
        "os.system",
        "os.popen",
        "subprocess.",
        "create_subprocess",
        ".write_text(",
        ".write_bytes(",
        "open(",
    ):
        assert forbidden not in source


def test_plan_does_not_execute_or_write(tmp_path):
    marker = tmp_path / "SHOULD_NOT_EXIST"
    result = tp.build_terminal_execution_plan(
        request(tmp_path, commands=[command(argv=["python", "-c", f"open({str(marker)!r},'w').write('x')"])])
    )
    assert result.ok and not marker.exists()


def test_working_directory_resolution_and_approved_root(tmp_path):
    project = tmp_path / "project"
    child = project / "backend"
    child.mkdir(parents=True)
    result = tp.build_terminal_execution_plan(
        request(project, commands=[command(working_directory="backend")])
    )
    assert result.ok and Path(result.steps[0].working_directory) == child.resolve()
    outside = tmp_path / "outside"
    outside.mkdir()
    result = tp.build_terminal_execution_plan(
        tp.TerminalExecutionPlanRequest(
            "p", str(project), str(outside), ["cmd-1"], [command()]
        )
    )
    assert error(result) == "outside_approved_root"


def test_path_traversal_and_missing_working_directory_rejected(tmp_path):
    assert error(tp.build_terminal_execution_plan(request(tmp_path, commands=[command(working_directory="../")])) ) == "path_traversal"
    assert error(tp.build_terminal_execution_plan(request(tmp_path, commands=[command(working_directory="missing")])) ) == "invalid_working_directory"


def test_requires_fc_bt_4a_contract_and_known_ids(tmp_path):
    mismatch = request(tmp_path, discovered_command_contract_version="other.v1")
    assert error(tp.build_terminal_execution_plan(mismatch)) == "command_contract_mismatch"
    unknown = request(tmp_path, command_ids=["missing"])
    assert error(tp.build_terminal_execution_plan(unknown)) == "unknown_command_id"


def test_duplicate_and_step_limits(tmp_path):
    duplicate = request(tmp_path, command_ids=["cmd-1", "cmd-1"])
    assert error(tp.build_terminal_execution_plan(duplicate)) == "duplicate_command_id"
    policy = tp.TerminalExecutionPolicy(maximum_steps=1)
    commands = [command("a"), command("b")]
    result = tp.build_terminal_execution_plan(
        request(tmp_path, commands=commands, command_ids=["a", "b"], policy=policy)
    )
    assert error(result) == "step_limit_exceeded"


@pytest.mark.parametrize(
    "argv,code",
    [
        (["bash", "-lc", "pytest"], "executable_denied"),
        (["ruby", "test.rb"], "executable_not_allowed"),
        (["C:\\Python\\python.exe", "-m", "pytest"], "executable_path_rejected"),
        (["python", "-m", "pytest", "&&", "echo"], "shell_metacharacter_rejected"),
        (["python", "-c", "print(`x`)"], "shell_metacharacter_rejected"),
    ],
)
def test_executable_and_shell_controls(tmp_path, argv, code):
    assert error(tp.build_terminal_execution_plan(request(tmp_path, commands=[command(argv=argv)]))) == code


def test_category_allowlist(tmp_path):
    policy = tp.TerminalExecutionPolicy(allowed_categories=["unit_test"])
    result = tp.build_terminal_execution_plan(request(tmp_path, policy=policy))
    assert error(result) == "category_not_allowed"


@pytest.mark.parametrize(
    "changes,code",
    [
        ({"requires_network": True}, "network_not_allowed"),
        ({"installs_dependencies": True}, "dependency_install_not_allowed"),
        ({"mutates_files": True}, "file_mutation_not_allowed"),
        ({"starts_long_running_process": True}, "long_running_not_allowed"),
        ({"metadata": {"git_read": True}}, "git_read_not_allowed"),
        ({"metadata": {"git_write": True}}, "git_write_not_allowed"),
        ({"metadata": {"deployment": True}}, "deployment_not_allowed"),
    ],
)
def test_side_effect_policy_defaults_deny(tmp_path, changes, code):
    result = tp.build_terminal_execution_plan(request(tmp_path, commands=[command(**changes)]))
    assert error(result) == code


def test_critical_risk_is_never_plannable(tmp_path):
    policy = tp.TerminalExecutionPolicy(
        allow_network=True,
        allow_long_running=True,
        allow_dependency_install=True,
        allow_file_mutation=True,
        allow_git_write=True,
        allow_deployment=True,
    )
    result = tp.build_terminal_execution_plan(
        request(tmp_path, commands=[command(risk="critical")], policy=policy)
    )
    assert error(result) == "critical_risk_rejected"


def test_risk_approval_and_approval_grant(tmp_path):
    test_command = command(category="unit_test", argv=["python", "-m", "pytest"])
    result = tp.build_terminal_execution_plan(request(tmp_path, commands=[test_command]))
    assert result.ok and result.risk == "medium" and result.requires_approval
    assert result.steps[0].requires_approval and not result.steps[0].approval_granted
    approved = tp.build_terminal_execution_plan(
        request(tmp_path, commands=[test_command], approved_command_ids=["cmd-1"])
    )
    assert approved.ok and not approved.requires_approval and approved.steps[0].approval_granted


def test_long_running_stop_strategy_and_approval(tmp_path):
    policy = tp.TerminalExecutionPolicy(allow_long_running=True)
    result = tp.build_terminal_execution_plan(
        request(
            tmp_path,
            commands=[
                command(
                    category="dev_server",
                    argv=["npm", "run", "dev"],
                    risk="medium",
                    starts_long_running_process=True,
                    requires_approval=True,
                )
            ],
            policy=policy,
        )
    )
    assert result.ok and result.risk == "high" and result.requires_approval
    assert result.steps[0].stop_strategy == "future_graceful_then_process_group_cancel"


def test_environment_filtering_and_sorting(tmp_path):
    environment = [
        tp.TerminalEnvironmentVariable("PYTHONUTF8", "1"),
        tp.TerminalEnvironmentVariable("CI", "true"),
    ]
    result = tp.build_terminal_execution_plan(request(tmp_path, environment=environment))
    assert result.ok and [item.name for item in result.steps[0].environment] == ["CI", "PYTHONUTF8"]


@pytest.mark.parametrize(
    "environment,code",
    [
        ([tp.TerminalEnvironmentVariable("OPENAI_API_KEY", "x")], "environment_variable_not_allowed"),
        ([tp.TerminalEnvironmentVariable("bad-name", "x")], "invalid_environment_variable"),
        ([tp.TerminalEnvironmentVariable("CI", "a;rm")], "shell_metacharacter_rejected"),
        ([tp.TerminalEnvironmentVariable("CI", "1"), tp.TerminalEnvironmentVariable("CI", "2")], "duplicate_environment_variable"),
    ],
)
def test_environment_rejections(tmp_path, environment, code):
    result = tp.build_terminal_execution_plan(request(tmp_path, environment=environment))
    assert error(result) == code


def test_environment_and_resource_limits(tmp_path):
    policy = tp.TerminalExecutionPolicy(
        maximum_environment_variables=1,
        maximum_timeout_seconds=10,
        maximum_output_bytes=10,
        maximum_error_bytes=10,
    )
    assert error(tp.build_terminal_execution_plan(request(
        tmp_path,
        policy=policy,
        environment=[tp.TerminalEnvironmentVariable("CI", "1"), tp.TerminalEnvironmentVariable("TZ", "UTC")],
        timeout_seconds=10,
        maximum_output_bytes=10,
        maximum_error_bytes=10,
    ))) == "environment_limit_exceeded"
    assert error(tp.build_terminal_execution_plan(request(
        tmp_path,
        policy=policy,
        timeout_seconds=11,
        maximum_output_bytes=10,
        maximum_error_bytes=10,
    ))) == "timeout_limit_exceeded"
    assert error(tp.build_terminal_execution_plan(request(
        tmp_path,
        policy=policy,
        timeout_seconds=10,
        maximum_output_bytes=11,
        maximum_error_bytes=10,
    ))) == "output_limit_exceeded"


def test_deterministic_steps_serialization_and_json(tmp_path):
    one = tp.build_terminal_execution_plan(request(tmp_path))
    two = tp.build_terminal_execution_plan(request(tmp_path))
    assert tp.serialize_terminal_execution_plan(one) == tp.serialize_terminal_execution_plan(two)
    assert one.steps[0].step_id == two.steps[0].step_id
    payload = tp.terminal_execution_plan_json(one)
    assert json.loads(payload) == tp.serialize_terminal_execution_plan(one)
    assert payload == tp.terminal_execution_plan_json(two)
