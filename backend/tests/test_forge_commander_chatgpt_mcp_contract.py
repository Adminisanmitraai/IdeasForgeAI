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
