#!/usr/bin/env bash
# sync-pull — Pull Hetzner workspace-genesis -> local genesis-zero-bot
#
# Remote-newer files win (--update skips local files that are newer).
#
# Usage: ./sync-pull.sh [--dry-run] [--delete]
#   --delete  Remove local files that were deleted on the server

set -euo pipefail

LOCAL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REMOTE_HOST="hetzner-ian"
REMOTE_DIR="/home/ian/.openclaw/workspace-genesis"
DRY_RUN=""
DELETE=""

for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN="--dry-run"; echo "Dry run mode -- no changes will be made" ;;
    --delete)  DELETE="--delete";    echo "Delete mode -- local files not on server will be removed" ;;
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
  # Local-only files -- don't overwrite from server
  --exclude='sync-pull.sh'
  --exclude='sync-push.sh'
  --exclude='sync-genesis.sh'
  # Large source docs
  --exclude='*Full Guide*'
)

echo ""
echo "--- PULL: Hetzner -> Local ---"
rsync "${RSYNC_BASE[@]}" $DRY_RUN $DELETE \
  "${REMOTE_HOST}:${REMOTE_DIR}/" \
  "${LOCAL_DIR}/"

echo ""
echo "Pull complete"
