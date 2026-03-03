#!/usr/bin/env bash
# gdrive-auth.sh — Get a Google Drive access token from a service account JSON key
# Usage: bash gdrive-auth.sh /path/to/service-account.json [impersonate-email]
# Outputs: access token string (or "null" on failure)
#
# When impersonate-email is provided, the service account acts on behalf of that
# user via domain-wide delegation (requires Workspace admin setup).
set -euo pipefail

SA_KEY_FILE="${1:?Usage: gdrive-auth.sh /path/to/service-account.json [impersonate-email]}"
IMPERSONATE="${2:-}"

CLIENT_EMAIL=$(jq -r '.client_email' "$SA_KEY_FILE")
PRIVATE_KEY=$(jq -r '.private_key' "$SA_KEY_FILE")

b64url() { openssl base64 -e -A | tr '+/' '-_' | tr -d '='; }

HEADER=$(printf '{"alg":"RS256","typ":"JWT"}' | b64url)

NOW=$(date +%s)
EXP=$((NOW + 3600))

if [ -n "$IMPERSONATE" ]; then
  CLAIM=$(printf '{"iss":"%s","sub":"%s","scope":"https://www.googleapis.com/auth/drive","aud":"https://oauth2.googleapis.com/token","iat":%d,"exp":%d}' \
    "$CLIENT_EMAIL" "$IMPERSONATE" "$NOW" "$EXP" | b64url)
else
  CLAIM=$(printf '{"iss":"%s","scope":"https://www.googleapis.com/auth/drive","aud":"https://oauth2.googleapis.com/token","iat":%d,"exp":%d}' \
    "$CLIENT_EMAIL" "$NOW" "$EXP" | b64url)
fi

SIGNATURE=$(printf '%s.%s' "$HEADER" "$CLAIM" | \
  openssl dgst -sha256 -sign <(printf '%s' "$PRIVATE_KEY") | b64url)

JWT="${HEADER}.${CLAIM}.${SIGNATURE}"

curl -s -X POST "https://oauth2.googleapis.com/token" \
  -d "grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Ajwt-bearer" \
  -d "assertion=${JWT}" | jq -r '.access_token'
