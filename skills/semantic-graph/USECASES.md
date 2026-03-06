# Graph Extraction Skill — Usage Scenarios

## What it does

Takes any document (PDF, DOCX, HTML, Markdown, code, images) and builds a **live semantic knowledge graph** in SurrealDB: named concepts as nodes, directed meaning-typed edges between them, every claim carrying NARS epistemic weight (frequency × confidence).

---

## Quick start

```bash
# Single file
python graph_extract.py --input architecture.pdf --db ws://localhost:8000 -v

# Pipe markdown
cat README.md | python graph_extract.py --stdin --mime text/markdown

# Whole directory
python graph_extract.py --dir ./docs/ --batch-size 6 -v

# Python API
async with GraphExtractor.connect("ws://localhost:8000") as gx:
    doc_id = await gx.ingest("spec.pdf")
```

---

## Use cases

### 1 · Codebase understanding
Ingest all READMEs, architecture docs, and source comments. Query: *what does `SpineCache` cause? what does `BindSpace` depend on?* Navigate the dependency graph without reading every file.

```sql
SELECT ->relates[WHERE verb = 'DEPENDS_ON']->(concept) FROM concept:SpineCache;
```

### 2 · Research synthesis
Feed 50 papers on a topic. Concepts that appear across many documents get high `nars_confidence` via the revision formula. Contradictions surface as `CONTRADICTS` edges with low frequency scores. Find consensus vs. disputed claims at a glance.

```sql
SELECT * FROM relates WHERE verb = 'CONTRADICTS' AND nars_confidence > 0.6;
```

### 3 · Contract / legal document analysis
Ingest contracts and policies. Extract obligation chains (`REQUIRES`, `ENABLES`, `PREVENTS`), parties (`person` nodes), and time-bounded clauses (`valid_from / valid_until`). Spot missing obligations or circular dependencies.

```sql
SELECT * FROM relates WHERE verb_category = 'Causal' AND valid_until != NONE;
```

### 4 · Incident post-mortem
Paste runbooks, logs summaries, and the post-mortem doc. The graph shows causal chains (`TRIGGERS`, `CAUSES`, `AMPLIFIES`) from root causes to symptoms, with rung level indicating whether a finding is literal (R0) or an abstracted pattern (R4+).

### 5 · Knowledge base Q&A substrate
Extract all internal docs into one graph. Any retrieval system can traverse `->relates->` edges instead of doing flat vector search — answers carry provenance (exact chunk + confidence) and multi-hop reasoning paths.

### 6 · Competitive intelligence
Ingest earnings calls, blog posts, job postings. Track how concepts (`product`, `strategy`, `pricing`) relate over time using `valid_from` edges. Watch for `DEPRECATED` temporal edges signalling pivots.

### 7 · Personal research notebook
Ingest everything you read over months. High-rung concepts (R5+, abstracted ideas) cluster into latent themes. Low-confidence nodes flag gaps in your understanding. The Grammar Triangle `dominant_mode` field separates technical reading from emotional/reflective writing.

---

## Output anatomy

Every ingested document produces:

| Layer | What's stored | Key fields |
|---|---|---|
| `document` | Source file metadata | title, mime_type, word_count, quality |
| `chunk` | Text segments | Grammar Triangle (NSM, qualia, causality, dominant_mode) |
| `concept` | Named nodes | type, rung R0–R9, nars_frequency, nars_confidence |
| `relates` | Typed edges | verb (1 of 144), verb_category, evidence quote, NARS truth |

---

## Querying the graph

```sql
-- 3-hop causal chain from a concept
SELECT ->relates[WHERE verb_category='Causal']->(concept)
       ->relates->(concept)->relates->concept
FROM concept:redis;

-- All high-confidence abstract ideas (R4+)
SELECT name, description, rung, nars_confidence FROM concept
WHERE rung >= 4 ORDER BY nars_confidence DESC LIMIT 20;

-- What concepts are most argued-about (low freq, high confidence)
SELECT * FROM concept WHERE nars_frequency < 0.5 AND nars_confidence > 0.7;

-- Full subgraph for a document
SELECT *, ->contains->(chunk)->mentions->(concept)
FROM document:abc123;
```
