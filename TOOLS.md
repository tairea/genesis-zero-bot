# TOOLS.md — Environment Notes

This file is server-only. It documents Genesis's operational environment — paths, binaries, quirks.

## Server

- **Host:** Hetzner VPS, Debian
- **User:** ian
- **Timezone:** America/New_York

## Workspace

- **Path:** `~/.openclaw/workspace-genesis` (not the default `~/.openclaw/workspace`)
- **Config:** `~/.openclaw/openclaw.json`
- **Secrets:** `~/.openclaw/.env` (loaded via systemd EnvironmentFile)
- **Service:** `openclaw-gateway.service` (user systemd unit)

## Env Vars (from .env)

- `TELEGRAM_BOT_TOKEN` — BotFather token for Genesis
- `GOOGLE_SERVICE_ACCOUNT_KEY` — path to service account JSON key for Drive
- `GOOGLE_IMPERSONATE_EMAIL` — Drive owner email for impersonation
- `GENESIS_DRIVE_FOLDER_ID` — Genesis folder ID on Google Drive

## Binaries & Paths

- **Python:** system python3.12, pip packages in `~/.local/bin` (not on PATH by default)
- **Node/npm:** system node, global packages in `~/.npm-global/bin`
- **clawhub CLI:** `~/.npm-global/bin/clawhub`
- **duckduckgo-search:** installed via pip `--user --break-system-packages`
- **jq, curl, bash:** system-installed, always available

## Skills That Need Setup

These are installed but not yet fully configured:

- **gog** — Needs `gog` binary installed + OAuth credentials (`gog auth credentials` + `gog auth add`)
- **summarize** — Needs `summarize` binary + an LLM API key (e.g. `GEMINI_API_KEY`)
- **transcribe** — Needs Docker + `install.sh` run to build whisper image. Change default language from `es` to `en`.

## Telegram

- Bot token is at `channels.telegram.botToken` in openclaw.json (flat, not nested under accounts)
- Genesis is bound to Telegram via `bindings` in openclaw.json

### Message Sending — Compulsory Rule

**Before every Telegram reply, check:**

- **Short reply (<3 lines, no structure):** Send directly via the OpenClaw `message` tool. Done.
- **Anything else (>3 lines, or has lists/stats/sections/reports):** You **must** spawn telegram-compose as a sub-agent. Do not send long or structured messages via the `message` tool — they will look broken.

### How to Spawn telegram-compose

The incoming message context gives you `ChatId` and `MessageThreadId` (the topic thread). **Always pass both** when available.

```
sessions_spawn(
  model: "MiniMax-M2.1",
  task: "Read the telegram-compose skill at skills/telegram-compose/SKILL.md for formatting rules, then format and send this content to Telegram.

Chat ID: {ChatId}
Thread ID: {MessageThreadId}

Content to format:
---
<your raw content here>
---

After sending, reply with the message_id on success or the error on failure. Do NOT include the formatted message in your reply — it's already been sent to Telegram."
)
```

**After spawning:** Reply `NO_REPLY` to the main session. The sub-agent's curl call delivers to Telegram — if you also reply via the message tool, the user gets a duplicate.

**Omit the `Thread ID:` line only** if `MessageThreadId` is empty/absent (i.e. it's a DM or non-forum group).

## Knowledge Graph (Genesis Brain)

Genesis has a semantic knowledge graph stored in SurrealDB with 5,000+ concepts, vector embeddings, and NARS epistemic truth values.

- **Pipeline:** `~/.openclaw/workspace-genesis/skills/semantic-graph/pipeline.py`
- **Venv:** `~/.openclaw/workspace-genesis/skills/semantic-graph/.venv/`
- **SurrealDB:** runs as `surrealdb.service` (user systemd), `ws://127.0.0.1:8000`, namespace `semantic_graph/main`
- **Env vars needed:** `SURREAL_PASS`, `OPENROUTER_API_KEY` (both in `~/.openclaw/.env`)

### Activation pattern (required before any pipeline command):
```bash
cd ~/.openclaw/workspace-genesis/skills/semantic-graph
source .venv/bin/activate
export $(grep -v "^#" ~/.openclaw/.env | xargs)
```

### Genesis Brain scripts (in `skills/genesis-brain/scripts/`):
| Script | Usage | Purpose |
|--------|-------|---------|
| `ingest.sh <file>` | Ingest a document | Returns JSON: concepts, relations, connections |
| `query.sh "<query>"` | Semantic search | Returns JSON: results, connections |
| `relate.sh "<A>" "<B>"` | Find relationships | Returns JSON: direct, paths, shared neighbors |
| `capture.sh "<text>"` | Capture text snippet | Returns JSON: doc_id, counts |
| `stats.sh` | Knowledge graph stats | Returns JSON: counts, types, verbs |

### When to use the knowledge graph:
- **Community question asked** → Run `query.sh` FIRST, before using training. Cite graph results.
- **User sends a file/attachment** → Run `ingest.sh` to absorb into the graph
- **User asks "what do you know about X"** → Run `query.sh` for semantic search
- **User asks "how does X relate to Y"** → Run `relate.sh` for graph traversal
- **User says "remember this"** → Run `capture.sh` to store in the graph
- **@mention in Regen Tribes with substantive content** → Silently run `capture.sh`
- **Any question that could benefit from graph context** → Run `query.sh` and include results in a `<blockquote expandable>` via telegram-compose

## Google Drive (Alchemy Skill)

- Uses service account with domain-wide delegation (impersonates Drive owner for storage quota)
- Env vars: `GOOGLE_SERVICE_ACCOUNT_KEY`, `GOOGLE_IMPERSONATE_EMAIL`, `GENESIS_DRIVE_FOLDER_ID`
- Auth script: `skills/alchemy/scripts/gdrive-auth.sh`
- Setup docs: `skills/alchemy/references/admin-setup.md`

## Gotchas

- pip requires `--user --break-system-packages` on this Debian (PEP 668)
- clawhub installs to default workspace (`~/.openclaw/workspace/skills/`) — must manually move to `workspace-genesis/skills/`
- ClawHub rate limits aggressively — wait 3-5 min between installs
