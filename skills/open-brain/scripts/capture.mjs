#!/usr/bin/env node
// capture.mjs — Ingest a thought into open-brain
// Usage: node capture.mjs <content> [source] [telegram_chat_id] [telegram_message_id]

import { surrealQuery, embed, extractMetadata, escapeId } from './lib.mjs';

const content = process.argv[2];
if (!content) {
  console.error('Usage: node capture.mjs "<content>" [source] [chat_id] [msg_id]');
  process.exit(1);
}

const source = process.argv[3] || 'manual';
const telegramChatId = process.argv[4] || null;
const telegramMessageId = process.argv[5] || null;

try {
  // Run embedding and metadata extraction in parallel
  const [embedding, meta] = await Promise.all([
    embed(content),
    extractMetadata(content),
  ]);

  // Insert the thought
  const thoughtResult = await surrealQuery(`
    CREATE thought SET
      content = $content,
      embedding = $embedding,
      type = $type,
      action_items = $action_items,
      source = $source,
      telegram_chat_id = $chat_id,
      telegram_message_id = $msg_id;
  `.replace('$content', JSON.stringify(content))
    .replace('$embedding', JSON.stringify(embedding))
    .replace('$type', JSON.stringify(meta.type || 'note'))
    .replace('$action_items', JSON.stringify(meta.action_items || []))
    .replace('$source', JSON.stringify(source))
    .replace('$chat_id', telegramChatId ? JSON.stringify(telegramChatId) : 'NONE')
    .replace('$msg_id', telegramMessageId ? JSON.stringify(telegramMessageId) : 'NONE')
  );

  const thoughtId = thoughtResult[0].result[0].id;

  // Create graph edges for people
  const edgePromises = [];
  for (const personName of (meta.people || [])) {
    const pid = escapeId(personName);
    edgePromises.push(surrealQuery(`
      INSERT INTO person (id, name) VALUES ('${pid}', '${personName.replace(/'/g, "\\'")}')
        ON DUPLICATE KEY UPDATE name = name;
      RELATE ${thoughtId}->mentions->person:${pid};
    `));
  }

  // Create graph edges for topics
  for (const topicName of (meta.topics || [])) {
    const tid = escapeId(topicName);
    edgePromises.push(surrealQuery(`
      INSERT INTO topic (id, name) VALUES ('${tid}', '${topicName.replace(/'/g, "\\'")}')
        ON DUPLICATE KEY UPDATE name = name;
      RELATE ${thoughtId}->tagged->topic:${tid};
    `));
  }

  await Promise.all(edgePromises);

  // Output confirmation
  const result = {
    id: thoughtId,
    type: meta.type || 'note',
    topics: meta.topics || [],
    people: meta.people || [],
    action_items: meta.action_items || [],
  };
  console.log(JSON.stringify(result, null, 2));
} catch (err) {
  console.error('Capture failed:', err.message);
  process.exit(1);
}
