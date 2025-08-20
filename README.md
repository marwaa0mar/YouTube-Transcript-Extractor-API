# YouTube Transcript Extractor API

A FastAPI-based service that extracts transcripts from YouTube videos using yt-dlp.

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Generate fresh cookies (IMPORTANT!):**
   ```bash
   python generate_cookies.py
   ```
   
   This will extract fresh YouTube cookies from your browser to avoid bot detection.

3. **Run the API:**
   ```bash
   python main.py
   ```

4. **Test the API:**
   ```
   GET /transcript/dQw4w9WgXcQ
   ```

## 🔐 Authentication Issues

If you get the error "Sign in to confirm you're not a bot", your cookies are expired or invalid.

### Solution 1: Use the helper script (Recommended)
```bash
python generate_cookies.py
```

### Solution 2: Manual cookie export
1. Install browser extension: "Get cookies.txt LOCALLY" for Chrome/Firefox
2. Go to YouTube and make sure you're logged in
3. Use the extension to export cookies
4. Save as `cookies.txt` in your project root

### Solution 3: Command line with yt-dlp
```bash
yt-dlp --cookies-from-browser chrome --cookies cookies.txt
```

## 📡 API Endpoints

- `GET /` - API info and examples
- `GET /transcript/{video_id}` - Extract transcript from YouTube video
- `GET /health` - Health check
- `GET /auth-status` - Check cookie authentication status

## 🎯 Example Usage

```bash
# Get transcript for a video
curl "http://localhost:8000/transcript/dQw4w9WgXcQ"

# Check authentication status
curl "http://localhost:8000/auth-status"
```

## 🔧 Configuration

The API automatically looks for `cookies.txt` in the project root. If found, it will use it for authentication.

## 🚨 Common Issues

1. **"Sign in to confirm you're not a bot"**
   - Your cookies are expired
   - Run `python generate_cookies.py` to get fresh ones

2. **"No English captions available"**
   - The video doesn't have English subtitles
   - Try a different video

3. **Cookie format errors**
   - Ensure cookies.txt is in Netscape format
   - Use the helper script to generate proper format

## 📝 Notes

- Cookies expire quickly (usually within hours/days)
- You need to be logged into YouTube in your browser
- The API includes browser-like headers to avoid detection
- Supports both manual and automatic captions

## 🛠️ Development

```bash
# Run with auto-reload
python main.py

# Run with uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📦 Dependencies

- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `yt-dlp` - YouTube downloader
- `requests` - HTTP client
- `pydantic` - Data validation
