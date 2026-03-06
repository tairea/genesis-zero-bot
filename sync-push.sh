#!/usr/bin/env bash
# sync-push — Push local genesis-zero-bot -> Hetzner workspace-genesis
#
# Local-newer files win (--update skips remote files that are newer).
#
# Usage: ./sync-push.sh [--dry-run] [--delete]
#   --delete  Remove server files that were deleted locally

set -euo pipefail

LOCAL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REMOTE_HOST="hetzner-ian"
REMOTE_DIR="/home/ian/.openclaw/workspace-genesis"
DRY_RUN=""
DELETE=""

for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN="--dry-run"; echo "Dry run mode -- no changes will be made" ;;
    --delete)  DELETE="--delete";    echo "Delete mode -- server files not present locally will be removed" ;;
  esac
done

RSYNC_BASE=(
  -avz
  --checksum
  --update
  --exclude='.git/'
  --exclude='*.swp'
  --exclude='.DS_Store'
  # Runtime dirs and files -- server-only, never synced
  --exclude='cron/'
  --exclude='memory/'
  --exclude='sessions/'
  --exclude='state/'
  --exclude='BOOTSTRAP.md'
  --exclude='BOOTSTRAP.md.done'
  --exclude='MEMORY.md'
  --exclude='TOOLS.md'
  --exclude='.openclaw/'
  # Local-only files -- don't push to server
  --exclude='sync-pull.sh'
  --exclude='sync-push.sh'
  --exclude='sync-genesis.sh'
  # Large source docs
  --exclude='*Full Guide*'
)

echo ""
echo "--- PUSH: Local -> Hetzner ---"
rsync "${RSYNC_BASE[@]}" $DRY_RUN $DELETE \
  "${LOCAL_DIR}/" \
  "${REMOTE_HOST}:${REMOTE_DIR}/"

echo ""
echo "Push complete"
