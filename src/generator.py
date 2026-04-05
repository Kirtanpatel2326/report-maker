"""
LLM-powered viral shorts generator.

Sends the transcript + metadata to OpenAI and returns a structured list of
short-form video ideas with all required fields.
"""
import json
import os

from openai import OpenAI

_SYSTEM_PROMPT = """\
You are a viral short-form content strategist with deep expertise in YouTube Shorts,
Instagram Reels, and TikTok (2025–2026 formats).

Your job: given a YouTube video transcript and its metadata, identify the BEST
3–7 clips that can become viral short-form videos (15–60 seconds each).

For EVERY short you must return a JSON object with exactly these fields:
{
  "short_number": <int>,
  "title": "<viral, curiosity-driven, ≤60 chars, power words + emojis>",
  "hook": "<extremely engaging opening line, first 3 seconds>",
  "script": "<clean rewritten transcript, fast-paced short sentences>",
  "timestamp_start": "<MM:SS>",
  "timestamp_end": "<MM:SS>",
  "captions": [
    {"text": "<3-5 word chunk>", "start": "<MM:SS>", "end": "<MM:SS>"},
    ...
  ],
  "thumbnail": {
    "text": "<3-5 word thumbnail text>",
    "background": "<background description>",
    "emotion": "<emotion to convey>",
    "face_expression": "<expression description>",
    "color_psychology": "<color palette rationale>"
  },
  "on_screen_text": ["<overlay 1>", "<overlay 2>", "<overlay 3>"],
  "editing_guide": {
    "zoom_effects": "<description>",
    "jump_cuts": "<description>",
    "captions_style": "<description>",
    "sound_effects": "<description>",
    "background_music": "<music type/mood>"
  },
  "social_media_pack": {
    "youtube_shorts": {
      "title": "<SEO title>",
      "description": "<SEO description with keywords>",
      "tags": ["<tag1>", ..., "<tag20+>"]
    },
    "instagram_reels": {
      "caption": "<engaging caption>",
      "hashtags": ["<#tag1>", ..., "<#tag10+>"]
    },
    "tiktok": {
      "caption": "<caption>",
      "trending_hashtags": ["<#tag1>", ..., "<#tag10+>"]
    }
  },
  "optimization_notes": "<brief note on watch time, rewatchability, shareability>"
}

Return ONLY a valid JSON array of these objects — no markdown fences, no extra text.
"""


def generate_shorts(transcript_segments: list[dict], metadata: dict, api_key: str) -> list[dict]:
    """
    Call OpenAI to analyze the transcript and generate viral short ideas.

    Args:
        transcript_segments: list of {text, start, duration} dicts
        metadata: dict with title, description, duration, channel, etc.
        api_key: OpenAI API key

    Returns:
        list of short dicts (parsed from LLM JSON output)
    """
    client = OpenAI(api_key=api_key)

    # Build a compact transcript representation (text + timestamp)
    transcript_lines = []
    for seg in transcript_segments:
        start = seg.get("start", 0)
        mins = int(start) // 60
        secs = int(start) % 60
        transcript_lines.append(f"[{mins:02d}:{secs:02d}] {seg['text'].strip()}")
    transcript_text = "\n".join(transcript_lines)

    # Truncate if extremely long (GPT-4o context window is large but let's be safe)
    max_chars = 80_000
    if len(transcript_text) > max_chars:
        transcript_text = transcript_text[:max_chars] + "\n[... transcript truncated ...]"

    user_message = f"""VIDEO METADATA
Title: {metadata.get('title', 'Unknown')}
Channel: {metadata.get('channel', 'Unknown')}
Duration: {_seconds_to_mmss(metadata.get('duration', 0))}
Views: {metadata.get('view_count', 'N/A')}

TRANSCRIPT
{transcript_text}

Generate 3–7 viral short-form clips from this video. Return only the JSON array."""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.85,
        max_tokens=8192,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content.strip()

    # The model returns {"shorts": [...]} or a bare array — handle both
    parsed = json.loads(raw)
    if isinstance(parsed, list):
        return parsed
    # Look for the first list value in the dict
    for value in parsed.values():
        if isinstance(value, list):
            return value
    raise ValueError(f"Unexpected LLM response structure: {list(parsed.keys())}")


def _seconds_to_mmss(seconds: int) -> str:
    mins = seconds // 60
    secs = seconds % 60
    return f"{mins:02d}:{secs:02d}"
