# regen-tribes-notes skill

This skill governs all publication to the Radicle `regen-tribes-notes` repository.

## Repository

```
rad:z4WAr7CiNkf5JAoAb1srwi7gDz8nU/z6MkhgHUCtE8dW8S89wziVgThbCUDuK5f3A2qdbfiSXDP4Ye
```

Web: https://app.radicle.xyz/nodes/iris.radicle.xyz/rad:z4WAr7CiNkf5JAoAb1srwi7gDz8nU

Repo path: `~/.radicle/regen-tribes-notes/`

## Publishing Workflow

When the human asks to publish a new note to regen-tribes-notes:

### Step 1: Create the document

Write a `.md` file in `~/.radicle/regen-tribes-notes/` with:
- Number: next available (check `README.md` table, highest existing + 1)
- Filename: `<NNN>-<slug>.md`
- Frontmatter: `title`, `topic`, `author`, `published` (ISO date), `status: published`, `level: 3`, `domain: C`
- Content: ASD-STE100 Simplified Technical English — one sentence per line, no paragraphs longer than 25 words

### Step 2: Enforce ASCII-only encoding

Before committing, verify the file contains no non-ASCII characters:

```bash
grep -Pn '[^\x00-\x7F]' <file>.md
```

If any output, fix immediately. Common mistakes:
- Em dashes (`—`) → ` - `
- Chinese characters → translate or remove
- Box-drawing characters (`│─┌┐└┘`) → remove
- Accented letters (`ü`, `ö`, `ä`, `é`) → replace with ASCII equivalent

### Step 3: Verify abbreviation definitions

Every abbreviation must be defined on first use. Use `## Abbreviations` section near the top of the document with format:
```
NSA is national security agency.
```

Common abbreviations that need defining:
- AI, WASM, IoT, ECS, SurrealDB, MeTTa, Hyperon, FOT, AME, FCL, ITC, COS, FRS, CDS, OAD, RBE, NOI, OPEX, PV, LED, LP, DAO, NFT, RAG, BDD, NAL

### Step 4: Update README index (append-only)

Run the update script — never edit README by hand:

```bash
~/.radicle/regen-tribes-notes/update-index.sh <NNN> "<Title>"
```

The script handles finding the correct row position, inserting the new row, and verifying ASCII.

If the script is not available, use this sed approach (no file loaded into context):

```bash
# Get last row number
LAST=$(grep -E "^\| [0-9]+ \|" ~/.radicle/regen-tribes-notes/README.md | tail -1 | sed 's/| *\([0-9]*\) *|.*/\1/')
# Insert new row after last row where number <= NNN
NEW_N="<NNN>"
NEW_TITLE="<Title>"
INSERT_LINE=$(grep -nE "^\| [0-9]+ \|" ~/.radicle/regen-tribes-notes/README.md | while read line; do
  NUM=$(echo "$line" | sed 's/| *\([0-9]*\) *|.*/\1/')
  [ "$NUM" -le "$NEW_N" ] && echo "$line"
done | tail -1 | cut -d: -f1)
sed -i "${INSERT_LINE}a | $NEW_N | body | information | $NEW_TITLE |" ~/.radicle/regen-tribes-notes/README.md
```

### Step 5: Commit

```bash
cd ~/.radicle/regen-tribes-notes
git add -A
git commit -m "Add <NNN>: <Title>"
```

### Step 6: Verify 1:1 correspondence

Before push, verify the README index exactly matches the files:

```bash
cd ~/.radicle/regen-tribes-notes
# Count numbered .md files
FILE_COUNT=$(ls [0-9]*.md 2>/dev/null | wc -l)
# Count rows in README table
ROW_COUNT=$(grep -cE "^\| [0-9]+ \| body" README.md)
if [ "$FILE_COUNT" != "$ROW_COUNT" ]; then
  echo "MISMATCH: $FILE_COUNT files, $ROW_COUNT rows"
  exit 1
fi
echo "PASS: $FILE_COUNT files, $ROW_COUNT rows"
```

If mismatch, investigate and fix before push.

### Step 7: Push

```bash
cd ~/.radicle/regen-tribes-notes
git push rad main
```

If push fails due to SSH blocking (Hetzner VPS), the local repo is still correct — push from a machine with SSH access.

## Document Numbering

- Numbers are permanent. Never change a number once assigned.
- Numbers are sequential. Use the next available number.
- The number appears in both filename and frontmatter.
- Example: `042-some-topic.md` with `number: 042`

## ASD-STE100 Rules

- Maximum 25 words per sentence
- Maximum 20 words for procedural sentences
- One sentence per line
- No em-dashes
- No bullet lists with sub-clauses
- Spell out one to nine, use digits for 10+
- Active voice only
- Present tense only
- No hedging (possibly, perhaps, might)
- No filler (leverage, utilize, optimize, holistic, synergy)

## Frontmatter Template

```
---
title: "<Title>"
topic: <topic-slug>
author: <author>
published: YYYY-MM-DDTHH:MM:SSZ
status: published
level: 3
domain: C
---
```

## Content Formatting

- One sentence per line (hard rule)
- Separate major sections with `##`
- No markdown tables — use bullet lists with short sentences
- Use `<blockquote expandable>` for Telegram-formatted quotes
- Keep lines under 120 characters

## Encoding Rules (MANDATORY)

**ASCII only. No exceptions.**

Never use:
- Chinese, Japanese, Korean, or Cyrillic characters
- Em dashes (`—`) — use ` - `
- Box-drawing characters (`│─┌┐└┘`)
- Accented letters — use ASCII equivalents (TUV not TÜV)
- Smart quotes (`" "`) — use straight quotes
- Emoji in content — use only in examples or as markers

Before every commit, run:
```bash
grep -Pn '[^\x00-\x7F]' <file>.md
```
If any output, fix before committing.

## Abbreviation Definition Rules

Every abbreviation must be defined on first use in every document.

Format: `ABBREV is what it stands for.` in an `## Abbreviations` section near the top.

Abbreviations used across docs (must be defined in each doc that uses them):
- AI is artificial intelligence
- WASM is webassembly
- IoT is internet of things
- ECS is entity component system
- SurrealDB is surrealdb
- MeTTa is meta-text
- Hyperon is hyperon
- FOT is field of trust
- AME is affinity mapping engine
- FCL is formation coding language
- ITC is integrity transaction convention
- COS is constitution operating system
- FRS is federation relationship standard
- CDS is coordination design system
- OAD is ownership architecture design
- RBE is resource-based economy
- NOI is net operating income
- OPEX is operating expenditure
- PV is photovoltaic
- LED is light-emitting diode
- LP is limited partnership
- DAO is decentralized autonomous organization
- NFT is non-fungible token
- RAG is retrieval-augmented generation
- BDD is behavior-driven development
- NAL is non-axiomatic logic

## Skill Manifest (Deployed)

- Path: `~/.openclaw/workspace-genesis/skills/regen-tribes-notes/SKILL.md`
- Version: 2026-04-22

## Important Notes

- The radicle repo SKILL.md is the canonical skill. The workspace copy is for reference only.
- Numbers are permanent once assigned. Never reuse numbers.
- Never delete a document. Deprecate with `status: deprecated` instead.
- The README index is the single source of truth for document inventory.
- Always verify 1:1 correspondence between files and README rows before push.