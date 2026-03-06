# Open Brain — Knowledge Memory System

Auto-captures thoughts from Telegram, stores them in SurrealDB with vector embeddings and graph relationships.

## Intention

Give Genesis persistent memory by capturing knowledge from the Regen Tribes Telegram group. When someone @mentions Genesis, the message is silently stored with extracted metadata, embeddings, and topic/person graph links. Members can then search, browse, and query Genesis's accumulated knowledge.

## Stack

- **Node.js (mjs)** — capture and query scripts
- **SurrealDB** — storage with vector embeddings and graph relationships
- **OpenRouter API** — embeddings and metadata extraction

## Components

| File | Role |
|------|------|
| `scripts/capture.mjs` | Store a thought with metadata extraction (source, chat ID, message ID) |
| `scripts/search.mjs` | Semantic search across captured thoughts |
| `scripts/list.mjs` | Browse/filter thoughts by type, person, topic, date |
| `scripts/stats.mjs` | Memory statistics and analytics |

## Auto-Capture Rule

- **Trigger:** Message @mentions Genesis in Regen Tribes group (chat ID `-1001921904187`)
- **Behaviour:** Silently capture — no confirmation reply to preserve group flow
- **Scope:** Only captures @Genesis mentions, ignores other group messages

## Environment

Required env vars (in `~/.openclaw/.env`):
- `SURREAL_PASS` — SurrealDB root password
- `OPENROUTER_API_KEY` — for embeddings and metadata extraction

## Limitations

- **Single group only** — hardcoded to Regen Tribes chat ID `-1001921904187`
- **OpenRouter dependency** — requires API key and network access for embeddings
- **Script paths hardcoded** — references `~/.openclaw/workspace-genesis/skills/open-brain/scripts/`

## Next Steps

1. Make chat ID configurable (support multiple groups)
2. Add a "forget" command for GDPR-style deletion
3. Add periodic summarization of accumulated knowledge
4. Connect to semantic-graph for richer entity/relation extraction from captured thoughts
