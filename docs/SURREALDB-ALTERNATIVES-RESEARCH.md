# SurrealDB & Alternatives — Research Document

**Version:** 0.1 (draft)
**Date:** 2026-04-21
**Research scope:** Compare SurrealDB to alternatives for the Genesis Brain use case (knowledge graph + vector search + document storage for a community AI agent). Include industry direction.

---

## The Core Question

Genesis Brain currently uses **SurrealDB v3** as its knowledge graph. Should it stay there, or should the architecture shift?

The answer depends on: whether SurrealDB's multi-model approach is genuinely better than composable best-of-breed (a dedicated vector DB + a dedicated graph DB), and where the industry is moving.

---

## 1. SurrealDB — Current Choice

### What It Is

SurrealDB is a **multi-model database** built in Rust that natively fuses document, graph, relational, key-value, time-series, and vector data into a single engine with one query language (SurrealQL) and one ACID transaction boundary.

GitHub: `surrealdb/surrealdb` — 30k+ stars. Built by a well-funded startup (~£20M Series A).

### Strengths

- **Single transaction across all models** — a write to a graph edge, a document, and a vector index either all succeed or all fail. No partial-write corruption between systems.
- **One query, one round trip** — SurrealQL composes graph traversal (`->`), vector similarity (`vector::similarity::cosine`), full-text search, and temporal filtering in a single statement. No multi-system orchestration.
- **Built for AI agents** — their positioning is explicitly "the context layer for AI agents." Spectron (their memory layer) + SurrealDB = working memory + semantic memory + episodic memory + procedural memory all in one engine.
- **Built-in auth and row-level permissions** — not an afterthought. `DEFINE ACCESS` with RECORD type, `crypto::argon2`, and `PERMISSIONS FOR` clauses live inside the database.
- **No glue code** — the database is also the API backend. `DEFINE TABLE` + `DEFINE FUNCTION` gives you a REST/WebSocket API without writing a separate service.
- **Runs the way you want** — embedded (WASM in browser), edge, single-node self-hosted, or distributed cluster. Storage can be commodity object storage (S3/GCS/Azure Blob) with compute-storage separation.
- **Native HNSW vector indexes** — not bolted on. `embedding <|20,COSINE|> $vec` is a first-class index type.

### Weaknesses

- **Young — v3 is still maturing** — the storage engine (Spectrometa) was rewritten for v3. Some edge cases in distributed mode are still being ironed out.
- **SurrealQL is novel** — no Cypher, no Gremlin, no SPARQL. Teams with existing graph expertise face a learning curve. SurrealQL is SQL-inspired but fundamentally different.
- **No native full-text stemmer** — depends on an external stemming server for certain languages.
- **Distributed consensus is newer** — the Raft-based clustering in v3 is less battle-tested than Neo4j's causal clustering or CockroachDB's distributed SQL.
- **Ecosystem** — fewer integrations than Neo4j (which has a massive connector ecosystem: Tableau, PowerBI, Apache Spark, etc.).
- **Vendor lock-in risk** — SurrealDB Cloud is the managed offering. If the startup stumbles, self-hosting is fine but the cloud roadmap may shift.

### Where SurrealDB Is Headed

SurrealDB's current push is **Spectron** — their "agent memory layer." The thesis: AI agents fail not because of model capability but because of context fragmentation across five systems (vector DB, graph DB, document store, auth service, cache). Spectron + SurrealDB = one transaction from storage to memory. They're explicitly building for the agentic AI era.

---

## 2. Neo4j — The Enterprise Graph Standard

### What It Is

The established leader in graph databases. Property graph model with **Cypher** query language (openCypher, now standardized). AuraDB is the managed cloud offering. Used heavily in fraud detection, knowledge graphs, network/IT ops, and recommendation systems.

### Strengths

- **Battle-tested at scale** — Neo4j has been production-hardened for 15+ years. Fortune 500 deployments with billions of nodes/edges.
- **Cypher is excellent** — expressive, readable, now an open standard. Widely adopted beyond Neo4j (Amazon Neptune, RedisGraph, etc.).
- **Massive ecosystem** — connectors for Spark, Tableau, PowerBI, TIBCO, Kafka, Python (Py2Neo), Java, JavaScript. If you need to integrate with an existing enterprise stack, Neo4j has the connector.
- **Graph data science** — native graph algorithms (PageRank, community detection, pathfinding, centrality) with a trained model library. Excellent for knowledge graph inference.
- **Bloom visualization** — native graph visualization tool for exploration.
- **Strong commercial support** — enterprise SLAs, professional services, certified partners.

### Weaknesses

- **Single-model (graph only)** — Neo4j is not a vector store, not a document store, not a time-series DB. To use it with vectors, you'd add Pinecone or link to an embedding pipeline. The multi-system orchestration problem SurrealDB solves doesn't exist in Neo4j's DNA.
- **Licensing cost** — AuraDB (managed) is not cheap. Self-hosted requires significant ops investment.
- **Inflexible schema** — label-overloaded property model can get messy at scale. `(:Person {name})-[:KNOWS]->(:Person {name})` vs. typed edges with specific properties requires careful design.
- **Not built for agents** — you'd need to layer on a separate vector DB, document store, and auth service. Same fragmentation problem.

### Verdict for Genesis Brain

Neo4j is overkill for a community knowledge graph of 3,400 concepts. The licensing, ops overhead, and single-model limitation don't fit a small community's resources. But for a large enterprise building a serious knowledge graph with deep integration needs, Neo4j remains the safe bet.

---

## 3. Dedicated Vector DBs — Pinecone, Weaviate, Qdrant

### What They Are

Vector databases are purpose-built for **semantic similarity search** — storing embeddings and finding the K nearest neighbors. Essential for RAG (Retrieval Augmented Generation) in LLM pipelines.

### How They Compare

| | **Pinecone** | **Weaviate** | **Qdrant** |
|---|---|---|---|
| **Hosting** | Cloud-only (managed) | Self-hosted or cloud | Self-hosted or cloud |
| **Vector models** | HNSW, FLAT | HNSW, PQ | HNSW, PQ, binary |
| **Multi-tenancy** | Yes | Yes | Yes (payload-based) |
| **Built-in ML** | Sparse + dense hybrid | Sparse (BM25) + dense hybrid | Sparse + dense hybrid |
| **Graph connectors** | None native | Yes (import from 60+ sources) | None native |
| **Cost** | ~$70-700/mo managed | Free (self-hosted) / ~$50/mo cloud | Free (self-hosted) / managed available |
| **Best for** | Pure vector similarity | Semantic search with connectors | Payload-rich filtered search |

### Strengths

- **Best-in-class vector search** — HNSW with quantization, hybrid sparse+dense, filtered search. Purpose-built for this one thing.
- **Cloud-native** — Pinecone and Qdrant Cloud require zero ops.
- **Active development** — all three are well-funded and moving fast.

### Weaknesses

- **No graph traversal** — can't query "find X where X->relates->Y->part_of->Z". They're flat similarity engines, not graph databases.
- **Still need a primary database** — documents, auth, user sessions, relationships all need somewhere else. A vector DB alone is not a knowledge system.
- **Redundant with SurrealDB** — SurrealDB's HNSW implementation is competitive with dedicated vector DBs for most use cases. Adding Pinecone on top of SurrealDB would be redundant.

### Verdict for Genesis Brain

If Genesis Brain needed only vector search (pure RAG), Qdrant or Weaviate would be strong candidates — especially Qdrant for self-hosted zero-cost. But the use case includes typed relations, community detection, and NARS epistemic values — all of which need graph semantics, not flat vectors.

---

## 4. Amazon Neptune — AWS-Integrated Graph

### What It Is

AWS's managed graph database supporting **Apache TinkerPop Gremlin** (property graph) and **SPARQL** (RDF). Part of the AWS ecosystem, tightly integrated with IAM, VPC, CloudWatch.

### Strengths

- **Zero-ops managed** — fully serverless option available. No database administration.
- **IAM-native security** — fine-grained access control through AWS's identity model.
- **Neptune Analytics** — new engine for graph analytics (PR, community detection) with 10x faster Louvain community detection than openCypher Gremlin.

### Weaknesses

- **Dual-model confusion** — Gremlin vs. SPARQL are fundamentally different data models. Choosing wrong at design time is painful to migrate.
- **Expensive** — serverless Neptune can run $0.02/hour with per-query charges that scale unpredictably.
- **AWS-only** — not an option for a community project without cloud vendor commitment.
- **No native vectors** — Neptune added vector search only via an extension (neptune-ml). Not first-class.

### Verdict for Genesis Brain

Not relevant. AWS dependency, no native vectors, wrong fit for a small community project.

---

## 5. TiDB (PingCAP) — Distributed SQL with HTAP

### What It Is

MySQL-compatible distributed SQL database (NewSQL) with HTAP (Hybrid Transactional/Analytical Processing) capabilities. Not a graph database, but often considered for knowledge graphs because it handles documents + SQL + analytics.

### Strengths

- **Horizontal scale** — MySQL-compatible with TiKV under the hood. Scales to petabytes.
- **HTAP** — runs OLTP and OLAP workloads on the same data without ETL pipelines.
- **Strong open-source lineage** — PingCAP backs TiDB, with significant enterprise adoption in Asia.

### Weaknesses

- **No graph model** — no native graph traversal, no edge tables, no graph query language. Not a graph database at all — just a very good distributed SQL DB.
- **No native vectors** — requires a separate vector index layer.

### Verdict for Genesis Brain

Not a contender for the knowledge graph layer.

---

## 6. NebulaGraph — Purpose-Built Distributed Graph

### What It Is

Open-source distributed graph database optimized for large-scale graphs (billions of vertices/edges). Used by Xiaomi, Meituan, Uber. nGQL is the query language.

### Strengths

- **Scales beyond Neo4j** — designed for ultra-large graphs. Better performance than Neo4j at >100B edges.
- **Open-source** — Apache 2.0, with a managed NebulaGraph Cloud.
- **Good for hot/cold graph partitioning** — separates frequently accessed subgraph from archive data.

### Weaknesses

- **nGQL is non-standard** — similar to Cypher but different enough to require full rewrite.
- **No vectors, no documents** — pure play graph. Still needs a separate vector DB and document store.
- **Smaller ecosystem** — far fewer integrations, connectors, and community resources than Neo4j.

### Verdict for Genesis Brain

Overkill for 3,400 concepts. Designed for internet-scale graphs. But worth knowing as an option if the RegenTribes knowledge graph grows to millions of concepts.

---

## 7. Industry Direction — Where Is This All Going?

### The Agentic AI Shift Is Reshaping Database Design

The single biggest trend: **AI agents need a single system for context, not a pipeline of five databases.**

From Stanford's 2026 AI Index: agents approach human performance on benchmarks, $582B+ invested in AI, and the bottleneck is no longer model capability — it's **context reliability**. Agents need persistent memory that spans sessions, not just prompt context within a session.

The database industry is responding:

**SurrealDB's bet** — they call it "the context layer." One engine, one transaction, from object storage to agent memory. This is the most direct answer to the fragmentation problem.

**Oracle, MongoDB, SingleStore** — all adding vector indexes to existing document/relational databases. "We already have your data, just add embeddings." The pitch: don't add another system, extend what you have.

**Neo4j's positioning** — leaning into "Graph Intelligence" for AI. LangChain integration, LlamaIndex integration, GQL (Graph Query Language, ISO-standardized in 2024). Positioned as the structured reasoning layer for AI.

**The convergence thesis** — databases are moving toward:
1. **Multi-model** (graph + vector + document + full-text in one)
2. **Built-in embedding generation** (not just storage)
3. **ACID consistency for hybrid workloads** (transactions that span graph and vectors)
4. **Row-level security as a first-class feature** (not bolted on)

The old separation (vector DB for embeddings, graph DB for relationships, document DB for text) is being challenged by the practical needs of AI agent architectures.

### What This Means for Genesis Brain

**SurrealDB is well-positioned for this direction.** The current architecture (SurrealDB + Kreuzberg for extraction + OpenRouter for embeddings) is ahead of the curve — it's already doing what the industry says is the right model.

The risks of switching:
- **Neo4j** would require adding a separate vector DB + losing the single-transaction model
- **Qdrant/Weaviate** would require adding a separate graph DB
- **Anything cloud-managed** creates vendor dependency for a community project

The current stack is architecturally sound and matches where the industry is going. The main question is not "should we switch" but "should we deepen" — automate the radicle→SurrealDB sync, deploy the live visualization, and add more community documents to the graph.

---

## 8. Decision Framework

| Scenario | Recommendation |
|----------|----------------|
| Community stays small (<10K concepts, <100 docs) | **Stay with SurrealDB**. Self-hosted, zero-cost, well-suited. |
| Graph grows to enterprise scale | Evaluate NebulaGraph for pure graph; SurrealDB for multi-model |
| Need enterprise integrations (BI tools, Spark, Kafka) | Add Neo4j as a read replica synced from SurrealDB |
| Need managed cloud (no self-hosting) | Evaluate Neptune (if AWS-locked) or SurrealDB Cloud |
| Pure RAG with no graph traversal needs | Qdrant (self-hosted) or Pinecone (managed) as supplement |

---

## 9. Summary: SurrealDB vs. Alternatives at a Glance

| | **SurrealDB** | **Neo4j** | **Pinecone** | **Weaviate** | **Qdrant** | **NebulaGraph** | **Neptune** |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Graph traversal** | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Vector search** | ✅ | ❌+ | ✅ | ✅ | ✅ | ❌ | ❌+ |
| **Document model** | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| **ACID transactions** | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Built-in auth** | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ (IAM) |
| **Self-hosted free** | ✅ | ✅ (CE) | ❌ | ✅ | ✅ | ✅ | ❌ |
| **Industry weight** | Growing | Dominant | Leading | Strong | Strong | Growing | AWS-native |
| **Best for** | AI agents / multi-model | Enterprise graphs | Pure vector RAG | Semantic search | Filtered vectors | Internet-scale graph | AWS ecosystem |
| **Risk** | Young, single startup | Expensive, single-model | Vendor lock-in | Less graph | Less graph | Narrow focus | AWS lock-in |

*❌+ = available via extension, not native*

---

## Key Sources

- SurrealDB website — `surrealdb.com` (positioning, architecture, SurrealQL examples)
- SurrealDB GitHub — `github.com/surrealdb/surrealdb` (technical docs, features)
- Stanford HAI 2026 AI Index — `hai.stanford.edu` (agentic AI trends, $582B investment figure)
- Oracle AI Database agentic AI features — `forbes.com` (Oracle's agent-in-database push, March 2026)
- Neo4j product documentation — `neo4j.com/docs/`
- VentureBeat Enterprise AI Survey — `venturebeat.com` (enterprise AI adoption gaps, April 2026)
