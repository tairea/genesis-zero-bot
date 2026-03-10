# Genesis

**Core identity files for Genesis** — an AI agent being developed to help the [RegenTribes](https://regentribes.com) community achieve its goals.

The goal is to evolve Genesis into a super helpful assistant to the community via its Telegram group.

## Skills

Modular skills that extend Genesis with specialised knowledge and workflows for the RegenTribes community.

### Community & Knowledge

| Skill | Description | Author | Status |
|-------|-------------|--------|--------|
| [🔺 alchemy](skills/alchemy/) | Guides a community vision holder through the full Community Alchemy Playbook — all 11 areas — helping them articulate their regenerative neighbourhood vision. Persists progress across sessions, compiles a completed playbook, delivers via Telegram and Google Drive. | Ian | Testing |
| [🌠 dreamcatcher](skills/dreamcatcher/) | Captures member ideas and helps flesh them out into full development specifications (.md), then commits to a new repo and creates a GitHub issue for a coding agent to execute. | Ian | In Development |
| [🧠 genesis-brain](skills/genesis-brain/) | Genesis' knowledge brain — ingests documents and links into a semantic knowledge graph, enriches responses with graph context, answers knowledge queries with evidence. Auto-captures @Genesis mentions in Regen Tribes. | Ian | Active |
| [📜 telegram-history](skills/telegram-history/) | Versioned Telegram conversation archive with query capabilities — full-text search, topic extraction, member profiling, link cataloging. | Vitali | In Development |

### Knowledge Graph Pipeline

| Skill | Description | Author | Status |
|-------|-------------|--------|--------|
| [semantic-graph](skills/semantic-graph/) | Backend extraction engine for genesis-brain. LLM-powered document-to-knowledge-graph pipeline using Kreuzberg + Claude + SurrealDB with NARS truth values, vector embeddings, and HNSW semantic search. **Not user-facing — use genesis-brain instead.** | Vitali | Active |
| [🌐 regen-viz](skills/regen-viz/) | 3D force-directed graph visualizations of RegenTribes knowledge structures. 19+ HTML variants, JSON datasets, pre-publish validation suite. Served via GitHub Pages. | Vitali | In Development |
| [📦 regen-cas](skills/regen-cas/) | Content-addressable file storage in Rust. Store by content hash, retrieve by address, with LZ4 compression and OpenDAL backend abstraction (fs/s3/gcs). | Vitali | Prototype |

### Reference & Tooling

| Skill | Description | Author | Status |
|-------|-------------|--------|--------|
| [kreuzberg](skills/kreuzberg/) | API reference for the Kreuzberg document intelligence library — 75+ format extraction. Used by semantic-graph for document ingestion. | Vitali | Reference |
| [surreal-skills](skills/surreal-skills/) | Comprehensive SurrealDB 3 reference — SurrealQL, data modeling, graph queries, vector search, security, deployment, SDKs. 11 rule files + diagnostic scripts. | Vitali | Reference |
| [ralph-presets](skills/ralph-presets/) | 26+ Ralph Orchestrator presets for multi-agent workflows (TDD, adversarial review, Socratic learning, mob programming, etc.) plus 8 RegenTribes project templates. | Vitali | In Development |

### Genesis Core

| Skill | Description | Author | Status |
|-------|-------------|--------|--------|
| [telegram-compose](skills/telegram-compose/) | Telegram message composition and delivery | Ian | Active |
| [telegram](skills/telegram/) | Core Telegram integration | Ian | Active |
| [🎮 gog](skills/gog/) | Google Drive integration | Ian | Active |
| [🧾 summarize](skills/summarize/) | Text summarization | Ian | Active |
| [transcribe](skills/transcribe/) | Audio/video transcription | Ian | Active |
| [web-search](skills/web-search/) | Web search capability | Ian | Active |
| [🔬 deep-research-pro](skills/deep-research-pro/) | Deep research and analysis | Ian | Active |
| [find-skills](skills/find-skills/) | Skill discovery meta-skill | Ian | Active |

![Genesis](genesis-zero-bot.jpeg)
