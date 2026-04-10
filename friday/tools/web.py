"""
friday/tools/web.py — web-related MCP tools.

Tools
-----
- search_web        Search the web with DuckDuckGo (no API key required).
- fetch_url         Fetch and extract the text content of any URL.
- get_world_news    Pull the latest world headlines from the BBC RSS feed.
- open_world_monitor  Open a URL in the host machine's default web browser.
"""

from __future__ import annotations

import webbrowser
from typing import Annotated

import httpx
from bs4 import BeautifulSoup
from fastmcp import FastMCP

_DUCKDUCKGO_HTML = "https://html.duckduckgo.com/html/"
_BBC_WORLD_RSS = "https://feeds.bbci.co.uk/news/world/rss.xml"
_HTTP_TIMEOUT = 15.0
_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0 Safari/537.36"
)


def register(mcp: FastMCP) -> None:
    """Register all web tools with *mcp*."""

    @mcp.tool()
    async def search_web(
        query: Annotated[str, "Search query string"],
    ) -> str:
        """Search the web using DuckDuckGo and return the top results."""
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.post(
                _DUCKDUCKGO_HTML,
                data={"q": query, "b": "", "kl": ""},
                headers={"User-Agent": _USER_AGENT},
                timeout=_HTTP_TIMEOUT,
            )
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        results: list[str] = []
        for result in soup.select(".result")[:6]:
            title_tag = result.select_one(".result__title")
            snippet_tag = result.select_one(".result__snippet")
            url_tag = result.select_one(".result__url")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""
            url = url_tag.get_text(strip=True) if url_tag else ""
            parts = [f"**{title}**"]
            if snippet:
                parts.append(snippet)
            if url:
                parts.append(f"URL: {url}")
            results.append("\n".join(parts))

        return "\n\n".join(results) if results else "No results found."

    @mcp.tool()
    async def fetch_url(
        url: Annotated[str, "Full URL to fetch (https://…)"],
    ) -> str:
        """Fetch and return the readable text content of a web page (max 4,000 chars)."""
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                url,
                headers={"User-Agent": _USER_AGENT},
                timeout=_HTTP_TIMEOUT,
            )
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "head"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)
        return text[:4000] if len(text) > 4000 else text

    @mcp.tool()
    async def get_world_news() -> str:
        """Fetch the latest world news headlines from the BBC News RSS feed."""
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(
                _BBC_WORLD_RSS,
                headers={"User-Agent": _USER_AGENT},
                timeout=_HTTP_TIMEOUT,
            )
            response.raise_for_status()

        soup = BeautifulSoup(response.content, "xml")
        items = soup.find_all("item")[:10]
        headlines: list[str] = []
        for item in items:
            title_tag = item.find("title")
            desc_tag = item.find("description")
            date_tag = item.find("pubDate")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            desc = desc_tag.get_text(strip=True) if desc_tag else ""
            date = date_tag.get_text(strip=True) if date_tag else ""
            line = f"• {title}"
            if desc:
                line += f"\n  {desc}"
            if date:
                line += f"\n  ({date})"
            headlines.append(line)

        return "\n\n".join(headlines) if headlines else "No news available at this time."

    @mcp.tool()
    def open_world_monitor(
        url: Annotated[str, "URL to open (defaults to BBC World News)"] = "https://www.bbc.com/news/world",
    ) -> str:
        """Open a URL in the default web browser on the host machine."""
        webbrowser.open(url)
        return f"Opened {url} in the default browser."
