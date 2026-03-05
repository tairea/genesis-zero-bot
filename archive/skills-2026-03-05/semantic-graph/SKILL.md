# SKILL: Arbitrary Input → Semantic Knowledge Graph → SurrealDB

## Purpose

Transform any document — PDF, DOCX, HTML, Markdown, code, plain text, or
images — into a richly typed, traversable knowledge graph stored in SurrealDB.
Uses Kreuzberg for text extraction, a no-LLM Grammar Triangle for semantic
annotation, and Claude for concept/relation extraction with NARS epistemic
truth values.

**Assumes both `kreuzberg` and `surrealdb` Python packages are already installed.**

---

## When to invoke this skill

- "Convert this document into a knowledge graph"
- "Extract entities and relationships from…"
- "Index this content into a graph database"
- "Build a semantic graph from…"
- "What concepts and connections are in this file?"
- Any task requiring structured knowledge extraction to a graph store
- Any task requiring multi-document synthesis with provenance tracking

---

## File structure

| File | Role |
|------|------|
| `graph_extract.py` | Main pipeline: CLI entry point + `GraphExtractor` class |
| `llm_parser.py` | Claude API calls for concept + relation extraction |
| `grammar_triangle.py` | No-LLM semantic annotation + text chunker |
| `verbs.py` | 144-verb taxonomy with normalization |
| `schema.surql` | SurrealDB schema (apply once) |

---

## Pipeline

```
[ANY INPUT: file path / bytes / stdin]
         │
         ▼
  Kreuzberg extraction
  extract_bytes_sync(raw_bytes, mime_type=...)
  → .content      — clean unicode text
  → .metadata     — title, language, quality_score, page_count, …
  → .tables       — extracted table structures (if any)
         │
         ▼
  Semantic chunker  (grammar_triangle.chunk_text)
  • Split on double-newline paragraph boundaries
  • Max 800 chars per chunk, 200-char overlap between adjacent chunks
  • Code blocks (``` fenced) → isolated chunk, type="code"
  • Markdown tables (|…|) → isolated chunk, type="table"
  • Headings (#…) → type="heading", lists → type="list"
  • Each chunk annotated with Grammar Triangle (no LLM, pure signal)
         │
         ▼
  Grammar Triangle annotation  (per chunk, zero API cost)
  • NSM weights   — 20 Wierzbicka semantic primitives
  • Qualia coords — 8 phenomenal dimensions
  • Causality     — past/present/future tense balance + agency
  • dominant_mode — emotional | cognitive | existential |
                    emergent | relational | technical
         │
         ▼
  Claude semantic parser  (llm_parser.extract_chunks)
  • Batched: default 4 chunks per API call
  • Returns: concepts (nodes) + relations (edges) as JSON
  • Verbs normalised to 144-verb taxonomy
  • NARS truth values assigned per extraction
         │
         ▼
  SurrealDB graph writer  (graph_extract.GraphExtractor)
  • UPSERT document record
  • UPSERT chunk records + RELATE document→contains→chunk
  • UPSERT concept records — deduplicated by (name.lower(), type)
    — NARS revision merges evidence when same concept seen again
  • RELATE concept:A →relates→ concept:B with full verb metadata
  • RELATE chunk →mentions→ concept (provenance)
```

---

## SurrealDB schema

All tables are `SCHEMALESS` — fields can be added at any time without
migration. `TYPE RELATION` tables enable native `->` graph traversal.

```sql
-- NODE TABLES
DEFINE TABLE document SCHEMALESS;   -- source file record
DEFINE TABLE chunk    SCHEMALESS;   -- text segment + Grammar Triangle
DEFINE TABLE concept  SCHEMALESS;   -- named entity / idea / event / system

-- EDGE TABLES (TYPE RELATION = native graph, enables -> traversal)
DEFINE TABLE contains TYPE RELATION SCHEMALESS;  -- document → chunk
DEFINE TABLE mentions TYPE RELATION SCHEMALESS;  -- chunk → concept
DEFINE TABLE relates  TYPE RELATION SCHEMALESS;  -- concept [verb] concept
```

### document fields
| Field | Type | Notes |
|-------|------|-------|
| `source` | string | file path, URL, or "stdin" |
| `mime_type` | string | e.g. "application/pdf" |
| `title` | string? | from Kreuzberg metadata or filename |
| `word_count` | int? | |
| `language` | string? | BCP-47, e.g. "en" |
| `quality` | float? | Kreuzberg `quality_score` 0–1 |
| `metadata` | object | remaining Kreuzberg metadata |
| `created_at` | datetime | |

### chunk fields
| Field | Type | Notes |
|-------|------|-------|
| `text` | string | raw chunk text |
| `index` | int | position in document (0-based) |
| `char_start` | int? | byte offset in full text |
| `char_end` | int? | |
| `chunk_type` | string | paragraph \| heading \| code \| table \| list \| quote |
| `nsm` | object | `{FEEL:0.8, THINK:0.3, KNOW:0.5, …}` — 20 primitives |
| `qualia` | object | `{valence:0.7, arousal:0.2, certainty:0.6, …}` — 8 dims |
| `causality` | object | `{past:0.3, present:0.5, future:0.2, temporality:−0.1, agency:0.6}` |
| `dominant_mode` | string | emotional \| cognitive \| existential \| emergent \| relational \| technical |

### concept fields
| Field | Type | Notes |
|-------|------|-------|
| `name` | string | canonical name |
| `type` | string | entity \| system \| process \| idea \| attribute \| event \| person \| place \| quantity \| quality \| relation |
| `description` | string? | one-sentence summary |
| `aliases` | string[] | acronyms, variants, camelCase names |
| `rung` | int | abstraction depth R0–R9 |
| `nars_frequency` | float | 0–1, how consistently true |
| `nars_confidence` | float | 0–1, evidence strength |
| `evidence_count` | int | observations seen; drives NARS revision |
| `qualia` | object | concept's felt character |
| `tags` | string[] | free-form labels |
| `properties` | object | arbitrary extras from extraction |
| `first_seen_in` | record<document> | |

### relates fields (the core semantic edge)
| Field | Type | Notes |
|-------|------|-------|
| `in` | record<concept> | subject |
| `out` | record<concept> | object |
| `verb` | string | one of 144 canonical verbs |
| `verb_category` | string | Structural \| Causal \| Temporal \| Epistemic \| Agentive \| Experiential |
| `weight` | float | = nars_confidence |
| `nars_frequency` | float | |
| `nars_confidence` | float | |
| `evidence_count` | int | |
| `evidence` | string? | ≤50-char quote from source text |
| `source_chunk` | record<chunk>? | provenance |
| `source_doc` | record<document>? | |
| `valid_from` | datetime? | for time-bounded facts |
| `valid_until` | datetime? | |

---

## Grammar Triangle (no-LLM semantic annotation)

Every chunk is annotated before any LLM call using pure keyword activation.
This gives a continuous semantic fingerprint at zero API cost.

### NSM — 20 Wierzbicka semantic primitives
Keyword activation, score = min(1.0, hit_count × 0.12):

| Primitive | Keywords (sample) |
|-----------|-------------------|
| FEEL | feel, sense, experience, emotion, heart, aware |
| THINK | think, thought, consider, ponder, reflect, believe |
| KNOW | know, knowledge, understand, realize, recognize |
| WANT | want, desire, wish, yearn, need, strive, seek |
| SEE | see, observe, perceive, notice, witness |
| DO | do, act, perform, execute, create, make, run, build |
| HAPPEN | happen, occur, arise, emerge, become, unfold |
| SAY | say, speak, express, communicate, define, describe |
| GOOD | good, correct, valid, safe, efficient, clean, fast |
| BAD | bad, wrong, broken, unsafe, slow, buggy, error |
| EXIST | exist, be, being, presence, there is, instance |
| SELF | self, own, itself, internal, its |
| OTHER | other, external, third-party, caller, user, client |
| BECAUSE | because, reason, cause, therefore, since, thus |
| IF | if, when, unless, condition, conditional, guard |
| CAN | can, could, able, possible, capable, allows, supports |
| MAYBE | maybe, perhaps, might, uncertain, optional, todo |
| AFTER | after, then, next, later, subsequently, following |
| BEFORE | before, prior, earlier, first, initially, previously |
| NOT | not, no, never, without, lack, missing, absent |

### Qualia — 8 phenomenal dimensions
| Dimension | Method | Range |
|-----------|--------|-------|
| valence | (pos_hits − neg_hits + 4) / 8 | 0–1 (0.5 = neutral) |
| arousal | scalar keyword count × 0.18 | 0–1 |
| intimacy | scalar keyword count × 0.18 | 0–1 |
| certainty | (high_hits − low_hits + 3) / 6 | 0–1 |
| agency | (active_hits − passive_hits + 3) / 6 | 0–1 |
| emergence | scalar keyword count × 0.18 | 0–1 |
| continuity | scalar keyword count × 0.18 | 0–1 |
| abstraction | scalar keyword count × 0.18 | 0–1 |

### Causality — 5 flow indicators
`past`, `present`, `future` (fraction of temporal markers), `temporality`
(future − past normalised, negative = looking back), `agency` (mirrors qualia).

### dominant_mode
Winning score among: emotional (FEEL + intimacy), cognitive (THINK + KNOW),
existential (EXIST + SELF), emergent (emergence + HAPPEN), relational
(OTHER + BECAUSE), technical (DO + CAN).

---

## The 144-verb taxonomy

Six categories × 24 verbs = 144 total. Every `relates` edge uses exactly one.
LLM output is fuzzy-matched then normalised; unknown verbs fall back to `RELATED_TO`.

### Structural (ontology + logic)
`IS_A`, `HAS_A`, `PART_OF`, `CONTAINS`, `INSTANCE_OF`, `SUBCLASS_OF`,
`RELATED_TO`, `ADJACENT_TO`, `LOCATED_IN`, `CONNECTED_TO`, `DERIVED_FROM`,
`COMPOSED_OF`, `DEPENDS_ON`, `IMPLIES`, `CONTRADICTS`, `SUPPORTS`,
`EXEMPLIFIES`, `DEFINES`, `CLASSIFIES`, `DESCRIBES`, `ATTRIBUTES`,
`MEASURES`, `COUNTS`, `BOUNDS`

### Causal (mechanism + force)
`CAUSES`, `ENABLES`, `PREVENTS`, `TRIGGERS`, `BLOCKS`, `AMPLIFIES`,
`REDUCES`, `TRANSFORMS`, `PRODUCES`, `REQUIRES`, `ALLOWS`, `INHIBITS`,
`ACCELERATES`, `DELAYS`, `INITIATES`, `TERMINATES`, `MAINTAINS`,
`DISRUPTS`, `REGULATES`, `MEDIATES`, `MODULATES`, `FACILITATES`,
`SUPPRESSES`, `INDUCES`

### Temporal (Allen interval algebra)
`BEFORE`, `AFTER`, `DURING`, `MEETS`, `OVERLAPS`, `STARTS`, `FINISHES`,
`EQUALS_TIME`, `PRECEDES`, `FOLLOWS`, `SIMULTANEOUS`, `CONTINUOUS`,
`PERIODIC`, `CYCLICAL`, `SEQUENTIAL`, `CONCURRENT`, `IMMEDIATE`,
`EVENTUAL`, `GRADUAL`, `SUDDEN`, `PERSISTENT`, `TRANSIENT`,
`RECURRING`, `DEPRECATED`

### Epistemic (belief + knowledge)
`KNOWS`, `BELIEVES`, `INFERS`, `EXPECTS`, `ASSUMES`, `HYPOTHESIZES`,
`DOUBTS`, `CONFIRMS`, `DENIES`, `QUESTIONS`, `UNDERSTANDS`, `REMEMBERS`,
`PREDICTS`, `LEARNS`, `DISCOVERS`, `REALIZES`, `PERCEIVES`, `RECOGNIZES`,
`INTERPRETS`, `EVALUATES`, `ANALYZES`, `SYNTHESIZES`, `CONCLUDES`,
`JUSTIFIES`

### Agentive (intention + action)
`DOES`, `WANTS`, `DECIDES`, `TRIES`, `ACHIEVES`, `FAILS`, `PLANS`,
`EXECUTES`, `MONITORS`, `ADAPTS`, `CREATES`, `DESTROYS`, `MODIFIES`,
`ACQUIRES`, `RELEASES`, `COMMUNICATES`, `COORDINATES`, `DELEGATES`,
`CONTROLS`, `OBSERVES`, `INTERVENES`, `RESPONDS`, `INITIATES_ACTION`,
`TERMINATES_ACTION`

### Experiential (felt + qualitative)
`FEELS`, `SEES`, `ENJOYS`, `FEARS`, `EXPERIENCES`, `SUFFERS`,
`DESIRES`, `APPRECIATES`, `DISLIKES`, `WONDERS`, `IMAGINES`, `DREAMS`,
`HOPES`, `REGRETS`, `CELEBRATES`, `MOURNS`, `REFLECTS`, `CONTEMPLATES`,
`RESONATES`, `YEARNS`, `EMBRACES`, `REJECTS`, `SEEKS`, `AVOIDS`

---

## NARS truth values

Every concept and relation carries a Non-Axiomatic Reasoning System epistemic
state: `(frequency, confidence, evidence_count)`.

**Revision formula** — when the same fact is observed again:
```python
w1 = c1 / (1 − c1) × n1        # prior weight
w2 = c2 / (1 − c2) × n2        # new weight
freq_new = (w1×f1 + w2×f2) / (w1 + w2)
conf_new = (w1 + w2) / (w1 + w2 + 1.0)
n_new    = n1 + n2
```

**Confidence assignment by LLM:**
- Direct statement in text → 0.8–0.95
- Clearly implied → 0.4–0.7
- Speculative / hedged → 0.1–0.4

---

## Rung levels (R0–R9)

Abstraction depth assigned by the LLM per concept.

| Rung | Name | Example |
|------|------|---------|
| R0 | Surface literal | "Redis", "port 8080", "cargo.toml" |
| R1 | Shallow inference | "HTTP server", "build flag", "cache layer" |
| R2 | Contextual | "storage backend", "feature flag system" |
| R3 | Analogical | "SpineCache is like a blackboard" |
| R4 | Abstract pattern | "zero-copy architecture", "lock-free design" |
| R5 | Structural schema | "content-addressable memory model" |
| R6 | Counterfactual | "if Lance API were fixed, latency would halve" |
| R7 | Meta | "reasoning about the reasoning system" |
| R8 | Recursive | "the system observing its own observation" |
| R9 | Transcendent | "consciousness substrate", "ground of being" |

---

## CLI usage

```bash
# Apply schema once
surreal import --conn ws://localhost:8000 \
               --user root --pass root \
               --ns knowledge --db main \
               schema.surql

# Single file
python graph_extract.py --input architecture.pdf --db ws://localhost:8000 -v

# Stdin pipe
cat README.md | python graph_extract.py --stdin --mime text/markdown \
    --db ws://localhost:8000 --ns myproject --database docs

# Whole directory
python graph_extract.py --dir ./docs/ --batch-size 6 -v

# Dry run (parse only, no SurrealDB write)
python graph_extract.py --input spec.md --dry-run -v
```

Full CLI flags: `--input FILE`, `--stdin`, `--dir PATH`, `--db URL`,
`--ns NAMESPACE`, `--database NAME`, `--user`, `--pass`, `--mime TYPE`,
`--title NAME`, `--batch-size N`, `--skip-schema`, `--dry-run`, `-v`.

---

## Python API

```python
import asyncio
from graph_extract import GraphExtractor

async def main():
    async with await GraphExtractor.connect(
        url="ws://localhost:8000",
        namespace="knowledge",
        database="main",
    ) as gx:
        await gx.ensure_schema()

        # Ingest a file
        doc_id = await gx.ingest("paper.pdf", verbose=True)

        # Ingest raw bytes (e.g. from a web download)
        raw = open("report.pdf", "rb").read()
        doc_id = await gx.ingest(raw, mime_type="application/pdf",
                                  title="Q3 Report", batch_size=6)

        # Query helpers
        concepts = await gx.concepts_for_doc(doc_id)
        subgraph  = await gx.subgraph("BindSpace")

asyncio.run(main())
```

---

## SurrealDB query patterns

```sql
-- All causal neighbours of a concept
SELECT ->relates[WHERE verb_category = 'Causal']->(concept)
FROM concept WHERE name = 'Redis';

-- 3-hop traversal
SELECT ->relates->(concept)->relates->(concept)->relates->concept
FROM concept WHERE name = 'fingerprint';

-- High-confidence structural relations
SELECT * FROM relates
WHERE verb_category = 'Structural' AND nars_confidence > 0.7;

-- Abstract concepts only (R4+), ranked by confidence
SELECT name, type, rung, description, nars_confidence FROM concept
WHERE rung >= 4 ORDER BY nars_confidence DESC LIMIT 20;

-- Disputed claims: often false but confidently said
SELECT * FROM concept
WHERE nars_frequency < 0.5 AND nars_confidence > 0.7;

-- Full document subgraph (concepts + provenance)
SELECT *, ->contains->(chunk)->mentions->(concept)
FROM document WHERE title = 'README.md';

-- Time-bounded facts (contracts, policies)
SELECT * FROM relates
WHERE valid_until != NONE ORDER BY valid_until ASC;

-- Concepts first seen in a specific document
SELECT * FROM concept WHERE first_seen_in = document:abc123;

-- All contradictions with strong evidence
SELECT *, in.name AS subject, out.name AS object FROM relates
WHERE verb = 'CONTRADICTS' AND nars_confidence > 0.6;

-- Emotionally loaded chunks (high arousal + negative valence)
SELECT text, dominant_mode, qualia FROM chunk
WHERE qualia.arousal > 0.5 AND qualia.valence < 0.35;
```

---

## Use cases

### 1 · Codebase understanding
Ingest READMEs, architecture docs, comments. Query what `SpineCache` causes,
what `BindSpace` depends on, which modules `CONTRADICTS` each other.
Navigate the dependency graph without reading every file.

```sql
SELECT ->relates[WHERE verb = 'DEPENDS_ON']->(concept) FROM concept WHERE name = 'SpineCache';
```

### 2 · Research synthesis across many papers
Feed 50+ papers. Concepts repeated across documents accumulate high
`nars_confidence` via revision. `CONTRADICTS` edges with low `nars_frequency`
surface disputed claims. Find scientific consensus vs. active controversy
at a glance.

```sql
SELECT *, in.name, out.name FROM relates
WHERE verb = 'CONTRADICTS' AND nars_confidence > 0.6;
```

### 3 · Contract and legal document analysis
Extract obligation chains (`REQUIRES`, `ENABLES`, `PREVENTS`), parties
(`person` nodes), and clauses with deadlines (`valid_from / valid_until`).
Spot missing obligations, circular dependencies, or expired terms.

```sql
SELECT * FROM relates
WHERE verb_category = 'Causal' AND valid_until != NONE ORDER BY valid_until;
```

### 4 · Incident post-mortem
Paste runbooks, log summaries, the post-mortem doc. The graph surfaces causal
chains (`TRIGGERS`, `CAUSES`, `AMPLIFIES`) from root cause to symptom. Rung
level distinguishes literal findings (R0–R1) from abstracted patterns (R4+).

### 5 · Knowledge base Q&A substrate
Extract all internal documentation. Any RAG system can traverse `->relates->`
edges for multi-hop reasoning instead of flat vector search. Every answer
carries provenance (exact chunk + confidence score).

### 6 · Competitive intelligence
Ingest earnings calls, blog posts, job postings over time. Track how concepts
(`pricing`, `product`, `strategy`) relate across quarters. `DEPRECATED`
temporal edges signal pivots. Low-confidence nodes flag rumours.

### 7 · Personal research notebook
Ingest everything you read for months. High-rung concepts (R5+) cluster into
latent themes. Low-confidence nodes reveal gaps. Grammar Triangle
`dominant_mode` separates technical reading from emotional/reflective writing —
useful for distinguishing objective sources from opinion pieces.

### 8 · Multi-document cross-reference
Ingest a specification and its implementation docs separately. `CONTRADICTS`
edges between them reveal spec drift. `SUPPORTS` edges confirm alignment.
Query which spec claims have the most implementation evidence.

```sql
SELECT *, in.name, out.name, evidence FROM relates
WHERE verb = 'CONTRADICTS'
  AND source_doc IN [document:spec_hash, document:impl_hash];
```

---

## Deduplication and evolvability

**Concept deduplication:** stable ID from `sha256(name.lower() + "_" + type)[:16]`.
`UPSERT MERGE` preserves all fields; NARS revision formula merges epistemic
state when the same concept appears in multiple documents.

**Relation deduplication:** stable ID from `sha256(subj_id + "_" + verb + "_" + obj_id)[:16]`.
Same UPSERT + NARS revision on repeated observation.

**Schema evolvability rules:**
1. Never `DROP` fields — only add new ones
2. All new fields use `DEFINE FIELD IF NOT EXISTS`
3. New semantic types = new verb string, no schema change
4. Grammar Triangle dimensions are additive; old chunks keep old keys
5. New concept types just use a new `type` string value

---

## Kreuzberg integration notes

`kreuzberg.extract_bytes_sync(raw_bytes, mime_type=...)` returns:
- `.content` — clean unicode text (OCR applied to images automatically)
- `.metadata` — dict with `title`, `language`, `quality_score`, `page_count`,
  `author`, `creation_date`, and format-specific extras
- `.tables` — list of extracted table structures (for DOCX, HTML, PDF)
- `.mime_type` — detected or confirmed MIME type

Supported input formats: PDF (pdfium + Tesseract OCR), DOCX, PPTX, XLSX,
HTML, Markdown, plain text, RTF, ODT, images (JPEG, PNG, TIFF, WebP via OCR).

The `quality_score` field (0–1) from Kreuzberg is stored on `document.quality`
and can be used to filter low-quality extractions (e.g. scanned PDFs with
poor OCR). Recommend discarding chunks from documents with `quality < 0.3`.

---

## LLM prompt design (llm_parser.py)

The system prompt sent to `claude-sonnet-4-20250514` includes:
- Concept type taxonomy (11 types)
- Rung level definitions (R0–R9)
- Full 144-verb list grouped by category
- NARS confidence assignment guidelines
- Strict JSON output schema (no fences, no preamble)

Output schema per call:
```json
{
  "concepts": [
    { "name": "…", "type": "…", "description": "…", "rung": 0,
      "aliases": [], "tags": [], "qualia": {}, "nars_frequency": 1.0,
      "nars_confidence": 0.9 }
  ],
  "relations": [
    { "subject": "…", "verb": "CAUSES", "object": "…",
      "evidence": "≤50 char quote", "nars_frequency": 1.0,
      "nars_confidence": 0.8, "valid_from": null, "valid_until": null }
  ]
}
```

Batch size defaults to 4 chunks per call. Increase to 6–8 for dense technical
docs; decrease to 2 for very long code blocks.
