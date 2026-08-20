from dataclasses import dataclass

import pytest

from backend.platform.forgecode_capability_facade import (
    CONTRACT_VERSION,
    ForgeCodeRequest,
    capability_catalogue,
    invoke_adapter,
    invoke,
)


def test_catalogue_is_stable_and_governed():
    items = {item.name: item for item in capability_catalogue()}
    assert set(items) == {
        "inspect_repository", "discover_validation", "preview_change",
        "plan_execution", "execute_plan", "report_result",
    }
    assert items["execute_plan"].mutates_repository is True
    assert items["execute_plan"].requires_approval is True
    assert all(not item.mutates_repository for name, item in items.items() if name != "execute_plan")


def test_adapter_preserves_correlation_and_normalizes_dataclass():
    @dataclass
    class SpecialistResult:
        files: int

    result = invoke_adapter(
        ForgeCodeRequest("inspect_repository", "corr-1", {"root": "repo"}),
        lambda payload: SpecialistResult(files=3),
    )
    assert result.status == "ok"
    assert result.correlation_id == "corr-1"
    assert result.data == {"files": 3}
    assert result.contract_version == CONTRACT_VERSION


def test_unsupported_operation_returns_stable_error():
    result = invoke_adapter(
        ForgeCodeRequest("raw_internal_call", "corr-2"), lambda payload: payload
    )
    assert result.status == "error"
    assert result.error is not None
    assert result.error.code == "unsupported_operation"
    assert result.error.category == "validation"


def test_specialist_failure_is_normalized_without_leaking_exception():
    class SpecialistPolicyError(RuntimeError):
        pass

    def fail(payload):
        raise SpecialistPolicyError("approval required")

    result = invoke_adapter(ForgeCodeRequest("execute_plan", "corr-3"), fail)
    assert result.status == "error"
    assert result.error is not None
    assert result.error.code == "SpecialistPolicyError"
    assert result.error.category == "policy"


def test_blank_correlation_id_is_rejected():
    with pytest.raises(ValueError, match="correlation_id is required"):
        invoke_adapter(ForgeCodeRequest("inspect_repository", " "), lambda payload: payload)


def test_repository_and_validation_adapters(tmp_path):
    project = tmp_path / "repo"
    project.mkdir()
    (project / "package.json").write_text(
        '{"scripts":{"test":"vitest run","build":"vite build"},"devDependencies":{"vite":"1","vitest":"1"}}',
        encoding="utf-8",
    )
    (project / "app.py").write_text("print('ok')\n", encoding="utf-8")

    inspected = invoke(ForgeCodeRequest(
        "inspect_repository", "corr-inspect",
        {"project_path": str(project), "approved_root": str(tmp_path)},
    ))
    assert inspected.status == "ok"
    assert inspected.data["summary"]["project_name"] == "repo"

    discovered = invoke(ForgeCodeRequest(
        "discover_validation", "corr-discover",
        {"project_id": "p1", "project_root": str(project), "approved_root": str(tmp_path)},
    ))
    assert discovered.status == "ok"
    assert discovered.data["ok"] is True
    assert {item["category"] for item in discovered.data["commands"]} >= {"unit_test", "build"}


def test_preview_change_is_dry_run_and_non_mutating(tmp_path):
    project = tmp_path / "repo"
    project.mkdir()
    target = project / "a.txt"
    target.write_text("old\n", encoding="utf-8")
    import hashlib
    digest = hashlib.sha256(target.read_bytes()).hexdigest()

    result = invoke(ForgeCodeRequest(
        "preview_change", "corr-preview",
        {
            "project_id": "p1", "project_root": str(project),
            "approved_root": str(project), "approved_paths": ["a.txt"],
            "files": [{"path": "a.txt", "operation": "replace", "new_content": "new\n", "expected_sha256": digest}],
        },
    ))
    assert result.status == "ok"
    assert result.data["ok"] is True
    assert result.data["dry_run"] is True
    assert result.data["applied"] is False
    assert target.read_text(encoding="utf-8") == "old\n"


def test_plan_execution_wraps_existing_terminal_planner(tmp_path):
    project = tmp_path / "repo"
    project.mkdir()
    command = {
        "id": "cmd-1", "category": "typecheck", "label": "Typecheck",
        "argv": ["python", "-m", "compileall", "."], "working_directory": ".",
        "risk": "low", "requires_approval": False, "read_only": True,
        "mutates_files": False, "installs_dependencies": False,
        "starts_long_running_process": False, "requires_network": False,
        "expected_outputs": [], "warnings": [], "metadata": {},
    }
    result = invoke(ForgeCodeRequest(
        "plan_execution", "corr-plan",
        {
            "project_id": "p1", "project_root": str(project),
            "approved_root": str(tmp_path), "command_ids": ["cmd-1"],
            "discovered_commands": [command],
        },
    ))
    assert result.status == "ok"
    assert result.data["ok"] is True
    assert result.data["statistics"]["steps"] == 1
    assert result.data["steps"][0]["command_id"] == "cmd-1"


def _runtime_payload(project, *, authorized):
    command = {
        "id": "cmd-run", "category": "syntax_check", "label": "Smoke",
        "argv": ["python", "-c", "print('forgecode-ok')"],
        "working_directory": ".", "risk": "low",
        "requires_approval": False, "read_only": True,
        "mutates_files": False, "installs_dependencies": False,
        "starts_long_running_process": False, "requires_network": False,
        "expected_outputs": [], "required_files": [], "warnings": [], "metadata": {},
    }
    return {
        "project_id": "p1", "project_root": str(project),
        "approved_root": str(project), "command_ids": ["cmd-run"],
        "discovered_commands": [command], "approved_command_ids": [],
        "execution_id": "fc-test-execution", "execution_authorized": authorized,
        "total_timeout_seconds": 30,
    }


def test_execute_plan_requires_explicit_facade_authorization(tmp_path):
    project = tmp_path / "repo"
    project.mkdir()
    result = invoke(ForgeCodeRequest(
        "execute_plan", "corr-denied", _runtime_payload(project, authorized=False)
    ))
    assert result.status == "error"
    assert result.error is not None
    assert result.error.category == "policy"
    assert "authorization" in result.error.message


def test_execute_plan_uses_controlled_runtime_and_reports_result(tmp_path):
    project = tmp_path / "repo"
    project.mkdir()
    executed = invoke(ForgeCodeRequest(
        "execute_plan", "corr-exec", _runtime_payload(project, authorized=True)
    ))
    assert executed.status == "ok"
    assert executed.data["ok"] is True
    assert executed.data["status"] == "succeeded"
    assert executed.data["steps"][0]["status"] == "succeeded"
    assert "forgecode-ok" in executed.data["steps"][0]["stdout"]

    report = invoke(ForgeCodeRequest(
        "report_result", "corr-exec", {"runtime_result": executed.data}
    ))
    assert report.status == "ok"
    assert report.data["correlation_id"] == "corr-exec"
    assert report.data["execution_id"] == "fc-test-execution"
    assert report.data["status"] == "succeeded"
    assert report.data["ok"] is True
    assert report.data["step_statuses"][0]["command_id"] == "cmd-run"
    assert report.data["plan_sha256"]
    assert report.data["runtime_contract_version"] == "forgecode.terminal-runtime.v1"
