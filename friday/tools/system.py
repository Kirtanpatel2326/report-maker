"""
friday/tools/system.py — system-information MCP tools.

Tools
-----
- get_current_time   Return the current date and time.
- get_system_info    Return CPU, memory, disk, and OS information.
"""

from __future__ import annotations

import platform
from datetime import datetime, timezone

import psutil
from fastmcp import FastMCP


def register(mcp: FastMCP) -> None:
    """Register all system tools with *mcp*."""

    @mcp.tool()
    def get_current_time() -> str:
        """Return the current date and time in ISO-8601 format (UTC)."""
        now = datetime.now(tz=timezone.utc)
        local_now = datetime.now()
        return (
            f"UTC:   {now.strftime('%Y-%m-%d %H:%M:%S %Z')}\n"
            f"Local: {local_now.strftime('%Y-%m-%d %H:%M:%S')}"
        )

    @mcp.tool()
    def get_system_info() -> str:
        """Return a summary of the host system (OS, CPU, memory, disk)."""
        uname = platform.uname()
        cpu_count = psutil.cpu_count(logical=True)
        cpu_freq = psutil.cpu_freq()
        cpu_percent = psutil.cpu_percent(interval=0.5)

        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        freq_str = f"{cpu_freq.current:.0f} MHz" if cpu_freq else "N/A"
        mem_total_gb = mem.total / (1024**3)
        mem_used_gb = mem.used / (1024**3)
        disk_total_gb = disk.total / (1024**3)
        disk_used_gb = disk.used / (1024**3)

        return (
            f"OS:          {uname.system} {uname.release} ({uname.machine})\n"
            f"Node:        {uname.node}\n"
            f"Python:      {platform.python_version()}\n"
            f"CPU:         {cpu_count} logical cores @ {freq_str}  —  {cpu_percent:.1f}% used\n"
            f"Memory:      {mem_used_gb:.1f} GB / {mem_total_gb:.1f} GB used ({mem.percent:.1f}%)\n"
            f"Disk (/):    {disk_used_gb:.1f} GB / {disk_total_gb:.1f} GB used ({disk.percent:.1f}%)"
        )
