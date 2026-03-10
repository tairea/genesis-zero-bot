#!/usr/bin/env bash
# ingest.sh — Ingest a file into Genesis' knowledge graph
# Usage: bash ingest.sh <file_path> [author]
# Output: JSON with concepts_count, relations_count, elapsed, doc_id, top_concepts, connections
set -euo pipefail

FILE="$1"
AUTHOR="${2:-}"

if [ ! -f "$FILE" ]; then
  echo '{"error": "File not found: '"$FILE"'"}' >&2
  exit 1
fi

SKILL_DIR="$HOME/.openclaw/workspace-genesis/skills/semantic-graph"
cd "$SKILL_DIR"
source .venv/bin/activate
export $(grep -v "^#" "$HOME/.openclaw/.env" | xargs)

# Run ingestion pipeline
if [ -n "$AUTHOR" ]; then
    OUTPUT=$(python pipeline.py ingest "$FILE" --embed -v --meta "{\"author\":\"$AUTHOR\"}" 2>&1)
else
    OUTPUT=$(python pipeline.py ingest "$FILE" --embed -v 2>&1)
fi

# Parse the summary line: "Done in 18.6s  |  chunks=2  concepts=10  relations=5  doc=document:abc"
SUMMARY=$(echo "$OUTPUT" | grep -oP 'Done in \K.*' || echo "")

if [ -z "$SUMMARY" ]; then
  # Check for errors
  ERROR=$(echo "$OUTPUT" | tail -3)
  echo "{\"error\": $(echo "$ERROR" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()))')}"
  exit 1
fi

ELAPSED=$(echo "$SUMMARY" | grep -oP '[\d.]+(?=s)' || echo "0")
CONCEPTS=$(echo "$SUMMARY" | grep -oP 'concepts=\K\d+' || echo "0")
RELATIONS=$(echo "$SUMMARY" | grep -oP 'relations=\K\d+' || echo "0")
DOC_ID=$(echo "$SUMMARY" | grep -oP 'doc=\K\S+' || echo "unknown")

# Get the new concepts and their connections
SEARCH_TERM=$(basename "$FILE" | sed 's/\.[^.]*$//' | sed 's/[-_]/ /g')
TOP_CONCEPTS=$(python pipeline.py search "$SEARCH_TERM" --limit 5 2>/dev/null | grep -oP '(?<=\] ).*(?= \()' | head -5 || echo "")
CONNECTIONS=$(python3 -c "
import asyncio, json, os
from surrealdb import AsyncSurreal
async def q():
    db = AsyncSurreal(url='ws://127.0.0.1:8000')
    await db.connect()
    await db.signin({'username': 'root', 'password': os.environ['SURREAL_PASS']})
    await db.use('semantic_graph', 'main')
    r = await db.query('''
        SELECT in.name as source, verb, out.name as target,
               evidence, nars_confidence
        FROM relates WHERE source_doc = \$doc
        ORDER BY nars_confidence DESC LIMIT 8
    ''', {'doc': '$DOC_ID'.replace('document:', '', 1)})
    await db.close()
    # Handle RecordID objects
    results = []
    for item in (r or []):
        results.append({
            'source': str(item.get('source', '')),
            'verb': str(item.get('verb', '')),
            'target': str(item.get('target', '')),
            'evidence': str(item.get('evidence', '')),
            'confidence': float(item.get('nars_confidence', 0))
        })
    print(json.dumps(results))
asyncio.run(q())
" 2>/dev/null || echo "[]")

# Build JSON result
python3 -c "
import json
result = {
    'doc_id': '$DOC_ID',
    'concepts_count': int('$CONCEPTS'),
    'relations_count': int('$RELATIONS'),
    'elapsed': float('$ELAPSED'),
    'top_concepts': [c.strip() for c in '''$TOP_CONCEPTS'''.strip().split('\n') if c.strip()],
    'connections': json.loads('''$CONNECTIONS'''),
}
print(json.dumps(result, indent=2))
"
