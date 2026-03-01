#!/usr/bin/env bash
# weekly-nudge.sh
# Sends a Telegram reminder to any vision holder who has an in-progress
# Community Alchemy guide and hasn't been active in 3+ days.
#
# Run via cron — e.g. every Monday at 9am:
#   0 9 * * 1 TELEGRAM_BOT_TOKEN=xxx bash /path/to/weekly-nudge.sh
#
# Required env:
#   TELEGRAM_BOT_TOKEN   — your Telegram bot token
#
# Optional env:
#   ALCHEMY_DATA_DIR     — defaults to ~/.zeroclaw/alchemy
#   INACTIVE_DAYS        — days of inactivity before nudging (default: 3)
#   NUDGE_COOLDOWN_DAYS  — min days between nudges per user (default: 6)

set -euo pipefail

ALCHEMY_DATA_DIR="${ALCHEMY_DATA_DIR:-$HOME/.zeroclaw/alchemy}"
INACTIVE_DAYS="${INACTIVE_DAYS:-3}"
NUDGE_COOLDOWN_DAYS="${NUDGE_COOLDOWN_DAYS:-6}"
NOW_TS=$(date +%s)

if [ -z "${TELEGRAM_BOT_TOKEN:-}" ]; then
  echo "ERROR: TELEGRAM_BOT_TOKEN is not set." >&2
  exit 1
fi

if [ ! -d "$ALCHEMY_DATA_DIR" ]; then
  echo "No alchemy data directory found at $ALCHEMY_DATA_DIR — nothing to nudge."
  exit 0
fi

# Cross-platform ISO timestamp to epoch
iso_to_epoch() {
  local ts="$1"
  # Try GNU date first, then BSD date (macOS)
  date -d "$ts" +%s 2>/dev/null || \
  date -j -f "%Y-%m-%dT%H:%M:%SZ" "$ts" +%s 2>/dev/null || \
  echo 0
}

days_since() {
  local ts="$1"
  local epoch
  epoch=$(iso_to_epoch "$ts")
  if [ "$epoch" -eq 0 ]; then echo 9999; return; fi
  echo $(( (NOW_TS - epoch) / 86400 ))
}

NUDGED=0
SKIPPED=0
ERRORS=0

for progress_file in "$ALCHEMY_DATA_DIR"/*/progress.json; do
  [ -f "$progress_file" ] || continue

  # Parse key fields
  status=$(jq -r '.status // "unknown"' "$progress_file")
  [ "$status" = "in_progress" ] || { SKIPPED=$((SKIPPED+1)); continue; }

  chat_id=$(jq -r '.chatId // ""' "$progress_file")
  name=$(jq -r '.name // "friend"' "$progress_file")
  community_name=$(jq -r '.communityName // "your community"' "$progress_file")
  current_area=$(jq -r '.currentArea // 0' "$progress_file")
  last_active=$(jq -r '.lastActiveAt // "1970-01-01T00:00:00Z"' "$progress_file")
  last_nudged=$(jq -r '.lastNudgedAt // "1970-01-01T00:00:00Z"' "$progress_file")

  if [ -z "$chat_id" ]; then
    echo "WARN: No chatId in $progress_file — skipping." >&2
    ERRORS=$((ERRORS+1))
    continue
  fi

  # Skip if too recently active
  days_inactive=$(days_since "$last_active")
  if [ "$days_inactive" -lt "$INACTIVE_DAYS" ]; then
    SKIPPED=$((SKIPPED+1))
    continue
  fi

  # Skip if nudged too recently
  days_since_nudge=$(days_since "$last_nudged")
  if [ "$days_since_nudge" -lt "$NUDGE_COOLDOWN_DAYS" ]; then
    SKIPPED=$((SKIPPED+1))
    continue
  fi

  # Build area name map
  area_name() {
    case "$1" in
      0)  echo "Where Are You Now" ;;
      1)  echo "Hone Your Vision" ;;
      2)  echo "Recruit Your Ideal Members" ;;
      3)  echo "Group Agreements & Governance" ;;
      4)  echo "Business Models & Infrastructure" ;;
      5)  echo "Acquire the Best Land" ;;
      6)  echo "Identify Your Funding Needs" ;;
      7)  echo "Strategize Your Marketing" ;;
      8)  echo "Master Plan Sustainable Systems" ;;
      9)  echo "Build Your Neighborhoods" ;;
      10) echo "Activate Community Culture" ;;
      11) echo "Manage & Review Your Ecosystem" ;;
      *)  echo "the Action Plan" ;;
    esac
  }

  next_area_name=$(area_name "$current_area")
  completed_count=$(jq '.completedAreas | length' "$progress_file")
  remaining=$((12 - completed_count))

  message="🌱 Hey ${name}! Just checking in on *${community_name}*.

You're ${completed_count} of 11 areas through your Community Alchemy journey — up next is *Area ${current_area}: ${next_area_name}*.

Ready to continue? Just reply with *resume* or *continue my alchemy guide* and I'll pick up right where we left off. 🔺

(${remaining} areas to go — you're closer than you think!)"

  # Send the message
  http_code=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    -H "Content-Type: application/json" \
    -d "$(jq -n \
      --arg chat_id "$chat_id" \
      --arg text "$message" \
      '{chat_id: $chat_id, text: $text, parse_mode: "Markdown"}')")

  if [ "$http_code" = "200" ]; then
    # Update lastNudgedAt in progress.json
    now_iso=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    updated=$(jq --arg now "$now_iso" '.lastNudgedAt = $now' "$progress_file")
    echo "$updated" > "$progress_file"
    echo "Nudged: $name ($chat_id) — ${community_name} [Area ${current_area}]"
    NUDGED=$((NUDGED+1))
  else
    echo "ERROR: Failed to send nudge to $chat_id (HTTP $http_code)" >&2
    ERRORS=$((ERRORS+1))
  fi

done

echo "---"
echo "Done. Nudged: $NUDGED | Skipped: $SKIPPED | Errors: $ERRORS"
