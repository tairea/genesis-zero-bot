#!/usr/bin/env bash
# add-entry.sh — append a single row to README index (append-only, O(lines_to_header))
# Usage: add-entry.sh <title> <topic> <published> <commit>
set -euo pipefail

TITLE="${1:-}"
TOPIC="${2:-}"
PUBLISHED="${3:-}"
COMMIT="${4:-}"
COMMIT_SHORT="${COMMIT:0:12}"

REPO_DIR="$HOME/.radicle/regen-tribes-notes"
README="$REPO_DIR/README.md"
IRIS_BASE="https://app.radicle.xyz/nodes/iris.radicle.xyz/rad:z4WAr7CiNkf5JAoAb1srwi7gDz8nU"

cd "$REPO_DIR"

if [[ ! -f "$README" ]]; then
  echo "Error: README not found: $README" >&2
  exit 1
fi

if [[ -z "$TITLE" || -z "$COMMIT" ]]; then
  echo "Error: missing required args" >&2
  exit 1
fi

# Count existing data rows: lines starting with "| " + digit
# grep -c returns 1 exit if 0 matches → use ${var:-0} guard + tr to strip newlines
RAW_COUNT=$(grep -cE '^\| [0-9]+\|' "$README" 2>/dev/null || true)
RAW_COUNT=${RAW_COUNT:-0}
ENTRY_COUNT=$(echo "$RAW_COUNT" | tr -d '\n' | sed 's/[^0-9]//g')
[[ "$ENTRY_COUNT" =~ ^[0-9]+$ ]] || ENTRY_COUNT=0
NEW_NUM=$((ENTRY_COUNT + 1))

LINK="[${COMMIT_SHORT}](${IRIS_BASE}/tree/${COMMIT})"
TITLE_ESC=$(echo "$TITLE" | sed 's/|/\\|/g')
TOPIC_ESC=$(echo "$TOPIC" | sed 's/|/\\|/g')
NEW_ROW="| $NEW_NUM | $TITLE_ESC | $TOPIC_ESC | $PUBLISHED | $LINK |"

# Find table header separator line (|---|...|---|)
HEADER_LINE=$(grep -nE '^\|---+' "$README" 2>/dev/null | head -1 | cut -d: -f1)
if [[ -z "$HEADER_LINE" ]]; then
  echo "Error: could not find table header separator in README" >&2
  exit 1
fi

# Split README at separator:
#   head -n HEADER_LINE          → prologue + header row + separator
#   tail -n +$((HEADER_LINE+1)) → rest (existing rows + closing marker)
# Write: head + new_row + tail
{
  head -n "$HEADER_LINE" "$README"
  echo "$NEW_ROW"
  tail -n +$((HEADER_LINE + 1)) "$README"
} > "${README}.tmp" && mv "${README}.tmp" "${README}"
