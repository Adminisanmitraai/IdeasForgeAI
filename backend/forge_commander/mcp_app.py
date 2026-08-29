from __future__ import annotations

from .gateway_api import session_manager
from .mcp_server import build_mcp_server

FORGE_COMMANDER_MCP_APP_VERSION = "forge-commander.mcp-app.v2"
FORGE_COMMANDER_V2_RESOURCE = "https://commander.ideasforgeai.com/forge-commander-v2/mcp"

mcp_server = build_mcp_server(session_manager)
mcp_app = mcp_server.streamable_http_app()
mcp_server_v2 = build_mcp_server(
    session_manager,
    server_name="ForgeCommander FC-6U.6C.2",
    resource_url=FORGE_COMMANDER_V2_RESOURCE,
)
mcp_app_v2 = mcp_server_v2.streamable_http_app()

__all__ = [
    "FORGE_COMMANDER_MCP_APP_VERSION", "FORGE_COMMANDER_V2_RESOURCE",
    "mcp_server", "mcp_app", "mcp_server_v2", "mcp_app_v2",
]
