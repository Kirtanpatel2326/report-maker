"""
agent_friday.py — LiveKit voice-agent entry-point.

Run with:
    uv run friday_voice
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys
from typing import Annotated

from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, llm
from livekit.agents.pipeline import VoicePipelineAgent
from livekit.plugins import silero

load_dotenv()

logger = logging.getLogger("friday.agent")

# ── Provider selection ────────────────────────────────────────────────────────
STT_PROVIDER = os.getenv("STT_PROVIDER", "sarvam")   # "sarvam" | "deepgram" | "whisper"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")   # "gemini" | "openai"
TTS_PROVIDER = os.getenv("TTS_PROVIDER", "openai")   # "openai" | "sarvam"

# Resolved at import time (handles WSL → Windows host auto-detection)
from friday.config import get_mcp_sse_url  # noqa: E402

MCP_SSE_URL = get_mcp_sse_url()


# ── Provider factories ────────────────────────────────────────────────────────

def _build_stt():
    if STT_PROVIDER == "sarvam":
        from livekit.plugins import sarvam
        return sarvam.STT(
            model="saaras:v3",
            api_key=os.getenv("SARVAM_API_KEY"),
        )
    elif STT_PROVIDER == "deepgram":
        from livekit.plugins import deepgram
        return deepgram.STT(api_key=os.getenv("DEEPGRAM_API_KEY"))
    else:
        from livekit.plugins import openai as openai_plugin
        return openai_plugin.STT(model="whisper-1")


def _build_llm():
    if LLM_PROVIDER == "gemini":
        from livekit.plugins import google as google_plugin
        return google_plugin.LLM(
            model="gemini-2.5-flash-preview-04-17",
            api_key=os.getenv("GOOGLE_API_KEY"),
        )
    else:
        from livekit.plugins import openai as openai_plugin
        return openai_plugin.LLM(model="gpt-4o")


def _build_tts():
    if TTS_PROVIDER == "openai":
        from livekit.plugins import openai as openai_plugin
        return openai_plugin.TTS(voice="nova")
    else:
        from livekit.plugins import sarvam
        return sarvam.TTS(api_key=os.getenv("SARVAM_API_KEY"))


# ── MCP tool bridge ───────────────────────────────────────────────────────────

async def _call_mcp(tool_name: str, arguments: dict) -> str:
    """Connect to the MCP SSE server, call a tool, and return its text output."""
    from mcp.client.sse import sse_client
    from mcp import ClientSession

    async with sse_client(url=MCP_SSE_URL) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments)
            texts = [
                c.text for c in result.content if hasattr(c, "text") and c.text
            ]
            return "\n".join(texts) if texts else "(no output)"


class FridayFunctions(llm.FunctionContext):
    """MCP-backed function context exposed to the Gemini LLM."""

    # ── Web tools ─────────────────────────────────────────────────────────────

    @llm.ai_callable(description="Search the web using DuckDuckGo and return the top results.")
    async def search_web(
        self,
        query: Annotated[str, llm.TypeInfo(description="Search query string")],
    ) -> str:
        return await _call_mcp("search_web", {"query": query})

    @llm.ai_callable(description="Fetch and return the text content of a web page.")
    async def fetch_url(
        self,
        url: Annotated[str, llm.TypeInfo(description="Full URL to fetch (https://…)")],
    ) -> str:
        return await _call_mcp("fetch_url", {"url": url})

    @llm.ai_callable(description="Get the latest world news headlines from BBC News RSS.")
    async def get_world_news(self) -> str:
        return await _call_mcp("get_world_news", {})

    @llm.ai_callable(description="Open a URL in the default web browser on the host machine.")
    async def open_world_monitor(
        self,
        url: Annotated[
            str,
            llm.TypeInfo(description="URL to open (defaults to BBC World News)"),
        ] = "https://www.bbc.com/news/world",
    ) -> str:
        return await _call_mcp("open_world_monitor", {"url": url})

    # ── System tools ──────────────────────────────────────────────────────────

    @llm.ai_callable(description="Return the current date and time in ISO-8601 format.")
    async def get_current_time(self) -> str:
        return await _call_mcp("get_current_time", {})

    @llm.ai_callable(description="Return information about the host system (OS, CPU, memory, disk).")
    async def get_system_info(self) -> str:
        return await _call_mcp("get_system_info", {})

    # ── Utility tools ─────────────────────────────────────────────────────────

    @llm.ai_callable(description="Pretty-print a JSON string.")
    async def format_json(
        self,
        data: Annotated[str, llm.TypeInfo(description="Raw JSON string to format")],
    ) -> str:
        return await _call_mcp("format_json", {"data": data})

    @llm.ai_callable(description="Count the number of words in a text string.")
    async def word_count(
        self,
        text: Annotated[str, llm.TypeInfo(description="Text whose words should be counted")],
    ) -> str:
        return await _call_mcp("word_count", {"text": text})


# ── Agent entry-point ─────────────────────────────────────────────────────────

SYSTEM_PROMPT = (
    "You are FRIDAY, an advanced AI assistant in the style of Tony Stark's FRIDAY. "
    "You are helpful, witty, and extremely capable. "
    "You have access to tools for searching the web, fetching URLs, getting the latest news, "
    "checking system information, and more. "
    "Keep responses concise and natural for voice conversation. "
    "When the user asks about current events or needs real-time information, use your tools."
)


async def entrypoint(ctx: JobContext) -> None:
    initial_ctx = llm.ChatContext().append(
        role="system",
        text=SYSTEM_PROMPT,
    )

    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    participant = await ctx.wait_for_participant()
    logger.info("FRIDAY connecting to participant: %s", participant.identity)

    agent = VoicePipelineAgent(
        vad=silero.VAD.load(),
        stt=_build_stt(),
        llm=_build_llm(),
        tts=_build_tts(),
        chat_ctx=initial_ctx,
        fnc_ctx=FridayFunctions(),
    )

    agent.start(ctx.room, participant)

    await agent.say(
        "Hello! I'm FRIDAY. How can I assist you today?",
        allow_interruptions=True,
    )

    # Keep the agent alive for the duration of the session
    await asyncio.sleep(float("inf"))


# ── Script helpers ────────────────────────────────────────────────────────────

def dev() -> None:
    """Entry-point that auto-injects the 'dev' CLI flag (used by uv run friday_voice)."""
    sys.argv = [sys.argv[0], "dev"]
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
