"""
friday/tools/__init__.py — register every tool module with the MCP server.

Adding a new module
-------------------
1. Create ``friday/tools/my_module.py`` with a ``register(mcp)`` function.
2. Import and call it here inside ``register_all``.
"""

from fastmcp import FastMCP

from friday.tools import system, utils, web


def register_all(mcp: FastMCP) -> None:
    """Register all tool modules with *mcp*."""
    web.register(mcp)
    system.register(mcp)
    utils.register(mcp)
