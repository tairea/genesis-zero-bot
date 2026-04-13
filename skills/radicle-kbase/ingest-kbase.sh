#!/bin/bash
# ingest-kbase.sh — Copy all genesis-authored .md files into the kbase rad repo
# with flat structure, consistent naming, and auto-generated INDEX.md
set -euo pipefail

WORKSPACE="$HOME/.openclaw/workspace-genesis"
KBASE="$HOME/.radicle/kbase"
INDEX_FILE="$KBASE/README.md"

# ── 1. collect source files ──────────────────────────────────────────────────
# Exclude: cloned repos (reference material), node_modules, venv, .git, archive dumps
mapfile -t FILES < <(
  cd "$WORKSPACE"
  find . \
    \( -name '*.md' -o -name '*.txt' -o -name '*.html' \) \
    -type f \
    -not -path '*/cloned/*' \
    -not -path '*/node_modules/*' \
    -not -path '*/.venv/*' \
    -not -path '*/.git/*' \
    -not -path '*/archive/skills-2026-03-05/*' \
    -not -path '*/skills/aisystant-fpf/references/*' \
    -not -path '*/skills/semantic-graph/.venv/*' \
    -not -path '*/skills/video-transcript-downloader/node_modules/*' \
    -not -path '*/skills/surreal-skills/node_modules/*' \
    -not -path '*/skills/telegram_bigspace/node_modules/*' \
    -not -path '*/dumps/*' \
    -not -path '*/telegram_bigspace/*' \
    -not -path '*/big_space/node_modules/*' \
    -not -path '*/skills/aisystant-fpf/references/*' \
    -not -path '*/.ralph/*' \
    -not -path '*/skills/semantic-graph/.venv/*' \
    -not -path '*/3d-force-graph/*' \
    -not -path '*/big_space/node_modules/*' \
    -not -path '*/regen-app-stack/pwa-starter/node_modules/*' \
    -not -path '*/regen-app-stack/matrix-homeserver/node_modules/*' \
    | sort
)

[[ ${#FILES[@]} -eq 0 ]] && echo "No files found" && exit 0

echo "Found ${#FILES[@]} files to process"

# ── 2. clean previous run ───────────────────────────────────────────────────
rm -f "$KBASE"/*.md "$KBASE"/*.txt "$KBASE"/*.html "$KBASE/README.md"
rm -f "$KBASE/.meta"

# ── 3. process each file ───────────────────────────────────────────────────
declare -A SEEN_BASE
INDEX_ENTRIES=()
COUNT=0

for src in "${FILES[@]}"; do
  src="${src#./}"
  
  IFS='/' read -ra parts <<< "$src"
  
  # ── derive category from path ──
  case "${parts[0]}" in
    docs)         category="doc" ;;
    memory)       category="mem" ;;
    projects)     category="prj" ;;
    skills)       category="skl" ;;
    research)     category="rsr" ;;
    prompts)      category="prm" ;;
    transcripts)  category="trn" ;;
    dumps)        category="dmp" ;;
    regen-neighborhood-framework) category="rnf" ;;
    regen-app-stack) category="app" ;;
    telegram-syntheses) category="syn" ;;
    *)            category="mis" ;;
  esac
  
  # ── base name (last segment, stripped extension) ──
  basename="${parts[-1]}"
  name_no_ext="${basename%.*}"
  
  # ── slugify: lowercase, spaces/hyphens to dashes, strip odd chars ──
  slug=$(echo "$name_no_ext" | sed \
    -e 's/[^a-zA-Z0-9_-]/-/g' \
    -e 's/----*/-/g' \
    -e 's/^-//' -e 's/-$//' \
    | tr '[:upper:]' '[:lower:]')
  
  # ── disambiguate: if same slug seen, append short path-hash ──
  key="$slug"
  hash_suffix=""
  if [[ -n "${SEEN_BASE[$key]:-}" ]]; then
    path_hash=$(printf '%s' "$src" | md5sum | cut -c1-4)
    hash_suffix="-$path_hash"
    slug="$slug$hash_suffix"
  fi
  SEEN_BASE[$key]=1
  
  # ── final filename ──
  ext="${basename##*.}"
  dest_filename="${category}-${slug}.${ext}"
  dest="$KBASE/$dest_filename"
  
  # ── copy with metadata comment header ──
  {
    echo "<!--"
    echo "  source: $src"
    echo "  category: $category"
    echo "  ingested: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "-->"
    echo ""
    cat "$WORKSPACE/$src"
  } > "$dest"
  
  # ── generate index entry ──
  description=$(sed -n '/^<!--/d; /./{p; q}' "$WORKSPACE/$src" 2>/dev/null | \
    cut -c1-120 | sed 's/^[ ]*//; s/[ ]*$//')
  [[ -z "$description" ]] && description="(no description)"
  
  INDEX_ENTRIES+=("| \`$dest_filename\` | $category | $description | $src |")
  
  COUNT=$((COUNT + 1))
done

echo "Copied $COUNT files"

# ── 4. write INDEX.md (README.md) ───────────────────────────────────────────
{
  cat << 'HEADER'
# RegenTribes Knowledge Base

**Genesis bot · Distributed · Radicle RID:** `rad:z2GNG6Nt3c7NWPge18xTRKZkkxSTy`

Auto-generated index of all `.md` / `.txt` / `.html` files produced by the Genesis agent,
organized in a flat structure with consistent naming.

---

## Index

| File | Category | Description | Source |
|------|----------|-------------|--------|
HEADER
  printf '%s\n' "${INDEX_ENTRIES[@]}"
  echo ""
  echo "---"
  echo "*Generated $(date -u +%Y-%m-%dT%H:%M:%SZ) · Do not edit manually*"
} > "$INDEX_FILE"

echo "Index written: $INDEX_FILE ($COUNT entries)"

# ── 5. stage in git ───────────────────────────────────────────────────────────
cd "$KBASE"
echo "Staged files:"
git add *.md *.txt *.html README.md 2>/dev/null || true
git status --short | head -30

echo ""
echo "Done. Commit with: cd $KBASE && git commit -m 'ingest $(date -u +%Y-%m-%d)'"
