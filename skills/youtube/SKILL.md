---
name: youtube
description: YouTube Data API v3 integration + transcript extraction via yt-dlp with auth cookies. Use when asked to look up a YouTube video, search for videos, or get video content/transcripts.
---

# YouTube Skill

Uses YouTube Data API v3 for metadata + yt-dlp with cookies for transcripts.

## Setup

### API Key
1. Enable YouTube Data API v3 in Google Cloud Console
2. Create an API key
3. Add to `~/.openclaw/.env`: `YOUTUBE_API_KEY=your_key`

### Auth Cookies (for transcripts)
Cookies are stored at `/tmp/yt_cookies.txt` (Netscape format). They bypass Hetzner VPS IP block.

To refresh cookies:
1. Go to YouTube in your browser and log in
2. Export cookies as JSON (EditThisCookie extension)
3. Convert to Netscape format using `scripts/cookies_to_netscape.py`

## Commands

```bash
# Video metadata (title, description, channel, views, likes, duration, thumbnails)
youtube.js info <videoId>

# Search videos
youtube.js search <query>

# Get video transcript (requires cookies at /tmp/yt_cookies.txt)
transcript.sh <videoId> [lang]
```

## What it CAN do

- ✅ Video metadata: title, description, channel, publish date, duration, views, likes
- ✅ Video thumbnails (all sizes)
- ✅ Search by keyword
- ✅ Transcripts via yt-dlp + auth cookies (for videos that have captions)

## What it CANNOT do

- ❌ Watch/play video (no browser on server)
- ❌ Transcripts for videos without captions
- ❌ Downloads that require high-quality format selection
