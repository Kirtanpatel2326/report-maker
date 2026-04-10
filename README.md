# FRIDAY — Tony Stark Voice Agent 🤖

A real-time, Tony Stark–style AI voice assistant powered by:

| Layer | Technology |
|---|---|
| **Microphone → STT** | Sarvam Saaras v3 (Indian-English optimised) |
| **LLM** | Google Gemini 2.5 Flash |
| **TTS → Speaker** | OpenAI TTS (nova voice) |
| **Real-time transport** | LiveKit Agents |
| **Tool server** | FastMCP over SSE |

---

## How it works

```
Microphone ──► STT (Sarvam Saaras v3)
                    │
                    ▼
             LLM (Gemini 2.5 Flash)  ◄──────► MCP Server (FastMCP / SSE)
                    │                              ├─ get_world_news
                    ▼                              ├─ open_world_monitor
             TTS (OpenAI nova)                     ├─ search_web
                    │                              ├─ fetch_url
                    ▼                              ├─ get_current_time
             Speaker / LiveKit room                ├─ get_system_info
                                                   ├─ format_json
                                                   └─ word_count
```

The voice agent connects to the MCP server via SSE at `http://127.0.0.1:8000/sse`
(auto-resolved to the Windows host IP when running inside WSL).

---

## Project structure

```
friday-tony-stark-demo/
├── server.py           # uv run friday       → starts the MCP server (SSE on :8000)
├── agent_friday.py     # uv run friday_voice → starts the LiveKit voice agent
├── pyproject.toml
├── .env.example        # copy → .env and fill in your keys
│
└── friday/             # MCP server package
    ├── config.py       # env-var loading & app-wide settings
    ├── tools/          # MCP tools (callable by the LLM)
    │   ├── web.py      # search_web, fetch_url, get_world_news, open_world_monitor
    │   ├── system.py   # get_current_time, get_system_info
    │   └── utils.py    # format_json, word_count
    ├── prompts/        # MCP prompt templates (summarize, explain_code, …)
    └── resources/      # MCP resources exposed to clients (friday://info)
```

---

## Quick start

### 1. Prerequisites

- Python ≥ 3.11
- [uv](https://docs.astral.sh/uv/) — `pip install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`
- A [LiveKit Cloud](https://livekit.io/) project (free tier works)

### 2. Clone & install

```bash
git clone https://github.com/Kirtanpatel2326/report-maker.git
cd report-maker
uv sync          # creates .venv and installs all dependencies
```

### 3. Set up environment

```bash
cp .env.example .env
# Open .env and fill in your API keys (see the table below)
```

### 4. Run — two terminals

**Terminal 1 — MCP server** (must start first)

```bash
uv run friday
```

Starts the FastMCP server on `http://127.0.0.1:8000/sse`.
The voice agent connects here to fetch its tools.

**Terminal 2 — Voice agent**

```bash
uv run friday_voice
```

Starts the LiveKit voice agent in dev mode — it joins a LiveKit room and begins
listening. Open the [LiveKit Agents Playground](https://agents-playground.livekit.io/)
and connect to your room to talk to FRIDAY.

---

## `uv run friday` vs `uv run friday_voice`

| Command | Entry point | What it does |
|---|---|---|
| `uv run friday` | `server.py → main()` | Launches the FastMCP server over SSE transport on port 8000. Registers all tools, prompts, and resources. |
| `uv run friday_voice` | `agent_friday.py → dev()` | Launches the LiveKit voice agent. Builds the STT / LLM / TTS pipeline, connects to the LiveKit room, and wires up the MCP server as a tool source. The `dev()` wrapper auto-injects the dev CLI flag. |

Both processes must run simultaneously. The voice agent calls the MCP server in
real time whenever it needs a tool (e.g. fetching news).

---

## Environment variables

Copy `.env.example` → `.env` and fill in the values below.

| Variable | Required | Where to get it |
|---|---|---|
| `LIVEKIT_URL` | ✅ | LiveKit Cloud dashboard → your project URL |
| `LIVEKIT_API_KEY` | ✅ | LiveKit Cloud → API Keys |
| `LIVEKIT_API_SECRET` | ✅ | LiveKit Cloud → API Keys |
| `SARVAM_API_KEY` | ✅ (default STT) | [dashboard.sarvam.ai](https://dashboard.sarvam.ai/) |
| `GOOGLE_API_KEY` | ✅ (default LLM) | [aistudio.google.com](https://aistudio.google.com/) |
| `OPENAI_API_KEY` | ✅ (default TTS) | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) |
| `GROQ_API_KEY` | optional | [console.groq.com](https://console.groq.com/) — only needed if you switch `LLM_PROVIDER` to `"groq"` |
| `DEEPGRAM_API_KEY` | optional | [console.deepgram.com](https://console.deepgram.com/) |
| `GOOGLE_APPLICATION_CREDENTIALS` | optional | GCP service-account JSON path — only for `STT_PROVIDER = "google"` |
| `SUPABASE_URL` | optional | [supabase.com](https://supabase.com/) — for the ticketing tool |
| `SUPABASE_API_KEY` | optional | Supabase project → API settings |
| `MCP_HOST` | optional | Override MCP server host (default: `127.0.0.1`) |
| `MCP_PORT` | optional | Override MCP server port (default: `8000`) |

---

## Switching providers

Open `agent_friday.py` and change the provider constants at the top
(or set the corresponding environment variable):

```python
STT_PROVIDER = "sarvam"   # "sarvam" | "deepgram" | "whisper"
LLM_PROVIDER = "gemini"   # "gemini" | "openai"
TTS_PROVIDER = "openai"   # "openai" | "sarvam"
```

---

## Adding a new tool

1. Create or open a file in `friday/tools/`
2. Define a `register(mcp)` function and decorate tools with `@mcp.tool()`
3. Import and call `register(mcp)` inside `friday/tools/__init__.py`

The MCP server will pick it up on next start.

**Example:**

```python
# friday/tools/my_tool.py
from typing import Annotated
from fastmcp import FastMCP

def register(mcp: FastMCP) -> None:
    @mcp.tool()
    def greet(name: Annotated[str, "Name to greet"]) -> str:
        """Return a friendly greeting."""
        return f"Hello, {name}! I am FRIDAY."
```

---

## Tech stack

- [FastMCP](https://github.com/jlowin/fastmcp) — MCP server framework
- [LiveKit Agents](https://docs.livekit.io/agents/) — real-time voice pipeline
- [Sarvam Saaras v3](https://www.sarvam.ai/) — STT (Indian-English optimised)
- [Google Gemini 2.5 Flash](https://ai.google.dev/) — LLM
- [OpenAI TTS](https://platform.openai.com/docs/guides/text-to-speech) (nova voice) — TTS
- [uv](https://docs.astral.sh/uv/) — fast Python package manager

---

## License

MIT
