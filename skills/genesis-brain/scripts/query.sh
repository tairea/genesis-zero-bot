#!/usr/bin/env bash
# query.sh — Search Genesis' knowledge graph (hybrid retrieval)
# Usage: bash query.sh "<natural language query>" [limit]
# Output: JSON with concepts, relations, chunks, communities, and scores
set -euo pipefail

QUERY="$1"
LIMIT="${2:-10}"

SKILL_DIR="$HOME/.openclaw/workspace-genesis/skills/semantic-graph"
cd "$SKILL_DIR"
source .venv/bin/activate
export $(grep -v "^#" "$HOME/.openclaw/.env" | xargs)

python3 pipeline.py retrieve "$QUERY" --limit "$LIMIT" --hops 2 --json
