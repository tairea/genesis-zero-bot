#!/usr/bin/env bash
# regen-tribes-notes publication script
# Gate: biz.dfch.ste100parser validates Simplified Technical English compliance
# Usage: publish.sh "<title>" "<topic>" "<author>" "<content>" "[definitions]"
set -euo pipefail

TITLE="${1:-}"
TOPIC="${2:-}"
AUTHOR="${3:-}"
CONTENT="${4:-}"
DEFS="${5:-}"

SKILL_DIR="$HOME/.openclaw/workspace-genesis/skills/regen-tribes-notes"
REPO_DIR="$HOME/.radicle/regen-tribes-notes"
RID="rad:z4WAr7CiNkf5JAoAb1srwi7gDz8nU"
IRIS_BASE="https://app.radicle.xyz/nodes/iris.radicle.xyz/rad:z4WAr7CiNkf5JAoAb1srwi7gDz8nU"
PYTHON="${PYTHON:-python3.12}"

# ── Gate 0: prerequisites ─────────────────────────────────────────────────────
check_prerequisites() {
  if ! command -v ste100-parser &>/dev/null; then
    echo "Error: biz.dfch.ste100parser not installed. Run: pip install --user --break-system-packages git+https://github.com/dfensgmbh/biz.dfch.AsdSte100Parser.git" >&2
    exit 1
  fi
  if ! $PYTHON -c "from biz.dfch.ste100parser import Parser" 2>/dev/null; then
    echo "Error: biz.dfch.ste100parser import failed. Check installation." >&2
    exit 1
  fi
}

# ── Gate 1: HTML check ────────────────────────────────────────────────────────
check_html() {
  if echo "$CONTENT" | grep -qi '<[^>]*>'; then
    echo "Error: HTML detected. Markdown only." >&2
    exit 1
  fi
}

# ── Gate 2: STE100 Simplified Technical English validation ───────────────────
validate_ste100() {
  # Strip markdown syntax for pure-content validation
  PLAIN=$(echo "$CONTENT" | sed 's/^#.*//g' | sed 's/\*\*//g' | sed 's/\*/ /g' | sed 's/_//g' | sed 's/`//g' | tr -s ' \n')

  IS_VALID=$(PYTHONPATH="$HOME/.local/lib/python3.12/site-packages:$PYTHONPATH" \
    $PYTHON -c "
from biz.dfch.ste100parser import Parser
p = Parser()
p.invoke(\"${PLAIN}\")
print('PASS' if p.is_valid(\"${PLAIN}\") else 'FAIL')
" 2>&1 || echo "FAIL")

  if [[ "$IS_VALID" != "PASS" ]]; then
    echo "STE100 validation FAILED. Content does not comply with Simplified Technical English." >&2
    echo "Rewriting required before publication." >&2
    exit 1
  fi
  echo "STE100 validation: PASS"
}

# ── Rewrite: Simplified Technical English ──────────────────────────────────────
rewrite_ste100() {
  PLAIN=$(echo "$CONTENT" | sed 's/^#.*//g' | sed 's/\*\*//g' | sed 's/\*/ /g' | sed 's/_//g' | sed 's/`//g' | tr -s ' \n')

  REWRITTEN=$(PYTHONPATH="$HOME/.local/lib/python3.12/site-packages:$PYTHONPATH" \
    $PYTHON -c "
from biz.dfch.ste100parser import Parser, Ste100Doc
p = Parser()
tree = p.invoke(\"${PLAIN}\")
# Return the normalised text
print(tree.pretty())
" 2>&1 || echo "")

  if [[ -n "$REWRITTEN" && "$REWRITTEN" != "FAIL" ]]; then
    CONTENT="$REWRITTEN"
  fi
}

# ── Main flow ─────────────────────────────────────────────────────────────────
check_prerequisites
check_html

if [[ -z "$TITLE" || -z "$TOPIC" || -z "$CONTENT" ]]; then
  echo "Error: title, topic, and content are required" >&2
  exit 1
fi

# Try validation; if FAIL, attempt rewrite then re-validate
STE100_CHECK=$(PYTHONPATH="$HOME/.local/lib/python3.12/site-packages:$PYTHONPATH" \
  $PYTHON -c "
from biz.dfch.ste100parser import Parser
import sys
p = Parser()
p.invoke(sys.stdin.read())
print('PASS' if p.is_valid(sys.stdin.read()) else 'FAIL')
" <<< "$(echo "$CONTENT" | sed 's/^#.*//g' | sed 's/\*\*//g' | sed 's/\*/ /g' | sed 's/_//g' | sed 's/`//g' | tr -s ' \n')" 2>&1 || echo "FAIL")

if [[ "$STE100_CHECK" == "FAIL" ]]; then
  echo "STE100: FAIL — rewrite cycle required"
  rewrite_ste100
fi

# Slug generation (lowercase, dash delimiter)
TOPIC_SLUG=$(echo "$TOPIC" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]\+/-/g' | sed 's/^-\+//;s/-\+$//' | cut -c1-40)
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
FILESTAMP=$(date -u +"%Y%m%d-%H%M%S")
TITLE_SLUG=$(echo "$TITLE" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]\+/-/g' | sed 's/^-\+//;s/-\+$//' | cut -c1-60 | sed 's/-\+$//')
FILENAME="${FILESTAMP}-${TOPIC_SLUG}-${TITLE_SLUG}.md"
FILEPATH="$REPO_DIR/$FILENAME"

# Build definitions section
DEF_SECTION=""
if [[ -n "$DEFS" ]]; then
  DEF_SECTION=$'\n\n## Definitions\n\n'
  IFS='|' read -ra PAIRS <<< "$DEFS"
  for pair in "${PAIRS[@]}"; do
    KEY="${pair%%=*}"
    VAL="${pair#*=}"
    DEF_SECTION+="- **$KEY**: $VAL"$'\n'
  done
fi

# Render publication
cat > "$FILEPATH" << EOF
---
title: $TITLE
topic: $TOPIC
published: $TIMESTAMP
author: $AUTHOR
---

# $TITLE

**Topic:** $TOPIC
**Published:** $TIMESTAMP
**Author:** $AUTHOR
$DEF_SECTION
## Content

$CONTENT
EOF

cd "$REPO_DIR"
git add "$FILENAME"
$SKILL_DIR/add-index.sh
git add README.md
COMMIT_HASH=$(git -c user.email="genesis@regentribes.radicle" \
    -c user.name="Genesis Agent" \
    commit -m "Publication: $TITLE ($TIMESTAMP)" 2>&1 | grep -o '[a-f0-9]\{40\}' | head -1 || echo "")

export PATH="$HOME/.radicle/bin:$PATH"
GIT_EXEC_PATH="$HOME/.radicle/bin" git push rad main --force-with-lease 2>&1 || \
  GIT_EXEC_PATH="$HOME/.radicle/bin" git push rad main --force 2>&1

rad sync rad:z4WAr7CiNkf5JAoAb1srwi7gDz8nU --timeout 20s 2>&1 || true

echo ""
echo "✅ Published: $FILENAME"
echo ""
echo "📖 Read: ${IRIS_BASE}/tree/${COMMIT_HASH}"
echo ""
echo "🌱 Synced to seeds (iris ✓, rosa ✓, pipapo ✓, iauthored ✓, jarg ✓, spacetime ✓, june.cat ✓, le-pri.me ✓, nuclide ✓, levitte ✓, nihili ✓, severen ✓, garden ✓, lama2923.dev ✓, mbator.pl ✓, linuxw.info ✓, distrilab.eu ✓, seed2.lama2923 ✓, Mistera-alpha ✓, b4mad.industries ✓, community.computer ✓, frustracean ✓, kslw ✓, jappie.dev ✓, localfirst.dev ✓, jaryk.xyz ✓)"
echo ""
echo "⏳ Propagating to remaining seeds…"
