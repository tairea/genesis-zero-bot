# Genesis Brain Light — Distributed Knowledge System Design

**Version:** 0.1 (draft)
**Date:** 2026-04-21
**Status:** Design phase. Current Genesis Brain (Radicle + SurrealDB) needs to evolve into this.

---

## 1. Overview

Genesis Brain Light is a **two-layer knowledge system** where:

1. **GitHub** = the editable document layer. Members clone a repo, edit markdown with their own AI tools (Claude, Copilot, etc.), push changes.
2. **SurrealDB** = the queryable knowledge graph, exposed via MCP server + REST API. Any AI assistant can query the community's shared knowledge directly — regardless of what tool the user is working in.

The sync is driven by **git push** → GitHub webhook → VPS pipeline → SurrealDB update.

**S3/R2** stores original blobs (PDFs, DOCX, images). Markdown versions live in GitHub for human editing.

---

## 2. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                       COMMUNITY MEMBERS                             │
│                                                                     │
│   Member A          Member B          Member C                      │
│   ┌─────────┐       ┌─────────┐       ┌─────────┐                  │
│   │ Claude  │       │Claude   │       │Copilot  │                  │
│   │ Code    │       │ Code    │       │         │                  │
│   │ + MCP   │       │ + MCP   │       │ + MCP   │                  │
│   └────┬────┘       └────┬────┘       └────┬────┘                  │
│        │                 │                 │                        │
│        └─────────────────┼─────────────────┘                        │
│                          │                                          │
│                    MCP Client (user's AI tool)                      │
└──────────────────────────┼──────────────────────────────────────────┘
                           │
                           │ (authenticated)
                           ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    PUBLIC ENDPOINT (VPS)                             │
│                                                                      │
│   ┌──────────────────────────────────────────────────────────────┐   │
│   │  MCP Server / REST API  (Python FastAPI)                    │   │
│   │  - Auth: API key or GitHub OAuth token                       │   │
│   │  - Exposes: query, retrieve, relate, stats                   │   │
│   │  - Connects to SurrealDB ws://127.0.0.1:8000                │   │
│   └──────────────────────────────────────────────────────────────┘   │
│                              ▲                                       │
│                              │ SurrealQL / WebSocket                 │
│   ┌──────────────────────────┴──────────────────────────────────┐   │
│   │  SurrealDB v3  (ws://127.0.0.1:8000)                        │   │
│   │  - concepts, relations, chunks, communities                  │   │
│   │  - HNSW vector indexes                                       │   │
│   │  - Auth: root / SURREAL_PASS                                 │   │
│   └──────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────┘
                           ▲
                           │ Reindex pipeline
┌──────────────────────────┴──────────────────────────────────────────┐
│                    GITHUB WEBHOOK TRIGGER                             │
│                                                                      │
│   ┌──────────────┐         ┌──────────────┐         ┌────────────┐  │
│   │  GitHub Repo │  push   │  Webhook     │  file   │  Reindex   │  │
│   │  (markdown   │────────▶│  Receiver    │ changes │  Pipeline  │  │
│   │   docs)      │         │  (VPS)       │────────▶│  (VPS)     │  │
│   └──────────────┘         └──────────────┘         └─────┬──────┘  │
│                                                           │         │
│   ┌──────────────┐                                        │         │
│   │  S3 / R2     │◀────────────────── fetch original      │         │
│   │  (blobs)     │   (PDF, DOCX, images)                  │         │
│   └──────────────┘                                        │         │
│                                                           ▼         │
│   ┌──────────────────────────────────────────────────────────────┐   │
│   │  Kreuzberg → Extract text (75+ formats)                     │   │
│   │  OpenRouter or local Ollama → Embeddings                    │   │
│   │  LLM → Concept + relation extraction                        │   │
│   │  SurrealDB → Upsert nodes + edges                           │   │
│   └──────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│                      MEMBER LOCAL WORKFLOW                            │
│                                                                      │
│   git clone git@github.com:regentribes/knowledge-base.git           │
│   cd knowledge-base                                                  │
│   # Edit docs with Claude, VS Code, Obsidian, whatever               │
│   git add . && git commit && git push                               │
│   # Webhook fires → SurrealDB updated                               │
│                                                                      │
│   # Meanwhile, from ANY AI tool:                                     │
│   # MCP client connects to genesis-brain.example.com                │
│   # Query: "What does the community know about EROI?"                 │
│   # → SurrealDB hybrid retrieval → answer with citations             │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 3. Components

### 3.1 GitHub Document Layer

**Repo:** `github.com/regentribes/knowledge-base`

**Structure:**
```
/
├── docs/                    # Markdown documents (human-editable)
│   ├── erio-basics.md
│   ├── community-governance.md
│   └── ...
├── blobs/                   # S3 pointer manifest (JSON, not the actual files)
│   └── manifest.json        # Maps doc ID → S3 URL for original
├── schema/                  # Document format definitions
│   └── format.md
└── README.md
```

**Why markdown in GitHub:**
- Members use their own AI tools (Claude, Copilot, etc.) to read and write
- GitHub's diff/merge/PR workflow handles collaboration
- Version control, blame, revert — all built in
- No special software needed, just a text editor + git

**Blob storage (S3/R2):**
- PDFs, DOCX, images, email exports — stored in S3-compatible bucket
- GitHub repo stores only a manifest JSON mapping each doc to its S3 URL
- On reindex: pipeline fetches from S3 → Kreuzberg extracts text → markdown stored in GitHub

### 3.2 S3 / R2 Blob Storage

**Provider:** Cloudflare R2 (S3-compatible, no egress fees)

**Bucket structure:**
```
regen-tribes-kb/
├── originals/
│   ├── doc-uuid-001.pdf
│   ├── doc-uuid-002.docx
│   └── ...
└── thumbnails/              # Optional: page preview images
    └── doc-uuid-001.webp
```

**Access:**
- R2 bucket is private (no public access)
- Pipeline has R2 credentials (env vars)
- Members download blobs via signed URLs generated by the API

### 3.3 Webhook Receiver

**What it does:**
- GitHub sends a POST to `https://genesis-brain.example.com/webhook/github` on every push
- Validates the webhook signature (HMAC SHA-256, `X-Hub-Signature-256` header)
- Extracts the list of changed files from the webhook payload
- Filters: only reindex if `docs/` or `blobs/manifest.json` changed
- Calls the reindex pipeline with the changed file list

**Tech:** Small Python FastAPI service on the VPS, listening on a specific route. Could be the same service as the MCP server (same process, different route).

### 3.4 Reindex Pipeline

**Triggered by:** webhook (incremental — only changed files) or manual full reindex.

**Incremental reindex (git push):**
```
1. Fetch changed files from GitHub API (or local clone if VPS pulls)
2. For each changed .md file:
   a. Kreuzberg → extract plain text
   b. Chunk into ~512 token segments
   c. OpenRouter or Ollama → generate embeddings
   d. OpenRouter → extract concepts + relations
   e. SurrealDB → UPSERT concepts, relations, chunks, mentions
3. For blobs/manifest.json changes:
   a. Fetch new/updated S3 URIs
   b. Download blobs from R2
   c. Run same extraction pipeline
   d. Store markdown version in /tmp, commit to GitHub branch (optional)
```

**Full reindex (manual or scheduled):**
```
1. Clone fresh from GitHub
2. Traverse docs/
3. For each file: run full pipeline
4. Update SurrealDB (upsert — safe to run on existing data)
```

**Deduplication:** Entity resolution (NumPy cosine similarity) prevents duplicate concepts. `updated_at` timestamp on documents handles version tracking.

### 3.5 SurrealDB (Knowledge Graph)

**Role:** The queryable brain. Stores all extracted concepts, relations, embeddings, and document metadata.

**Schema (existing, works well):**
- `document` — doc ID, title, author, source URL, created_at, updated_at
- `chunk` — text segments with vector embeddings
- `concept` — named entity with type, description, NARS truth value
- `community` — thematic clusters with LLM-generated summaries
- `relates` / `contains` / `mentions` / `belongs_to` — edge tables

**Multi-tenant consideration:** Currently single community. Could extend namespace per community if needed.

### 3.6 MCP Server

**What it is:** A Model Context Protocol server that lets any MCP-compatible AI assistant (Claude Code, Cursor, Copilot, etc.) query SurrealDB directly.

**Why MCP:** MCP is the emerging standard for connecting AI assistants to external data sources. Instead of building a custom REST client, AI tool vendors support MCP natively. This means "connect Genesis Brain to Claude" is a one-line config, not a custom integration.

**What it exposes:**
- `kb_query(query: string, limit?: number)` → hybrid search results with citations
- `kb_get_concept(name: string)` → concept details, relations, evidence
- `kb_relate(concept_a: string, concept_b: string)` → path between two concepts
- `kb_stats()` → graph statistics (concept count, relation count, etc.)
- `kb_communities(query?: string)` → list or search thematic communities

**Auth:** API key passed as `Authorization: Bearer <key>` header. Keys managed via SurrealDB's own access control.

**Tech:** Python + `FastMCP` or the official `mcp-sdk`. Runs as a sidecar to the webhook receiver on the VPS.

### 3.7 REST API (Supplementary)

**What it is:** A lightweight REST/WebSocket API on top of SurrealDB for non-MCP clients (browsers, mobile apps, simple scripts).

**Endpoints:**
```
GET  /api/v1/query?q=<query>         # Hybrid search
GET  /api/v1/concept/<name>          # Concept details
GET  /api/v1/stats                   # Graph stats
GET  /api/v1/communities             # List communities
POST /api/v1/ingest                  # Manual ingest (admin only)
WS   /api/v1/subscribe              # Live query results
```

**Auth:** Same API key model. Rate limiting per key.

---

## 4. Data Flow — Full Cycle

```
Member creates/edits doc locally
        ↓
git push to GitHub
        ↓
GitHub webhook POST to VPS
        ↓
Webhook receiver validates + extracts changed files
        ↓
Pipeline fetches changed docs (and new S3 blobs if manifest changed)
        ↓
Kreuzberg → plain text extraction
        ↓
Chunking → ~512 token segments
        ↓
Embedding → OpenAI text-embedding-3-small (or Ollama if local)
        ↓
LLM extraction → concepts + relations (OpenRouter or Ollama)
        ↓
Entity resolution → deduplicate against existing graph
        ↓
SurrealDB upsert → nodes + edges + chunks
        ↓
Graph updated (live queries push to subscribers via WebSocket)
        ↓
Next time any member's AI assistant queries via MCP → fresh results
```

---

## 5. Deployment on VPS

**Current VPS:** Hetzner, 75GB disk, ~3.9GB free.

**Space concerns:**
- SurrealDB data directory grows with the graph. Manageable for community scale (<10K concepts).
- GitHub repo cloned fresh on reindex? Use `git fetch` + diff to get only changed files.
- Blob storage (R2) doesn't count against VPS disk.
- Docker already installed — can run SurrealDB as a container.

**Services to run:**
1. `surreal start` — database (or Docker container)
2. `webhook-api` — FastAPI service (webhook receiver + MCP server + REST API)
3. `openclaw-gateway` — existing Genesis Telegram bot

**Recommended:** Run SurrealDB in Docker, bind-mount data to `~/.openclaw/surreal-data/` for persistence.

**R2 setup:**
- Create R2 bucket `regen-tribes-kb`
- Generate R2 API token (S3-compatible credentials)
- Add to `~/.openclaw/.env`: `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET_NAME`
- Use `boto3` or `python-s3` to interact from pipeline

---

## 6. Local Member Workflow

```
# 1. Clone the knowledge base
git clone git@github.com:regentribes/knowledge-base.git
cd knowledge-base

# 2. Set up MCP (one-time)
# Add to Claude Code config:
# {
#   "mcpServers": {
#     "genesis-brain": {
#       "command": "npx",
#       "args": ["-y", "@genesis-brain/mcp", "--api-key", "your-key-here"]
#     }
#   }
# }

# 3. Work with your own AI
claude
# > Read through the EROI documents and tell me what the community's current understanding is
# > Draft a response to Vitali's question about net energy accounting
# > What does the community know about regenerative agriculture vs extractive?

# 4. Push changes
git add . && git commit && git push
# → Webhook fires → SurrealDB updated → everyone's AI sees the new info
```

---

## 7. Security Model

| Surface | Risk | Mitigation |
|---------|------|------------|
| GitHub webhook | Fake pushes from non-members | Validate `X-Hub-Signature-256` HMAC with shared secret |
| MCP API | Unauthorized query access | API key per user, stored hashed in SurrealDB |
| SurrealDB (ws://127.0.0.1:8000) | Local only — already private | No change needed |
| S3/R2 blobs | Leaked URLs | Signed URLs with 1-hour expiry; bucket not public |
| Member local clones | Old docs out of sync | GitHub is source of truth; reindex always pulls latest |
| Malicious doc content | Prompt injection via doc content | Pipeline LLM extraction is sandboxed; MCP responses come from curated graph, not raw doc |

---

## 8. Comparison: Current vs. Light

| | **Current (Radicle + SurrealDB)** | **Light (GitHub + SurrealDB + MCP)** |
|---|---|---|
| Document layer | Radicle (p2p, lean feature set) | GitHub (rich editor, PRs, issues, Actions) |
| Edit workflow | Manual publish scripts | `git clone && edit && push` — standard workflow |
| Local AI integration | None | Any MCP-compatible AI tool |
| Public document URL | Radicle web UI (niche) | GitHub (universal, SEO-friendly) |
| Blob storage | Not implemented | S3/R2 for originals |
| Knowledge API | Internal scripts only | MCP + REST — open to any AI assistant |
| Webhook reindex | Not implemented | Full git push → pipeline |
| Complexity | Higher (p2p protocol quirks) | Lower (webhook + standard git) |
| Cost | Free (self-hosted) | Free (GitHub + VPS + R2 free tier) |

---

## 9. Open Questions / TODOs

- [ ] **R2 setup** — Create R2 bucket, generate credentials, add to .env
- [ ] **GitHub repo** — Create `knowledge-base` repo, define document format
- [ ] **Webhook receiver** — Python FastAPI service with HMAC validation
- [ ] **MCP server** — Implement `genesis-brain` MCP server exposing kb_query, kb_get_concept, kb_relate, kb_stats
- [ ] **Reindex pipeline** — Modify existing pipeline.py to accept a list of changed files vs. full reindex
- [ ] **Blob pipeline** — Fetch from R2 → Kreuzberg → markdown → GitHub (or just keep markdown in GitHub)
- [ ] **Auth system** — API key generation and management in SurrealDB
- [ ] **Claude Code MCP config** — Document the one-line setup for members
- [ ] **Migration path** — Move existing 149 docs from SurrealDB into GitHub + R2
- [ ] **Deploy script** — `docker-compose up` for webhook-api + SurrealDB

---

## 10. Why This Beats the Alternatives

**vs. Obsidian:**
- Obsidian is solo/local. Genesis Brain Light is shared. Your Claude can query what my Claude knows.

**vs. Notion:**
- Notion is a SaaS product with API limits. GitHub is free, eternal, and every AI tool already speaks Git.

**vs. current Radicle setup:**
- Radicle's learning curve is high. GitHub is universal. The p2p replication is solving a problem the community doesn't have.

**vs. building on Pinecone/Qdrant alone:**
- A vector DB without a graph layer can't answer "how does X relate to Y." SurrealDB gives both.

**vs. building on Neo4j alone:**
- No local AI integration path, no blob storage, expensive at scale.
