#!/usr/bin/env bash
# stats.sh — Show Genesis knowledge graph stats
# Usage: bash stats.sh
# Output: JSON with counts, top types, top verbs, embedding coverage
set -euo pipefail

SKILL_DIR="$HOME/.openclaw/workspace-genesis/skills/semantic-graph"
cd "$SKILL_DIR"
source .venv/bin/activate
export $(grep -v "^#" "$HOME/.openclaw/.env" | xargs)

python3 -c "
import asyncio, json, os
from surrealdb import AsyncSurreal

async def run():
    db = AsyncSurreal(url='ws://127.0.0.1:8000')
    await db.connect()
    await db.signin({'username': 'root', 'password': os.environ['SURREAL_PASS']})
    await db.use('semantic_graph', 'main')

    async def count(table):
        r = await db.query(f'SELECT count() as cnt FROM {table} GROUP ALL')
        if r and isinstance(r, list) and r:
            first = r[0]
            if isinstance(first, dict):
                return first.get('cnt', 0)
        return 0

    stats = {
        'documents': await count('document'),
        'chunks': await count('chunk'),
        'concepts': await count('concept'),
        'relations': await count('relates'),
        'mentions': await count('mentions'),
    }

    # Embedding coverage
    emb = await db.query('SELECT count() as cnt FROM concept WHERE embedding IS NOT NONE GROUP ALL')
    emb_count = emb[0].get('cnt', 0) if emb and isinstance(emb, list) and emb and isinstance(emb[0], dict) else 0
    stats['embedded'] = emb_count

    # Top types
    types = await db.query('SELECT type, count() as cnt FROM concept GROUP BY type ORDER BY cnt DESC LIMIT 5')
    stats['top_types'] = [{str(k): v for k, v in t.items()} for t in (types or []) if isinstance(t, dict)]

    # Top verbs
    verbs = await db.query('SELECT verb, count() as cnt FROM relates GROUP BY verb ORDER BY cnt DESC LIMIT 5')
    stats['top_verbs'] = [{str(k): v for k, v in v.items()} for v in (verbs or []) if isinstance(v, dict)]

    # Recent documents
    docs = await db.query('SELECT title, word_count FROM document LIMIT 5')
    stats['recent_docs'] = [{str(k): (str(v) if hasattr(v, 'table_name') else v) for k, v in d.items()} for d in (docs or []) if isinstance(d, dict)]

    print(json.dumps(stats, indent=2, default=str))
    await db.close()

asyncio.run(run())
"
