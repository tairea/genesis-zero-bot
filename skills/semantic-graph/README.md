# Semantic Graph — Document to Knowledge Graph

LLM-powered extraction pipeline that transforms any document into a typed, traversable knowledge graph in SurrealDB with NARS epistemic truth values, vector embeddings, and hybrid retrieval.

## Intention

Ingest documents in any format (PDF, DOCX, HTML, Markdown, code, images) and extract structured concepts (nodes) and semantic relations (edges) into a graph database. Every claim carries calibrated confidence scores via Non-Axiomatic Reasoning System (NARS) truth values, enabling evidence accumulation across multiple documents. The graph supports hybrid retrieval (vector + graph + community summaries) for RAG consumption.

## Stack

- **Python 3.12** — pipeline orchestration
- **Kreuzberg** — document text extraction (75+ formats, OCR)
- **OpenRouter** — LLM extraction (configurable model via `EXTRACTION_MODEL` env var)
- **SurrealDB v3** — graph storage with native `->` traversal, HNSW vector indexes
- **OpenAI text-embedding-3-small** — 1536d embeddings via OpenRouter
- **NumPy** — cosine similarity for entity resolution and MMR reranking
- **3d-force-graph** — interactive 3D visualization (viz/)

## Components

| File | Role |
|------|------|
| `pipeline.py` | Unified CLI entry point for all commands |
| `graph_extract.py` | Ingestion pipeline: text extraction, chunking, LLM parse, graph storage, temporal contradiction detection |
| `llm_parser.py` | LLM extraction with RegenTribes ontology (13 types), junk filtering, type normalization |
| `embeddings.py` | Vector embedding for concepts and chunks, HNSW index management, semantic search |
| `retriever.py` | Hybrid retrieval: vector search + graph traversal + chunk search + community summaries + RRF + MMR + domain boosting |
| `communities.py` | Community detection (label propagation), LLM-generated summaries, embedding-based community search |
| `entity_resolution.py` | Numpy-optimized duplicate detection (cosine similarity matrix), LLM-confirmed merges |
| `evaluate.py` | Evaluation framework: graph health metrics, retrieval benchmarks, extraction F1 |
| `cleanup.py` | Junk concept removal (stopwords, newlines, generic terms) |
| `grammar_triangle.py` | Zero-cost semantic annotation: 20 NSM primitives, 8 Qualia dimensions, 5 Causality indicators, text chunking |
| `verbs.py` | 144-verb taxonomy (6 categories x 24 verbs), fuzzy matching and normalization |
| `schema.surql` | SurrealDB schema: node tables (document, chunk, concept, community), edge tables (contains, mentions, relates, belongs_to) |
| `viz/graph_viz.py` | 3D visualization generator — queries SurrealDB, produces self-contained HTML |

## CLI

All commands via `python pipeline.py <command>`:

```
# Ingest
pipeline.py ingest <path>              # Ingest file or directory
pipeline.py ingest <path> --embed      # Ingest + generate embeddings

# Embeddings
pipeline.py embed                      # Embed all concepts
pipeline.py embed-chunks               # Embed all text chunks

# Search
pipeline.py search "query"             # Semantic vector search
pipeline.py similar concept:id         # Find similar concepts
pipeline.py retrieve "query"           # Hybrid retrieval (vector + graph + chunks + communities)
pipeline.py retrieve "query" --hops 2  # With 2-hop graph traversal

# Graph Analysis
pipeline.py communities detect --summarize  # Detect and summarize communities
pipeline.py communities list                # List communities
pipeline.py communities search "query"      # Search community summaries
pipeline.py resolve --dry-run               # Find duplicate entities
pipeline.py resolve                         # Merge duplicates

# Quality
pipeline.py evaluate health            # Graph health metrics
pipeline.py evaluate retrieval         # Run retrieval benchmarks
pipeline.py cleanup --dry-run          # Preview junk concept removal

# Utilities
pipeline.py stats                      # Database overview
pipeline.py viz                        # Generate 3D visualization
pipeline.py export -o graph.json       # Export as JSON
```

## Schema

```
document ──contains──> chunk ──mentions──> concept
                                               |
                                          relates (edge)
                                               |
                                          concept
                                               |
                                        belongs_to (edge)
                                               |
                                          community
```

- **document** — source file metadata (title, mime_type, word_count, language, quality)
- **chunk** — text segment with Grammar Triangle (NSM, Qualia, Causality), 1536d embedding
- **concept** — named entity/idea with type (13 RegenTribes types), rung (R0-R9), NARS truth values, 1536d embedding
- **community** — cluster of related concepts with LLM-generated summary, 1536d embedding
- **contains** — document to chunk provenance
- **mentions** — chunk to concept provenance (with salience)
- **relates** — concept to concept (verb from 144 taxonomy, evidence, temporal validity)
- **belongs_to** — concept to community membership

## RegenTribes Ontology (13 concept types)

person, organization, project, skill, resource, place, event, system, process, practice, idea, attribute, quantity

## Retrieval Pipeline

The `retrieve()` function implements a 6-stage hybrid retrieval:

1. **Vector search** — cosine similarity on concept embeddings
2. **Domain detection** — keyword-based query intent classification (12 domains)
3. **Domain-focused search** — rewritten query targeting domain-specific terms, deduplicated against original results
4. **Graph traversal** — 1-2 hop neighbor expansion from seed concepts
5. **Community search** — embedding similarity on community summaries
6. **Reranking** — Weighted RRF fusion, domain-aware type boosting, name deduplication with stemming, MMR for diversity
7. **Chunk retrieval** — graph-based source chunks + vector-based passage search

## Environment Variables

```
OPENROUTER_API_KEY    # Required: LLM and embedding API access
SURREALDB_URL         # Default: ws://127.0.0.1:8000
SURREAL_PASS          # Default: root
EXTRACTION_MODEL      # Default: google/gemini-3.1-flash-lite-preview
EMBEDDING_MODEL       # Default: openai/text-embedding-3-small
```

## Current Metrics (March 2026)

```
Graph:      1505 concepts, 1584 relations, 605 chunks, 210 communities, 34 documents
Coverage:   100% concept embeddings, 100% chunk embeddings
Retrieval:  75% pass rate, 59% concept recall, 91% theme coverage
Latency:    p50=5.3s, p95=6.6s (includes embedding API calls)
Health:     1.05 edge/node ratio, 9% orphan concepts, 66 unique verbs
```

## Docs

- `KNOWLEDGE-GRAPH-EVALUATION.md` — research-backed evaluation against industry best practices, with roadmap and baseline metrics
- `USECASES.md` — 8 usage scenarios
- `PRIME.md` — LLM-consumable system primer for future development sessions
