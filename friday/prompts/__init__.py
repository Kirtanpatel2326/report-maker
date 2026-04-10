"""
friday/prompts/__init__.py — MCP prompt templates.

Prompts are reusable instruction templates that the LLM client can request
by name to get pre-built system / user messages for common tasks.
"""

from __future__ import annotations

from fastmcp import FastMCP


def register_all(mcp: FastMCP) -> None:
    """Register all prompt templates with *mcp*."""

    @mcp.prompt()
    def summarize(text: str) -> str:
        """Summarize a piece of text concisely."""
        return (
            f"Please summarize the following text in 3-5 bullet points. "
            f"Be concise and focus on the key takeaways.\n\n{text}"
        )

    @mcp.prompt()
    def explain_code(code: str, language: str = "Python") -> str:
        """Explain what a code snippet does in plain English."""
        return (
            f"Explain the following {language} code in plain English. "
            f"Describe what it does, the key logic, and any important details.\n\n"
            f"```{language.lower()}\n{code}\n```"
        )

    @mcp.prompt()
    def translate(text: str, target_language: str = "English") -> str:
        """Translate text to a target language."""
        return (
            f"Translate the following text to {target_language}. "
            f"Preserve the original tone and meaning.\n\n{text}"
        )

    @mcp.prompt()
    def analyze_sentiment(text: str) -> str:
        """Analyze the sentiment of a piece of text."""
        return (
            f"Analyze the sentiment of the following text. "
            f"Classify it as positive, negative, or neutral, and explain why.\n\n{text}"
        )
