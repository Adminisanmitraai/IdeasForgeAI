from __future__ import annotations

from .gateway_api import session_manager
from .mcp_server import build_mcp_server

FORGE_COMMANDER_MCP_APP_VERSION = "forge-commander.mcp-app.v1"

mcp_server = build_mcp_server(session_manager)
mcp_app = mcp_server.streamable_http_app()

__all__ = ["FORGE_COMMANDER_MCP_APP_VERSION", "mcp_server", "mcp_app"]
