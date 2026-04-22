#!/bin/bash
# update-index.sh — Append-only README index update for regen-tribes-notes
# Usage: ./update-index.sh <NNN> "<Title>"
# Example: ./update-index.sh 113 "Some New Topic"

set -e

NNN="$1"
TITLE="$2"
README="/home/ian/.radicle/regen-tribes-notes/README.md"
REPO="/home/ian/.radicle/regen-tribes-notes"

if [ -z "$NNN" ] || [ -z "$TITLE" ]; then
    echo "Usage: $0 <NNN> <Title>"
    exit 1
fi

NEW_ROW="| $NNN | body | information | $TITLE |"

# Verify ASCII-only title
if echo "$TITLE" | grep -qP '[^\x00-\x7F]'; then
    echo "ERROR: Title contains non-ASCII characters"
    exit 1
fi

# Verify NNN is numeric
if ! echo "$NNN" | grep -qP '^[0-9]+$'; then
    echo "ERROR: NNN must be numeric"
    exit 1
fi

cd "$REPO"

# Find last row with number <= NNN
INSERT_LINE=$(grep -nE "^\| [0-9]+ \|" README.md | while IFS= read -r line; do
    NUM=$(echo "$line" | sed 's/| *\([0-9]*\) *|.*/\1/')
    if [ "$NUM" -le "$NNN" ]; then
        echo "$line"
    fi
done | tail -1 | cut -d: -f1)

if [ -z "$INSERT_LINE" ]; then
    # No row found, insert after header
    INSERT_LINE=$(grep -n "^| N |" README.md | cut -d: -f1)
fi

# Insert after found line
sed -i "${INSERT_LINE}a $NEW_ROW" README.md

echo "Inserted row $NNN: $TITLE after line $INSERT_LINE"

# Verify 1:1 correspondence
FILE_COUNT=$(ls [0-9]*.md 2>/dev/null | wc -l)
ROW_COUNT=$(grep -cE "^\| [0-9]+ \| body \|" README.md)

if [ "$FILE_COUNT" != "$ROW_COUNT" ]; then
    echo "WARNING: MISMATCH — $FILE_COUNT files, $ROW_COUNT rows"
    echo "  Fix before commit"
else
    echo "PASS: $FILE_COUNT files, $ROW_COUNT rows"
fi
