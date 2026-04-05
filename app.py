"""
Flask web application – YouTube Viral Shorts Generator.
"""
import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

from src.transcript import extract_video_id, fetch_transcript, get_video_metadata
from src.generator import generate_shorts

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json(silent=True) or {}
    youtube_url = (data.get("url") or "").strip()
    api_key = (data.get("api_key") or os.environ.get("OPENAI_API_KEY") or "").strip()

    if not youtube_url:
        return jsonify({"error": "Please provide a YouTube URL."}), 400

    if not api_key:
        return jsonify(
            {"error": "No OpenAI API key found. Provide it in the form or set OPENAI_API_KEY env var."}
        ), 400

    # 1. Extract video ID
    video_id = extract_video_id(youtube_url)
    if not video_id:
        return jsonify({"error": "Could not parse a valid YouTube video ID from that URL."}), 400

    # 2. Fetch transcript
    try:
        segments = fetch_transcript(video_id)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 422

    # 3. Fetch metadata (best-effort)
    metadata = get_video_metadata(video_id)

    # 4. Generate viral shorts via LLM
    try:
        shorts = generate_shorts(segments, metadata, api_key)
    except Exception as exc:
        return jsonify({"error": f"Content generation failed: {exc}"}), 500

    return jsonify({"metadata": metadata, "shorts": shorts})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
