# XTRACT - Document to Knowledge Graph
## Specification v1.0

---

## Overview

Transform documents into a traversable knowledge graph stored in SurrealDB. Pipeline: Text → Grammar Triangle → Fingerprint → SPO Crystal → Graph.

---

## Architecture

### 1. Input Processing
- **Source**: Any text file (.md, .txt, .py, .js, .yaml)
- **Chunking**: Split on paragraph boundaries, max 800 chars per chunk

### 2. Grammar Triangle

Three semantic vectors per chunk:

**NSM Primitives (20)**
```
FEEL, THINK, KNOW, WANT, SEE, DO, HAPPEN, SAY
GOOD, BAD, EXIST, SELF, OTHER, BECAUSE, IF, CAN, MAYBE, AFTER, BEFORE, NOT
```
- Score: keyword_hits × 0.12, clamped 0-1

**Qualia Dimensions (8)**
```
valence, arousal, intimacy, certainty, agency, emergence, continuity, abstraction
```
- Score: keyword_hits × 0.18, clamped 0-1

**Causality**
```
past: was, before, previous, earlier, ago
present: is, now, current, present, today  
future: will, shall, future, next, later, soon
```
- Normalized distribution + agency default 0.5

### 3. 144-Verb Taxonomy

| Category | Count | Examples |
|----------|-------|----------|
| Structural | 24 | IS_A, HAS_A, CONTAINS, PART_OF |
| Causal | 24 | CAUSES, ENABLES, REQUIRES, TRANSFORMS |
| Temporal | 24 | BEFORE, AFTER, DURING, OVERLAPS |
| Epistemic | 24 | KNOWS, BELIEVES, INFERS, PREDICTS |
| Agentive | 24 | DOES, WANTS, DECIDES, CREATES |
| Experiential | 24 | FEELS, ENJOYS, IMAGINES, YEARNS |

### 4. NARS Truth Values

```python
# Prior weight
w1 = c1/(1-c1) * n1
# New weight  
w2 = c2/(1-c2) * n2

# Revision
freq_new = (w1*f1 + w2*f2) / (w1 + w2)
conf_new = (w1 + w2) / (w1 + w2 + 1.0)
```

---

## Implementation

### Database Schema

```sql
DEFINE TABLE document SCHEMALESS;
DEFINE TABLE concept SCHEMALESS;
DEFINE TABLE relates TYPE RELATION SCHEMALESS;
```

### Concept Record
```json
{
  "name": "string",
  "type": "entity|system|process|idea|event",
  "fingerprint": "hash(NSM+Qualia+Causality)",
  "nars_frequency": 0.0-1.0,
  "nars_confidence": 0.0-1.0,
  "evidence_count": integer
}
```

### Relation Record
```json
{
  "in": "concept_id (subject)",
  "out": "concept_id (object)", 
  "verb": "IS_A|HAS_A|DEPENDS_ON|...",
  "category": "Structural|Causal|Temporal|...",
  "nars_frequency": 0.0-1.0,
  "nars_confidence": 0.0-1.0
}
```

---

## SurrealDB Configuration

| Setting | Value |
|---------|-------|
| URL | ws://127.0.0.1:8000 |
| Namespace | xtract_graph |
| Database | main |
| User | root |
| Pass | (configured) |

---

## Files

| File | Purpose |
|------|---------|
| `skills/xtract/SKILL.md` | Skill documentation |
| `skills/xtract/xtract.py` | Main extraction script |
| `skills/xtract/viewer.html` | 2D Canvas viewer (live) |
| `artifacts/xtract-v2-embedded.html` | 3D-force-graph with embedded data |

---

## CLI Usage

```bash
# Extract from directory
python skills/xtract/xtract.py --dir ./docs/

# Extract single file
python skills/xtract/xtract.py --input file.md

# Clear and re-extract
python skills/xtract/xtract.py --clear --dir ./docs/
```

---

## Current Results

| Metric | Count |
|--------|-------|
| Documents processed | 94 |
| Concepts extracted | 4,494 |
| Relations extracted | 0 |

**Note**: Relations are 0 because source documents lack explicit relational language. Add documents with sentences like "X uses Y" or "A depends on B" to generate edges.

---

## Viewer Comparison

| Viewer | Type | Data Source | Pros | Cons |
|--------|------|-------------|------|------|
| `viewer.html` | 2D Canvas | Live SurrealDB | Real-time updates | Limited visualization |
| `xtract-v2-embedded.html` | 3D WebGL | Embedded JSON | Rich 3D, no DB needed | Static, larger file |

Both use:
- Hover for node details
- Click disabled
- Optimized for 4000+ nodes

---

## Reproduction Checklist

1. [ ] Connect to SurrealDB at ws://127.0.0.1:8000
2. [ ] Create namespace: `xtract_graph`
3. [ ] Run: `python xtract.py --clear --dir ~/.openclaw/workspace-genesis`
4. [ ] Verify: 4,000+ concepts in database
5. [ ] Open `artifacts/xtract-v2-embedded.html` in browser

---

## External Dependencies

- **3D Rendering**: https://unpkg.com/3d-force-graph (UMD)
- **Three.js**: https://unpkg.com/three (auto-loaded by 3d-force-graph)
- **SurrealDB SDK**: https://cdn.jsdelivr.net/npm/surrealdb@1.0.8/+esm

No build step required. All self-contained HTML files work offline after initial CDN load.
