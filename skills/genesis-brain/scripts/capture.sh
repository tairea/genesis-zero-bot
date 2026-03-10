#!/usr/bin/env bash
# capture.sh — Capture text into Genesis' knowledge graph
# Usage: bash capture.sh "<text content>" [title] [author]
# Output: JSON with doc_id, concepts_count, relations_count
set -euo pipefail

CONTENT="$1"
TITLE="${2:-capture-$(date +%s)}"
AUTHOR="${3:-}"

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HANDLE_MAP="$SCRIPTS_DIR/handle-map.json"

# Normalise author: resolve known handles, auto-register new ones
if [ -n "$AUTHOR" ]; then
    AUTHOR=$(python3 -c "
import json, os, re

raw = '$AUTHOR'
handle_map_path = '$HANDLE_MAP'

# Load existing map (create empty if missing)
if os.path.exists(handle_map_path):
    with open(handle_map_path) as f:
        handle_map = json.load(f)
else:
    handle_map = {}

# Resolve if already mapped
resolved = handle_map.get(raw) or handle_map.get(raw.lstrip('@'))
if resolved:
    print(resolved)
else:
    # Normalise: strip @, title-case first word
    clean = re.sub(r'^@', '', raw)
    display = clean.split('_')[0].title()

    # Auto-register both raw and stripped forms
    handle_map[raw] = display
    handle_map[clean] = display
    with open(handle_map_path, 'w') as f:
        json.dump(handle_map, f, indent=2)

    print(display)
")
fi

# Save to temp file
mkdir -p /tmp/genesis-ingest
TMPFILE="/tmp/genesis-ingest/${TITLE}.md"
echo "$CONTENT" > "$TMPFILE"

SKILL_DIR="$HOME/.openclaw/workspace-genesis/skills/semantic-graph"
cd "$SKILL_DIR"
source .venv/bin/activate
export $(grep -v "^#" "$HOME/.openclaw/.env" | xargs)

# Ingest
if [ -n "$AUTHOR" ]; then
    OUTPUT=$(python pipeline.py ingest "$TMPFILE" --embed -v --meta "{\"author\":\"$AUTHOR\"}" 2>&1)
else
    OUTPUT=$(python pipeline.py ingest "$TMPFILE" --embed -v 2>&1)
fi

# Parse summary
SUMMARY=$(echo "$OUTPUT" | grep -oP 'Done in \K.*' || echo "")

if [ -z "$SUMMARY" ]; then
  echo '{"captured": true, "concepts_count": 0, "relations_count": 0, "note": "Text was too short for extraction"}'
  exit 0
fi

CONCEPTS=$(echo "$SUMMARY" | grep -oP 'concepts=\K\d+' || echo "0")
RELATIONS=$(echo "$SUMMARY" | grep -oP 'relations=\K\d+' || echo "0")
DOC_ID=$(echo "$SUMMARY" | grep -oP 'doc=\K\S+' || echo "unknown")

echo "{\"captured\": true, \"doc_id\": \"$DOC_ID\", \"concepts_count\": $CONCEPTS, \"relations_count\": $RELATIONS}"

# Cleanup
rm -f "$TMPFILE"
