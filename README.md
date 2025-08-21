# YouTube Transcript Extractor API

A FastAPI-based service that extracts transcripts from YouTube videos with **timestamps** using yt-dlp. Includes both API endpoints and a GUI interface.

## ✨ Features

- 🎯 **Extract transcripts with timestamps** (mm:ss format)
- 🌐 **REST API** for programmatic access
- 🖥️ **GUI Interface** for easy manual extraction
- 🔗 **ngrok integration** for public URL access
- 🔐 **Cookie authentication** to avoid YouTube bot detection
- 📊 **Video metadata** (title, duration, uploader, etc.)
- 🎬 **Support for both manual and automatic captions**

## 📁 Project Structure

```
YouTube-Transcript-Extractor-API/
├── main.py                 # FastAPI server with timestamp extraction
├── gui_interface.py        # GUI application for manual extraction
├── generate_cookies.py     # Helper to extract YouTube cookies
├── requirements.txt        # Python dependencies
├── cookies.txt            # YouTube authentication cookies
├── ngrok.yml              # ngrok configuration
├── start_with_ngrok.bat   # Windows batch script to start API + ngrok
├── start_with_ngrok.ps1   # PowerShell script to start API + ngrok
├── run_gui.bat            # Windows batch script to launch GUI
└── README.md              # This file
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Authentication (IMPORTANT!)
```bash
python generate_cookies.py
```
This extracts fresh YouTube cookies from your browser to avoid bot detection.

### 3. Choose Your Interface

#### Option A: GUI Interface (Recommended for beginners)
```bash
# Start the API server first
python main.py

# In a new terminal, launch the GUI
python gui_interface.py
# OR double-click run_gui.bat
```

#### Option B: API Only
```bash
python main.py
```
Then use Postman or curl to test endpoints.

#### Option C: Public URL with ngrok
```bash
# Double-click start_with_ngrok.bat
# OR run start_with_ngrok.ps1 in PowerShell
```

## 🖥️ GUI Interface

The GUI provides a user-friendly way to extract transcripts:

1. **Launch**: Run `python gui_interface.py` or double-click `run_gui.bat`
2. **Enter Video ID**: Paste a YouTube video ID (e.g., `FuqNluMTIR8`)
3. **Click Extract**: See results with timestamps

**Example Output:**
```
Video ID: FuqNluMTIR8
Title: [Video Title]
Duration: 120 seconds
Uploader: [Channel Name]
Caption Type: auto
Success: True
================================================================================

[  1] 00:01 - 00:03: Hello everyone, welcome to this video

[  2] 00:03 - 00:06: Today we're going to talk about...

[  3] 00:06 - 00:09: Let's get started with the first topic
```

## 🌐 Public URL with ngrok

### Setup
1. **Install ngrok**: Download from https://ngrok.com/download
2. **Configure**: Update `ngrok.yml` with your authtoken
3. **Start**: Double-click `start_with_ngrok.bat`

### Usage
The script will print a public HTTPS URL like:
```
🌐 Public: https://abc123.ngrok-free.app
```

Use this URL in Postman or share with others.

## 📡 API Endpoints

| Endpoint | Description | Example |
|----------|-------------|---------|
| `GET /` | API info and examples | `http://localhost:8000/` |
| `GET /video-info/{video_id}` | **Get video info + captions with timestamps** | `http://localhost:8000/video-info/FuqNluMTIR8` |
| `GET /transcript/{video_id}` | Get plain transcript | `http://localhost:8000/transcript/FuqNluMTIR8` |
| `GET /health` | Health check | `http://localhost:8000/health` |
| `GET /auth-status` | Check cookie status | `http://localhost:8000/auth-status` |
| `GET /test-youtube` | Test YouTube connectivity | `http://localhost:8000/test-youtube` |

## 🧪 Testing in Postman

### Local Testing
```
GET http://localhost:8000/video-info/FuqNluMTIR8
```

### ngrok Testing
```
GET https://your-ngrok-url.ngrok-free.app/video-info/FuqNluMTIR8
```

### Expected Response
```json
{
  "video_id": "FuqNluMTIR8",
  "video_url": "https://www.youtube.com/watch?v=FuqNluMTIR8",
  "title": "Video Title",
  "duration": 120,
  "view_count": 1000,
  "uploader": "Channel Name",
  "upload_date": "20231201",
  "description": "Video description...",
  "has_captions": true,
  "available_caption_languages": ["en"],
  "caption_type": "auto",
  "captions": [
    {
      "start": "00:01",
      "end": "00:03", 
      "start_ms": 1000,
      "end_ms": 3000,
      "text": "Hello everyone, welcome to this video"
    }
  ],
  "success": true,
  "message": "Video information extracted successfully"
}
```

## 🔐 Authentication Issues

### Error: "Sign in to confirm you're not a bot"
Your cookies are expired or invalid.

**Solutions:**
1. **Recommended**: Run `python generate_cookies.py`
2. **Manual**: Export cookies from browser extension
3. **Command line**: `yt-dlp --cookies-from-browser chrome --cookies cookies.txt`

### Cookie Management
- Cookies expire quickly (hours/days)
- Must be logged into YouTube in browser
- File must be named `cookies.txt` in project root
- Use Netscape format (generated by helper script)

## 🚨 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "Sign in to confirm you're not a bot" | Run `python generate_cookies.py` |
| "No English captions available" | Try a different video with captions |
| "ngrok subdomain error" | Remove `subdomain:` line from `ngrok.yml` |
| "API not responding" | Check if `python main.py` is running |
| "GUI not connecting" | Ensure API server is running first |

## 🛠️ Development

### Local Development
```bash
# Run with auto-reload
python main.py

# Run with uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### File Paths
- **API Server**: `http://localhost:8000` (default)
- **ngrok Status**: `http://127.0.0.1:4040/status`
- **Cookies File**: `./cookies.txt` (project root)
- **GUI API URL**: Line 15 in `gui_interface.py` (change for ngrok)

## 📦 Dependencies

- `fastapi` - Web framework
- `uvicorn` - ASGI server  
- `yt-dlp` - YouTube downloader
- `requests` - HTTP client
- `pydantic` - Data validation
- `tkinter` - GUI framework (built-in)

## 🎯 What's New

### Version 1.0.2 Updates:
- ✅ **Timestamp extraction** (mm:ss format)
- ✅ **GUI interface** for easy manual use
- ✅ **Enhanced API** with detailed video info
- ✅ **ngrok integration** for public URLs
- ✅ **Better error handling** and user feedback
- ✅ **Cookie management** improvements

## 📝 Notes

- **No AI/ML**: This is a data extraction tool, not an AI application
- **Captions required**: Videos must have captions/subtitles
- **Browser headers**: Uses realistic browser headers to avoid detection
- **Multiple formats**: Supports JSON3, SRV3, VTT, and TTML caption formats
- **Threading**: GUI uses threading to prevent freezing during API calls

## 🔗 Quick Commands

```bash
# Start everything (API + ngrok)
start_with_ngrok.bat

# Start GUI only
run_gui.bat

# Generate fresh cookies
python generate_cookies.py

# Test API health
curl http://localhost:8000/health
```
