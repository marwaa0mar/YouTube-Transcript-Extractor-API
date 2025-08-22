import yt_dlp
import json
import re
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn
import os
import time
import random
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="YouTube Transcript API",
    description="Extract video info and transcripts from YouTube videos",
    version="1.0.2"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:8000"] for local testing
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoResponse(BaseModel):
    video_url: str
    video_name: str
    transcript: str
    success: bool
    message: Optional[str] = None


def _format_ms_to_mmss(milliseconds: int) -> str:
    """Convert milliseconds to mm:ss string."""
    total_seconds = int(max(milliseconds, 0) // 1000)
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes:02d}:{seconds:02d}"


def _parse_vtt_time_to_ms(time_str: str) -> int:
    """Parse a VTT timestamp (hh:mm:ss.mmm or mm:ss.mmm) to milliseconds."""
    # Support both hh:mm:ss.mmm and mm:ss.mmm
    parts = time_str.split(":")
    if len(parts) == 3:
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = float(parts[2])
    elif len(parts) == 2:
        hours = 0
        minutes = int(parts[0])
        seconds = float(parts[1])
    else:
        return 0
    return int(((hours * 60 + minutes) * 60 + seconds) * 1000)


def _extract_captions_with_timestamps(info: dict) -> dict:
    """Return captions with timestamps if available.

    Returns dict: { 'captions': [ {start, end, text} ], 'caption_type': 'manual'|'auto'|None }
    """
    subtitles = info.get("subtitles", {})
    auto_subs = info.get("automatic_captions", {})
    caption_tracks = None
    caption_type = None

    if "en" in subtitles:
        caption_tracks = subtitles["en"]
        caption_type = "manual"
    elif "en" in auto_subs:
        caption_tracks = auto_subs["en"]
        caption_type = "auto"

    if not caption_tracks:
        return {"captions": [], "caption_type": None}

    # Prefer JSON-based tracks (json3/srv3), then fall back to VTT/TTML
    chosen = next((c for c in caption_tracks if c.get("ext") in ("json3", "srv3")), None)
    if not chosen:
        chosen = next((c for c in caption_tracks if c.get("ext") in ("vtt", "ttml", "xml")), caption_tracks[0])

    try:
        resp = requests.get(chosen["url"])  # type: ignore[index]
        if resp.status_code != 200:
            return {"captions": [], "caption_type": caption_type}
        # JSON captions
        if chosen.get("ext") in ("json3", "srv3"):
            try:
                data = resp.json()
            except Exception:
                data = None
            if not data:
                return {"captions": [], "caption_type": caption_type}

            results = []
            for event in data.get("events", []):
                start_ms = event.get("tStartMs")
                duration_ms = event.get("dDurationMs")
                if start_ms is None:
                    continue
                if duration_ms is None:
                    duration_ms = 0
                end_ms = start_ms + duration_ms
                segments = event.get("segs", []) or []
                text_parts = []
                for seg in segments:
                    piece = (seg.get("utf8") or "").replace("\n", " ").strip()
                    if piece:
                        text_parts.append(piece)
                text = " ".join(text_parts).strip()
                if not text:
                    continue
                results.append({
                    "start": _format_ms_to_mmss(int(start_ms)),
                    "end": _format_ms_to_mmss(int(end_ms)),
                    "text": text
                })
            return {"captions": results, "caption_type": caption_type}

        # VTT/TTML fallback (best-effort parsing)
        text = resp.text
        lines = text.splitlines()
        results = []
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if "-->" in line:
                # Example: 00:00:01.000 --> 00:00:03.000
                try:
                    parts = [p.strip() for p in line.split("-->")]
                    start_ms = _parse_vtt_time_to_ms(parts[0])
                    end_ms = _parse_vtt_time_to_ms(parts[1].split(" ")[0])
                    i += 1
                    text_lines = []
                    while i < len(lines) and lines[i].strip() != "":
                        payload = re.sub(r"<[^>]+>", "", lines[i]).strip()
                        if payload and not payload.isdigit():
                            text_lines.append(payload)
                        i += 1
                    text_joined = " ".join(text_lines).strip()
                    if text_joined:
                        results.append({
                            "start": _format_ms_to_mmss(int(start_ms)),
                            "end": _format_ms_to_mmss(int(end_ms)),
                            "text": text_joined
                        })
                except Exception:
                    pass
            else:
                i += 1
        return {"captions": results, "caption_type": caption_type}
    except Exception:
        return {"captions": [], "caption_type": caption_type}


def get_video_info_and_transcript(video_id: str):
    """Extract video info + English transcript if available"""

    # Always try to load cookies.txt (if it exists in project root)
    cookies_file = "cookies.txt"
    ydl_opts = {
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": ["en"],
        "skip_download": True,
        "quiet": True,
        "no_warnings": True,
        # Add user-agent to appear more like a real browser
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-us,en;q=0.5",
            "Accept-Encoding": "gzip,deflate",
            "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
    }
    
    if os.path.exists(cookies_file):
        ydl_opts["cookiefile"] = cookies_file
        print(f"Using cookies file: {cookies_file}")
    else:
        print("No cookies file found, proceeding without authentication")

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)

            video_url = f"https://www.youtube.com/watch?v={video_id}"
            video_name = info.get("title", "Unknown Title")

            subtitles = info.get("subtitles", {})
            auto_subs = info.get("automatic_captions", {})

            # Check for English captions in both manual subtitles and auto-captions
            caption_tracks = None
            
            if "en" in subtitles:
                caption_tracks = subtitles["en"]
                caption_type = "manual"
            elif "en" in auto_subs:
                caption_tracks = auto_subs["en"]
                caption_type = "auto"
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
                    "message": f"Transcript extracted successfully ({caption_type} captions)"
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
                "message": f"Transcript extracted successfully ({caption_type} text captions)"
            }

    except Exception as e:
        error_msg = str(e)
        
        # Check if it's an authentication error
        if "Sign in to confirm you're not a bot" in error_msg:
            return {
                "video_url": f"https://www.youtube.com/watch?v={video_id}",
                "video_name": "Authentication Required",
                "transcript": "",
                "success": False,
                "message": "YouTube requires authentication. Please update your cookies.txt file with fresh cookies from your browser."
            }
        elif "cookies" in error_msg.lower():
            return {
                "video_url": f"https://www.youtube.com/watch?v={video_id}",
                "video_name": "Cookie Error",
                "transcript": "",
                "success": False,
                "message": "Cookie authentication failed. Please check your cookies.txt file format and ensure cookies are not expired."
            }
        elif "Requested format is not available" in error_msg:
            # Try a simpler approach - just get video info without transcript
            try:
                simple_opts = {
                    "skip_download": True,
                    "quiet": True,
                    "no_warnings": True,
                    "http_headers": ydl_opts["http_headers"]
                }
                
                if os.path.exists(cookies_file):
                    simple_opts["cookiefile"] = cookies_file
                
                with yt_dlp.YoutubeDL(simple_opts) as ydl:
                    info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
                    
                    return {
                        "video_url": f"https://www.youtube.com/watch?v={video_id}",
                        "video_name": info.get("title", "Unknown Title"),
                        "transcript": "",
                        "success": False,
                        "message": "Video info extracted but no transcript available. This video might not have captions or they might be restricted."
                    }
            except Exception as fallback_error:
                return {
                    "video_url": f"https://www.youtube.com/watch?v={video_id}",
                    "video_name": "Format Error",
                    "transcript": "",
                    "success": False,
                    "message": f"Video format issue. This might be a restricted or unavailable video. Try a different video ID. Error: {str(fallback_error)}"
                }
        else:
            return {
                "video_url": f"https://www.youtube.com/watch?v={video_id}",
                "video_name": "Error",
                "transcript": "",
                "success": False,
                "message": f"Exception: {error_msg}"
            }


@app.get("/")
async def root():
    return {
        "message": "YouTube Transcript API is running 🚀",
        "endpoints": {
            "/transcript/{video_id}": "Get transcript for a YouTube video",
            "/video-info/{video_id}": "Get video information without requiring captions",
            "/health": "Health check",
            "/auth-status": "Check cookie authentication status",
            "/test-youtube": "Test YouTube connectivity with current cookies"
        },
        "example": "/transcript/dQw4w9WgXcQ",
        "note": "If you get authentication errors, use /auth-status to check cookies and /test-youtube to test connectivity. Use /video-info/{video_id} to check if a video has captions available."
    }


@app.get("/transcript/{video_id}", response_model=VideoResponse)
async def transcript(video_id: str):
    if not video_id or len(video_id) != 11:
        raise HTTPException(status_code=400, detail="Invalid video ID (must be 11 characters)")
    return VideoResponse(**get_video_info_and_transcript(video_id))


@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Healthy"}


@app.get("/auth-status")
async def auth_status():
    """Check authentication status and provide guidance"""
    cookies_file = "D:\Caption_n8n\YouTube-Transcript-Extractor-API\cookies.txt"
    if os.path.exists(cookies_file):
        try:
            with open(cookies_file, 'r') as f:
                content = f.read()
                lines = content.strip().split('\n')
                cookie_count = len([line for line in lines if line.strip() and not line.startswith('#')])
                
                # Check if cookies are expired (basic check)
                expired_count = 0
                current_time = int(time.time())
                for line in lines:
                    if line.strip() and not line.startswith('#'):
                        parts = line.split('\t')
                        if len(parts) >= 5:
                            try:
                                expiry = int(parts[4])
                                if expiry > 0 and expiry < current_time:
                                    expired_count += 1
                            except ValueError:
                                pass
                
                return {
                    "cookies_file_exists": True,
                    "total_cookies": cookie_count,
                    "expired_cookies": expired_count,
                    "status": "expired" if expired_count > 0 else "valid",
                    "message": f"Found {cookie_count} cookies, {expired_count} expired" if expired_count > 0 else f"Found {cookie_count} valid cookies"
                }
        except Exception as e:
            return {
                "cookies_file_exists": True,
                "error": str(e),
                "status": "error",
                "message": "Error reading cookies file"
            }
    else:
        return {
            "cookies_file_exists": False,
            "status": "missing",
            "message": "No cookies.txt file found. Please create one with fresh YouTube cookies."
        }


@app.get("/test-youtube")
async def test_youtube():
    """Test YouTube connectivity with current cookies"""
    try:
        # Test with a simple video that should have captions
        test_video_id = "dQw4w9WgXcQ"  # Rick Roll - should have captions
        result = get_video_info_and_transcript(test_video_id)
        
        return {
            "test_video_id": test_video_id,
            "test_result": result,
            "cookies_working": result["success"],
            "message": "YouTube connectivity test completed"
        }
    except Exception as e:
        return {
            "test_video_id": "dQw4w9WgXcQ",
            "test_result": None,
            "cookies_working": False,
            "error": str(e),
            "message": "YouTube connectivity test failed"
        }


@app.get("/video-info/{video_id}")
async def get_video_info_only(video_id: str):
    """Get video information without requiring captions"""
    if not video_id or len(video_id) != 11:
        raise HTTPException(status_code=400, detail="Invalid video ID (must be 11 characters)")
    
    try:
        cookies_file = "cookies.txt"
        ydl_opts = {
            "skip_download": True,
            "quiet": True,
            "no_warnings": True,
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-us,en;q=0.5",
                "Accept-Encoding": "gzip,deflate",
                "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }
        }
        
        if os.path.exists(cookies_file):
            ydl_opts["cookiefile"] = cookies_file
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            
            # Check for captions
            subtitles = info.get("subtitles", {})
            auto_subs = info.get("automatic_captions", {})
            
            has_english_captions = "en" in subtitles or "en" in auto_subs
            caption_languages = list(set(list(subtitles.keys()) + list(auto_subs.keys())))
            extracted = _extract_captions_with_timestamps(info)
            
            return {
                "video_id": video_id,
                "video_url": f"https://www.youtube.com/watch?v={video_id}",
                "title": info.get("title", "Unknown"),
                "duration": info.get("duration"),
                "view_count": info.get("view_count"),
                "uploader": info.get("uploader"),
                "upload_date": info.get("upload_date"),
                "description": info.get("description", "")[:500] + "..." if info.get("description") and len(info.get("description", "")) > 500 else info.get("description", ""),
                "has_captions": has_english_captions,
                "available_caption_languages": caption_languages,
                "captions": extracted.get("captions", []),
                "caption_type": extracted.get("caption_type"),
                "success": True,
                "message": "Video information extracted successfully"
            }
            
    except Exception as e:
        return {
            "video_id": video_id,
            "video_url": f"https://www.youtube.com/watch?v={video_id}",
            "success": False,
            "error": str(e),
            "message": "Failed to extract video information"
        }


if __name__ == "__main__":
    import uvicorn
    import os
    
    # Get port from environment (Railway sets this) or use default
    port = int(os.environ.get("PORT", 8000))
    
    # Use 0.0.0.0 for Railway, localhost for local development
    host = "0.0.0.0" if os.environ.get("RAILWAY_ENVIRONMENT") else "127.0.0.1"
    
    print(f"Starting server on {host}:{port}")
    uvicorn.run("main:app", host=host, port=port, reload=False)