# Genesis Brain — Knowledge Infrastructure Architecture

**Version:** 0.1 (draft)
**Date:** 2026-04-21
**Status:** Live, single-node. Sync pipeline needs rebuilding.

---

## Overview

The Genesis Brain is a two-layer knowledge system:

1. **Document Layer (Radicle)** — Versioned markdown documents, replicated across a p2p network
2. **Knowledge Graph Layer (SurrealDB)** — Semantic graph with concepts, relations, vector embeddings, community detection

These are **separate systems**. They do not auto-sync. The pipeline between them is manual/scripted.

---

## Layer 1: Document Layer — Radicle

**Purpose:** Decentralized, version-controlled document storage with p2p replication. Single source of truth for community knowledge documents.

| Field | Value |
|-------|-------|
| RID | `rad:z4WAr7CiNkf5JAoAb1srwi7gDz8nU` |
| Local path | `~/.radicle/regen-tribes-notes` |
| Seeds synced | ~14 (afteraction noted 26+ before the repo wipe; current count unverified since rad node isn't running) |
| Web UI | https://app.radicle.xyz/nodes/iris.radicle.xyz/rad:z4WAr7CiNkf5JAoAb1srwi7gDz8nU |
| Protocol | git-over-radicle (SSH blocked from Hetzner, uses wire protocol) |
| Node command | `rad node start` (requires `RAD_PASSPHRASE` env var) |

**What it does:**
- Stores markdown documents as a Git repo
- Replicates to public seed nodes (no server needed)
- RIDs are permanent — renaming a project changes only the identity doc, not the RID
- `rad sync` propagates changes within ~20-30 seconds

**Current state (2026-04-21):**
- Repo is empty — wiped clean after a failed mass-publish attempt (161 docs published with no stable format, then reset)
- Skill scripts exist in `skills/regen-tribes-notes/` but need rewriting before use
- `skills/radicle/SKILL.md` has the full command reference

**Key limitations:**
- SSH outbound to radicle.xyz blocked from Hetzner VPS — must use wire protocol
- No issues/PRs equivalent in the way GitHub has (lean feature set intentionally)
- Publishing workflow was never stabilized — next attempt should start with 3 test docs

---

## Layer 2: Knowledge Graph — SurrealDB

**Purpose:** Semantic query layer. Answers questions, finds relationships, surfaces connections across documents. This is what Genesis queries when you ask "what do you know about X."

| Field | Value |
|-------|-------|
| URL | `ws://127.0.0.1:8000` |
| Namespace | `semantic_graph/main` |
| Auth | `root` / `SURREAL_PASS` (from `~/.openclaw/.env`) |
| Service | `surrealdb.service` (user systemd) |
| Process | `surrealdb start --log debug --kvs vledb --ns semantic_graph --db main` |

**Current stats (2026-04-21):**
- 149 documents ingested
- 4,524 text chunks
- 3,413 concepts
- 3,872 relations
- 4,216 mentions
- 3,413 embedded concepts (1536d vectors via OpenAI text-embedding-3-small)

**Schema (from `schema.surql`):**
- Node tables: `document`, `chunk`, `concept`, `community`
- Edge tables: `contains`, `mentions`, `relates`, `belongs_to`
- HNSW vector index on concept and chunk embeddings

---

## The Pipeline — Connecting Docs to Graph

This is the **missing link** between the two layers.

### Pipeline Architecture

```
[File: PDF, DOCX, HTML, MD, etc.]
        ↓
[Kreuzberg] — text extraction (75+ formats, OCR)
        ↓
[Chunking] — split into ~512 token segments
        ↓
[LLM Parser] — extract concepts + relations (OpenRouter, configurable model)
        ↓
[Entity Resolution] — NumPy cosine similarity deduplication
        ↓
[Community Detection] — label propagation + LLM summaries
        ↓
[Embedding] — OpenAI text-embedding-3-small via OpenRouter
        ↓
[SurrealDB] — stored as nodes + edges
```

### Pipeline Scripts

All live in `skills/semantic-graph/`, require venv + env activation:

```bash
cd ~/.openclaw/workspace-genesis/skills/semantic-graph
source .venv/bin/activate
export $(grep -v "^#" ~/.openclaw/.env | xargs)
```

| Command | Purpose |
|---------|---------|
| `python pipeline.py ingest <file> --embed -v` | Full ingest + embed + verbose output |
| `python pipeline.py retrieve "<query>" --hops 2 --json` | Hybrid search (vector + graph + chunks + communities) |
| `python pipeline.py search "<query>" --limit N` | Vector-only similarity search |
| `python pipeline.py communities detect --summarize` | Detect + summarize thematic clusters |
| `python pipeline.py embed` | Re-embed all concepts |
| `python pipeline.py export -o file.json` | Export graph as JSON |

### Hybrid Retrieval (`retrieve`)

When you ask Genesis a knowledge question, it uses hybrid retrieval combining:

1. **Vector search** — cosine similarity on concept/chunk embeddings
2. **Graph traversal** — N-hop edge following (default 2 hops)
3. **Community summaries** — thematic clusters matching the query
4. **Source chunks** — original text passages with evidence quotes
5. **RRF + MMR** — Reciprocal Rank Fusion + Maximal Marginal Relevance for result ranking

### Genesis Brain Scripts (convenience wrappers)

In `skills/genesis-brain/scripts/` (these wrap the pipeline):

| Script | Purpose |
|--------|---------|
| `ingest.sh <file> [author]` | Ingest file → returns JSON with concept/relation counts + connections |
| `query.sh "<query>" [limit]` | Hybrid search → returns JSON with concepts, relations, chunks, communities |
| `capture.sh "<text>"` | Capture inline text snippet → returns doc_id |
| `relate.sh "<A>" "<B>"` | Find graph relationships between two concepts |
| `stats.sh` | Return graph statistics |

---

## Two Modes of Ingestion

### Mode A: File Ingestion (manual)

User shares a file → Genesis saves it → runs `ingest.sh` → results posted to Telegram.

```
Telegram file attachment
  → download via Bot API
  → save to /tmp/genesis-ingest/
  → pipeline.py ingest --embed
  → SurrealDB
  → respond with summary
```

Triggered by: file attachments, shared links, "read this", "ingest this"

### Mode B: Inline Capture (manual)

User says "remember this" → text captured to temp file → `pipeline.py ingest` → SurrealDB.

```
User message: "remember this..."
  → save to /tmp/genesis-ingest/capture-TIMESTAMP.md
  → pipeline.py ingest --embed
  → SurrealDB
  → brief confirmation
```

Triggered by: "remember this", "store this", "learn this"

### Mode C: Radicle → SurrealDB (MISSING — needs rebuilding)

Current gap: documents pushed to Radicle do NOT automatically appear in SurrealDB.

To rebuild:
1. Clone/pull from radicle repo
2. Run `batch_ingest_v2.py` across the document set
3. This was attempted before but the ingest script (`skills/radicle/ingest-kbase-v2.py`) is now missing

---

## What's Missing / Needs Work

| Gap | Priority | Notes |
|-----|----------|-------|
| Radicle → SurrealDB sync | High | No automated pipeline. Docs in radicle stay in radicle. |
| Stable radicle publish format | High | Repo is empty. Next attempt needs format defined FIRST. |
| Ingest script for radicle kbase | High | No ingest script exists for pulling radicle docs into SurrealDB. The `skills/regen-tribes-notes/` directory has publish scripts but nothing for the reverse direction (radicle → graph). Needs building from scratch. |
| Multi-node SurrealDB replication | Low | Single-node only. No cross-instance sync. |
| Live visualization | Low | `live_server.py` exists but not deployed |

---

## Environment Variables

From `~/.openclaw/.env` (loaded by pipeline scripts):

| Variable | Used by | Purpose |
|----------|---------|---------|
| `SURREAL_PASS` | SurrealDB auth | Database authentication |
| `OPENROUTER_API_KEY` | Pipeline | LLM extraction + embeddings via OpenRouter |
| `RAD_PASSPHRASE` | Radicle node | Node startup passphrase |
| `TELEGRAM_BOT_TOKEN` | Telegram | Bot API for file downloads |

---

## Tech Stack — Why Each Piece

**Radicle (p2p Git)** — Chosen to avoid single-server dependency. The original goal was a document store that doesn't rely on GitHub/GitLab or any centralized service. Radicle replicates documents across publicly operated seed nodes, so no single provider can disappear or deplatform the community. It speaks native Git, so nothing special is needed to read or write — just `git push rad` once the remote is configured. SSH outbound from Hetzner is blocked, so sync uses the wire protocol instead of git-over-SSH.

**Kreuzberg** — The document extraction library. Chosen because community knowledge arrives in every conceivable format: PDFs from members, DOCX templates, HTML pages, plain markdown, screenshots with OCR needs, Slack exports, email threads. Kreuzberg handles 75+ formats through a single API, so the ingest pipeline doesn't break when someone shares a PDF instead of a text file. One library, unified output, no format-by-format handlers to maintain.

**OpenRouter + OpenAI text-embedding-3-small** — Chosen for flexibility and cost. OpenRouter is a unified gateway to multiple LLM providers, meaning the extraction model can be swapped (or cost-optimized) without changing code. Embeddings use OpenAI's `text-embedding-3-small` at 1536 dimensions — not the cheapest, but the quality-to-cost ratio is the best in its class for semantic search. Both flow through OpenRouter, so one API key covers both extraction and embedding.

**SurrealDB v3** — Chosen because a knowledge graph needs a graph database, not a document store. SurrealDB speaks SurrealQL which treats edges as first-class citizens — `concept_a->relates->concept_b` is a native query, not a foreign-key workaround. It ships with HNSW vector indexes built in, so concept similarity and graph traversal live in the same database without a separate vector store. The namespace/database model maps cleanly to the "one graph per community" design. Runs as a single binary, no JVM, deploys in minutes.

**Hybrid retriever** — Not a separate product but a custom retrieval strategy. A pure vector store misses the structural relationships (X is_part_of Y, X enables Y); a pure graph traversal misses semantic similarity (X is conceptually close to Y even if unlinked). The hybrid retriever combines vector similarity, N-hop graph traversal, community summary matching, and source chunk retrieval — then fuses all four signal types with Reciprocal Rank Fusion and reranks with Maximal Marginal Relevance to avoid redundancy. The result is retrieval that neither keyword search nor pure embedding could produce alone.

**Community detection (label propagation + LLM summaries)** — Knowledge doesn't organize into a clean tree. Concepts cluster in overlapping, messy ways — EROI, Net Energy, and fossil fuel economics might share one community, while EROI, soil carbon, and regenerative agriculture share another. Label propagation finds these natural clusters without requiring the number of communities to be specified upfront. Each cluster then gets an LLM-generated summary so the retriever can match a query to a whole thematic area without matching any single concept exactly.

**Entity resolution (NumPy cosine similarity + LLM confirm)** — Different documents use different names for the same concept. "EROI," "Energy Return on Investment," and "energy return ratio" might all appear across the corpus. NumPy's cosine similarity matrix catches near-duplicates cheaply; the LLM confirmation step prevents false merges. This keeps the graph clean — same concept linked across many docs, not scattered as noise.

**3d-force-graph visualization** — Chosen for the "wow, look at what we know" effect. A knowledge graph that only lives in JSON is invisible to humans. The 3d-force-graph renders the full graph as an interactive self-contained HTML file — concepts as nodes, relations as edges, communities as colors. It makes the collective knowledge tangible in a way that numbers on a dashboard can't.

---

## File Locations

| What | Where |
|------|-------|
| Pipeline code | `~/.openclaw/workspace-genesis/skills/semantic-graph/` |
| Genesis Brain skill | `~/.openclaw/workspace-genesis/skills/genesis-brain/` |
| Radicle skill | `~/.openclaw/workspace-genesis/skills/radicle/` |
| Radicle publish scripts | `~/.openclaw/workspace-genesis/skills/regen-tribes-notes/` (publish.sh, publish-file.sh, add-index.sh) |
| Convenience scripts | `skills/genesis-brain/scripts/` |
| Radicle local repo | `~/.radicle/regen-tribes-notes/` |
| Community docs | `~/.openclaw/workspace-genesis/docs/` |
| Daily memory | `~/.openclaw/workspace-genesis/memory/YYYY-MM-DD.md` |
