"""
friday/config.py — environment-variable loading and app-wide settings.

All values are read once at import time from the environment (or a .env file).
"""

from __future__ import annotations

import os
import subprocess

from dotenv import load_dotenv

load_dotenv()

# ── LiveKit ───────────────────────────────────────────────────────────────────
LIVEKIT_URL: str = os.getenv("LIVEKIT_URL", "")
LIVEKIT_API_KEY: str = os.getenv("LIVEKIT_API_KEY", "")
LIVEKIT_API_SECRET: str = os.getenv("LIVEKIT_API_SECRET", "")

# ── LLM ───────────────────────────────────────────────────────────────────────
GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

# ── STT / TTS ─────────────────────────────────────────────────────────────────
SARVAM_API_KEY: str = os.getenv("SARVAM_API_KEY", "")
DEEPGRAM_API_KEY: str = os.getenv("DEEPGRAM_API_KEY", "")
GOOGLE_APPLICATION_CREDENTIALS: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")

# ── Optional integrations ─────────────────────────────────────────────────────
SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
SUPABASE_API_KEY: str = os.getenv("SUPABASE_API_KEY", "")

# ── MCP server ────────────────────────────────────────────────────────────────
MCP_HOST: str = os.getenv("MCP_HOST", "127.0.0.1")
MCP_PORT: int = int(os.getenv("MCP_PORT", "8000"))


# ── WSL host detection ────────────────────────────────────────────────────────

def _is_wsl() -> bool:
    """Return True when the process is running inside Windows Subsystem for Linux."""
    try:
        with open("/proc/sys/kernel/osrelease") as fh:
            return "microsoft" in fh.read().lower()
    except OSError:
        return False


def _wsl_host_ip() -> str | None:
    """
    Return the Windows host IP address as seen from WSL (the nameserver
    listed in /etc/resolv.conf is typically the Hyper-V virtual switch IP).
    """
    try:
        result = subprocess.run(
            ["cat", "/etc/resolv.conf"],
            capture_output=True,
            text=True,
            check=True,
        )
        for line in result.stdout.splitlines():
            parts = line.split()
            if parts and parts[0] == "nameserver":
                ip = parts[1]
                # Ignore loopback / systemd-resolved addresses
                if not ip.startswith("127."):
                    return ip
    except Exception:
        pass
    return None


def get_mcp_sse_url() -> str:
    """
    Build the MCP SSE URL.

    When running inside WSL and MCP_HOST is the default loopback address,
    the Windows host IP is substituted automatically so the agent can reach
    the MCP server that is running on the Windows side.
    """
    host = MCP_HOST
    if host == "127.0.0.1" and _is_wsl():
        wsl_ip = _wsl_host_ip()
        if wsl_ip:
            host = wsl_ip
    return f"http://{host}:{MCP_PORT}/sse"
