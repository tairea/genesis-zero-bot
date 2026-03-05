#!/usr/bin/env node
// search.mjs — Semantic vector search against open-brain
// Usage: node search.mjs "<query>" [limit]

import { surrealQuery, embed } from './lib.mjs';

const query = process.argv[2];
if (!query) {
  console.error('Usage: node search.mjs "<query>" [limit]');
  process.exit(1);
}

const limit = parseInt(process.argv[3]) || 10;

try {
  const embedding = await embed(query);

  const results = await surrealQuery(`
    SELECT id, content, type, source, action_items, created_at,
           vector::distance::knn() AS distance
    FROM thought
    WHERE embedding <|${limit},100|> ${JSON.stringify(embedding)};
  `);

  const thoughts = results[0].result.map(t => ({
    id: t.id,
    content: t.content,
    type: t.type,
    source: t.source,
    action_items: t.action_items,
    distance: t.distance,
    created_at: t.created_at,
  }));

  console.log(JSON.stringify(thoughts, null, 2));
} catch (err) {
  console.error('Search failed:', err.message);
  process.exit(1);
}
