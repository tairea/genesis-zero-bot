# regen-tribes-notes — Publication Skill

Publish Telegram topic content as a formatted, validated publication in the `regen-tribes-notes` Radicle repository.

## Repository

- **RID:** `rad:z4WAr7CiNkf5JAoAb1srwi7gDz8nU`
- **Local:** `~/.radicle/regen-tribes-notes`
- **Branch:** `main`
- **Browse:** https://app.radicle.xyz/nodes/iris.radicle.xyz/rad:z4WAr7CiNkf5JAoAb1srwi7gDz8nU

## Structure Rules

### Naming
- Filename: `YYYYMMDD-HHMMSS-topic-slug.md`
- Case: **lowercase only**
- Delimiter: **dash (-) only** (no underscores in filenames)
- Topic and slug segments max 60 chars each
- Markdown only (`.md`)

### README Index
- Append-only; updated via `add-entry.sh` on each publish — never rebuilds the whole table
- One table row per publication: # | Title | Topic | Published | Link
- Entries appended after the table header line (O(lines_to_header) reads, not O(file_size))

### Document Structure (note file)
```markdown
---
title: <title>
topic: <topic>
author: <author>
published: <ISO8601>
---

# <title>

<body>
```

### Note Metadata Parsing
The first 6 lines of every note contain YAML frontmatter-paired metadata.
Extract with: `head -n 6 <note.md> | grep '^(title|topic|author|published):'`

## Validation

1. **HTML check** — rejects content containing real HTML tags (`<div>`, `<span>`, etc.); markdown bold/italic `<b>`, `<i>`, `<code>` are allowed
2. **STE100** — optional Simplified Technical English check for short Telegram inputs only

## Invocation

```
@genesis_zero_bot publish
@genesis_zero_bot save to notes
@genesis_zero_bot capture publication
@genesis_zero_bot add to regen-tribes-notes
@genesis_zero_bot /publish <title> [topic]
@genesis_zero_bot /note <title>
```

Or reply to a message: `publish` / `save as note` / `make this a publication`

## Confirmation

```
✅ Published: <filename>
📖 Read: https://app.radicle.xyz/nodes/iris.radicle.xyz/rad:z4WAr7CiNkf5JAoAb1srwi7gDz8nU/tree/<commit>
🌱 Synced to 29 seeds
⏳ Propagating…
```

## Scripts

| Script | Purpose |
|--------|---------|
| `publish.sh` | Publish from Telegram (args: title topic author content [definitions]) |
| `publish-file.sh` | Publish from file (args: file.md topic [author]) |
| `add-entry.sh` | Append single row to README index (append-only, O(header_lines)) |

## README Index Maintenance

`add-entry.sh` appends a single row to the README index without reading the full file:

```
add-entry.sh <title> <topic> <published> <commit>
```

- Counts existing rows via `grep -cE '^\| [0-9]+\|' README.md` — O(1) on file size
- Finds the table header separator via `grep -nE '^\|---+'` — O(header_lines), typically ~15
- Reads only `head -n HEADER_LINE` + `tail -n +$((HEADER_LINE+1))` — O(header_lines + rest_of_table)
- Writes: `prologue_header + new_row + tail` — append-only, no full rewrite

This means even after 1,000 publications, each update still reads only ~15 lines.
