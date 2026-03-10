#!/usr/bin/env bash
# by-author.sh — Find documents shared by a specific member
# Usage: bash by-author.sh "<author name or @handle>" [limit]
# Output: JSON array of matching documents
set -euo pipefail

AUTHOR="$1"
LIMIT="${2:-10}"
SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HANDLE_MAP="$SCRIPTS_DIR/handle-map.json"

SKILL_DIR="$HOME/.openclaw/workspace-genesis/skills/semantic-graph"
cd "$SKILL_DIR"
source .venv/bin/activate
export $(grep -v "^#" "$HOME/.openclaw/.env" | xargs)

AUTHOR="$AUTHOR" LIMIT="$LIMIT" HANDLE_MAP="$HANDLE_MAP" python3 -c '
import asyncio, json, os
from surrealdb import AsyncSurreal

async def main():
    author = os.environ.get("AUTHOR", "")
    limit = int(os.environ.get("LIMIT", 10))
    handle_map_path = os.environ.get("HANDLE_MAP", "")

    # Resolve @handle -> display name via auto-maintained map
    if handle_map_path and os.path.exists(handle_map_path):
        with open(handle_map_path) as f:
            handle_map = json.load(f)
        author = handle_map.get(author) or handle_map.get(author.lstrip("@")) or author

    db = AsyncSurreal("ws://127.0.0.1:8000")
    await db.connect()
    await db.signin({"username": "root", "password": os.environ["SURREAL_PASS"]})
    await db.use("semantic_graph", "main")

    # Query top-level author field; also check metadata.author for older docs
    rows = await db.query(
        "SELECT id, title, author, word_count, created_at FROM document "
        "WHERE author = $author OR metadata.author = $author "
        "LIMIT $limit",
        {"author": author, "limit": limit}
    )

    docs = []
    for row in (rows or []):
        docs.append({
            "doc_id": str(row.get("id", "")),
            "title": str(row.get("title", "")),
            "author": str(row.get("author", "")),
            "word_count": row.get("word_count", 0),
            "created_at": str(row.get("created_at", "")),
        })

    print(json.dumps({"author": author, "count": len(docs), "documents": docs}, indent=2))

asyncio.run(main())
'
