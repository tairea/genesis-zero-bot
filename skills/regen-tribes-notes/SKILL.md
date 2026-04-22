# regen-tribes-notes — Publication Skill

## Repository

- **RID:** `rad:z4WAr7CiNkf5JAoAb1srwi7gDz8nU`
- **Local:** `~/.radicle/regen-tribes-notes`
- **Branch:** `main`
- **Browse:** https://app.radicle.xyz/nodes/iris.radicle.xyz/rad:z4WAr7CiNkf5JAoAb1srwi7gDz8nU

## The Book Structure

Numbers are fixed. They never change. This makes cross-references stable.

```
000  ROOT       Entry point. Defines the whole.
001-009  Cell    One person. One home. One skill.
010-019  Tissue  Small groups. Trust. Roles.
020-029  Organ   Neighborhoods. Shared infrastructure.
030-039  System  Bioregions. Federation. Trade.
040-049  Body    Planetary. Knowledge commons.
050+     Special topics. FCL. AME. FOT. Etc.
```

Four domains at every level:

```
physical     What you build. Cost. Method. Material.
social       Who does what. How decisions get made.
information  What you know. How you know it.
exchange     Value. Currency. Trade without extraction.
```

## Document Format — ASD-STE100

This is the only writing standard. Follow it exactly.

### Frontmatter

```yaml
---
title: <title>
number: <NNN>
level: <level>
domain: <domain>
---
```

- `title`: exactly as shown in the index
- `number`: three digits, zero-padded
- `level`: root, cell, tissue, organ, system, body
- `domain`: physical, social, information, exchange

### Body Text

```
# <title>

<One sentence per line.>
<One sentence per line.>

<Thematic group.>

<One sentence per line.>
```

Rules:
1. ONE line = ONE sentence or ONE fragment.
2. No paragraphs. Never combine sentences on the same line.
3. Blank line between thematic groups of sentences.
4. Max 20 words per sentence.
5. No em-dashes.
6. No banned words.
7. Simple present. Active voice.
8. Numbers: spell out one to nine. Use digits for 10 and above.
9. One idea per sentence.
10. Define abbreviations at the start of the body.

### Banned Words

leverage, utilize, optimize, holistic, synergy, very, really, quite, extremely, incredibly, basically, simply

## Tech Naming Rules

Use category names. Never use brand names or specific product names.

| Category | Use This | Not This |
|---|---|---|
| Time-series storage | time-series database | any specific brand |
| Knowledge graph | knowledge graph database | any specific brand |
| Microcontroller | microcontroller | any specific brand |
| Network protocol | sensor network protocol | any specific brand |
| Construction 3D printer | construction 3D printer | any specific brand |
| WASM runtime | WASM runtime | any specific brand |
| Message broker | message broker | any specific brand |
| Stream processing | stream processor | any specific brand |

Exception: If the document topic IS the specific technology, use it as the example and define it.

## Abbreviation Format

Define on first use:
```
FCL stands for Formation Coding Language.
```

After first use, use the abbreviation alone.

## Cross-References

End with:
```
See [NNN], [NNN], [000].
```

Use three-digit format.

## Validation

Run before every publish:

```
python3 scripts/validate-ste100.py <file.md>
```

Also check: no specific tech names, no brand names, no instance names.

## README Index

The README is the book index. It lists all documents in order.

## Append-Only Publication Rule

The repository is an append-only knowledge base. This rule is non-negotiable.

**ALLOWED operations:**
- Create new document (new number, never reuse)
- Edit existing document (add content, never remove)
- Fix formatting, grammar, or encoding errors
- Update cross-references

**FORBIDDEN operations:**
- Delete a document (never delete, even if incorrect)
- Delete a section within a document (mark as deprecated instead)
- Remove content (replace with corrected content)
- Rename a document to a different number (numbers are permanent)

**Exception:** Only direct explicit request from the human owner to edit or trash specific content.

**Rationale:** Numbers provide stable cross-references. Deletion breaks the knowledge graph. Deprecation preserves the reference while signaling obsolescence.

**Deprecation instead of deletion:** If content is wrong, add a frontmatter line:
```
status: deprecated
```
Then create a new corrected document with a new number.

## Confirmation

For each document created, output:

```
Published: NNN-title.md
URL: https://app.radicle.xyz/nodes/iris.radicle.xyz/rad:z4WAr7CiNkf5JAoAb1srwi7gDz8nU/tree/HEAD/<NNN>-title.md
```

The RID never changes. The document path is always `<NNN>-<slug>.md` where slug matches the title converted to lowercase with hyphens.
