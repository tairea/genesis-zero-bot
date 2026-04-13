#!/usr/bin/env python3
"""
ingest-kbase-v2.py
Clean ingest for RegenTribes Knowledge Base v2.

Rules:
- .md files only (no .html, no .txt)
- No external project noise
- Keep tech stack (surreal-skills, semantic-graph, mythogen, aisystant core skills)
- Keep research, prompts, telegram-syntheses
- Keep Vic's AME-PC docs
- Proper Title Case titles in metadata
- Flat structure: category-slug.md
"""
import os
import re
import subprocess
import hashlib
import shutil
from pathlib import Path

WORKSPACE = Path.home() / ".openclaw" / "workspace-genesis"
KBASE = Path.home() / ".radicle" / "kbase-v2"
INDEX_FILE = KBASE / "README.md"

# ── exclusions (prefix-based) ──────────────────────────────────────────────────
EXCLUDE_PREFIXES = [
    # External/archived projects (not genesis-authored)
    "archive/",
    "big_space/",
    "cloned/",
    "dumps/",
    "digital-twin-fragments/",
    "system-prompts/",
    "regen-app-stack/",
    "3d-force-graph/",
    ".ralph/",
    "telegram_bigspace/",
    ".openclaw/",
    "deepwiki_exports/",
    "RNF_Complete_Framework_Structure.md",
    # Config / identity / personal (root level)
    "AGENTS.md",
    "BOOTSTRAP.md",
    "HEARTBEAT.md",
    "IDENTITY.md",
    "MEMORY.md",
    "USER.md",
    "TOOLS.md",
    "SOUL.md",
    "README.md",
    "SPEC.md",
    "SPEC-chain-stories-update.md",
    "KNOWLEDGE-GRAPH-EVALUATION.md",
    "closed-loop-life-support.md",
    # Task artifacts
    "tmp/spawn_task",
    "tmp/rgem-light-spec.md",
    "tmp/vitali-ian-thread-summary.md",
    # Noise skills
    "skills/aisystant-fpf/references/",
    "skills/semantic-graph/.venv/",
    "skills/semantic-graph/.venv/",
    "skills/telegram_bigspace/",
    "skills/surreal-skills/.github/",
    "skills/surreal-skills/skills/",
    "skills/surreal-skills/rules/",
    "skills/surreal-skills/references/",
    "skills/regen-vision/references/sources/",
    "regen-viz/",
    "skills/space-js/",
    "skills/alien-js-dev/",
    "skills/fragment-engine/",
    "skills/llm-pareto-analyzer/",
    "skills/regen-viz/",
    "skills/rust-skill/",
    "skills/ralph-runner/",
    "skills/telegram-export-analyzer/",
    "skills/telegram-history/",
    "skills/telegram/references/",
    "skills/tetra-format/",
    "skills/web-search/",
    "skills/transcribe/",
    "skills/video-transcript-downloader/",
    "skills/deep-research-pro/",
    "skills/deepwiki-repo-analyzer/",
    "skills/gog/",
    "skills/find-skills/",
    "skills/skill-creator/",
    "skills/summarize/",
    "skills/regen-cas/",
    "skills/knowledge-extraction/meaning-capsule/",
    "skills/kreuzberg/references/",
    "skills/surreal-skills/README.md",
    "skills/surreal-skills/AGENTS.md",
    "skills/surreal-skills/CHANGELOG.md",
    "skills/surreal-skills/CONTRIBUTING.md",
    "skills/surreal-skills/SECURITY.md",
    "skills/surreal-skills/references/online_docs.md",
    "archive/skills-2026-03-05/",
]

# ── category mapping ─────────────────────────────────────────────────────────────
CATEGORY_MAP = {
    "docs":                         "doc",
    "memory":                       "mem",
    "projects":                     "prj",
    "skills":                       "skl",
    "research":                     "rsr",
    "prompts":                      "prm",
    "transcripts":                  "trn",
    "regen-neighborhood-framework": "rnf",
    "telegram-syntheses":            "syn",
    "ame-pc-export":                 "ame",
}

# ── helpers ─────────────────────────────────────────────────────────────────────
def is_excluded(path_str: str) -> bool:
    """Check if any exclusion prefix matches the beginning of the path."""
    path_str = path_str.replace("\\", "/")
    for prefix in EXCLUDE_PREFIXES:
        if path_str.startswith(prefix):
            return True
        # Also check for / delimited match at any path segment boundary
        if "/" + prefix in path_str or prefix + "/" in path_str:
            return True
    return False

def to_title_case(name: str) -> str:
    """Convert SNAKE_CASE or snake-case to Title Case."""
    words = re.split(r'[-_]+', name)
    small_words = {
        'a','an','and','as','at','by','for','in',
        'of','on','or','the','to','is','it','i',''
    }
    result = []
    for i, w in enumerate(words):
        wl = w.lower()
        if wl in small_words and i > 0:
            result.append(wl)
        else:
            result.append(wl.capitalize())
    return ' '.join(result).strip()

def slugify(name: str) -> str:
    """Slugify: lowercase, non-alnum to dash, collapse dashes, trim."""
    s = name.lower()
    s = re.sub(r'[^a-z0-9_-]', '-', s)
    s = re.sub(r'-+', '-', s)
    return s.strip('-')

def get_description(content: str) -> str:
    """First non-empty, non-comment line, truncated to 100 chars."""
    for line in content.splitlines():
        line = line.strip()
        if line and not line.startswith('<!--') and not line.startswith('*'):
            return line[:100].strip()
    return "(no description)"

def md5_path(path_str: str) -> str:
    return hashlib.md5(path_str.encode()).hexdigest()[:4]

# ── collect files ───────────────────────────────────────────────────────────────
files = []
workspace = WORKSPACE.resolve()
for path in workspace.rglob("*.md"):
    rel = path.relative_to(workspace)
    rel_str = str(rel).replace('\\', '/')
    if is_excluded(rel_str):
        continue
    files.append(rel_str)

files.sort()
print(f"Found {len(files)} source files")

# ── clean and ingest ────────────────────────────────────────────────────────────
if KBASE.exists():
    shutil.rmtree(KBASE)
KBASE.mkdir(parents=True, exist_ok=True)

SEEN = {}
INDEX = []
COUNT = 0
SKIPPED = 0

for rel_str in files:
    parts = rel_str.split('/')
    
    # category
    top = parts[0]
    category = CATEGORY_MAP.get(top, "mis")
    
    # basename
    basename = parts[-1]
    name_no_ext = Path(basename).stem
    
    # title case
    title = to_title_case(name_no_ext)
    if len(title) > 60:
        title = title[:57] + "..."
    
    # slug + disambiguate
    slug_raw = slugify(name_no_ext)
    slug = slug_raw
    if slug_raw in SEEN:
        slug = f"{slug_raw}-{md5_path(rel_str)}"
    SEEN[slug_raw] = True
    
    # destination
    dest_name = f"{category}-{slug}.md"
    dest_path = KBASE / dest_name
    src_path = WORKSPACE / rel_str
    
    if not src_path.exists():
        print(f"SKIP (not found): {src_path}")
        SKIPPED += 1
        continue
    
    content = src_path.read_text(encoding='utf-8', errors='replace')
    
    # write with metadata header
    now = subprocess.run(
        ['date', '-u', '+%Y-%m-%dT%H:%M:%SZ'],
        capture_output=True, text=True
    ).stdout.strip()
    
    header = (
        f"<!--\n"
        f"  source: {rel_str}\n"
        f"  category: {category}\n"
        f"  title: {title}\n"
        f"  ingested: {now}\n"
        f"-->\n"
    )
    dest_path.write_text(header + "\n" + content, encoding='utf-8')
    
    # description for index
    description = get_description(content)
    INDEX.append(f"| `{dest_name}` | {category} | {description} | {rel_str} |")
    COUNT += 1

print(f"Ingested {COUNT} files" + (f" ({SKIPPED} skipped)" if SKIPPED else ""))

# ── write README.md ────────────────────────────────────────────────────────────
now = subprocess.run(
    ['date', '-u', '+%Y-%m-%dT%H:%M:%SZ'],
    capture_output=True, text=True
).stdout.strip()

readme = f"""# RegenTribes Knowledge Base

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
"""
readme += "\n".join(INDEX)
readme += f"\n\n---\n*Generated {now} · Do not edit manually*\n"

INDEX_FILE.write_text(readme, encoding='utf-8')
print(f"Index written: {INDEX_FILE} ({COUNT} entries)")

# ── git init and commit ─────────────────────────────────────────────────────────
os.chdir(KBASE)
subprocess.run(["git", "init", "-b", "main"], check=True, capture_output=True)
subprocess.run(["git", "config", "user.email", "genesis@regentribe"], check=True, capture_output=True)
subprocess.run(["git", "config", "user.name", "Genesis Bot"], check=True, capture_output=True)
subprocess.run(["git", "add", "-A"], check=True, capture_output=True)
subprocess.run(["git", "commit", "-m", f"Initial clean ingest {now}"], check=True, capture_output=True)

result = subprocess.run(["git", "log", "--oneline"], capture_output=True, text=True)
print(f"\nCommit: {result.stdout.strip()}")

result = subprocess.run(["ls", "*.md"], capture_output=True, text=True, shell=True)
counts = {}
for line in result.stdout.splitlines():
    if line == "README.md":
        continue
    prefix = line.split('-')[0]
    counts[prefix] = counts.get(prefix, 0) + 1

print("\nFile count per category:")
for k, v in sorted(counts.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")
total = sum(counts.values())
print(f"  TOTAL: {total}")
