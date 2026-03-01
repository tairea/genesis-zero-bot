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

## 2. Google Drive API — Service Account (Recommended)

The skill uploads completed playbooks to Google Drive and shares them with the user's email. This requires a Google Cloud service account with Drive API access.

> **Why a service account?** Unlike OAuth user tokens (which expire and need a browser to refresh), service account tokens are automatically refreshed using a JSON key file — no user interaction needed.

### 2a. Create a Google Cloud Project

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Click **Select a project → New Project**
3. Name it (e.g. `genesis-bot`) and click **Create**

### 2b. Enable the Drive API

1. In your project, go to **APIs & Services → Library**
2. Search for **Google Drive API** and click **Enable**

### 2c. Create a Service Account

1. Go to **APIs & Services → Credentials**
2. Click **Create Credentials → Service Account**
3. Give it a name (e.g. `genesis-alchemy`) and click **Create and Continue**
4. Skip optional role/user grants — click **Done**
5. Back on the Credentials page, click your new service account
6. Go to the **Keys** tab → **Add Key → Create new key → JSON**
7. Download the JSON key file — store it securely on your server (e.g. `/etc/genesis/gdrive-key.json`)

### 2d. Generate an Access Token at Runtime

Service accounts use short-lived Bearer tokens generated from the key file. The skill expects `GOOGLE_DRIVE_TOKEN` to be a valid token at runtime.

Install the `google-auth-library` helper or use this `curl`+`jwt` approach — or simplest, use the `gcloud` CLI:

```bash
# One-time: authenticate gcloud with the service account
gcloud auth activate-service-account --key-file=/etc/genesis/gdrive-key.json

# Generate a token (valid for 1 hour)
GOOGLE_DRIVE_TOKEN=$(gcloud auth print-access-token)
export GOOGLE_DRIVE_TOKEN
```

For long-running bots, wrap token refresh in a helper script called before any Drive operation:

```bash
# /usr/local/bin/gdrive-token.sh
#!/usr/bin/env bash
gcloud auth activate-service-account --key-file=/etc/genesis/gdrive-key.json --quiet 2>/dev/null
gcloud auth print-access-token
```

Then in the bot environment:
```bash
export GOOGLE_DRIVE_TOKEN=$(bash /usr/local/bin/gdrive-token.sh)
```

### 2e. Grant the Service Account Access to a Shared Drive Folder (Optional)

By default, files uploaded by the service account live in the service account's own Drive (not visible to you). To organise completed playbooks in a shared folder:

1. Create a folder in your Google Drive (e.g. `Alchemy Playbooks`)
2. Share it with the service account's email address (found in the JSON key file under `client_email`) — give it **Editor** access
3. Note the folder ID from the URL: `drive.google.com/drive/folders/{FOLDER_ID}`
4. Set `GOOGLE_DRIVE_FOLDER_ID` and update the upload curl in `SKILL.md` to include:
   ```
   "parents": ["{FOLDER_ID}"]
   ```
   in the metadata JSON.

---

## 3. Environment Variables Summary

Set all of these in your OpenClaw server environment before starting the bot:

| Variable | Required | Description |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | Yes | From @BotFather |
| `GOOGLE_DRIVE_TOKEN` | Yes | Short-lived Bearer token from service account |
| `GOOGLE_DRIVE_FOLDER_ID` | No | Parent folder ID for uploaded playbooks |
| `ALCHEMY_DATA_DIR` | No | Defaults to `$HOME/.openclaw/alchemy` |

**Recommended:** Store secrets in a `.env` file (never committed to git) and load with:
```bash
set -a; source /etc/genesis/.env; set +a
```

---

## 4. Weekly Nudge Cron Job

The skill can send weekly Telegram nudges to users with incomplete guides.

```bash
crontab -e
# Add this line (runs every Monday at 9am server time):
0 9 * * 1 set -a; source /etc/genesis/.env; set +a; bash /path/to/skills/alchemy/scripts/weekly-nudge.sh
```

Or if your env is already loaded by the shell:
```bash
0 9 * * 1 TELEGRAM_BOT_TOKEN=your_token bash /path/to/skills/alchemy/scripts/weekly-nudge.sh
```

---

## 5. Verifying the Setup

### Test Telegram delivery:
```bash
curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -d chat_id=YOUR_CHAT_ID \
  -d text="Genesis alchemy skill — admin test" | jq .ok
```

### Test Drive upload:
```bash
echo "test" > /tmp/test.txt
curl -s -X POST \
  "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart" \
  -H "Authorization: Bearer ${GOOGLE_DRIVE_TOKEN}" \
  -F "metadata={\"name\":\"test.txt\"};type=application/json" \
  -F "file=@/tmp/test.txt;type=text/plain" | jq .id
# Should return a file ID, not null
```

### Test file sharing:
```bash
# Using the file ID from above
curl -s -X POST "https://www.googleapis.com/drive/v3/files/{FILE_ID}/permissions" \
  -H "Authorization: Bearer ${GOOGLE_DRIVE_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"type":"user","role":"writer","emailAddress":"youremail@example.com"}' | jq .id
# Should return a permission ID
```

---

## 6. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `401 Unauthorized` on Drive calls | Token expired or invalid | Re-run `gcloud auth print-access-token` |
| `403 Forbidden` on Drive calls | API not enabled or wrong project | Enable Drive API in Cloud Console |
| `403 Forbidden` on permissions call | Service account can't share files | The file is owned by service account — sharing works but recipient gets a link, not ownership. This is expected. |
| Telegram `sendDocument` fails | Bot not in chat / chat_id wrong | Ensure user has started the bot (`/start`) before delivery |
| `FILE_ID` is `null` after upload | Upload failed silently | Check full curl response — often a quota or auth issue |
