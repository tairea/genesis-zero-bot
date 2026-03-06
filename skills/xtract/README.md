# XTRACT — Lightweight Document to Graph

Zero-LLM document-to-graph extraction using regex pattern matching and Grammar Triangle fingerprinting. A simplified alternative to the semantic-graph skill that trades extraction quality for speed and zero API cost.

## Intention

Fast, free ingestion of text files into a SurrealDB knowledge graph without LLM API calls. Uses regex-based entity and relation extraction with keyword-based semantic fingerprinting for concept deduplication.

## Stack

- **Python** — single-file pipeline
- **SurrealDB** — graph storage (async client)
- **Canvas 2D API** — built-in browser viewer (no libraries)
- **SurrealDB JS SDK** — viewer connects to DB via CDN

## Components

| File | Role |
|------|------|
| `xtract.py` | Complete pipeline: text chunking, regex concept extraction, 12 relation patterns, SurrealDB storage |
| `viewer.html` | Live 2D force-directed graph viewer — connects to SurrealDB WebSocket, hand-rolled physics (100 iterations), dark theme, hover tooltips |
| `artifacts/` | Example generated viewer outputs (xtract-viewer, xtract-3d-viewer, xtract-v2-embedded) |

## Schema

Simplified 2-table + 1-edge schema (no chunk or provenance layer):

- **document** — source file record (source, title, created_at)
- **concept** — extracted entity (name, type, fingerprint, NARS values)
- **relates** — concept-to-concept edge (verb, category, source_doc)

## How Extraction Works

**Concepts** — found via 3 regex patterns:
- Capitalized phrases: `[A-Z][a-z]+ [A-Z][a-z]+`
- Technical suffixes: words ending in -tion, -ment, -ness, -ity, etc.
- Acronyms: words containing API, SDK, CLI, HTTP, etc.

**Relations** — found via 12 hardcoded patterns:
`X is a Y`, `X has Y`, `X contains Y`, `X depends on Y`, `X uses Y`, `X provides Y`, `X requires Y`, `X relates to Y`, `X connects to Y`, `X enables Y`, `X creates Y`, `X manages Y`

**Types** — assigned by keyword matching: system, process, idea, or default entity.

## Limitations

- **Hardcoded credentials** — SurrealDB password at `xtract.py:109` and `viewer.html:173`
- **Hardcoded NARS values** — frequency=0.7, confidence=0.5, evidence_count=1 for everything. The NARS revision formula is documented in SKILL.md but not implemented in code.
- **Only 12 relation patterns** — misses implicit relationships, causality, temporal relations
- **Text files only** — handles .md, .txt, .py, .js, .yaml. No PDF/DOCX/image support (no Kreuzberg)
- **Regex-only extraction** — misses non-capitalized concepts, multi-word entities, context-dependent meanings
- **No chunk provenance** — document links directly to concepts with no intermediate chunk records
- **Grammar Triangle not searchable** — fingerprints computed but hashed to a string for dedup only, not stored as vectors
- **SPO Crystal not implemented** — described in SKILL.md but absent from code
- **Viewer CSS bug** — syntax error at `viewer.html:55-56`
- **No Chinese keyword matching** — Chinese keywords defined in NSM/Qualia dicts but regex patterns are English-only

## Next Steps

1. Implement NARS revision (fetch existing record from DB, merge via formula)
2. Move credentials to environment variables
3. Add more relation patterns or optionally use LLM extraction
4. Store Grammar Triangle as float arrays for vector similarity search
5. Fix viewer CSS bug at line 55-56
6. Add Kreuzberg support for multi-format document ingestion
7. Either implement SPO Crystal or remove from SKILL.md documentation
8. Add chunk table for provenance tracking
9. Consider merging best parts into semantic-graph skill as the primary extraction tool
