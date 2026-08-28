from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

FORGE_COMMANDER_CHATGPT_MCP_VERSION = "forge-commander.chatgpt-mcp.v1"
ToolName = Literal[
    "list_devices", "get_device_status", "run_device_task",
    "write_file_text", "run_terminal_profile",
]

@dataclass(frozen=True, slots=True)
class McpToolSpec:
    name: ToolName
    description: str
    read_only: bool
    destructive: bool
    idempotent: bool
    requires_device: bool


def forge_commander_tool_specs() -> tuple[McpToolSpec, ...]:
    return (
        McpToolSpec(
            "list_devices",
            "Use this when the user wants to see enrolled ForgeCommander devices.",
            True, False, True, False,
        ),
        McpToolSpec(
            "get_device_status",
            "Use this when the user wants current status or capabilities for one enrolled device.",
            True, False, True, True,
        ),
        McpToolSpec(
            "run_device_task",
            "Use this when the user asks ForgeCommander to perform a governed task on an enrolled device.",
            False, True, False, True,
        ),
        McpToolSpec(
            "write_file_text",
            "Write bounded text inside an approved root after explicit user approval.",
            False, True, False, True,
        ),
        McpToolSpec(
            "run_terminal_profile",
            "Run an allowlisted terminal profile after explicit user approval.",
            False, True, False, True,
        ),
    )


def tool_spec(name: ToolName) -> McpToolSpec:
    return next(spec for spec in forge_commander_tool_specs() if spec.name == name)


__all__ = [
    "FORGE_COMMANDER_CHATGPT_MCP_VERSION", "ToolName", "McpToolSpec",
    "forge_commander_tool_specs", "tool_spec",
]
