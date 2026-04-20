#!/usr/bin/env python3
"""
YouTube transcript extraction using youtube-transcript-api with auth cookies.
Bypasses Hetzner VPS IP block by using YouTube session cookies.
"""

import sys
import os
import json
import http.cookiejar

# Add yt-dlp's cookiejar compatibility
sys.path.insert(0, '/home/ian/.local/lib/python3.12/site-packages')

import requests
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._transcripts import Session


def load_netscape_cookies(cookie_file: str) -> requests.Session:
    """Load cookies from Netscape-format file into a requests Session."""
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
    })
    
    # Parse Netscape cookies
    jar = http.cookiejar.MozillaCookieJar(cookie_file)
    jar.load(ignore_discard=True, ignore_expires=True)
    
    # Copy to session
    for cookie in jar:
        session.cookies.set_cookie(cookie)
    
    return session


def get_transcript(video_id: str, cookie_file: str = '/tmp/yt_cookies.txt', 
                   languages: list = None, output_format: str = 'text') -> str:
    """
    Get transcript for a YouTube video using authenticated session.
    
    Args:
        video_id: YouTube video ID
        cookie_file: Path to Netscape-format cookies
        languages: Preferred languages (default: ['en'])
        output_format: 'text' (plain), 'srt', 'vtt'
    
    Returns:
        Transcript text
    """
    if languages is None:
        languages = ['en']
    
    # Create authenticated session
    session = load_netscape_cookies(cookie_file)
    
    # Get transcript with authenticated session
    api = YouTubeTranscriptApi(http_client=session)
    
    # Get the transcript list first to find available languages
    transcript_list = api.list(video_id)
    
    # Try to get transcript in preferred language
    transcript = None
    for lang in languages:
        try:
            for t in transcript_list:
                if t.language_code.startswith(lang):
                    transcript = api.fetch(video_id, languages=[lang])
                    break
        except Exception:
            pass
        if transcript:
            break
    
    # Fallback to any available
    if not transcript:
        transcript = api.fetch(video_id)
    
    # Format output
    if output_format == 'text':
        return ' '.join([seg['text'] for seg in transcript])
    elif output_format == 'srt':
        lines = []
        for i, seg in enumerate(transcript):
            start = seg['start']
            end = start + seg['duration']
            lines.append(f"{i+1}\n{format_timestamp(start, 'srt')} --> {format_timestamp(end, 'srt')}\n{seg['text']}\n")
        return '\n'.join(lines)
    elif output_format == 'vtt':
        lines = ['WEBVTT\n']
        for seg in transcript:
            start = seg['start']
            end = start + seg['duration']
            lines.append(f"{format_timestamp(start, 'vtt')} --> {format_timestamp(end, 'vtt')}\n{seg['text']}\n")
        return '\n'.join(lines)
    else:
        return str(transcript)


def format_timestamp(seconds: float, fmt: str) -> str:
    """Format seconds to SRT or VTT timestamp."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    if fmt == 'srt':
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    else:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def main():
    if len(sys.argv) < 2:
        print("Usage: transcript_with_cookies.py <videoId> [lang] [output_format]", file=sys.stderr)
        sys.exit(1)
    
    video_id = sys.argv[1]
    lang = sys.argv[2] if len(sys.argv) > 2 else 'en'
    output_fmt = sys.argv[3] if len(sys.argv) > 3 else 'text'
    cookie_file = '/tmp/yt_cookies.txt'
    
    if not os.path.exists(cookie_file):
        print(f"Error: Cookie file not found: {cookie_file}", file=sys.stderr)
        sys.exit(1)
    
    try:
        transcript = get_transcript(video_id, cookie_file, languages=[lang], output_format=output_fmt)
        print(transcript)
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
