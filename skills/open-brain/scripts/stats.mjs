#!/usr/bin/env node
// stats.mjs — Thought stats via graph queries
// Usage: node stats.mjs

import { surrealQuery } from './lib.mjs';

try {
  const [countRes, typesRes, peopleRes, topicsRes, recentRes] = await surrealQuery(`
    SELECT count() AS total FROM thought GROUP ALL;
    SELECT type, count() AS count FROM thought GROUP BY type ORDER BY count DESC;
    SELECT name, count(<-mentions<-thought) AS mention_count FROM person ORDER BY mention_count DESC LIMIT 10;
    SELECT name, count(<-tagged<-thought) AS tag_count FROM topic ORDER BY tag_count DESC LIMIT 10;
    SELECT id, content, type, created_at FROM thought ORDER BY created_at DESC LIMIT 5;
  `);

  const stats = {
    total_thoughts: countRes.result[0]?.total || 0,
    by_type: typesRes.result,
    top_people: peopleRes.result,
    top_topics: topicsRes.result,
    recent: recentRes.result.map(t => ({
      id: t.id, content: t.content?.substring(0, 100) + (t.content?.length > 100 ? '...' : ''),
      type: t.type, created_at: t.created_at,
    })),
  };

  console.log(JSON.stringify(stats, null, 2));
} catch (err) {
  console.error('Stats failed:', err.message);
  process.exit(1);
}
