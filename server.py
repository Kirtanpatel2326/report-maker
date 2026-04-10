"""
server.py — MCP server entry-point.

Run with:
    uv run friday
"""

from friday import create_mcp_server
from friday.config import MCP_HOST, MCP_PORT


def main() -> None:
    """Start the FastMCP server over SSE transport."""
    mcp = create_mcp_server()
    mcp.run(transport="sse", host=MCP_HOST, port=MCP_PORT)


if __name__ == "__main__":
    main()
