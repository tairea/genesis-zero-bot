# Semantic Graph — System Primer

This document primes an LLM on the full architecture, data flow, key decisions, and known issues for the RegenTribes semantic knowledge graph. Use it to onboard quickly for improvements, debugging, or feature development.

## What This System Does

Transforms documents into a queryable knowledge graph with hybrid retrieval for RAG. The pipeline: extract text -> chunk -> LLM extraction -> SurrealDB graph -> embeddings -> community detection -> hybrid retrieval. Built for the RegenTribes regenerative neighborhood community.

## Architecture Overview

```
Documents (PDF, MD, DOCX, etc.)
    |
    v
[Kreuzberg] -- text extraction
    |
    v
[grammar_triangle.py] -- chunking (800 chars, 200 overlap) + NSM/Qualia/Causality annotation
    |
    v
[llm_parser.py] -- LLM extraction (concepts + relations as JSON)
    |                Uses RegenTribes ontology (13 types)
    |                Junk filtering (_is_junk_concept)
    |                Type normalization (_normalize_type)
    v
[graph_extract.py] -- SurrealDB storage
    |                  NARS revision on duplicate concepts
    |                  Temporal contradiction detection (_CONTRADICTIONS)
    |                  SHA256 stable IDs for dedup
    v
[embeddings.py] -- OpenAI text-embedding-3-small via OpenRouter
    |               Concepts: "name (type): description"
    |               Chunks: raw text (truncated to 2000 chars)
    |               HNSW cosine index on concept.embedding and chunk.embedding
    v
[communities.py] -- Label propagation (no networkx dependency)
    |                LLM-generated summaries per community
    |                Embeddings on community summaries
    v
[retriever.py] -- Hybrid retrieval for RAG consumption
                   Vector + domain search + graph traversal + community search
                   RRF fusion + domain boosting + name dedup + MMR
```

## Key Files and What They Do

### pipeline.py (CLI entry point)
- Wires all commands into argparse subcommands
- `_connect_db()` helper for shared DB connection pattern
- Every command is an `async def cmd_*(args)` function
- Commands: ingest, embed, embed-chunks, search, similar, retrieve, communities, resolve, cleanup, evaluate, viz, export, stats

### graph_extract.py (ingestion engine)
- `GraphExtractor` class with `connect()` classmethod and `ingest()` method
- `ensure_schema()` runs schema.surql statements
- `_store_concept()` uses NARS revision formula for evidence accumulation
- `_store_relation()` checks `_CONTRADICTIONS` dict before inserting; sets `valid_until` on contradicted edges
- SHA256-based stable IDs: `concept:{sha256(name.lower() + "_" + type)[:16]}`
- Critical: uses `_rid()` helper to convert string IDs to `RecordID` objects (SurrealDB SDK v1.x requirement)
- Relation storage: `INSERT RELATION INTO relates {...} ON DUPLICATE KEY UPDATE` (NOT `UPSERT` — that doesn't work for SurrealDB v3 relation tables)

### llm_parser.py (LLM extraction)
- System prompt defines the 13 RegenTribes concept types with examples
- Extraction model configurable via `EXTRACTION_MODEL` env var
- `_is_junk_concept(name)` — shared stopword filter (also used by cleanup.py)
- `_normalize_type(raw_type)` — maps LLM output types to valid ontology types via `_TYPE_MAP`
- `normalize_parsed(data)` — post-processes LLM JSON: cleans newlines from names, filters junk, normalizes types
- Batch processing: chunks sent in configurable batch sizes (default 4)

### retriever.py (hybrid retrieval)
- `RetrievalContext` dataclass with `.text` property for LLM prompt injection
- `retrieve(db, query, limit, hops, include_chunks)` — main entry point
- 6 stages: vector search -> domain-focused search -> graph traversal -> RRF fusion -> community search -> chunk retrieval
- **Domain boosting**: `DOMAIN_BOOSTS` maps 12 keyword sets to concept type boost weights
- `detect_domain_boosts(query)` — returns `{type: multiplier}` dict
- `_make_domain_query(query, boosts)` — appends domain-specific search terms
- `_dedup_by_name(results, limit)` — word-overlap dedup with minimal stemmer (75% threshold)
- `mmr_rerank(items, query_vec, embeddings, lambda_, limit)` — numpy-based MMR for diversity
- `reciprocal_rank_fusion(*ranked_lists, key, k, weights)` — weighted RRF

### embeddings.py
- OpenAI API via OpenRouter (`OPENROUTER_API_KEY`)
- `embed_text(text)` / `embed_texts(texts)` — single/batch embedding
- `embed_concepts(db)` — embeds "name (type): description" strings
- `embed_chunks(db)` — embeds raw chunk text (truncated to 2000 chars)
- `ensure_vector_schema(db)` — defines HNSW indexes
- `search(db, query)` / `find_similar(db, concept_id)` — standalone search functions

### communities.py
- `label_propagation(nodes, edges, max_iter, min_community_size)` — pure Python, no dependencies
- `_summarize_community()` — LLM generates 2-3 sentence summary per community
- `_store_communities()` — creates community nodes + belongs_to edges + embeddings
- Important: must use `RecordID("community", f"c{id}")` not string IDs for UPDATE/RELATE queries
- `detect_communities(db)` and `search_communities(db, query)` — main entry points

### entity_resolution.py
- Numpy-optimized: loads all concept embeddings as matrix, computes cosine sim per type group
- `find_duplicate_candidates(db, threshold)` — returns pairs above threshold (default 0.88)
- `resolve_entities(db, threshold, dry_run, verbose)` — LLM confirms merges, then:
  - Redirects edges from merged concept to canonical
  - Combines NARS evidence counts
  - Adds old name as alias
  - Deletes merged concept

### evaluate.py
- `graph_health(db)` — counts, density, edge/node ratio, orphans, type entropy, embedding coverage
- `eval_retrieval(db)` — 8 built-in test queries with expected concepts and themes
  - Fuzzy concept matching (substring check)
  - Theme coverage (keyword in formatted text)
  - Latency p50/p95
- `eval_extraction(db, ground_truth_path)` — precision/recall/F1 against labeled JSON
- `generate_ground_truth_template(db, doc_title)` — creates template from existing data for manual review

### cleanup.py
- `_is_junk_concept(name)` — stops on: len<=2, newlines, stopwords, short lowercase single words
- `cleanup(dry_run)` — manages own DB connection, deletes concepts + their relates/mentions edges

## SurrealDB Specifics (v3.0.2)

- **SDK v1.x**: returns flat lists from queries (not `{"result": [...]}`), uses `RecordID` objects
- **RecordID gotcha**: string IDs like `"concept:abc"` don't work in parameterized queries (`UPDATE $id SET ...`). Must use `RecordID("concept", "abc")`
- **Relations**: `UPSERT` doesn't work for relation tables. Use `INSERT RELATION INTO relates {...} ON DUPLICATE KEY UPDATE`
- **Vector search**: `vector::similarity::cosine(embedding, $vec)` in SELECT with ORDER BY score DESC
- **Namespace**: `semantic_graph/main`
- **Binary location**: `/home/ian/.surrealdb/surreal` on server
- **Data store**: `surrealkv:/home/ian/open-brain/data/brain.db`

## NARS Truth Values

Every concept and relation carries:
- `nars_frequency` (float, default 1.0) — truth frequency
- `nars_confidence` (float, default 0.5) — confidence level
- `evidence_count` (int, default 1) — observation count

Revision formula on duplicate evidence:
```
new_freq = (old_freq * old_evidence + new_freq) / (old_evidence + 1)
new_conf = (old_evidence + 1) / (old_evidence + 2)  # approaches 1.0 asymptotically
```

## Temporal Contradiction Detection

`graph_extract.py` defines 15 contradiction verb pairs:
```python
_CONTRADICTIONS = {
    "ENABLES": "PREVENTS", "CAUSES": "PREVENTS", "SUPPORTS": "CONTRADICTS",
    "ALLOWS": "BLOCKS", "AMPLIFIES": "REDUCES", "CREATES": "DESTROYS",
    "INITIATES": "TERMINATES", "INCLUDES": "EXCLUDES", "ACCELERATES": "DELAYS",
    # ... and reverses
}
```
Before inserting a relation, checks for existing contradictory edges. If found, sets `valid_until = time::now()` on the old edge rather than deleting it.

## Domain Boosting (12 domains)

The retriever detects query intent and boosts concept types accordingly:

| Domain | Example keywords | Top boosted types |
|--------|-----------------|-------------------|
| Finance | fund, capital, invest, revenue | quantity 2.0x, system 1.4x |
| Food | farm, permaculture, aquaponics | process 1.8x, system 1.5x |
| Energy | solar, wind, battery, microgrid | system 1.8x, resource 1.5x |
| Water | water, rainwater, greywater | system 1.8x, process 1.5x |
| Governance | govern, consensus, vote | process 1.8x, system 1.5x |
| People | team, founder, recruit | person 2.0x, skill 1.8x |
| Land | land, property, zoning | place 2.0x, resource 1.5x |
| Legal | legal, permit, LLC | system 1.6x, process 1.5x |
| Construction | build, house, architect | system 1.6x, process 1.5x |
| Community | culture, onboard, conflict | practice 1.8x, process 1.5x |
| Education | learn, workshop, curriculum | skill 1.8x, event 1.5x |
| Technology | software, platform, IoT | system 1.6x, skill 1.4x |

The domain search also rewrites the query by appending domain-specific terms and runs a second vector search, whose results are deduplicated against the original search and given 2x weight in RRF fusion.

## Known Issues and Improvement Opportunities

### Data Quality
- **Old concept types persist**: 208 `entity` and 11 `quality` type concepts from pre-ontology ingestion remain. Could be re-typed with a migration script.
- **Orphan concepts**: 9% of concepts have no edges. Some are genuine isolates, others result from edge storage failures.
- **Concept:Relation ratio**: 1.05 — healthy but could be higher (2-5x is ideal). More documents and better extraction prompts would help.

### Retrieval
- **Latency**: 5-6 seconds per query, dominated by 2 embedding API calls (query + domain rewrite). Could cache query embeddings or use a local embedding model.
- **Concept recall**: 59% — broad queries still return broad concepts. Better with domain boosting but still room for improvement.
- **Missing BM25**: No full-text keyword search. SurrealDB supports `@@` search operator — adding BM25 as a third retrieval source would improve exact-match queries.
- **Community summaries not in RRF**: Community results are separate from concept ranking. Integrating community member concepts into the main RRF fusion could help.

### Infrastructure
- **No tests**: No automated test suite. The evaluation framework measures quality but doesn't prevent regressions.
- **Embedding dependency**: Every query requires an OpenRouter API call. A local embedding model (e.g. sentence-transformers) would eliminate latency and cost.
- **Graph viz outdated**: `viz/graph_viz.py` may have stale credential handling; hasn't been updated with the new schema additions.
- **batch_ingest scripts**: `batch_ingest.py` and `batch_ingest_v2.py` are superseded by `pipeline.py ingest <dir>` — could be removed.

### Architecture
- **No incremental updates**: Re-ingesting a document creates duplicate chunks/concepts rather than diffing against existing data. Would need content-hash-based chunk dedup.
- **Community detection is offline**: Communities must be manually re-detected after new documents are ingested. Could be triggered automatically post-ingest.
- **No cross-document coreference**: Entity resolution runs as a separate pass, not inline during ingestion. Running it inline would prevent duplicates from accumulating.

## Server Deployment

- **Server**: Hetzner (`5.78.116.97`, user `ian`, SSH alias `hetzner-ian`)
- **Workspace**: `~/.openclaw/workspace-genesis/skills/semantic-graph/`
- **Venv**: `.venv/` in the semantic-graph directory
- **SurrealDB**: runs as background process, data at `surrealkv:/home/ian/open-brain/data/brain.db`
- **Env vars**: `~/.openclaw/.env` (load with `export $(grep -v "^#" ~/.openclaw/.env | xargs)`)
- **Sync**: `sync-genesis.sh` (local script, gitignored) rsyncs to/from server

## Running the Pipeline

```bash
# On server
cd ~/.openclaw/workspace-genesis/skills/semantic-graph
export $(grep -v "^#" ~/.openclaw/.env | xargs)

# Full pipeline for a new document
.venv/bin/python pipeline.py ingest /path/to/doc.pdf --embed -v
.venv/bin/python pipeline.py embed-chunks
.venv/bin/python pipeline.py resolve
.venv/bin/python pipeline.py communities detect --summarize

# Query
.venv/bin/python pipeline.py retrieve "your question here" --hops 2

# Check quality
.venv/bin/python pipeline.py evaluate health
.venv/bin/python pipeline.py evaluate retrieval
.venv/bin/python pipeline.py stats
```

## File Dependencies

```
pipeline.py
  -> graph_extract.py -> llm_parser.py -> verbs.py
                      -> grammar_triangle.py
                      -> schema.surql (via ensure_schema)
  -> embeddings.py (OpenRouter API)
  -> retriever.py -> embeddings.py
  -> communities.py -> embeddings.py
  -> entity_resolution.py -> embeddings.py
  -> evaluate.py -> retriever.py
  -> cleanup.py
  -> viz/graph_viz.py
```

All modules share: `surrealdb` (AsyncSurreal, RecordID), `openai` (via OpenRouter)
