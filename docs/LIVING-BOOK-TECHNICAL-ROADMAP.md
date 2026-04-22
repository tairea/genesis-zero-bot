# The Living Book — Technical Roadmap

**Version:** 0.1
**Date:** 2026-04-21
**Based on:** Genesis Brain Light Design
**Status:** Early draft — for group review

---

## The Starting Point

We adapt the Genesis Brain Light architecture. Two layers:

1. **GitHub** — document layer, editable by author on their own computer
2. **SurrealDB** — queryable knowledge graph, exposed via API

Sync: `git push` → GitHub webhook → VPS pipeline → SurrealDB update.

For The Living Book, we extend this with two distinct **lenses** (coherence streams) from day one:

- **Author Lens** — the canonical text, curated and maintained by the author
- **Community Lens** — all validated contributions from the community

The author edits locally on their own machine (standard git workflow). Community contributions flow in through a structured review process. Both views are queryable simultaneously, and the reader can switch between them.

This is version 0. Small. Real. Buildable now.

---

## Version 0 — Two Lenses (MVP)

**Goal:** Author publishes a book. Community reads and annotates. Both streams exist separately.

### What we're building

```
GitHub (documents)
    ├── /author/           ← canonical text, author-only edits
    │   ├── chapter-01.md
    │   ├── chapter-02.md
    │   └── ...
    ├── /community/         ← community annotations and extensions
    │   ├── annotations/
    │   ├── sources/
    │   └── extensions/
    └── /blobs/             ← S3 manifest (pointers to originals)

SurrealDB (knowledge graph)
    ├── Author concepts + relations (from /author/)
    └── Community concepts + relations (from /community/)

API (FastAPI on VPS)
    ├── GET /author/query?q=...
    ├── GET /community/query?q=...
    └── GET /stats
```

### Components we need (all exist, just integration)

| Component | Technology | What it does |
|-----------|-----------|-------------|
| Document store | GitHub private repo | Author edits locally, pushes. Community reads. |
| Blob storage | Cloudflare R2 (S3-compatible) | Store original PDFs, DOCX |
| Webhook receiver | Python FastAPI on VPS | GitHub push → trigger pipeline |
| Text extraction | Kreuzberg | PDF/DOCX/75+ formats → markdown |
| Embeddings | OpenRouter (text-embedding-3-small) | 1536d vectors for concepts |
| Knowledge graph | SurrealDB (existing) | Store concepts, relations, chunks |
| Query API | FastAPI + REST | Expose graph queries to readers |

### Version 0 workflow

**Author publishes:**
1. Author clones the GitHub repo locally
2. Writes or uploads canonical text (markdown)
3. `git push` → webhook fires → pipeline extracts concepts → SurrealDB updated
4. Author lens is queryable

**Reader accesses:**
1. Reader purchases token access
2. Reader can query: "what does the author say about X?" → Author lens
3. Reader can query: "what has the community added about X?" → Community lens
4. Both streams are navigable, attributable, separate

**Community contributes:**
1. Contributor writes annotation in `/community/annotations/` folder
2. Author reviews (via GitHub PR) and validates
3. Validated annotation enters the community lens
4. Contributor earns a stake (tracked in SurrealDB as attribution record)

### What version 0 does NOT do

- No automatic community stream generation (it's just a folder of markdown for now)
- No tokenization / credit system (that's v1)
- No multiple authority streams (just author + community)
- No sophisticated gating (just PR review by author)
- No settlement layer

Version 0 proves the concept: two lenses, one corpus, real infrastructure.

### Deliverables for v0

- [ ] GitHub repo with `/author/` and `/community/` folder structure
- [ ] Author-facing git workflow (clone, edit, push)
- [ ] Webhook receiver on VPS
- [ ] Reindex pipeline (GitHub → SurrealDB) with lens separation
- [ ] Reader API: two query endpoints (author vs community)
- [ ] Basic attribution tracking (who contributed what)
- [ ] R2 blob storage for original documents

---

## Phase 1 — Access Control + Contribution Layer

**Goal:** Token-gated access. Structured contribution workflow. Quality filtering.

### What's new

**Token access system:**
- Reader purchases access → receives API key
- API key grants read access to both lenses
- Credits consumed per query (AI queries cost more than simple lookups)
- Contributor earns credits when their work is validated and accessed

**Structured contribution:**
- Contributors submit via GitHub PR to `/community/`
- Annotations, sources, extensions — each in its own folder
- Author or delegated reviewers approve via merge
- Approved contributions trigger reindex into community lens

**Gating implementation:**
- Tier 0: Read access (anyone with token)
- Tier 1: Annotate (verified email + accept terms)
- Tier 2: Extend (5+ quality annotations or author invitation)

**Infrastructure additions:**

| Component | Technology | What it does |
|-----------|-----------|-------------|
| Credit tracking | SurrealDB tables | Per-user credit balance, transaction log |
| Access validation | FastAPI middleware | Check API key, deduct credits, route |
| Contribution tracker | GitHub PR metadata + SurrealDB | Track PRs, approvals, contributor stakes |
| Notification system | Simple email script | Alert author when contributions need review |
| Contributor dashboard | Static web UI | Show own contributions, earned credits, status |

### Phase 1 deliverables

- [ ] Token purchase + key issuance flow
- [ ] Credit-deducted API queries
- [ ] Structured contribution folders with validation workflow
- [ ] Author review dashboard (list of pending PRs)
- [ ] Contributor attribution linked to credit stakes
- [ ] Tier gating (annotate vs extend)

---

## Phase 2 — Coherence Streams + Settlement

**Goal:** Multiple authority lenses. Automated settlement. Community signal.

### What's new

**Multiple coherence streams:**
- Author can designate "authority stream holders" — trusted contributors whose lens becomes a named stream
- Each stream is a named, attributed view: "Dr. Smith's lens on Chapter 3"
- Streams computed from contribution graph + reader engagement signal
- Readers choose which stream to follow as their primary lens

**Automated settlement:**
- Every access purchase triggers split: author share + contributor shares
- Settlement runs on a schedule (daily or per transaction, configurable)
- Contributors see their earned credits grow in real-time (or near-real-time)
- Full transparency: anyone can audit the settlement ledger

**Community signal:**
- Which annotations get cited most?
- Which extensions are referenced in new contributions?
- Which sources lead to new insights?
- This becomes the "community stream" — not manually curated, algorithmically generated from validated usage

**Infrastructure additions:**

| Component | Technology | What it does |
|-----------|-----------|-------------|
| Stream generator | Python service | Computes named lenses from contribution graph |
| Settlement engine | Python + SurrealDB transactions | Splits access revenue per contribution attribution |
| Signal tracker | SurrealDB + background job | Tracks citations, references, engagement metrics |
| Stream registry | SurrealDB table | Named streams with creator, description, query endpoint |
| Reader dashboard | Static web UI | Choose stream, see credits, track reading history |

### Phase 2 deliverables

- [ ] Multiple named coherence streams (author + community + individual holders)
- [ ] Automated settlement ledger with audit trail
- [ ] Engagement signal tracking (what gets cited, referenced, extended)
- [ ] Stream generator service
- [ ] Reader stream selector UI
- [ ] Contributor credit history and earnings dashboard

---

## Phase 3 — Advanced Architecture

**Goal:** Full multi-perspective system. Sophisticated graph. P2P replication. Custom tooling.

### What's in this phase (heavier lift, custom design)

**Knowledge graph enhancements:**
- NARS-style truth values on concepts (uncertainty, confidence, relevance)
- Community detection: automatic clustering of related concepts into themes
- Temporal tracking: how ideas evolved over versions of the corpus
- Cross-book references: a concept in Book A cited in Book B's extension

**Coherence stream computation:**
- Full graph traversal + ranking algorithm for stream generation
- Reader personalization: which stream to recommend based on reading history
- Drift detection: when a stream's view diverges significantly from the author lens

**P2P replication (beyond GitHub):**
- Option for communities that want full decentralization (not dependent on GitHub)
- Radicle integration for communities that prefer p2p document layer
- IPFS for blob storage alternatives
- This is for communities that need it — not default for v0-v2

**Custom search + retrieval:**
- Hybrid search: keyword + semantic + temporal + authority-weighted
- Not just "find relevant chunks" but "find the most authoritative view on X"
- Custom ranking that weighs author endorsement, community signal, and stream holder reputation

**Advanced token mechanics:**
- Reputation-weighted staking: contributors with higher reputation earn proportionally more
- Stake locking: early contributors' stakes vest over time (prevent immediate dump)
- Author can set contribution reward percentage (e.g., "I take 70%, contributors split 30%")

### Phase 3 deliverables

- [ ] NARS truth values on graph nodes
- [ ] Temporal knowledge graph (how ideas evolved)
- [ ] Cross-book concept references
- [ ] Stream ranking + recommendation engine
- [ ] P2P option (Radicle + IPFS) for communities that need it
- [ ] Advanced search: authority-weighted hybrid retrieval
- [ ] Sophisticated staking model with vesting

---

## Technology Choices — Current vs Future

| Layer | Version 0 | Phase 1 | Phase 2 | Phase 3 |
|-------|-----------|---------|---------|---------|
| Document store | GitHub | GitHub | GitHub | GitHub or Radicle |
| Blob storage | R2 | R2 | R2 | R2 or IPFS |
| Knowledge graph | SurrealDB | SurrealDB | SurrealDB + custom | SurrealDB + NARS |
| Query API | FastAPI REST | FastAPI + credits | FastAPI + streams | Custom ranking |
| Embeddings | OpenRouter | OpenRouter | OpenRouter | Configurable |
| Text extraction | Kreuzberg | Kreuzberg | Kreuzberg | Kreuzberg |
| Access tokens | None | Simple key | Credit system | Staking model |
| Settlement | None | Manual | Automated | Automated + vesting |
| Streams | Author + Community | + author delegates | + named individuals | + recommendation |
| P2P | None | None | None | Optional Radicle/IPFS |

---

## Key Design Decisions to Make as a Group

1. **Token system:** Simple credit ledger (Phase 1) or stake-weighted with vesting (Phase 3)? Affects contributor incentives significantly.

2. **Settlement frequency:** Real-time per transaction or daily batch? Real-time feels better but adds infrastructure complexity.

3. **Stream generation:** Fully automated (algorithm picks winners) or author-designated (author approves who gets a named stream)? The latter is safer for quality; the former is more democratic.

4. **Cross-book references:** If someone extends Book A using a concept from Book B, should Book B's author see a notification? Should they earn from it? This has community-wide implications.

5. **Default view:** When a reader opens the book, which stream do they see first? Author's? Community's? Last-visited? This shapes the experience significantly.

6. **Blob storage:** R2 is the plan, but what about communities that want full sovereignty? IPFS + pinning service could be an alternative for Phase 3.

---

*This is a working document. Additions, revisions, and challenge welcome.*