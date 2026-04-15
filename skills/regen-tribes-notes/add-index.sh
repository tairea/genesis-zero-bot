#!/usr/bin/env bash
# regen-tribes-notes index maintenance
# Replaces the index between <!-- NOTES_INDEX --> markers in README.md
set -euo pipefail

REPO_DIR="$HOME/.radicle/regen-tribes-notes"
README="$REPO_DIR/README.md"
IRIS_BASE="https://app.radicle.xyz/nodes/iris.radicle.xyz/rad:z4WAr7CiNkf5JAoAb1srwi7gDz8nU"
MARKER_START="<!-- NOTES_INDEX -->"
MARKER_END="<!-- /NOTES_INDEX -->"

cd "$REPO_DIR"

# Get the README prologue (everything before the start marker)
if grep -q "$MARKER_START" "$README" 2>/dev/null; then
  PROLOGUE=$(awk -v m="$MARKER_START" 'NR==1,/'"$MARKER_START"'/{if(/'"$MARKER_START"'/){sub(/'"$MARKER_START"'/,"");print}else print}' "$README")
else
  PROLOGUE=$(cat "$README")
fi

# Extract all .md files except README.md
NOTES=$(find . -maxdepth 1 -name "*.md" ! -name "README.md" -type f 2>/dev/null | sort)

# Build index table
INDEX=""

if [[ -n "$NOTES" ]]; then
  INDEX="$INDEX\n\n| # | Title | Topic | Published | Link |"
  INDEX="$INDEX\n|---|-------|-------|-----------|------|"

  COUNT=1
  while IFS= read -r nf; do
    TITLE=$(grep '^title:' "$nf" 2>/dev/null | sed 's/title: //' | sed 's/^"//;s/"$//' | sed "s/^'//;s/'$//")
    TOPIC=$(grep '^topic:' "$nf" 2>/dev/null | sed 's/topic: //' | sed 's/^"//;s/"$//' | sed "s/^'//;s/'$//")
    PUBLISHED=$(grep '^published:' "$nf" 2>/dev/null | sed 's/published: //' | sed 's/^"//;s/"$//' | sed "s/^'//;s/'$//")
    COMMIT=$(git log --all --format="%H" -- "$nf" 2>/dev/null | head -1)
    COMMIT_SHORT=$(echo "$COMMIT" | cut -c1-12)

    if [[ -z "$TITLE" ]]; then
      TITLE=$(basename "$nf" .md)
    fi
    if [[ -z "$TOPIC" ]]; then
      TOPIC="general"
    fi

    if [[ -n "$COMMIT" ]]; then
      LINK="[${COMMIT_SHORT}](${IRIS_BASE}/tree/${COMMIT})"
    else
      LINK="—"
    fi

    INDEX="$INDEX\n| $COUNT | $TITLE | $TOPIC | $PUBLISHED | $LINK |"
    COUNT=$((COUNT + 1))
  done <<< "$NOTES"
fi

INDEX="$INDEX\n\n$MARKER_END"

# Write complete README
{
  echo -e "$PROLOGUE"
  echo -e "$MARKER_START"
  echo -e "$INDEX"
} > "$README"

NOTE_COUNT=$(echo "$NOTES" | wc -l | tr -d ' ')
echo "Index: $NOTE_COUNT notes"
