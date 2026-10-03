from backend.forge_commander.chatgpt_mcp_contract import (
    forge_commander_tool_specs, tool_spec,
)


def test_read_tools_are_non_destructive():
    specs = {s.name: s for s in forge_commander_tool_specs()}
    assert specs["list_devices"].read_only is True
    assert specs["list_devices"].destructive is False
    assert specs["get_device_status"].read_only is True
    assert specs["get_device_status"].destructive is False


def test_run_device_task_is_mutating_and_device_scoped():
    spec = tool_spec("run_device_task")
    assert spec.read_only is False
    assert spec.destructive is True
    assert spec.idempotent is False
    assert spec.requires_device is True


def test_write_tools_are_separate_and_destructive():
    for name in ("write_file_text", "delete_file", "run_terminal_profile"):
        spec = tool_spec(name)
        assert spec.read_only is False
        assert spec.destructive is True
        assert spec.idempotent is False
        assert spec.requires_device is True


def test_production_mcp_tool_surface_is_pinned():
    import ast
    from pathlib import Path

    source = Path(__file__).resolve().parents[1] / "forge_commander" / "mcp_server.py"
    tree = ast.parse(source.read_text(encoding="utf-8"))
    names = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for decorator in node.decorator_list:
            if (
                isinstance(decorator, ast.Call)
                and isinstance(decorator.func, ast.Attribute)
                and isinstance(decorator.func.value, ast.Name)
                and decorator.func.value.id == "mcp"
                and decorator.func.attr == "tool"
            ):
                name = next(
                    (keyword.value for keyword in decorator.keywords if keyword.arg == "name"),
                    None,
                )
                names.append(node.name if name is None else ast.literal_eval(name))

    diagnostic_names = {
        "connector_snapshot_probe",
        "governed_patch_execute_probe",
        "diagnostic_tool_definitions",
    }
    assert diagnostic_names.isdisjoint(names), "Diagnostic-only MCP tools must stay absent"
    string_literals = {
        node.value for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    }
    assert diagnostic_names.isdisjoint(string_literals), "Temporary diagnostics must stay absent"
    assert len(names) == 22
    assert set(names) == {
        "list_devices",
        "get_device_status",
        "device_identity",
        "device_resources",
        "device_runtime",
        "device_hardware",
        "device_storage",
        "device_processes",
        "device_network",
        "device_software",
        "device_dev_environment",
        "file_list",
        "file_read_text",
        "terminal_read",
        "run_device_task",
        "deployment_artifact_attest",
        "deployment_action_validate",
        "deployment_action_execute",
        "security_surface_patch_execute",
        "write_file_text",
        "delete_file",
        "run_terminal_profile",
    }
