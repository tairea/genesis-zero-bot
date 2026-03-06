// lib.mjs — Shared utilities for open-brain skill
// SurrealDB client + OpenRouter embedding/extraction

const SURREAL_URL = process.env.SURREAL_URL || 'http://127.0.0.1:8000';
const SURREAL_USER = process.env.SURREAL_USER || 'root';
const SURREAL_PASS = process.env.SURREAL_PASS;
const SURREAL_NS = 'open_brain';
const SURREAL_DB = 'main';
const OPENROUTER_KEY = process.env.OPENROUTER_API_KEY;

if (!SURREAL_PASS) {
  console.error('Error: SURREAL_PASS env var is required');
  process.exit(1);
}

// --- SurrealDB HTTP client ---

export async function surrealQuery(sql, vars = {}) {
  const res = await fetch(`${SURREAL_URL}/sql`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'Authorization': 'Basic ' + btoa(`${SURREAL_USER}:${SURREAL_PASS}`),
      'Surreal-NS': SURREAL_NS,
      'Surreal-DB': SURREAL_DB,
    },
    body: sql,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`SurrealDB error ${res.status}: ${text}`);
  }
  const data = await res.json();
  // Each statement returns { status, result } — check for errors
  for (const stmt of data) {
    if (stmt.status === 'ERR') throw new Error(`SurrealQL error: ${stmt.result}`);
  }
  return data;
}

// --- OpenRouter embedding ---

export async function embed(text) {
  if (!OPENROUTER_KEY) throw new Error('OPENROUTER_API_KEY env var is required');
  const res = await fetch('https://openrouter.ai/api/v1/embeddings', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${OPENROUTER_KEY}`,
    },
    body: JSON.stringify({
      model: 'openai/text-embedding-3-small',
      input: text,
    }),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`OpenRouter embedding error ${res.status}: ${text}`);
  }
  const data = await res.json();
  return data.data[0].embedding;
}

// --- OpenRouter metadata extraction ---

export async function extractMetadata(content) {
  if (!OPENROUTER_KEY) throw new Error('OPENROUTER_API_KEY env var is required');
  const res = await fetch('https://openrouter.ai/api/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${OPENROUTER_KEY}`,
    },
    body: JSON.stringify({
      model: 'openai/gpt-4o-mini',
      messages: [
        {
          role: 'system',
          content: `Extract metadata from the following thought/message. Return JSON only, no markdown fences.
{
  "type": "idea|task|note|question|decision|reflection",
  "topics": ["topic1", "topic2"],
  "people": ["person name"],
  "action_items": ["action item if any"]
}
Rules:
- type: classify the thought into one of the listed types
- topics: 1-5 relevant topic tags, lowercase
- people: names of people mentioned (empty array if none)
- action_items: concrete action items (empty array if none)`,
        },
        { role: 'user', content },
      ],
      temperature: 0,
    }),
  });
  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`OpenRouter extraction error ${res.status}: ${errText}`);
  }
  const data = await res.json();
  const raw = data.choices[0].message.content.trim();
  try {
    return JSON.parse(raw);
  } catch {
    // Try stripping markdown fences
    const cleaned = raw.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
    return JSON.parse(cleaned);
  }
}

// --- Helpers ---

export function escapeId(name) {
  // SurrealDB record IDs: sanitize for use as string keys
  return name.toLowerCase().replace(/[^a-z0-9_-]/g, '_').replace(/_+/g, '_').replace(/^_|_$/g, '');
}
