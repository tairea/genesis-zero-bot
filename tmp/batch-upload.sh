#!/usr/bin/env bash
set -euo pipefail

export $(grep -v "^#" ~/.openclaw/.env | xargs)
GOOGLE_ACCESS_TOKEN=$(bash ~/.openclaw/workspace-genesis/skills/alchemy/scripts/gdrive-auth.sh "$GOOGLE_SERVICE_ACCOUNT_KEY")
GENESIS_FOLDER="1fJGG4sAypTpeNRVtcQE-3MaiuYQHhV0w"

echo "=== Uploading telegram-syntheses ==="
for f in ~/.openclaw/workspace-genesis/telegram-syntheses/*.md; do
  fname=$(basename "$f")
  result=$(curl -s -X POST "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart" \
    -H "Authorization: Bearer ${GOOGLE_ACCESS_TOKEN}" \
    -F "metadata={\"name\":\"$fname\",\"parents\":[\"${GENESIS_FOLDER}\"]};type=application/json" \
    -F "file=@$f;type=text/markdown")
  id=$(echo "$result" | jq -r '.id // empty')
  if [ -n "$id" ]; then
    echo "UPLOADED: $fname -> $id"
  else
    echo "FAILED: $fname -> $(echo "$result" | jq -r '.error.message // "unknown error")"
  fi
done

echo ""
echo "=== Uploading key workspace files ==="
FILES=(
  "memory/strategic-synthesis-vitali.md"
  "memory/2026-04-20.md"
  "memory/2026-04-19.md"
  "memory/2026-04-15.md"
  "memory/2026-04-13.md"
  "regentribes-notes/FCL-Formation-Coding-Language.md"
  "regentribes-notes/Resource-Ecosystem-Complete-Self-Taught-Stack.md"
  "regentribes-notes/Ben-Goertzel-Three-Gaps-in-Current-ML.md"
  "regentribes-notes/Craig-Reynolds-Boids-1986.md"
  "regentribes-notes/Inverse-Architecture-for-Correctness-Critical-Domains.md"
  "regentribes-notes/Obscuration-Problem-and-Instrument-Architecture.md"
  "drone-swarm-regenerative-communities.md"
  "closed-loop-life-support.md"
  "construction-3dp-ecosystem.md"
  "zero-cost-infrastructure-design.md"
  "RNF_Complete_Framework_Structure.md"
)

for relpath in "${FILES[@]}"; do
  f="$HOME/.openclaw/workspace-genesis/$relpath"
  if [ -f "$f" ]; then
    fname=$(basename "$f")
    result=$(curl -s -X POST "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart" \
      -H "Authorization: Bearer ${GOOGLE_ACCESS_TOKEN}" \
      -F "metadata={\"name\":\"$fname\",\"parents\":[\"${GENESIS_FOLDER}\"]};type=application/json" \
      -F "file=@$f;type=text/markdown")
    id=$(echo "$result" | jq -r '.id // empty')
    if [ -n "$id" ]; then
      echo "UPLOADED: $fname -> $id"
    else
      echo "FAILED: $fname -> $(echo "$result" | jq -r '.error.message // "unknown error")"
    fi
  fi
done
