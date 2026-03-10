# Kreuzberg — Document Extraction Reference

API reference skill for the Kreuzberg document intelligence library.

## Intention

Provide Genesis with comprehensive knowledge of the Kreuzberg API for writing code that extracts text, tables, metadata, and images from 75+ document formats. This is a reference skill — it contains documentation, not executable code.

## Stack

- **Kreuzberg** — Rust core library with Python, Node.js, Rust, and CLI bindings

## Components

| Path | Role |
|------|------|
| `SKILL.md` | Core API reference: installation, sync/async extraction, configuration, batch processing, error handling |
| `references/` | 8 detailed guides (Python API, Node.js API, Rust API, CLI, configuration, supported formats, advanced features, other bindings) |

## Used By

- `skills/semantic-graph/` — uses Kreuzberg for document text extraction in the ingestion pipeline

## Limitations

- **Reference only** — no executable code, just documentation for the LLM to use when writing Kreuzberg integration code
- **Version pinned** — documents a specific Kreuzberg version; may drift from upstream

## Next Steps

1. Add version tracking to detect when upstream Kreuzberg API changes
2. Consider merging into semantic-graph as reference material rather than standalone skill
