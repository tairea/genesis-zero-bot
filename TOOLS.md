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
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` / `GOOGLE_REFRESH_TOKEN` — OAuth for Drive uploads (alchemy skill)

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
- telegram-compose skill patched to read from this path
- Genesis is bound to Telegram via `bindings` in openclaw.json
- **For substantive messages (>3 lines or structured data):** Use `tg-send` helper with HTML formatting

### tg-send Helper

```bash
# Usage: tg-send "chat_id" "HTML message"
~/.openclaw/workspace-genesis/bin/tg-send "-1001921904187" "📋 <b>Title</b>

<b>Label:</b> Value

• Bullet 1
• Bullet 2"
```

HTML tags supported: `<b>`, `<i>`, `<u>`, `<s>`, `<code>`, `<pre>`, `<tg-spoiler>`, `<blockquote>`, `<a href="url">`

Rule: Use tg-send for messages with >3 lines or lists/stats/sections. Short replies OK via message tool.

## Google Drive (Alchemy Skill)

- Uses OAuth refresh token flow — token refreshed via curl before each API call
- Never expires unless revoked
- Setup docs: `skills/alchemy/references/admin-setup.md`

## Gotchas

- pip requires `--user --break-system-packages` on this Debian (PEP 668)
- clawhub installs to default workspace (`~/.openclaw/workspace/skills/`) — must manually move to `workspace-genesis/skills/`
- ClawHub rate limits aggressively — wait 3-5 min between installs
