# 🎬 Viral Shorts Generator

Turn any YouTube video into **ready-to-publish short-form content** (YouTube Shorts, Instagram Reels, TikTok) with one click — no video upload required.

## What it does

1. **Accepts a YouTube URL** – no file upload needed.
2. **Extracts the full transcript** automatically (manual or auto-generated captions).
3. **Analyzes** the video with GPT-4o to find the 3–7 best viral clip moments.
4. **Generates a complete content pack for each short:**
   - Viral title + hook
   - Rewritten script (fast-paced, short-form style)
   - Timestamps (exact start → end)
   - Captions (3–5 word chunks with timestamps)
   - Thumbnail concept (text, background, emotion, color psychology)
   - On-screen text overlays
   - CapCut / InVideo editing guide
   - Full social media pack (YouTube Shorts, Instagram Reels, TikTok)
   - Optimization notes

## Setup

### Prerequisites
- Python 3.10+
- An [OpenAI API key](https://platform.openai.com/account/api-keys)

### Installation

```bash
pip install -r requirements.txt
```

### Configuration

```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### Run

```bash
python app.py
```

Then open **http://localhost:5000** in your browser.

You can either paste your OpenAI API key directly in the web form (it is never stored) or set it as the `OPENAI_API_KEY` environment variable.

## Project structure

```
app.py              # Flask web application
src/
  transcript.py     # YouTube transcript & metadata extraction
  generator.py      # GPT-4o viral content generation
templates/
  index.html        # Web UI
requirements.txt
.env.example
```

## Tech stack

| Layer | Library |
|---|---|
| Web framework | Flask 3 |
| Transcript extraction | youtube-transcript-api |
| Video metadata | yt-dlp |
| Content generation | OpenAI GPT-4o |
| Environment config | python-dotenv |

