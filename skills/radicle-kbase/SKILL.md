---
name: radicle-kbase
description: Ingest, maintain, and sync Genesis's document knowledge base to Radicle (rad:z2GNG6Nt3c7NWPge18xTRKZkkxSTy). Use when: (1) syncing new workspace documents to the kbase, (2) committing Incremental updates, (3) pushing to Radicle network. Requires rad CLI, node running.
---

# Radicle Knowledge Base Skill

**RID:** `rad:z2GNG6Nt3c7NWPge18xTRKZkkxSTy`
**Name:** regen-tribes-kbase
**URL:** https://app.radicle.xyz/nodes/iris.radicle.xyz/rad:z2GNG6Nt3c7NWPge18xTRKZkkxSTy
**Repo:** `$HOME/.radicle/kbase`
**Workspace:** `$HOME/.openclaw/workspace-genesis`

## Overview

The kbase is a **flat-structure Radicle repo** containing every `.md` / `.txt` / `.html` file produced by the Genesis agent, renamed into a consistent `category-slug.ext` format with a single `README.md` serving as the living index.

- 626 files ingested on initial setup
- Radicle handles p2p replication — no GitHub/GitLab dependency
- The `ingest-kbase.sh` script automates incremental ingestion

---

## Prerequisites

- Radicle CLI: `$HOME/.radicle/bin/rad` (already installed)
- Radicle node running: `rad node status` shows `✓ Node is running`
- SSH agent has the radicle key: `ssh-add ~/.radicle/keys/radicle`

---

## Day-to-Day Workflow

### 1. Run ingest (sync workspace → kbase)

```bash
bash ~/.openclaw/workspace-genesis/skills/radicle-kbase/ingest-kbase.sh
```

This will:
- Scan `$WORKSPACE` for new/changed `.md`, `.txt`, `.html` files
- Copy them to `$KBASE` with `category-slug` rename
- Append new entries to `README.md` (index is auto-generated)
- `git add -A` all changes
- Print staged files

**Dry-run first** — review the staged files before committing:
```bash
bash ~/.openclaw/workspace-genesis/skills/radicle-kbase/ingest-kbase.sh
git status --short
```

### 2. Commit

```bash
cd $HOME/.radicle/kbase
git commit -m "$(date -u +'ingest %Y-%m-%dT%H:%M:%SZ')"
```

### 3. Push to Radicle network

The rad CLI uses SSH over the `git@rad:` remote. Requires the SSH agent to have the radicle key:

```bash
# Check key is loaded
ssh-add -l | grep radicle

# If not loaded:
chmod 600 ~/.radicle/keys/radicle
ssh-add ~/.radicle/keys/radicle
```

Then push:
```bash
cd $HOME/.radicle/kbase
git push rad main
```

### 4. Seed (make it available on the network)

If the repo is not yet being seeded by public nodes:
```bash
export PATH="$HOME/.radicle/bin:$PATH"
rad seed rad:z2GNG6Nt3c7NWPge18xTRKZkkxSTy
```

Check replication status:
```bash
rad sync status rad:z2GNG6Nt3c7NWPge18xTRKZkkxSTy
```

---

## Repository Structure

### File Naming Convention

Each file is renamed to `{category}-{slug}.{ext}`:

| Category | Source path prefix | Example |
|----------|-------------------|---------|
| `doc` | `docs/` | `doc-encoding-system-pdd.md` |
| `mem` | `memory/` | `mem-2026-03-29.md` |
| `prj` | `projects/` | `prj-mythogen-ame-readme.md` |
| `skl` | `skills/` | `skl-genesis-brain.md` |
| `rsr` | `research/` | `rsr-bioregional-analysis.md` |
| `prm` | `prompts/` | `prm-research-01-emergence-methodology.md` |
| `syn` | `telegram-syntheses/` | `syn-master-synthesis.md` |
| `trn` | `transcripts/` | `trn-yt-archive-playlist-analysis.md` |
| `rnf` | `regen-neighborhood-framework/` | `rnf-community-alchemy-playbook.md` |
| `app` | `regen-app-stack/` | `app-readme.md` |
| `mis` | everything else (misc) | `mis-soul.md` |

**Slug rules:**
- Lowercase
- Non-alphanumeric chars → `-`
- Consecutive dashes collapsed
- Leading/trailing dashes removed
- If two files produce the same slug, a 4-char MD5 hash of the path is appended

**Every file** includes a metadata header:

```html
<!--
  source: projects/mythogen-ame/README.md
  category: prj
  ingested: 2026-04-13T12:30:00Z
-->
```

### README.md (Index)

Auto-generated at the root of the kbase. Columns:

| File | Category | Description | Source |
|------|----------|-------------|--------|

- **File** — linkable `category-slug.ext`
- **Category** — 2-3 letter code
- **Description** — first substantive line of the original file (HTML comments stripped)
- **Source** — relative path in the original workspace

⚠️ **Do not edit README.md manually.** It is overwritten on every ingest.

### Excluded Paths

These are NOT ingested (reference material, generated artifacts, or ephemeral):

```
*/cloned/*              — external repos used as reference
*/node_modules/*        — npm/bower deps
*/.venv/*               — Python venvs
*/.git/*                — git internals
*/dumps/*               — session state dumps
*/telegram_bigspace/*   — bigspace bot project
*/big_space/node_modules/*
*/regen-app-stack/pwa-starter/node_modules/*
*/regen-app-stack/matrix-homeserver/node_modules/*
*/archive/*             — old archived material
*/skills/aisystant-fpf/references/*  — FPF reference texts (not genesis-authored)
*/.ralph/*              — Ralph agent scratchpad
```

---

## Automation Options

### Cron — Auto-ingest every hour

```bash
# Add to crontab (crontab -e):
0 * * * * bash $HOME/.openclaw/workspace-genesis/skills/radicle-kbase/ingest-kbase.sh \
  >> $HOME/.radicle/kbase/ingest.log 2>&1 \
  && cd $HOME/.radicle/kbase \
  && git commit -m "$(date -u +'hourly ingest %Y-%m-%dT%H:00Z')" \
  && git push rad main >> $HOME/.radicle/kbase/push.log 2>&1
```

### Cron — Daily sync at midnight

```bash
0 0 * * * cd $HOME/.radicle/kbase \
  && git commit -m "$(date -u +'daily sync %Y-%m-%d')" --allow-empty \
  && git push rad main
```

### Heartbeat — Ingest on every heartbeat

In `HEARTBEAT.md`, add a note to run the ingest script if there are new files. The script is idempotent — running it twice in a row is safe (it cleans and re-copies fresh each time).

---

## Troubleshooting

### "Could not add identity" when running ssh-add

The GPG SSH agent is in use. The key may already be loaded via GPG agent. Try:
```bash
export SSH_AUTH_SOCK=/run/user/1001/gnupg/S.gpg-agent.ssh
ssh-add -l | grep radicle
```

### "remote 'rad' already exists" on re-init

Remove the stale remote first:
```bash
cd $HOME/.radicle/kbase
git remote remove rad
```

### TTY required for `rad init`

`rad init` needs a TTY (interactive prompts). Use the `script` wrapper:
```bash
script -q -e -c 'rad init --name regen-tribes-kbase --description "..." --default-branch main --public --no-confirm --no-seed' /dev/null
```

### Push fails with "Could not resolve hostname rad"

DNS issue with the `git@rad:` SSH remote. The radicle node DNS resolution is down or unreachable from this network. Wait and retry, or check seed node connectivity with `rad sync status`.

### rad repo already exists error

```
✗ Error: repository: git: attempt to reinitialize '/home/ian/.radicle/storage/z2GNG6Nt3...'
```
The repo was already initialized. This is fine — `rad .` in the `$KBASE` directory confirms the RID. No action needed.

### Node not running

```bash
rad node start
```

If it fails, check the node log:
```bash
tail -100 ~/.radicle/node/node.log
```

---

## Key Scripts

| Script | Purpose |
|--------|---------|
| `ingest-kbase.sh` | Main ingestion script — scan, copy, rename, re-index |
| (future) `sync-kbase.sh` | Commit + push in one shot |
| (future) `watch-kbase.sh` | Inotify-based watcher for real-time ingestion |

---

## Adding New Source Paths

To add a new source directory to the ingest (e.g., `~/.openclaw/workspace-genesis/tmp/`):

1. Edit `ingest-kbase.sh`
2. Add a `-not -path '*/tmp/*'` clause to the `find` command
3. Add the path prefix to the `case` statement that maps paths → categories
4. Run ingest, commit, push

---

## Radicle vs GitHub

| | Radicle | GitHub |
|---|---|---|
| Hosting | P2P (peer nodes) | Centralized |
| Sync | `git push rad main` | `git push github main` |
| Access | SSH to `git@rad:` | SSH to `git@github.com:` |
| Identity | Radicle DID (SSH key) | GitHub personal access token |
| Visibility | `--public` / `--private` | Public/private repos |
| Forks | Native p2p | Pull request model |
| Issues | `rad issue new` | GitHub Issues |
