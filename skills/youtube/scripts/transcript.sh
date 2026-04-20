#!/bin/bash
# Usage: transcript.sh <videoId> [lang]
VIDEO_ID="$1"
LANG="${2:-en}"
COOKIE_FILE="/tmp/yt_cookies.txt"

if [ -z "$VIDEO_ID" ]; then
  echo "Usage: transcript.sh <videoId> [lang]"
  exit 1
fi

# Check cookies exist
if [ ! -f "$COOKIE_FILE" ]; then
  echo "Error: $COOKIE_FILE not found"
  exit 1
fi

# Get transcript via yt-dlp (uses cookies for auth)
yt-dlp --cookies "$COOKIE_FILE" \
  --skip-download \
  --write-auto-sub \
  --sub-lang "$LANG" \
  --output "/tmp/yt_sub_$VIDEO_ID" \
  "https://youtu.be/$VIDEO_ID" 2>&1
