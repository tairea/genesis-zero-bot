#!/usr/bin/env node
// list.mjs — List/filter thoughts
// Usage: node list.mjs [--type TYPE] [--person NAME] [--topic NAME] [--since DATE] [--limit N]

import { surrealQuery, escapeId } from './lib.mjs';

const args = process.argv.slice(2);
function getArg(flag) {
  const i = args.indexOf(flag);
  return i !== -1 && i + 1 < args.length ? args[i + 1] : null;
}

const type = getArg('--type');
const person = getArg('--person');
const topic = getArg('--topic');
const since = getArg('--since');
const limit = parseInt(getArg('--limit') || '20');

try {
  let query;

  if (person) {
    // Graph traversal: find thoughts that mention this person
    const pid = escapeId(person);
    query = `SELECT <-mentions<-thought.* AS thoughts FROM person:${pid};`;
    const res = await surrealQuery(query);
    let thoughts = res[0].result[0]?.thoughts || [];
    if (type) thoughts = thoughts.filter(t => t.type === type);
    if (since) thoughts = thoughts.filter(t => t.created_at >= since);
    thoughts = thoughts.slice(0, limit).map(t => ({
      id: t.id, content: t.content, type: t.type,
      source: t.source, action_items: t.action_items, created_at: t.created_at,
    }));
    console.log(JSON.stringify(thoughts, null, 2));
  } else if (topic) {
    // Graph traversal: find thoughts tagged with this topic
    const tid = escapeId(topic);
    query = `SELECT <-tagged<-thought.* AS thoughts FROM topic:${tid};`;
    const res = await surrealQuery(query);
    let thoughts = res[0].result[0]?.thoughts || [];
    if (type) thoughts = thoughts.filter(t => t.type === type);
    if (since) thoughts = thoughts.filter(t => t.created_at >= since);
    thoughts = thoughts.slice(0, limit).map(t => ({
      id: t.id, content: t.content, type: t.type,
      source: t.source, action_items: t.action_items, created_at: t.created_at,
    }));
    console.log(JSON.stringify(thoughts, null, 2));
  } else {
    // Direct query with filters
    const conditions = [];
    if (type) conditions.push(`type = '${type}'`);
    if (since) conditions.push(`created_at >= '${since}'`);
    const where = conditions.length > 0 ? `WHERE ${conditions.join(' AND ')}` : '';
    query = `SELECT id, content, type, source, action_items, created_at FROM thought ${where} ORDER BY created_at DESC LIMIT ${limit};`;
    const res = await surrealQuery(query);
    console.log(JSON.stringify(res[0].result, null, 2));
  }
} catch (err) {
  console.error('List failed:', err.message);
  process.exit(1);
}
