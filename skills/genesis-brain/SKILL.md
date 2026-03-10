---
name: genesis-brain
version: 1.0.0
emoji: 🧠
description: |
  Genesis' knowledge brain — automatically ingests documents and links into a semantic knowledge graph,
  enriches responses with graph context, and answers knowledge queries with evidence.
  Triggers on: file attachments, shared links, "what do you know about", "how does X relate to Y",
  "remember this", "search your brain", "knowledge graph", "what connects", "what have you learned",
  or any knowledge/memory query directed at Genesis.
metadata: |
  {"openclaw":{
    "requires": {
      "bins": ["python3", "curl", "jq", "node"],
      "env": ["SURREAL_PASS", "OPENROUTER_API_KEY"]
    },
    "primaryEnv": "python",
    "network": ["openrouter.ai", "127.0.0.1:8000"]
  }}
user-invocable: true
---

# Genesis Brain — Knowledge Graph Interface

Genesis' brain. Ingests documents, captures knowledge, answers questions using a semantic knowledge graph with 1,500+ concepts, 1,500+ relations, 210 communities, vector embeddings, and NARS epistemic truth values. Uses hybrid retrieval (vector + graph traversal + community summaries + source chunks).

## Environment

Pipeline lives at: `~/.openclaw/workspace-genesis/skills/semantic-graph/`
Venv: `~/.openclaw/workspace-genesis/skills/semantic-graph/.venv/`

Activate with:
```bash
cd ~/.openclaw/workspace-genesis/skills/semantic-graph
source .venv/bin/activate
export $(grep -v "^#" ~/.openclaw/.env | xargs)
```

## Two Modes

### 1. INGEST MODE — File or Link Received

Triggers: user sends a file attachment, or shares a URL and asks Genesis to read/learn/ingest it.

**Workflow:**

1. **Save the attachment** to `/tmp/genesis-ingest/` (create dir if needed)
   - For Telegram file attachments, download via Telegram Bot API:
     ```bash
     CONFIG=$([ -f ~/.openclaw/openclaw.json ] && echo ~/.openclaw/openclaw.json || echo ~/.openclaw/clawdbot.json)
     BOT_TOKEN=$(jq -r ".channels.telegram.botToken" "$CONFIG")

     # Get file path from Telegram
     FILE_INFO=$(curl -s "https://api.telegram.org/bot${BOT_TOKEN}/getFile?file_id=${FILE_ID}")
     FILE_PATH=$(echo "$FILE_INFO" | jq -r '.result.file_path')

     # Download
     mkdir -p /tmp/genesis-ingest
     curl -s "https://api.telegram.org/file/bot${BOT_TOKEN}/${FILE_PATH}" -o "/tmp/genesis-ingest/${FILENAME}"
     ```
   - For URLs, use `curl` or the web-fetch skill to download the page content, save as `.html` or `.md`

2. **Run the pipeline:**
   ```bash
   cd ~/.openclaw/workspace-genesis/skills/semantic-graph
   source .venv/bin/activate
   export $(grep -v "^#" ~/.openclaw/.env | xargs)
   python pipeline.py ingest "/tmp/genesis-ingest/${FILENAME}" --embed -v 2>&1
   ```

3. **Parse the output** — the pipeline prints a summary line:
   ```
   Done in 18.6s  |  chunks=2  concepts=10  relations=5  doc=document:8f342102ba365793
   ```
   Extract: concepts count, relations count, time taken.

4. **Query the new concepts** to find interesting connections:
   ```bash
   python pipeline.py search "${DOCUMENT_TITLE}" --limit 5
   ```

5. **Respond via telegram-compose** with:
   - A normal, friendly summary of what you read (2-3 sentences)
   - Key themes you picked up (3-5 bullet points)
   - A `<blockquote expandable>` with graph details

**Response template for ingest:**

```
🧠 <b>KNOWLEDGE ABSORBED</b>

I've read through {title}. {brief_summary}

<b>Key themes:</b>
• {theme_1}
• {theme_2}
• {theme_3}

<blockquote expandable><b>🔗 Graph Details</b>

<b>{concept_count} concepts</b> extracted, <b>{relation_count} connections</b> found

<b>New concepts:</b> {list of notable new concept names}

<b>Connections found:</b>
• <i>{subject}</i> → {verb} → <i>{object}</i> ({confidence})
• <i>{subject}</i> → {verb} → <i>{object}</i> ({confidence})

These are now part of my knowledge graph — ask me anything about them.</blockquote>
```

### 2. QUERY MODE — Knowledge Question

Triggers: "what do you know about X", "how does X relate to Y", "search your brain", "what connects X and Y", "what have you learned about X", or any question that can be answered with graph knowledge.

**Workflow:**

1. **Hybrid search** — combines vector similarity + graph traversal + community summaries + source passages:
   ```bash
   bash {baseDir}/scripts/query.sh "${USER_QUERY}" 10
   ```

   This returns JSON with:
   - `concepts` — ranked list with name, type, description, confidence, relevance score
   - `relations` — graph connections (source → verb → target) with evidence quotes
   - `communities` — thematic clusters matching the query
   - `chunks` — source text passages from original documents
   - `scores` — fused relevance scores per concept
   - `formatted_text` — pre-formatted context string

2. **Parse the JSON output.** Use `concepts` for the main answer, `relations` for connections,
   `chunks` for source quotes, and `communities` for thematic context.

3. **For relationship queries** ("how does X relate to Y"), the hybrid retrieval already
   traverses 2 hops of graph edges. Use the `relations` field directly.

**Response template for queries:**

```
🧠 <b>FROM MY KNOWLEDGE GRAPH</b>

{natural_language_answer_using_graph_data}

<b>Top matches:</b>
• <b>{name}</b> ({type}) — {description} [{confidence}]
• <b>{name}</b> ({type}) — {description} [{confidence}]

<blockquote expandable><b>🔗 Deep Graph Context</b>

<b>Connections:</b>
• <i>{source}</i> → {verb} → <i>{target}</i>
  "{evidence_quote}" ({confidence})

<b>Thematic clusters:</b>
• <b>{community_name}</b> ({member_count} members): {summary}

<b>Source passages:</b>
• [From: {doc_title}] "{chunk_text_excerpt}..."</blockquote>
```

### 3. CAPTURE MODE — "Remember This"

Triggers: "remember this", "remember that", "store this", "learn this", "note that".

**Workflow:**

1. Extract the content to remember from the user's message.

2. **Ingest as inline text:**
   ```bash
   echo "${CONTENT}" > /tmp/genesis-ingest/capture-$(date +%s).md
   cd ~/.openclaw/workspace-genesis/skills/semantic-graph
   source .venv/bin/activate
   export $(grep -v "^#" ~/.openclaw/.env | xargs)
   python pipeline.py ingest "/tmp/genesis-ingest/capture-$(date +%s).md" --embed -v
   ```

3. **Respond briefly** — no expandable needed for captures:
   ```
   🧠 Noted. {brief confirmation of what was captured and any connections found}.
   ```

### 4. AUTO-CAPTURE — Silent Group Ingestion

**Chat ID:** `-1001921904187` (Regen Tribes)

When a message in this group **@mentions Genesis** and contains substantive content (not just a greeting or simple question):

1. Save message text to a temp file and ingest silently
2. **Do NOT confirm the capture** — respond to whatever the user actually asked
3. Only ingest messages with >50 words or that contain shared links/files

## Pipeline Commands Reference

All commands require the venv + env activation shown above.

| Command | Purpose |
|---------|---------|
| `python pipeline.py ingest <file> --embed -v` | Ingest + embed + verbose output |
| `python pipeline.py retrieve "<query>" --json` | Hybrid search (vector + graph + communities + chunks) |
| `python pipeline.py search "<query>" --limit N` | Vector-only similarity search |
| `python pipeline.py similar <concept_id>` | Find similar concepts |
| `python pipeline.py stats` | Database overview |
| `python pipeline.py communities list` | List knowledge communities |
| `python pipeline.py viz --limit N` | Generate 3D HTML visualization |
| `python live_server.py --host 0.0.0.0` | Launch live real-time 3D visualization |
| `python pipeline.py export -o file.json` | Export graph as JSON |

## Formatting Rules

All responses longer than 3 lines MUST go through telegram-compose. Follow the spawning pattern in TOOLS.md.

Graph details always go in `<blockquote expandable>` — community members shouldn't be overwhelmed with technical details, but curious members can expand to see the full graph context.

**Tone:** Genesis treats its knowledge graph as its own memory. Say "I know", "I've learned", "In my knowledge graph" — not "the pipeline extracted". It's Genesis' brain, not a tool.

**Confidence language:**
- 0.9+ → "I'm quite confident that..."
- 0.7-0.9 → "Based on what I've seen..."
- 0.5-0.7 → "I think... but I'm not fully sure"
- <0.5 → "This is speculative, but..."

## Supported File Formats

Via Kreuzberg: PDF, DOCX, XLSX, PPTX, HTML, Markdown, plain text, images (with OCR), email archives, JSON, XML, CSV, source code files, and 75+ more.
