import yt_dlp
import json
import re
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn
import os

app = FastAPI(
    title="YouTube Transcript API",
    description="Extract video info and transcripts from YouTube videos",
    version="1.0.2"
)

class VideoResponse(BaseModel):
    video_url: str
    video_name: str
    transcript: str
    success: bool
    message: Optional[str] = None


def get_video_info_and_transcript(video_id: str):
    """Extract video info + English transcript if available"""

    # Always try to load cookies.txt (if it exists in project root)
    cookies_file = "cookies.txt"
    ydl_opts = {
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": ["en"],
        "skip_download": True,
    }
    if os.path.exists(cookies_file):
        ydl_opts["cookiefile"] = cookies_file

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)

            video_url = f"https://www.youtube.com/watch?v={video_id}"
            video_name = info.get("title", "Unknown Title")

            subtitles = info.get("subtitles", {})
            auto_subs = info.get("automatic_captions", {})

            if "en" in subtitles:
                caption_tracks = subtitles["en"]
            elif "en" in auto_subs:
                caption_tracks = auto_subs["en"]
            else:
                return {
                    "video_url": video_url,
                    "video_name": video_name,
                    "transcript": "",
                    "success": False,
                    "message": "No English captions available for this video"
                }

            if not caption_tracks:
                return {
                    "video_url": video_url,
                    "video_name": video_name,
                    "transcript": "",
                    "success": False,
                    "message": "No caption tracks found"
                }

            # Pick json3/srv3 first, fallback to VTT
            chosen = next((c for c in caption_tracks if c.get("ext") in ("json3", "srv3")), caption_tracks[0])

            resp = requests.get(chosen["url"])
            if resp.status_code != 200:
                return {
                    "video_url": video_url,
                    "video_name": video_name,
                    "transcript": "",
                    "success": False,
                    "message": f"Failed to download captions (HTTP {resp.status_code})"
                }

            # Parse JSON captions
            if chosen.get("ext") in ("json3", "srv3"):
                try:
                    data = resp.json()
                except Exception:
                    data = None

                if not data:
                    return {
                        "video_url": video_url,
                        "video_name": video_name,
                        "transcript": "",
                        "success": False,
                        "message": "Failed to parse JSON captions"
                    }

                texts = []
                for event in data.get("events", []):
                    for seg in event.get("segs", []):
                        text_piece = seg.get("utf8", "").replace("\n", " ").strip()
                        if text_piece:
                            texts.append(text_piece)

                transcript = " ".join(texts).strip()
                return {
                    "video_url": video_url,
                    "video_name": video_name,
                    "transcript": transcript,
                    "success": True,
                    "message": "Transcript extracted successfully"
                }

            # Parse VTT/TTML fallback
            clean_lines = [
                re.sub(r"<[^>]+>", "", line.strip()).replace("&nbsp;", " ")
                for line in resp.text.splitlines()
                if line.strip() and "-->" not in line and not line.strip().isdigit()
            ]

            transcript = " ".join(clean_lines).strip()
            return {
                "video_url": video_url,
                "video_name": video_name,
                "transcript": transcript,
                "success": True,
                "message": "Transcript extracted successfully (text captions)"
            }

    except Exception as e:
        return {
            "video_url": f"https://www.youtube.com/watch?v={video_id}",
            "video_name": "Error",
            "transcript": "",
            "success": False,
            "message": f"Exception: {str(e)}"
        }


@app.get("/")
async def root():
    return {
        "message": "YouTube Transcript API is running 🚀",
        "endpoints": {
            "/transcript/{video_id}": "Get transcript for a YouTube video",
            "/health": "Health check"
        },
        "example": "/transcript/dQw4w9WgXcQ"
    }


@app.get("/transcript/{video_id}", response_model=VideoResponse)
async def transcript(video_id: str):
    if not video_id or len(video_id) != 11:
        raise HTTPException(status_code=400, detail="Invalid video ID (must be 11 characters)")
    return VideoResponse(**get_video_info_and_transcript(video_id))


@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)