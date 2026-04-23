# Radicle Kbase - Note Index Enforcement Skill

## Purpose

Enforce correct sequential numbering for new notes in the regen-tribes-notes Radicle repository.

## ASD-STE100 Compliance

All notes MUST follow the ASD-STE100 Simplified Technical English standard (Issue 9, 2025).

**Reference the asd-ste100 skill for:**
- Complete list of banned words and approved alternatives
- Sentence length limits (20 words procedural, 25 words descriptive)
- Approved verb dictionary
- Writing rules and best practices

Key banned words that must be replaced:
- utilize -> use
- leverage -> use
- optimize -> improve
- holistic -> complete
- synergy -> combined effect

## Index Acquisition Procedure

Before creating any new note, run this command to get the current highest index:

Bash command:
```bash
ls ~/.radicle/regen-tribes-notes/*.md | sed 's/.*\///' | sed 's/-.*//' | sort -n | tail -1
```

This extracts the numeric prefix from each markdown file, sorts numerically, and returns the highest value.

The next note index = highest existing index + 1.

## Example

If the command returns: 144

Then the next note should be: 145-something-title.md

## Critical Rules

Never guess the next index. Always query the filesystem first.

If a duplicate index was created (e.g., two 141 files), the conflict must be resolved before continuing. The correct next index after 141 (duplicate), 142, 143, 144 would be 145 (NOT 142).

After creating a new note, verify it does not duplicate any existing index before committing.

## File Naming

Format: NNN-title-slug.md

NNN is the sequential index (zero-padded to 3 digits if below 100).

## Frontmatter Required

Every note must have:

```yaml
---
title: "Note Title"
topic: space-separated topic tags
author: RegenTribes Community
published: YYYY-MM-DDTHH:MM:SSZ
status: published
level: 1 to 5
domain: information or social or infrastructure or hardware
---
```

## Cross-References

At the end of each note, add references:

See [NNN], [MMM].

[NNN]: NNN-title-slug.md

Cross-reference numbers are permanent and must never break.

## Commit and Sync

After creating or editing notes:

```bash
cd ~/.radicle/regen-tribes-notes
git add -A
git commit -m "Description of changes"
git push rad main
```