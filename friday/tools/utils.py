"""
friday/tools/utils.py — general-purpose utility MCP tools.

Tools
-----
- format_json    Pretty-print a JSON string with indentation.
- word_count     Count the number of words in a text string.
"""

from __future__ import annotations

import json
from typing import Annotated

from fastmcp import FastMCP


def register(mcp: FastMCP) -> None:
    """Register all utility tools with *mcp*."""

    @mcp.tool()
    def format_json(
        data: Annotated[str, "Raw JSON string to format"],
    ) -> str:
        """Pretty-print a JSON string with 2-space indentation."""
        try:
            parsed = json.loads(data)
            return json.dumps(parsed, indent=2, ensure_ascii=False)
        except json.JSONDecodeError as exc:
            return f"Invalid JSON: {exc}"

    @mcp.tool()
    def word_count(
        text: Annotated[str, "Text whose words should be counted"],
    ) -> str:
        """Count the number of words, characters, and lines in a text string."""
        words = text.split()
        lines = text.splitlines()
        return (
            f"Words:      {len(words)}\n"
            f"Characters: {len(text)}\n"
            f"Lines:      {len(lines)}"
        )
