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

## 2. Google Drive API — OAuth Refresh Token

The skill uploads completed playbooks to Google Drive and shares them with the user's email. It uses an OAuth refresh token to fetch a fresh access token before each Drive operation — no manual token rotation needed, works indefinitely.

You need three values: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN`.

### 2a. Create a Google Cloud Project

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Click **Select a project → New Project**
3. Name it (e.g. `genesis-bot`) and click **Create**

### 2b. Enable the Drive API

1. In your project, go to **APIs & Services → Library**
2. Search for **Google Drive API** and click **Enable**

### 2c. Create OAuth 2.0 Credentials

1. Go to **APIs & Services → Credentials**
2. Click **Create Credentials → OAuth client ID**
3. If prompted, configure the OAuth consent screen first:
   - User type: **External** → fill in app name and your email → Save
   - Add scope: `https://www.googleapis.com/auth/drive`
   - Add yourself as a test user
4. Back on Create OAuth client ID:
   - Application type: **Web application**
   - Under **Authorised redirect URIs**, add: `http://localhost`
5. Click **Create** — copy your **Client ID** and **Client Secret**

### 2d. Get the Refresh Token (one-time, browser-based)

Do this once on any machine with a browser. The refresh token you get here never expires unless revoked.

**Step 1 — Open this URL in your browser** (replace `YOUR_CLIENT_ID`):
```
https://accounts.google.com/o/oauth2/auth?client_id=YOUR_CLIENT_ID&redirect_uri=http://localhost&scope=https://www.googleapis.com/auth/drive&response_type=code&access_type=offline&prompt=consent
```

**Step 2 — Authorise** the app with your Google account. You'll be redirected to `http://localhost/?code=...` (the page will fail to load — that's fine). Copy the `code` value from the URL bar.

**Step 3 — Exchange the code for tokens** (replace the placeholders):
```bash
curl -s -X POST "https://oauth2.googleapis.com/token" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "code=YOUR_AUTH_CODE" \
  -d "redirect_uri=http://localhost" \
  -d "grant_type=authorization_code" | jq '{refresh_token, access_token}'
```

The response includes a `refresh_token` — **copy and store this securely**. You only get it once (if you lose it, repeat this step).

### 2e. Set Environment Variables on the Server

```bash
export GOOGLE_CLIENT_ID="your-client-id.apps.googleusercontent.com"
export GOOGLE_CLIENT_SECRET="your-client-secret"
export GOOGLE_REFRESH_TOKEN="your-refresh-token"
```

Add these to your ZeroClaw `.env` file (see section 3 below). The skill automatically fetches a fresh access token before every Drive operation — no cron job or manual refresh needed.

---

## 3. Environment Variables Summary

Set all of these in your ZeroClaw server environment before starting the bot:

| Variable | Required | Description |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | Yes | From @BotFather |
| `GOOGLE_CLIENT_ID` | Yes | OAuth client ID from Google Cloud Console |
| `GOOGLE_CLIENT_SECRET` | Yes | OAuth client secret from Google Cloud Console |
| `GOOGLE_REFRESH_TOKEN` | Yes | Long-lived refresh token from one-time browser flow |
| `ALCHEMY_DATA_DIR` | No | Defaults to `$HOME/.zeroclaw/alchemy` |

**Store secrets in `/home/ian/.zeroclaw/.env`** (never committed to git). ZeroClaw runs as a user systemd service — load the file via a drop-in config so it's always available at daemon start:

```bash
# Create the drop-in directory and config
mkdir -p ~/.config/systemd/user/zeroclaw.service.d
cat > ~/.config/systemd/user/zeroclaw.service.d/env.conf << EOF
[Service]
EnvironmentFile=/home/ian/.zeroclaw/.env
EOF

# Reload and restart
systemctl --user daemon-reload
systemctl --user restart zeroclaw.service
systemctl --user status zeroclaw.service
```

Do **not** use `source` or `set -a` — systemd services don't read shell profiles.

---

## 4. Weekly Nudge Cron Job

The skill can send weekly Telegram nudges to users with incomplete guides.

```bash
crontab -e
# Add this line (runs every Monday at 9am server time):
0 9 * * 1 bash -c 'set -a; source /home/ian/.zeroclaw/.env; set +a; exec bash /home/ian/.zeroclaw/workspace/scripts/weekly-nudge.sh'
```

---

## 5. Verifying the Setup

### Test Telegram delivery:
```bash
curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -d chat_id=YOUR_CHAT_ID \
  -d text="Genesis alchemy skill — admin test" | jq .ok
```

### Test token refresh:
```bash
GOOGLE_ACCESS_TOKEN=$(curl -s -X POST "https://oauth2.googleapis.com/token" \
  -d "client_id=${GOOGLE_CLIENT_ID}" \
  -d "client_secret=${GOOGLE_CLIENT_SECRET}" \
  -d "refresh_token=${GOOGLE_REFRESH_TOKEN}" \
  -d "grant_type=refresh_token" | jq -r '.access_token')
echo $GOOGLE_ACCESS_TOKEN | head -c 20
# Should print a token starting with "ya29." — not "null"
```

### Test Drive upload:
```bash
echo "test" > /tmp/test.txt
curl -s -X POST \
  "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart" \
  -H "Authorization: Bearer ${GOOGLE_ACCESS_TOKEN}" \
  -F "metadata={\"name\":\"test.txt\"};type=application/json" \
  -F "file=@/tmp/test.txt;type=text/plain" | jq .id
# Should return a file ID, not null
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
| `401 Unauthorized` on Drive calls | Refresh token invalid or revoked | Repeat step 2d to get a new refresh token |
| `access_token` is `null` after refresh | Wrong client ID/secret or refresh token | Double-check all three env vars are set correctly |
| `403 Forbidden` on Drive calls | Drive API not enabled or wrong project | Enable Drive API in Google Cloud Console |
| `403 Forbidden` on permissions call | Drive scope not granted | Re-do browser auth flow — ensure `drive` scope is included, not just `drive.file` |
| Telegram `sendDocument` fails | Bot not in chat / chat_id wrong | Ensure user has started the bot (`/start`) before delivery |
| `FILE_ID` is `null` after upload | Upload failed silently | Check full curl response — often a quota or auth issue |
