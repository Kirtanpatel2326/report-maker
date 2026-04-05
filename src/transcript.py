"""
YouTube transcript and metadata extraction utilities.
"""
import re
from typing import Optional

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound


def extract_video_id(url: str) -> Optional[str]:
    """Extract the YouTube video ID from a variety of URL formats."""
    patterns = [
        r"(?:v=|/v/|youtu\.be/|/embed/|/shorts/)([a-zA-Z0-9_-]{11})",
        r"^([a-zA-Z0-9_-]{11})$",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def fetch_transcript(video_id: str) -> list[dict]:
    """
    Fetch the full transcript for a YouTube video.

    Returns a list of segment dicts with keys: text, start, duration.
    Tries English first, then falls back to any available language (auto-translated).
    """
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # Prefer manually created English transcripts
        try:
            transcript = transcript_list.find_manually_created_transcript(["en", "en-US", "en-GB"])
            return transcript.fetch()
        except NoTranscriptFound:
            pass

        # Fall back to auto-generated English
        try:
            transcript = transcript_list.find_generated_transcript(["en", "en-US", "en-GB"])
            return transcript.fetch()
        except NoTranscriptFound:
            pass

        # Fall back to any available transcript, auto-translated to English
        available = transcript_list._manually_created_transcripts or transcript_list._generated_transcripts
        if available:
            first = next(iter(available.values()))
            return first.translate("en").fetch()

    except TranscriptsDisabled:
        raise ValueError("Transcripts are disabled for this video.")
    except Exception as exc:
        raise ValueError(f"Could not fetch transcript: {exc}") from exc

    raise ValueError("No transcript available for this video.")


def build_full_text(segments: list[dict]) -> str:
    """Join transcript segments into a single block of text."""
    return " ".join(seg["text"].strip() for seg in segments if seg.get("text"))


def format_timestamp(seconds: float) -> str:
    """Convert fractional seconds to MM:SS format."""
    total = int(seconds)
    mins = total // 60
    secs = total % 60
    return f"{mins:02d}:{secs:02d}"


def get_video_metadata(video_id: str) -> dict:
    """
    Retrieve basic video metadata (title, description, duration) via yt-dlp.
    Returns a dict with keys: title, description, duration, url.
    Falls back gracefully if yt-dlp cannot fetch.
    """
    try:
        import yt_dlp  # imported here to keep the module optional at import time

        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "extract_flat": False,
        }
        url = f"https://www.youtube.com/watch?v={video_id}"
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                "title": info.get("title", ""),
                "description": info.get("description", ""),
                "duration": info.get("duration", 0),
                "url": url,
                "channel": info.get("uploader", ""),
                "view_count": info.get("view_count", 0),
            }
    except Exception:
        return {
            "title": "",
            "description": "",
            "duration": 0,
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "channel": "",
            "view_count": 0,
        }
