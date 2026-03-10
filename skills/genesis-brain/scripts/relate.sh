#!/usr/bin/env bash
# relate.sh — Find how two concepts relate in the knowledge graph
# Usage: bash relate.sh "<concept_a>" "<concept_b>"
# Output: JSON with direct connections, shared neighbors, and graph paths
set -euo pipefail

CONCEPT_A="$1"
CONCEPT_B="$2"

SKILL_DIR="$HOME/.openclaw/workspace-genesis/skills/semantic-graph"
cd "$SKILL_DIR"
source .venv/bin/activate
export $(grep -v "^#" "$HOME/.openclaw/.env" | xargs)

python3 -c "
import asyncio, json, os, sys
sys.path.insert(0, '.')
from surrealdb import AsyncSurreal
from embeddings import search

async def run():
    db = AsyncSurreal(url='ws://127.0.0.1:8000')
    await db.connect()
    await db.signin({'username': 'root', 'password': os.environ['SURREAL_PASS']})
    await db.use('semantic_graph', 'main')

    a = '''$CONCEPT_A'''
    b = '''$CONCEPT_B'''

    # Find concepts via semantic search (more robust than string matching)
    concept_a = await search(db, a, limit=3)
    concept_b = await search(db, b, limit=3)

    def clean(items):
        result = []
        for item in (items or []):
            c = {}
            for k, v in item.items():
                if hasattr(v, 'table_name'):
                    c[k] = str(v)
                else:
                    c[k] = v
            result.append(c)
        return result

    # Get the best-match names
    name_a = concept_a[0].get('name', a) if concept_a else a
    name_b = concept_b[0].get('name', b) if concept_b else b

    # Direct relations between them
    direct = await db.query('''
        SELECT in.name as source, verb, out.name as target,
               evidence, nars_confidence, verb_category
        FROM relates
        WHERE (in.name = \$a AND out.name = \$b)
           OR (in.name = \$b AND out.name = \$a)
    ''', {'a': name_a, 'b': name_b})

    # All relations touching A
    rels_a = await db.query('''
        SELECT in.name as source, verb, out.name as target, nars_confidence
        FROM relates
        WHERE in.name = \$n OR out.name = \$n
        LIMIT 10
    ''', {'n': name_a})

    # All relations touching B
    rels_b = await db.query('''
        SELECT in.name as source, verb, out.name as target, nars_confidence
        FROM relates
        WHERE in.name = \$n OR out.name = \$n
        LIMIT 10
    ''', {'n': name_b})

    # Find shared neighbors
    neighbors_a = set()
    for r in (rels_a or []):
        neighbors_a.add(str(r.get('source', '')))
        neighbors_a.add(str(r.get('target', '')))
    neighbors_b = set()
    for r in (rels_b or []):
        neighbors_b.add(str(r.get('source', '')))
        neighbors_b.add(str(r.get('target', '')))
    shared = list((neighbors_a & neighbors_b) - {name_a, name_b, ''})

    output = {
        'concept_a': clean(concept_a[:3]),
        'concept_b': clean(concept_b[:3]),
        'direct_relations': clean(direct),
        'connections_a': clean(rels_a[:5]),
        'connections_b': clean(rels_b[:5]),
        'shared_neighbors': shared[:10],
    }
    print(json.dumps(output, indent=2, default=str))
    await db.close()

asyncio.run(run())
"
