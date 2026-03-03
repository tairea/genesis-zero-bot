# Alchemy Skill — Bot Admin Setup

This file documents everything a bot admin needs to configure before the Community Alchemy skill can deliver completed playbooks via Telegram and Google Drive.

---

## 1. Telegram Bot Token

The skill sends files and messages via the Telegram Bot API.

**Required:** `TELEGRAM_BOT_TOKEN`

**Steps:**
1. Open Telegram and message [@BotFather](https://t.me/BotFather)
2. Run `/newbot` and follow the prompts to name and username your bot
3. Copy the token BotFather gives you (format: `123456789:AAF...`)
4. Set it as an environment variable on the server:
   ```bash
   export TELEGRAM_BOT_TOKEN="123456789:AAF..."
   ```
   Or add it to your OpenClaw `.env` / secrets config so it's available at runtime.

**Test it:**
```bash
curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe" | jq .ok
# Should return: true
```

---

## 2. Google Drive API — Service Account

The skill uploads completed playbooks to a shared Google Drive folder and shares them with the user's email. It uses a **service account** scoped to only the Genesis folder — no access to the rest of the Drive.

You need two values: `GOOGLE_SERVICE_ACCOUNT_KEY` (path to JSON key file) and `GENESIS_DRIVE_FOLDER_ID`.

### 2a. GCP Project & Service Account (already done)

Project `openclaw-bots-sunriselabs` with service account `genesis-folder-access@openclaw-bots-sunriselabs.iam.gserviceaccount.com`.

The JSON key file is at: `~/.openclaw/genesis-service-account.json`

### 2b. Folder Sharing (already done)

The "Genesis" folder on `ians_ai@sunriselabs.io`'s Google Drive has been shared with the service account email as **Editor**. The service account can only see this folder and its contents.

Folder ID: `1fJGG4sAypTpeNRVtcQE-3MaiuYQHhV0w`

### 2c. Set Environment Variables on the Server

```bash
GOOGLE_SERVICE_ACCOUNT_KEY="/home/ian/.openclaw/genesis-service-account.json"
GENESIS_DRIVE_FOLDER_ID="1fJGG4sAypTpeNRVtcQE-3MaiuYQHhV0w"
```

Add these to your OpenClaw `.env` file (see section 3 below). The skill uses `scripts/gdrive-auth.sh` to mint a fresh access token via JWT before every Drive operation — no manual refresh needed, no token expiry to worry about.

---

## 3. Environment Variables Summary

Set all of these in your OpenClaw server environment before starting the bot:

| Variable | Required | Description |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | Yes | From @BotFather |
| `GOOGLE_SERVICE_ACCOUNT_KEY` | Yes | Path to service account JSON key file (e.g. `~/.openclaw/genesis-service-account.json`) |
| `GENESIS_DRIVE_FOLDER_ID` | Yes | Google Drive folder ID for the Genesis folder (`1fJGG4sAypTpeNRVtcQE-3MaiuYQHhV0w`) |
| `ALCHEMY_DATA_DIR` | No | Defaults to `$HOME/.openclaw/alchemy` |

**Store secrets in `/home/ian/.openclaw/.env`** (never committed to git). OpenClaw runs as a user systemd service — load the file via a drop-in config so it's always available at daemon start:

```bash
# Create the drop-in directory and config
mkdir -p ~/.config/systemd/user/openclaw.service.d
cat > ~/.config/systemd/user/openclaw.service.d/env.conf << EOF
[Service]
EnvironmentFile=/home/ian/.openclaw/.env
EOF

# Reload and restart
systemctl --user daemon-reload
systemctl --user restart openclaw.service
systemctl --user status openclaw.service
```

Do **not** use `source` or `set -a` — systemd services don't read shell profiles.

---

## 4. Weekly Nudge Cron Job

The skill can send weekly Telegram nudges to users with incomplete guides.

```bash
crontab -e
# Add this line (runs every Monday at 9am server time):
0 9 * * 1 bash -c 'set -a; source /home/ian/.openclaw/.env; set +a; exec bash /home/ian/.openclaw/workspace-genesis/skills/alchemy/scripts/weekly-nudge.sh'
```

---

## 5. Verifying the Setup

### Test Telegram delivery:
```bash
curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -d chat_id=YOUR_CHAT_ID \
  -d text="Genesis alchemy skill — admin test" | jq .ok
```

### Test service account auth:
```bash
GOOGLE_ACCESS_TOKEN=$(bash /path/to/skills/alchemy/scripts/gdrive-auth.sh "$GOOGLE_SERVICE_ACCOUNT_KEY")
echo "$GOOGLE_ACCESS_TOKEN" | head -c 20
# Should print a token starting with "ya29." — not "null"
```

### Test Drive upload to Genesis folder:
```bash
echo "test" > /tmp/test.txt
curl -s -X POST \
  "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart" \
  -H "Authorization: Bearer ${GOOGLE_ACCESS_TOKEN}" \
  -F "metadata={\"name\":\"test.txt\",\"parents\":[\"${GENESIS_DRIVE_FOLDER_ID}\"]};type=application/json" \
  -F "file=@/tmp/test.txt;type=text/plain" | jq .id
# Should return a file ID, not null — file appears inside the Genesis folder
```

### Test file sharing:
```bash
# Using the file ID from above
curl -s -X POST "https://www.googleapis.com/drive/v3/files/{FILE_ID}/permissions" \
  -H "Authorization: Bearer ${GOOGLE_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"type":"user","role":"writer","emailAddress":"youremail@example.com"}' | jq .id
# Should return a permission ID
```

---

## 6. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `access_token` is `null` from gdrive-auth.sh | Service account JSON missing or malformed | Check `GOOGLE_SERVICE_ACCOUNT_KEY` path and that the file is valid JSON |
| `401 Unauthorized` on Drive calls | Token expired or auth script failed | Re-run gdrive-auth.sh — tokens last 1 hour |
| `403 Forbidden` on Drive calls | Drive API not enabled on the project | Enable Drive API in Google Cloud Console for `openclaw-bots-sunriselabs` |
| `404 Not Found` on folder operations | Folder not shared with service account | Re-share the Genesis folder with the service account email as Editor |
| Telegram `sendDocument` fails | Bot not in chat / chat_id wrong | Ensure user has started the bot (`/start`) before delivery |
| `FILE_ID` is `null` after upload | Upload failed silently | Check full curl response — often a quota or auth issue |
