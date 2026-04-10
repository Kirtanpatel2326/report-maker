"""
friday/resources/__init__.py — MCP resources exposed to clients.

Resources provide static or dynamic data that clients can read by URI
(e.g. ``friday://info`` for project metadata).
"""

from __future__ import annotations

import platform

from fastmcp import FastMCP


def register_all(mcp: FastMCP) -> None:
    """Register all resources with *mcp*."""

    @mcp.resource("friday://info")
    def friday_info() -> str:
        """General information about the FRIDAY MCP server."""
        return (
            "FRIDAY MCP Server\n"
            "=================\n"
            "Version:     0.1.0\n"
            f"Platform:    {platform.system()} {platform.release()}\n"
            "\n"
            "Available tool groups:\n"
            "  • web     — search_web, fetch_url, get_world_news, open_world_monitor\n"
            "  • system  — get_current_time, get_system_info\n"
            "  • utils   — format_json, word_count\n"
            "\n"
            "Available prompts:\n"
            "  • summarize, explain_code, translate, analyze_sentiment\n"
        )

    @mcp.resource("friday://status")
    def friday_status() -> str:
        """Live status of the FRIDAY MCP server."""
        import psutil
        from datetime import datetime, timezone

        cpu = psutil.cpu_percent(interval=0.2)
        mem = psutil.virtual_memory()
        return (
            f"Status:  OK\n"
            f"Time:    {datetime.now(tz=timezone.utc).isoformat()}\n"
            f"CPU:     {cpu:.1f}%\n"
            f"Memory:  {mem.percent:.1f}% used\n"
        )
