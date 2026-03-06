---
name: open-brain
version: 1.0.0
description: "Knowledge capture and retrieval system. Auto-captures thoughts from the capture group, stores with vector embeddings and graph relationships."
---

# Open Brain — Knowledge Memory System

Open Brain captures, stores, and retrieves thoughts using SurrealDB with vector embeddings and graph relationships (people, topics).

## Environment

All scripts are in: `~/.openclaw/workspace-genesis/skills/open-brain/scripts/`

Required env vars (set in `~/.openclaw/.env`):
- `SURREAL_PASS` — SurrealDB root password
- `OPENROUTER_API_KEY` — For embeddings and metadata extraction

## Auto-Capture Rule — Regen Tribes Group

**Chat ID:** `-1001921904187` (Regen Tribes)

When a message in this group **@mentions Genesis**, silently capture it:
1. Run `capture.mjs` with the message content, source "telegram", chat ID, and message ID
2. **Do NOT reply with a confirmation.** The group knows Genesis stores conversations. Just capture silently and continue handling the message normally (respond to whatever the user actually asked).

Only capture messages that @mention Genesis. Ignore other group messages — do not capture them.

## Scripts

### capture.mjs — Store a thought
```bash
node scripts/capture.mjs "<content>" [source] [chat_id] [message_id]
```
Returns JSON with: id, type, topics, people, action_items.

### search.mjs — Semantic search
```bash
node scripts/search.mjs "<query>" [limit]
```
Returns matching thoughts ranked by similarity.

### list.mjs — Browse/filter thoughts
```bash
node scripts/list.mjs [--type TYPE] [--person NAME] [--topic NAME] [--since DATE] [--limit N]
```
Types: idea, task, note, question, decision, reflection

### stats.mjs — Memory stats
```bash
node scripts/stats.mjs
```
Returns: total count, breakdown by type, top people, top topics, recent thoughts.

## When to Use

- **User asks "what do I know about X"** → Run `search.mjs` with X
- **User asks about a person** → Run `list.mjs --person "Name"`
- **User asks about a topic** → Run `list.mjs --topic "topic"`
- **User asks for stats/summary** → Run `stats.mjs`
- **User says "remember this" or "capture"** → Run `capture.mjs`
- **@mention in Regen Tribes** → Silently capture via `capture.mjs`, then respond to the user's actual message normally
