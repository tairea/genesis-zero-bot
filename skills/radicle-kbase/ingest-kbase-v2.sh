#!/bin/bash
# ingest-kbase-v2.sh — Clean ingest for RegenTribes Knowledge Base
# Rules: MD only, no HTML, no TXT, no external-project noise,
# keep tech stack (surreal-skills, semantic-graph, mythogen, aisystant),
# keep Vic's AME-PC docs, keep research, proper Title Case filenames
set -euo pipefail

WORKSPACE="$HOME/.openclaw/workspace-genesis"
KBASE="$HOME/.radicle/kbase-v2"
INDEX_FILE="$KBASE/README.md"

to_title_case() {
  # Take snake_case or SCREAMING_SNAKE, convert to Title Case
  # Input: "MASTER_SYNTHESIS" or "master-synthesis"
  # Output: "Master Synthesis"
  echo "$1" | tr '_-' '  ' | tr '[:upper:]' '[:lower:]' | while read -r word; do
    first=$(echo "$word" | cut -c1 | tr '[:lower:]' '[:upper:]')
    rest=$(echo "$word" | cut -c2-)
    printf '%s%s' "$first" "$rest"
  done | sed 's/ *$//'
}

# ── 1. collect source .md files ─────────────────────────────────────────────
mapfile -t FILES < <(
  cd "$WORKSPACE"
  find . \
    -name '*.md' \
    -type f \
    -not -path '*/node_modules/*' \
    -not -path '*/.git/*' \
    -not -path '*/.venv/*' \
    -not -path '*/cloned/*' \
    -not -path '*/dumps/*' \
    -not -path '*/.ralph/*' \
    -not -path '*/skills/aisystant-fpf/references/*' \
    -not -path '*/skills/semantic-graph/.venv/*' \
    -not -path '*/skills/telegram_bigspace/*' \
    -not -path '*/regen-app-stack/*' \
    -not -path '*/big_space/*' \
    -not -path '*/3d-force-graph/*' \
    -not -path '*/.openclaw/workspace/*' \
    -not -path './AGENTS.md' \
    -not -path './BOOTSTRAP.md' \
    -not -path './HEARTBEAT.md' \
    -not -path './IDENTITY.md' \
    -not -path './MEMORY.md' \
    -not -path './USER.md' \
    -not -path './TOOLS.md' \
    -not -path './SOUL.md' \
    -not -path './README.md' \
    -not -path './SPEC.md' \
    -not -path './SPEC-chain-stories-update.md' \
    -not -path './KNOWLEDGE-GRAPH-EVALUATION.md' \
    -not -path './closed-loop-life-support.md' \
    -not -path './tmp/spawn_task*' \
    -not -path './tmp/rgem-light-spec.md' \
    -not -path './tmp/vitali-ian-thread-summary.md' \
    -not -path './archive/skills-2026-03-05/*' \
    -not -path './archive/02-hardware/*' \
    -not -path './archive/03-humanware/*' \
    -not -path './archive/05-technology/*' \
    -not -path './archive/README.md' \
    -not -path './deepwiki_exports/*' \
    -not -path './digital-twin-fragments/*' \
    -not -path './system-prompts/*' \
    -not -path './skills/space-js/*' \
    -not -path './skills/alien-js-dev/*' \
    -not -path './skills/fragment-engine/*' \
    -not -path './skills/llm-pareto-analyzer/*' \
    -not -path './skills/regen-viz/*' \
    -not -path './skills/rust-skill/*' \
    -not -path './skills/ralph-runner/*' \
    -not -path './skills/telegram-export-analyzer/*' \
    -not -path './skills/telegram-history/*' \
    -not -path './skills/telegram/references/*' \
    -not -path './skills/tetra-format/*' \
    -not -path './skills/web-search/*' \
    -not -path './skills/transcribe/*' \
    -not -path './skills/video-transcript-downloader/*' \
    -not -path './skills/deep-research-pro/*' \
    -not -path './skills/deepwiki-repo-analyzer/*' \
    -not -path './skills/gog/*' \
    -not -path './skills/find-skills/*' \
    -not -path './skills/skill-creator/*' \
    -not -path './skills/summarize/*' \
    -not -path './skills/regen-cas/*' \
    -not -path './skills/knowledge-extraction/meaning-capsule/*' \
    -not -path './skills/kreuzberg/references/*' \
    -not -path './skills/surreal-skills/.github/*' \
    -not -path './skills/surreal-skills/skills/*' \
    -not -path './skills/surreal-skills/rules/*' \
    -not -path './skills/surreal-skills/references/online_docs.md' \
    -not -path './skills/surreal-skills/README.md' \
    -not -path './skills/surreal-skills/AGENTS.md' \
    -not -path './skills/surreal-skills/CHANGELOG.md' \
    -not -path './skills/surreal-skills/CONTRIBUTING.md' \
    -not -path './skills/surreal-skills/SECURITY.md' \
    -not -path './skills/surreal-skills/README.md' \
    -not -path './regen-viz/*' \
    -not -path './skills/regen-vision/references/sources/*' \
    | sort
)

[[ ${#FILES[@]} -eq 0 ]] && echo "No files found" && exit 0
echo "Found ${#FILES[@]} source files"

# ── 2. clean previous run ───────────────────────────────────────────────────
rm -rf "$KBASE"
mkdir -p "$KBASE"

# ── 3. process each file ─────────────────────────────────────────────────────
declare -A SEEN_BASE
INDEX_ENTRIES=()
COUNT=0

for src in "${FILES[@]}"; do
  src="${src#./}"
  
  IFS='/' read -ra parts <<< "$src"
  
  # ── derive category ──
  case "${parts[0]}" in
    docs)            category="doc" ;;
    memory)          category="mem" ;;
    projects)        category="prj" ;;
    skills)          category="skl" ;;
    research)        category="rsr" ;;
    prompts)         category="prm" ;;
    transcripts)     category="trn" ;;
    regen-neighborhood-framework) category="rnf" ;;
    telegram-syntheses) category="syn" ;;
    ame-pc-export)   category="ame" ;;
    *)               category="mis" ;;
  esac
  
  # ── make title from filename ──
  basename="${parts[-1]}"
  name_no_ext="${basename%.*}"
  
  # Title Case via python for reliability
  title=$(python3 -c "
import sys
s = '$name_no_ext'.replace('-', ' ').replace('_', ' ')
words = s.split()
result = []
for i, w in enumerate(words):
    if w.lower() in ('a','an','and','as','at','by','for','in','of','on','or','the','to','is','it','i'):
        if i == 0:
            result.append(w.capitalize())
        else:
            result.append(w.lower())
    else:
        result.append(w.capitalize())
print(' '.join(result))
" 2>/dev/null)
  
  [[ -z "$title" ]] && title="$name_no_ext"
  [[ ${#title} -gt 60 ]] && title="${title:0:57}..."
  
  # ── slugify ──
  slug=$(echo "$name_no_ext" | sed \
    -e 's/[^a-zA-Z0-9_-]/-/g' \
    -e 's/----*/-/g' \
    -e 's/^-//' -e 's/-$//' \
    | tr '[:upper:]' '[:lower:]')
  
  # ── disambiguate collisions ──
  key="$slug"
  if [[ -n "${SEEN_BASE[$key]:-}" ]]; then
    path_hash=$(printf '%s' "$src" | md5sum | cut -c1-4)
    slug="${slug}-${path_hash}"
  fi
  SEEN_BASE[$key]=1
  
  # ── final filename ──
  dest_filename="${category}-${slug}.md"
  dest="$KBASE/$dest_filename"
  
  # ── write with metadata header ──
  {
    printf '<!--\n'
    printf '  source: %s\n' "$src"
    printf '  category: %s\n' "$category"
    printf '  title: %s\n' "$title"
    printf '  ingested: %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    printf '-->\n'
    printf '\n'
    cat "$WORKSPACE/$src"
  } > "$dest"
  
  # ── index entry ──
  description=$(sed -n '/^<!--/d; /./{p; q}' "$WORKSPACE/$src" 2>/dev/null | \
    cut -c1-100 | sed 's/^[ ]*//; s/[ ]*$//')
  [[ -z "$description" ]] && description="(no description)"
  
  INDEX_ENTRIES+=("| \`$dest_filename\` | $category | $description | $src |")
  
  COUNT=$((COUNT + 1))
done

echo "Ingested $COUNT files"

# ── 4. write README.md ──────────────────────────────────────────────────────
{
  cat << 'HEADER'
# RegenTribes Knowledge Base

**Genesis bot · Distributed · Radicle RID:** `rad:z2GNG6Nt3c7NWPge18xTRKZkkxSTy`  
**URL:** https://app.radicle.xyz/nodes/iris.radicle.xyz/rad:z2GNG6Nt3c7NWPge18xTRKZkkxSTy

Flat-structure knowledge base. All files renamed to `category-slug.md` with metadata headers.
Auto-generated — do not edit manually.

---

## Category Key

| Prefix | Source | Description |
|--------|--------|-------------|
| `doc` | `docs/` | Community specs, GDDs, playbooks |
| `mem` | `memory/` | Daily logs, conversations, philosophy |
| `prj` | `projects/` | Project charters, plans, frameworks |
| `skl` | `skills/` | Agent skills, technical references |
| `syn` | `telegram-syntheses/` | Research synthesis reports |
| `rsr` | `research/` | Themed research deep-dives |
| `prm` | `prompts/` | Research and system prompts |
| `trn` | `transcripts/` | Transcript analysis |
| `rnf` | `regen-neighborhood-framework/` | Community alchemy RNF |
| `ame` | `ame-pc-export/` | Vic's AME-PC documentation |
| `mis` | other | Miscellaneous community docs |

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

# ── 5. git init and commit ─────────────────────────────────────────────────────
cd "$KBASE"
git init -b main
git config user.email "genesis@regentribe"
git config user.name "Genesis Bot"
git add -A
git commit -m "$(date -u +'Initial clean ingest %Y-%m-%dT%H:%M:%SZ')"
echo ""
echo "Commit complete: $KBASE"
git log --oneline
echo ""
echo "File count per category:"
ls *.md | sed 's/-.*//' | sort | uniq -c | sort -rn
