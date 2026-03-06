# Semantic Graph — Document to Knowledge Graph

LLM-powered extraction pipeline that transforms any document into a typed, traversable knowledge graph in SurrealDB with NARS epistemic truth values.

## Intention

Ingest documents in any format (PDF, DOCX, HTML, Markdown, code, images) and extract structured concepts (nodes) and semantic relations (edges) into a graph database. Every claim carries calibrated confidence scores via Non-Axiomatic Reasoning System (NARS) truth values, enabling evidence accumulation across multiple documents.

## Stack

- **Python** — pipeline orchestration
- **Kreuzberg** — document text extraction (75+ formats, OCR)
- **Anthropic Claude Sonnet** — concept and relation extraction via structured prompts
- **SurrealDB** — graph storage with native `->` traversal
- **3d-force-graph** — interactive 3D visualization (viz/)

## Components

| File | Role |
|------|------|
| `graph_extract.py` | Main pipeline: `GraphExtractor` class with async context manager, CLI, and Python API |
| `llm_parser.py` | Claude API integration — batched chunk extraction, JSON parsing, verb normalization |
| `grammar_triangle.py` | Zero-cost semantic annotation: 20 NSM primitives, 8 Qualia dimensions, 5 Causality indicators. Also handles text chunking with 200-char overlap |
| `subagent_parser.py` | Alternative parser entry point (used by graph_extract imports) |
| `verbs.py` | 144-verb taxonomy (6 categories x 24 verbs), fuzzy matching and normalization |
| `schema.surql` | Full SurrealDB schema: 3 node tables (document, chunk, concept), 3 edge tables (contains, mentions, relates), indexes, field definitions |
| `batch_ingest.py` | Bulk file ingestion script |
| `batch_ingest_v2.py` | Revised bulk ingestion |
| `nsm_keywords.json` | NSM primitive keyword mappings |
| `verb_taxonomy.json` | Verb category data |
| `viz/graph_viz.py` | 3D visualization generator — queries SurrealDB, produces self-contained HTML with embedded 3d-force-graph |
| `viz/SKILL.md` | Visualization sub-skill definition |
| `viz/artifacts/` | Generated HTML visualization outputs |

## Schema

```
document (node) ──contains──> chunk (node) ──mentions──> concept (node)
                                                              |
                                                         relates (edge)
                                                              |
                                                         concept (node)
```

- **document** — source file metadata (title, mime_type, word_count, language, quality)
- **chunk** — text segment with full Grammar Triangle (NSM, Qualia, Causality, dominant_mode)
- **concept** — named entity/idea/event with type, rung level (R0-R9), NARS truth values, aliases, tags
- **contains** — document to chunk provenance
- **mentions** — chunk to concept provenance (with salience score)
- **relates** — concept to concept semantic edge (verb from 144 taxonomy, evidence quote, temporal validity)

## Limitations

- **Hardcoded credentials** — SurrealDB password in `graph_viz.py:29` and `graph_extract.py:79`. Should use env vars.
- **Hardcoded model** — `llm_parser.py` uses `claude-sonnet-4-20250514`. Should be configurable.
- **Inconsistent namespace** — `schema.surql` uses `myproject/knowledge`, `graph_extract.py` defaults to `semantic_graph/main`. Need to unify.
- **No vector search** — Grammar Triangle stored as JSON objects, not as float arrays with vector indexes. Can't do cosine similarity or nearest-neighbor.
- **ARTIFACTS_DIR** in `graph_viz.py` uses a hardcoded relative path from the genesis workspace.
- **No tests** — no test suite for any component.
- **batch_ingest versions** — unclear if v2 supersedes v1 or they serve different purposes.

## Next Steps

1. Move all credentials to environment variables / config file
2. Unify SurrealDB namespace naming across all files
3. Add vector index to Grammar Triangle dimensions for similarity search
4. Add test suite (extraction accuracy, schema validation, round-trip)
5. Make Claude model configurable via env var
6. Evaluate whether batch_ingest_v2 supersedes v1 — consolidate if so
7. Connect viz output to a deployment target (GitHub Pages or file server)
8. Add NARS revision unit tests to verify evidence accumulation correctness

## Docs

- `USECASES.md` — 8 usage scenarios (codebase understanding, research synthesis, legal analysis, etc.)

Project-level specs live in `projects/knowledge-graph-docs/`:
- `PROJECT-objectives.md` — overall knowledge graph project goals
- `PIPELINE-design.md` — data pipeline architecture
- `SPEC-extraction-evaluation.md` — extraction evaluation criteria (Entity F1 >0.85, Relation F1 >0.80)
