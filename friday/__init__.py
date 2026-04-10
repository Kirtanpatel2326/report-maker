"""
friday — MCP server package.

Usage
-----
    from friday import create_mcp_server
    mcp = create_mcp_server()
    mcp.run(transport="sse", host="127.0.0.1", port=8000)
"""

from fastmcp import FastMCP

from friday import prompts, resources, tools


def create_mcp_server() -> FastMCP:
    """Create and return a fully configured FastMCP instance."""
    mcp = FastMCP(
        name="FRIDAY",
        instructions=(
            "You are FRIDAY, Tony Stark's AI assistant. "
            "Use the available tools to search the web, fetch URLs, "
            "get system information, and more."
        ),
    )

    tools.register_all(mcp)
    prompts.register_all(mcp)
    resources.register_all(mcp)

    return mcp
