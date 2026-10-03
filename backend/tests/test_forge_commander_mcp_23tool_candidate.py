from pathlib import Path
import re

MCP_SERVER = Path(__file__).parents[1] / "forge_commander" / "mcp_server.py"
EXPECTED = {
    "list_devices","get_device_status","device_identity","device_resources","device_runtime",
    "device_hardware","device_storage","device_processes","device_network","device_software",
    "device_dev_environment","file_list","file_read_text","terminal_read","run_device_task",
    "deployment_artifact_attest","deployment_action_validate","deployment_action_execute",
    "security_surface_patch_execute","write_file_text","file_replace_text","delete_file",
    "run_terminal_profile",
}

def _source():
    return MCP_SERVER.read_text(encoding="utf-8")

def test_mcp_server_compiles():
    compile(_source(), str(MCP_SERVER), "exec")

def test_exact_23_tool_surface():
    text=_source()
    names=[]
    for m in re.finditer(r"@mcp[.]tool",text):
        tail=text[m.end():m.end()+800]
        found=re.search(r"(?:async[ ]+)?def[ ]+([A-Za-z0-9_]+)[(]",tail)
        assert found
        names.append(found.group(1))
    assert len(names)==23
    assert set(names)==EXPECTED

def test_file_replace_text_uses_structured_approval_route():
    text=_source()
    assert '"file_replace_text": "file.replace_text"' in text
    assert '{"file.write_text", "file.replace_text", "file.delete", "terminal.execute_profile", "deployment_action_execute"}' in text
    start=text.index("    async def file_replace_text")
    end=text.index("    @mcp.tool",start)
    block=text[start:end]
    assert 'device_id, "file.replace_text"' in block
    assert '"old_text": old_text' in block
    assert '"new_text": new_text' in block
    assert '"expected_count": expected_count' in block
    assert "approval_granted, ctx" in block
