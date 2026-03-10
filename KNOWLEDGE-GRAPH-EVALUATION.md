# RegenTribes Knowledge Graph — Research Evaluation

Research-backed evaluation of our current implementation against industry best practices for knowledge graph + vector RAG systems (March 2026).

---

## What We're Doing Right

### 1. Hybrid Graph + Vector Architecture
Our dual approach — SurrealDB graph storage with HNSW vector embeddings — aligns with the consensus architecture. The industry has converged on "HybridRAG" as the recommended pattern: vector search for broad semantic recall, graph traversal for structured multi-hop reasoning. We have both.

### 2. LLM-Based Entity Extraction
Using Claude via OpenRouter for concept/relation extraction is the standard approach. KGGen (2025) benchmarks show LLM extraction produces 98% valid triples vs 55% for rule-based OpenIE. Our `llm_parser.py` follows this pattern correctly.

### 3. Evidence-Based Confidence (NARS)
Our NARS truth values (frequency, confidence, evidence_count) with a revision formula for evidence accumulation are *more sophisticated than most implementations*. Most systems use simple counts or binary flags. NARS gives us calibrated epistemic state that improves with each new document — this is genuinely novel and valuable.

### 4. Stable ID Deduplication
SHA256-based concept IDs from `(name.lower(), type)` handle basic deduplication. This is the simplest correct approach and prevents duplicate nodes for identical mentions.

### 5. Rich Metadata on Chunks
The Grammar Triangle (NSM + Qualia + Causality) is unusual and potentially valuable — zero-cost semantic fingerprinting before any LLM call. No other system we found does this. It could become a powerful filtering/routing signal.

### 6. Verb Taxonomy
Our 144-verb taxonomy with fuzzy normalization is more structured than most. GraphRAG implementations typically allow free-form relation types, which KGGen shows leads to sparsity (unique relation types nearly equaling edge count). Our controlled vocabulary avoids this.

---

## Critical Gaps

### Gap 1: No Community Detection (HIGH PRIORITY)

**What the research says:** Microsoft's GraphRAG and Zep both use community detection (Leiden algorithm or label propagation) to cluster densely-connected entities into communities, then generate community-level summaries. This enables "global search" — answering questions that require synthesizing information across many documents.

**Why it matters for RegenTribes:** A community of people naturally forms clusters (project teams, neighborhood groups, interest circles). Community detection would automatically surface these clusters and generate summaries like "The food sovereignty group includes 12 members focused on urban farming, seed saving, and community gardens."

**What we're missing:** We have no community detection. Every query must start from a specific concept and fan out. There's no way to ask "what are the main themes across everything you've learned?" — which is exactly the kind of question a community organizer needs answered.

**Recommendation:** Implement Leiden or label propagation on the concept graph. Store community nodes with LLM-generated summaries. Enable global search that queries community summaries first, then drills into entities.

---

### Gap 2: No Retrieval Pipeline for RAG (HIGH PRIORITY)

**What the research says:** The whole point of a knowledge graph for AI is *retrieval-augmented generation* — when a user asks a question, the system should: (1) search vectors for relevant concepts, (2) traverse the graph for connected context, (3) construct a rich context window, (4) feed it to the LLM for response generation.

Modern systems use multi-strategy retrieval:
- Cosine similarity (vector search)
- BM25 full-text search
- Breadth-first graph traversal (n-hop neighbors)
- Reciprocal Rank Fusion to merge results
- Reranking (MMR, cross-encoder, frequency-based)

**What we have:** Our `search` function does vector-only retrieval. Our `relate.sh` does basic graph queries. But nothing *combines* them into a unified retrieval pipeline that could serve as context for LLM generation.

**What we're missing:** A `retrieve(query) -> context` function that:
1. Embeds the query and finds top-k concepts by cosine similarity
2. For each hit, traverses 1-2 hops of graph edges to get related concepts + relations
3. Optionally includes community summaries
4. Applies reranking (at minimum, reciprocal rank fusion)
5. Formats everything into a structured context string for LLM consumption

**Recommendation:** Build a `retriever.py` that implements hybrid search (vector + graph + optional BM25). This is the single highest-value addition — it turns the knowledge graph from a database into an AI brain.

---

### Gap 3: No Entity Resolution Beyond Exact Match (HIGH PRIORITY)

**What the research says:** Entity resolution is the #1 challenge in knowledge graph construction. The same entity appears as "permaculture", "Permaculture", "permaculture design", "PDC" — our current system creates separate nodes for each because the `sha256(name.lower() + "_" + type)` only deduplicates exact case-insensitive matches.

Best practices (from KGGen, Zep, Neo4j agent-memory):
- **Embedding-based clustering**: S-BERT embeddings + k-means to find candidate duplicates
- **LLM-based resolution**: Within each cluster, ask the LLM "are these the same entity?"
- **Multi-strategy matching**: exact + fuzzy string + semantic similarity
- **Alias tracking**: Store all variant names as aliases on the canonical entity

**What we have:** Exact name+type matching only. We store aliases but don't use them for dedup.

**Impact:** With 5,184 concepts from only 10 documents, we almost certainly have significant duplication. This fragments the graph and weakens retrieval.

**Recommendation:** Add a post-processing entity resolution step:
1. Embed all concept names with S-BERT
2. Cluster with cosine similarity > 0.85
3. Within clusters, use LLM to confirm merges
4. Merge nodes, combine NARS evidence, redirect edges

---

### Gap 4: No Temporal Model (MEDIUM PRIORITY)

**What the research says:** Zep implements bi-temporal modeling — tracking both when facts were true in reality and when they entered the system. Facts aren't deleted; they're invalidated with timestamps. This enables:
- "What did we know about X as of last month?"
- Contradiction detection (new fact invalidates old fact)
- Temporal reasoning ("A happened before B")

**What we have:** We have `valid_from`/`valid_until` fields on relations and `created_at` timestamps, but:
- Nothing ever sets `valid_until` (facts never expire)
- No contradiction detection between new and existing facts
- No temporal queries in our retrieval pipeline

**Recommendation:** When ingesting new facts, compare against existing edges between the same entity pairs. If contradictory, set `valid_until` on the old edge. Track the invalidation chain.

---

### Gap 5: No Episodic Memory Layer (MEDIUM PRIORITY)

**What the research says:** Both Zep and Neo4j agent-memory implement a three-tier memory hierarchy:
1. **Episodic** — raw conversation/document records (non-lossy)
2. **Semantic** — extracted entities and relations
3. **Community** — clustered summaries

The episodic layer preserves raw context that the extraction might miss. It enables re-extraction with better models later, and provides provenance for debugging.

**What we have:** We store documents and chunks (which is the episodic layer), but our retrieval never touches them. We only search concepts. The raw text in chunks is invisible to queries.

**Recommendation:** Include chunk text in retrieval results alongside concept matches. When a concept matches, also return the source chunks that mention it — this gives the LLM the original language, not just the extracted summary.

---

### Gap 6: Missing Community-Specific Ontology (MEDIUM PRIORITY)

**What the research says:** For community organizations, the ontology should include:
- **Person** — members with skills, interests, roles
- **Project** — initiatives, working groups
- **Event** — meetings, workshops, gatherings
- **Skill** — capabilities, expertise areas
- **Resource** — tools, land, materials, funding
- **Place** — neighborhoods, sites, gardens

With relationships like: `Person --HAS_SKILL--> Skill`, `Person --MEMBER_OF--> Project`, `Project --NEEDS--> Skill`, `Person --ATTENDED--> Event`, `Project --LOCATED_AT--> Place`.

**What we have:** Our 11 generic concept types (entity, system, process, idea, attribute, event, person, place, quantity, quality, relation) are too abstract. The LLM assigns them, but there's no guidance toward community-relevant categories.

**Recommendation:** Extend the extraction prompt with RegenTribes-specific entity types and a seed ontology. Add `skill`, `project`, `resource`, `organization`, `practice` as first-class types. Add relationship types like `MEMBER_OF`, `HAS_SKILL`, `NEEDS`, `LOCATED_AT`, `PRACTICED_BY`.

---

### Gap 7: No Chunk-Level Embedding / Hybrid Retrieval (MEDIUM PRIORITY)

**What the research says:** Most RAG systems embed *chunks* (the actual text passages), not just extracted entities. This enables direct passage retrieval — finding the exact paragraph that answers a question. Our system only embeds concepts (short "name (type): description" strings).

**What we're missing:** When someone asks "what did Maria say about composting at the last meeting?", we need to find the actual chunk of text, not just the concept "composting".

**Recommendation:** Add embeddings to the chunk table alongside concept embeddings. During retrieval, search both concept embeddings (for structured knowledge) and chunk embeddings (for passage-level recall). Fuse results.

---

### Gap 8: Relation Count Anomaly (HIGH PRIORITY — BUG?)

**Current state:** ~5,184 concepts but only ~30 relations across 10 documents. This ratio is wildly off — a healthy knowledge graph typically has 2-5x more edges than nodes.

**Likely cause:** The `RELATE` command in `graph_extract.py` may not be persisting correctly in SurrealDB v3. The code uses `RELATE $subj->relates->$obj SET ...` but the stable ID (`relates:hash`) is computed but never used in the RELATE command — SurrealDB generates its own edge IDs, so NARS revision for duplicate edges may not be working, and worse, edges may be silently failing.

**Recommendation:** Debug this immediately. Run a test ingestion with verbose logging and verify edges are actually created. This could be the single biggest issue — a knowledge graph with almost no edges is just a list of concepts.

---

### Gap 9: No Reranking or Result Quality Control (LOW-MEDIUM)

**What the research says:** Zep uses 5 different rerankers:
- Reciprocal Rank Fusion (RRF) for combining search methods
- Maximal Marginal Relevance (MMR) for diversity
- Episode-mention frequency reranker
- Node distance reranker
- Cross-encoder LLM relevance scoring

**What we have:** Raw cosine similarity ordering. No reranking, no diversity, no fusion.

**Recommendation:** At minimum, implement RRF when combining vector + graph results. Consider MMR for diverse results.

---

### Gap 10: No Evaluation or Quality Metrics (LOW-MEDIUM)

**What the research says:** KGGen introduced the MINE benchmark. GraphRAG uses comprehensiveness, diversity, and factual accuracy metrics. The industry consensus is: you need automated evaluation.

**What we have:** No tests, no benchmarks, no extraction quality measurement.

**Recommendation:** Build a small evaluation set: 5-10 documents with manually labeled expected concepts and relations. Measure extraction F1. Track it over time as you improve the pipeline.

---

## Priority Roadmap

### Phase 1: Fix Foundations (immediate)
1. **Debug the relation storage bug** — verify edges actually persist in SurrealDB
2. **Add entity resolution** — embedding-based clustering + LLM confirmation
3. **Build the hybrid retrieval pipeline** — vector + graph + chunk text → structured context

### Phase 2: Community-Ready (next)
4. **Add community detection** — Leiden algorithm → community summaries
5. **RegenTribes ontology** — Person, Project, Skill, Resource, Event, Place, Practice
6. **Chunk-level embeddings** — embed raw text alongside concepts
7. **Temporal fact management** — contradiction detection + edge invalidation

### Phase 3: Production Quality (COMPLETE)
8. **Reranking** — RRF + MMR for retrieval quality ✓
9. **Evaluation framework** — graph health, retrieval benchmarks, extraction F1 ✓
10. **Episodic retrieval** — source chunks + community summaries in query results ✓

### Baseline Metrics (March 2026)
- Graph: 1505 concepts, 1584 relations, 605 chunks, 210 communities, 34 documents
- Edge/Node ratio: 1.05 (healthy range: 1.0-5.0)
- Embedding coverage: 100% concepts, 100% chunks
- Orphan concepts: 9.0% (135/1505 — no edges)
- Type balance: 0.70 (14 concept types, dominated by system/process)
- Retrieval: 75% pass rate, 59% concept recall, 91% theme coverage
- Latency: p50=5.3s, p95=6.6s (includes 2 embedding API calls for domain search)

### Domain-Aware Retrieval (enhancement beyond original roadmap)
- 12 RegenTribes domains defined (finance, food, energy, water, governance, people, land, legal, construction, community, education, technology)
- Domain detection from query keywords → type boost weights
- Dual vector search: original query + domain-focused rewritten query
- Weighted RRF fusion (domain results get 2x weight)
- Name deduplication with stemming (75% word overlap threshold)
- Before/after on funding query: "Capital Requirements" + "Financial Model" now in top 10 (were absent)

---

## Sources

- [Zep: Temporal Knowledge Graph Architecture for Agent Memory](https://arxiv.org/html/2501.13956v1) — Zep's three-tier hierarchy, bi-temporal modeling, entity resolution, and retrieval benchmarks
- [Neo4j Agent Memory](https://github.com/neo4j-labs/agent-memory) — POLE+O schema, multi-strategy deduplication, hybrid retrieval
- [KGGen: Extracting Knowledge Graphs from Plain Text](https://arxiv.org/html/2502.09956v2) — Entity resolution via embedding clustering + LLM, MINE benchmarks, sparsity reduction
- [Microsoft GraphRAG](https://microsoft.github.io/graphrag/) — Community detection with Leiden, local/global/DRIFT search, hierarchical summarization
- [Weaviate: Exploring RAG and GraphRAG](https://weaviate.io/blog/graph-rag) — Hybrid vector+graph retrieval architecture, Weaviate+Neo4j integration
- [Memgraph: HybridRAG](https://memgraph.com/blog/why-hybridrag) — Vector-first retrieval → graph enrichment pattern
- [GraphRAG Complete Guide 2026](https://calmops.com/ai/graphrag-complete-guide-2026/) — Schema design, entity extraction, reciprocal rank fusion
- [Multi-Layer Knowledge Graphs for Community Management](https://medium.com/togethercrew/multi-layer-knowledge-graphs-and-their-cutting-edge-applications-for-community-management-9d317e1447a0) — Interaction graphs vs information graphs, gap detection
- [Knowledge Graph for Community Building](https://www.meegle.com/en_us/topics/knowledge-graphs/knowledge-graph-for-community-building) — Community ontology design (members, skills, resources)
- [RAG in 2026: Bridging Knowledge and Generative AI](https://squirro.com/squirro-blog/state-of-rag-genai) — RAG as "knowledge runtime" concept
- [GraphRAG & Knowledge Graphs: AI-Ready for 2026](https://flur.ee/fluree-blog/graphrag-knowledge-graphs-making-your-data-ai-ready-for-2026/) — Enterprise knowledge graph maturity
- [Nature: RAG Model Based on Knowledge Graph](https://www.nature.com/articles/s41598-025-21222-z) — Academic evaluation of KG-enhanced RAG
