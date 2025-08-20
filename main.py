import yt_dlp
import json
import re
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn

app = FastAPI(
    title="YouTube Transcript API",
    description="Extract video info and transcripts from YouTube videos",
    version="1.0.0"
)

class VideoResponse(BaseModel):
    video_url: str
    video_name: str
    transcript: str
    success: bool
    message: Optional[str] = None

def get_video_info_and_transcript(video_id):
    ydl_opts = {
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['en'],
        'skip_download': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            
            # Extract video info
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            video_name = info.get('title', 'Unknown Title')
            
            # Try to get English subtitles (manual first, then auto)
            subtitles = info.get('subtitles', {})
            auto_subs = info.get('automatic_captions', {})

            if 'en' in subtitles:
                caption_tracks = subtitles['en']
            elif 'en' in auto_subs:
                caption_tracks = auto_subs['en']
            else:
                return {
                    'video_url': video_url,
                    'video_name': video_name,
                    'transcript': "No English transcripts found",
                    'success': False,
                    'message': "No English captions available for this video"
                }

            if not caption_tracks:
                return {
                    'video_url': video_url,
                    'video_name': video_name,
                    'transcript': "No caption data found",
                    'success': False,
                    'message': "No caption tracks found"
                }

            # Prefer JSON captions when available (YouTube srv3/json3) to extract 'utf8' segments
            chosen = None
            for cand in caption_tracks:
                if cand.get('ext') in ('json3', 'srv3'):
                    chosen = cand
                    break
            if chosen is None:
                # Fallback to the first available track (likely vtt or ttml)
                chosen = caption_tracks[0]

            caption_url = chosen['url']
            caption_ext = chosen.get('ext', '')
            resp = requests.get(caption_url)
            if resp.status_code != 200:
                return {
                    'video_url': video_url,
                    'video_name': video_name,
                    'transcript': "Failed to download caption data",
                    'success': False,
                    'message': f"HTTP {resp.status_code}: Failed to download captions"
                }

            # If JSON (srv3/json3), parse events -> segs -> utf8
            content_type = resp.headers.get('content-type', '')
            if caption_ext in ('json3', 'srv3') or content_type.startswith('application/json'):
                data = None
                try:
                    data = resp.json()
                except Exception:
                    try:
                        data = json.loads(resp.text)
                    except Exception:
                        data = None
                if not data:
                    return {
                        'video_url': video_url,
                        'video_name': video_name,
                        'transcript': "Failed to parse JSON captions",
                        'success': False,
                        'message': "Invalid JSON format in captions"
                    }

                texts = []
                for event in data.get('events', []):
                    for seg in event.get('segs', []):
                        text_piece = seg.get('utf8', '')
                        if text_piece:
                            # Normalize whitespace and strip newlines inside segments
                            text_piece = text_piece.replace('\n', ' ').strip()
                            if text_piece:
                                texts.append(text_piece)

                if not texts:
                    return {
                        'video_url': video_url,
                        'video_name': video_name,
                        'transcript': "No utf8 segments found in captions",
                        'success': False,
                        'message': "No text content found in captions"
                    }

                text = ' '.join(texts)
                text = re.sub(r'\s+', ' ', text).strip()
                return {
                    'video_url': video_url,
                    'video_name': video_name,
                    'transcript': text,
                    'success': True,
                    'message': "Transcript extracted successfully from JSON captions"
                }

            # Else: fallback to VTT/TTML plain text parsing
            caption_text = resp.text
            lines = caption_text.split('\n')
            clean_lines = []
            for line in lines:
                line = line.strip()
                # Skip timing/index lines
                if not line or line.isdigit() or '-->' in line:
                    continue
                clean_line = re.sub(r'<[^>]+>', '', line)  # Remove HTML tags
                clean_line = clean_line.replace('&nbsp;', ' ')
                if clean_line:
                    clean_lines.append(clean_line)
            if not clean_lines:
                return {
                    'video_url': video_url,
                    'video_name': video_name,
                    'transcript': "No caption text found",
                    'success': False,
                    'message': "No readable text found in captions"
                }
            return {
                'video_url': video_url,
                'video_name': video_name,
                'transcript': ' '.join(clean_lines),
                'success': True,
                'message': "Transcript extracted successfully from text captions"
            }
    except Exception as e:
        return {
            'video_url': f"https://www.youtube.com/watch?v={video_id}",
            'video_name': "Error occurred",
            'transcript': "Error processing video",
            'success': False,
            'message': f"Exception: {str(e)}"
        }

@app.get("/", response_model=dict)
async def root():
    """API information and available endpoints"""
    return {
        "message": "YouTube Transcript API",
        "description": "Extract video info and transcripts from YouTube videos",
        "endpoints": {
            "GET /transcript/{video_id}": "Get video info and transcript",
            "GET /health": "Health check"
        },
        "example": "/transcript/dQw4w9WgXcQ",
        "note": "Video ID is the part after 'v=' in YouTube URL"
    }

@app.get("/transcript/{video_id}", response_model=VideoResponse)
async def get_transcript(video_id: str):
    """Get video information and transcript by YouTube video ID"""
    if not video_id or len(video_id) != 11:
        raise HTTPException(status_code=400, detail="Invalid video ID. Must be 11 characters.")
    
    result = get_video_info_and_transcript(video_id)
    return VideoResponse(**result)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "YouTube Transcript API is running"}

if __name__ == "__main__":
    print("Starting YouTube Transcript API...")
    print("API docs: http://localhost:8000/docs")
    print("Test with: http://localhost:8000/transcript/dQw4w9WgXcQ")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)







