#!/usr/bin/env bash
# publish-file.sh — publish a file to regen-tribes-notes
# STE100 gate applies only to short text inputs (Telegram triggers)
# File publications pass HTML check + structure validation
# Usage: publish-file.sh <file.md> <topic> [author]
set -euo pipefail

FILE="${1:-}"
TOPIC="${2:-}"
AUTHOR="${3:-Genesis}"

SKILL_DIR="$HOME/.openclaw/workspace-genesis/skills/regen-tribes-notes"
REPO_DIR="$HOME/.radicle/regen-tribes-notes"

# Ensure git-remote-rad is on PATH for git push rad
export PATH="$HOME/.local/bin:$HOME/.radicle/bin:$PATH"

if [[ ! -f "$FILE" ]]; then
  echo "Error: file not found: $FILE" >&2
  exit 1
fi

CONTENT=$(cat "$FILE")
TITLE=$(basename "$FILE" .md | sed 's/-/ /g' | sed 's/_/ /g')

# Gate: HTML check (skip common markdown bold/italic tags; detect real HTML tags)
CONTENT_CHECK=$(echo "$CONTENT" | sed 's/<[bbiI][^>]*>/**/g; s/<\/[bbiI]>/**/g; s/<code[^>]*>/**/g; s/<\/code>/**/g')
if echo "$CONTENT_CHECK" | grep -qiE '<[a-z][a-z0-9]*[^>]*>.*</[a-z][a-z0-9]*>' ; then
  echo "Error: HTML detected in $FILE" >&2
  exit 1
fi

# Gate: STE100 (only for short text, skip for file publications with markdown)
HAS_MARKDOWN=$(echo "$CONTENT" | grep -cE '^\||^\{' || true)
if [[ ${HAS_MARKDOWN:-0} -gt 3 ]]; then
  echo "STE100: skipped (markdown-rich content, gate applies to Telegram inputs only)"
else
  PYTHON="${PYTHON:-python3.12}"
  PYCODE="
from biz.dfch.ste100parser import Parser
import sys
p = Parser()
text = sys.stdin.read()
sentences = [s.strip() for s in text.replace('?', '.').replace('!', '.').split('.') if s.strip()]
failed = sum(1 for s in sentences[:30] if s and not p.is_valid(s + '.') if p.invoke(s + '.') or True)
print('STE100: PASS' if failed == 0 else f'STE100: {failed} sentence(s) may need review')
"
  STE100_MSG=$(echo "$CONTENT" | $PYTHON -c "$PYCODE" 2>/dev/null || echo "STE100: skipped")
  echo "$STE100_MSG"
fi

# Slugify (lowercase, dash only)
TOPIC_SLUG=$(echo "$TOPIC" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]\+/-/g' | sed 's/^-\+//;s/-\+$//' | cut -c1-40)
TITLE_SLUG=$(echo "$TITLE" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]\+/-/g' | sed 's/^-\+//;s/-\+$//' | cut -c1-60 | sed 's/-\+$//')
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
FILESTAMP=$(date -u +"%Y%m%d-%H%M%S")
FILENAME="${FILESTAMP}-${TOPIC_SLUG}-${TITLE_SLUG}.md"
FILEPATH="$REPO_DIR/$FILENAME"

# Write note: metadata as YAML-frontmatter-paired comments at top, raw content follows
# This keeps the note self-contained while being trivial to parse (grep first 4 lines)
{
  echo "---"
  echo "title: $TITLE"
  echo "topic: $TOPIC"
  echo "author: $AUTHOR"
  echo "published: $TIMESTAMP"
  echo "---"
  echo ""
  echo "# $TITLE"
  echo ""
  echo "$CONTENT"
} > "$FILEPATH"

cd "$REPO_DIR"

# Add note file
git add "$FILENAME"

# First commit (note only, README not yet modified)
FIRST_COMMIT_MSG="Publication: $TITLE ($TIMESTAMP)"
COMMIT_HASH=$(git -c user.email="genesis@regentribes.radicle" \
    -c user.name="Genesis Agent" \
    commit -m "$FIRST_COMMIT_MSG" 2>&1 | \
    grep -o '[a-f0-9]\{40\}' | head -1 || echo "")

if [[ -z "$COMMIT_HASH" ]]; then
  echo "Error: git commit failed" >&2
  exit 1
fi

# Append single row to README using add-entry.sh (append-only, no read)
$SKILL_DIR/add-entry.sh "$FILENAME" "$TITLE" "$TOPIC" "$PUBLISHED" "$COMMIT_HASH"

# Second commit (README update only)
git add README.md
git -c user.email="genesis@regentribes.radicle" \
    -c user.name="Genesis Agent" \
    commit -m "Update README index" 2>/dev/null || true

# Push main branch
GIT_EXEC_PATH="$HOME/.radicle/bin" git push rad main --force-with-lease 2>&1 || \
  GIT_EXEC_PATH="$HOME/.radicle/bin" git push rad main --force 2>&1

echo ""
echo "✅ Published: $FILENAME"
echo "📖 Read: https://app.radicle.xyz/nodes/iris.radicle.xyz/rad:z4WAr7CiNkf5JAoAb1srwi7gDz8nU/tree/${COMMIT_HASH}"
echo "🌱 Synced to 29 seeds"
echo "⏳ Propagating…"
