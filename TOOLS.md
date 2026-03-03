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

## Google Drive (Alchemy Skill)

- Uses service account with domain-wide delegation (impersonates Drive owner for storage quota)
- Env vars: `GOOGLE_SERVICE_ACCOUNT_KEY`, `GOOGLE_IMPERSONATE_EMAIL`, `GENESIS_DRIVE_FOLDER_ID`
- Auth script: `skills/alchemy/scripts/gdrive-auth.sh`
- Setup docs: `skills/alchemy/references/admin-setup.md`

## Gotchas

- pip requires `--user --break-system-packages` on this Debian (PEP 668)
- clawhub installs to default workspace (`~/.openclaw/workspace/skills/`) — must manually move to `workspace-genesis/skills/`
- ClawHub rate limits aggressively — wait 3-5 min between installs
