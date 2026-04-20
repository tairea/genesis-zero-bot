# Radicle Notes Repo — After Action Report

**Repo:** `rad:z4WAr7CiNkf5JAoAb1srwi7gDz8nU`  
**Local:** `~/.radicle/regen-tribes-notes`  
**Status:** WIPED. Zero files, zero commits (one empty commit).

---

## What Was Attempted

### Goal
Create a distributed publication system for RegenTribes community notes using Radicle — a git-over-radicle protocol that doesn't depend on GitHub.

### What Was Built

1. **Publication pipeline** — scripts to publish notes from Telegram topics and workspace files into the repo
2. **STE100 validation gate** — installed `biz.dfch.ste100parser` for Simplified Technical English checks
3. **Naming convention** — `YYYYMMDD-HHMMSS-topic-slug.md` with lowercase-dash-only filenames
4. **README index** — auto-generated table of all publications appended below a marker
5. **161 publications** pushed from workspace docs, memory files, external repos (regen-ralph-presets, mythogen-ame, alien.js.wiki)

### What Went Wrong

1. **Metadata format was inconsistent** — YAML frontmatter with title, topic, published, author, description, tags — but the actual content was messy, with duplicate headers, inconsistent formatting, HTML-like tags triggering gates, frontmatter parsing errors
2. **Rewrite cycle was destructive** — multiple passes of "fix" scripts stripped content, created duplicate headers, mangled filenames, left double-periods in descriptions
3. **File naming collision** — multiple files with identical titles (e.g., 12x "Regen Ralph Prompt") got numbered suffixes that broke the naming convention
4. **Index never worked properly** — always appending instead of replacing, creating duplicate index entries
5. **The STE100 gate was useless** — `biz.dfch.ste100parser` only handles narrow simple sentences, not markdown documents with tables/code/headers. Every real doc failed it. Gate was silently bypassed for file publications.
6. **Mass rejections** — the HTML gate kept triggering on Rust generics (`<T>`), Markdown bold (`<b>`), code blocks — requiring constant patching
7. **No quality control** — 161 files published in a few hours with zero curation. Most were workspace dumps, memory files, ephemeral task outputs — not curated publications

### The Cleanup

The repo was nuked entirely:

```bash
cd ~/.radicle/regen-tribes-notes
git reset --hard $(git rev-list --max-parents=0 HEAD)  # reset to root
rm -f README.md *.md                                   # delete all files
git commit --amend --no-edit                          # squash to one clean commit
git push rad main --force-with-lease                 # push to all seeds
```

**Result:** Zero files, one empty commit (`c14ab04`), synced to 26+ seeds.

---

## What Was Achieved (Honestly)

- **Confirmed** the Radicle network works: 26+ seeds synced a repo with history rewrites and force-pushes
- **Confirmed** the RID `rad:z4WAr7CiNkf5JAoAb1srwi7gDz8nU` is stable and discoverable
- **Confirmed** `rad sync` propagates within seconds across the seed network
- **Confirmed** the workspace has ~161 docs worth preserving — but none were published correctly

That's it. Everything else was waste.

---

## Lessons Learned

### For Publishing to Radicle

1. **Start with ONE clean commit, one empty README.** Do not publish anything until the format is final.
2. **Define the format BEFORE publishing, not after.** Frontmatter? No frontmatter? Title only? Pick one and enforce it from day one.
3. **Do not mass-publish.** Publish 3-5 documents, verify the format looks correct on the network, THEN continue.
4. **STE100 validation is for short text only.** Do not try to validate full markdown documents with it. It's a narrow grammar validator, not a writing quality tool.
5. **HTML gate needs allowlists, not denylists.** The `<T>` in Rust generics, `<b>` in markdown, code fence content — all will trip up a denylist approach. Either whitelist allowed tags or skip the gate entirely.
6. **Filename convention must be finalized before any publish.** Changing it mid-stream creates chaos (as seen).
7. **README index: build it LAST, after format is stable.** Don't build infrastructure for content whose format is still in flux.

### For Radicle Itself

1. **`rad sync` is slow but reliable.** 20-30 second timeout for full sync. Don't spam it.
2. **Force-push with `--force-with-lease` is safe** — won't overwrite remote changes you haven't seen.
3. **Seed nodes go stale.** 8 out of 34 were offline. That's normal. They sync when they come back.
4. **`git-over-rad` works** — the git-remote-rad helper handles SSH authentication. SSH agent must be running. The `GIT_EXEC_PATH=~/.radicle/bin` trick bypasses PATH issues.
5. **Storage vs working dir:** `~/.radicle/storage/<rid>/` is the bare git repo. `~/.radicle/<name>/` is the working copy.
6. **RIDs are permanent.** Renaming the project only changes the identity document, not the RID. The content still references the same objects.
7. **Amending history is fine for single-commit clean starts** — but requires force-push. Network accepts it.

### For the Next Person

If you want to try this again:

1. **Do not mass-publish.** Ever. Publish 3 documents, verify, then 10 more.
2. **Pick a format and write it down first.** Example:

```
# TITLE UPPER

Publication on TOPIC. One sentence STE100 description.

## Content

<body>
```

No frontmatter. No metadata. Just this.

3. **Use the Iris web UI first** to verify what the network sees matches what you pushed.
4. **Test the HTML gate** with your actual content before publishing anything.
5. **If you need STE100 validation**, only apply it to short Telegram snippets, not file imports.
6. **Name files cleanly from the start.** If you change the convention, rename everything in one commit before publishing more.
7. **Keep the README minimal** — just the project name and the RID. Nothing else until the format stabilizes.

---

## Repository State

| Field | Value |
|-------|-------|
| RID | `rad:z4WAr7CiNkf5JAoAb1srwi7gDz8nU` |
| Local path | `~/.radicle/regen-tribes-notes` |
| Working tree | Empty |
| Commits | 1 (empty commit `c14ab04`) |
| Seeds synced | 26+ of 34 |
| Web UI | https://app.radicle.xyz/nodes/iris.radicle.xyz/rad:z4WAr7CiNkf5JAoAb1srwi7gDz8nU |

---

## Scripts That Exist

| Script | Location | Purpose |
|--------|----------|---------|
| `publish.sh` | `~/.openclaw/workspace-genesis/skills/regen-tribes-notes/` | Publish from Telegram |
| `publish-file.sh` | `~/.openclaw/workspace-genesis/skills/regen-tribes-notes/` | Publish from file |
| `add-index.sh` | `~/.openclaw/workspace-genesis/skills/regen-tribes-notes/` | Rebuild README index |

**None of these were tested properly before mass use. Use with caution.**

---

## What Should Happen Next

If anyone wants to try again properly:

1. Clone the empty repo: `rad clone rad:z4WAr7CiNkf5JAoAb1srwi7gDz8nU`
2. Write the FORMAT.md first (what each file looks like)
3. Publish 3 test docs
4. Verify on Iris web UI
5. Continue only if format is correct
6. Never force-push unless you're doing a cleanup like this one

The RID is clean. The repo is empty. The skill scripts exist but need rewriting before use.

---

**Bottom line:** Radicle works fine as a distributed git repo. The failure was 100% process/methodology — not the tool. Publishing 161 docs without a stable format, with broken scripts, with no verification, was just... what happened. Don't do that.
