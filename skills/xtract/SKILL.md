# SKILL: XTRACT - Document to Graph

## Purpose
Transform documents to knowledge graph in SurrealDB.

## Method
Text -> Grammar Triangle -> Fingerprint -> SPO Crystal -> Graph

## Use
- "extract graph from doc"
- "parse document to db"
- "ingest to graph"

## Input
File path or directory.

## Output
SurrealDB populated with concepts and relations.

## Algorithm

### 1. Grammar Triangle
Each chunk gets three vectors:

- NSM: 20 primitives (FEEL, THINK, WANT, KNOW, SEE, DO, HAPPEN, GOOD, BAD, EXIST, SELF, OTHER, BECAUSE, IF, CAN, MAYBE, AFTER, BEFORE, NOT, SAY)
- Qualia: 8 dims (valence, arousal, intimacy, certainty, agency, emergence, continuity, abstraction)
- Causality: past/present/future balance + agency

Score = keyword_hits * 0.12, clamped 0-1.

### 2. SPO Crystal
125-cell spatial grid:
- S (Subject): X axis
- P (Predicate): Y axis  
- O (Object): Z axis
- Q (Qualia): color

### 3. Resonance
Fingerprint = hash(NSM + Qualia + Causality)
Similarity = cosine_similarity(fingerprints)
Threshold = 0.7 for relation.

### 4. 144 Verbs
Categories:
- Structural (24): IS_A, HAS_A, PART_OF, CONTAINS, INSTANCE_OF, SUBCLASS_OF, RELATED_TO, ADJACENT_TO, LOCATED_IN, CONNECTED_TO, DERIVED_FROM, COMPOSED_OF, DEPENDS_ON, IMPLIES, CONTRADICTS, SUPPORTS, EXEMPLIFIES, DEFINES, CLASSIFIES, DESCRIBES, ATTRIBUTES, MEASURES, COUNTS, BOUNDS
- Causal (24): CAUSES, ENABLES, PREVENTS, TRIGGERS, BLOCKS, AMPLIFIES, REDUCES, TRANSFORMS, PRODUCES, REQUIRES, ALLOWS, INHIBITS, ACCELERATES, DELAYS, INITIATES, TERMINATES, MAINTAINS, DISRUPTS, REGULATES, MEDIATES, MODULATES, FACILITATES, SUPPRESSES, INDUCES
- Temporal (24): BEFORE, AFTER, DURING, MEETS, OVERLAPS, STARTS, FINISHES, EQUALS_TIME, PRECEDES, FOLLOWS, SIMULTANEOUS, CONTINUOUS, PERIODIC, CYCLICAL, SEQUENTIAL, CONCURRENT, IMMEDIATE, EVENTUAL, GRADUAL, SUDDEN, PERSISTENT, TRANSIENT, RECURRING, DEPRECATED
- Epistemic (24): KNOWS, BELIEVES, INFERS, EXPECTS, ASSUMES, HYPOTHESIZES, DOUBTS, CONFIRMS, DENIES, QUESTIONS, UNDERSTANDS, REMEMBERS, PREDICTS, LEARNS, DISCOVERS, REALIZES, PERCEIVES, RECOGNIZES, INTERPRETS, EVALUATES, ANALYZES, SYNTHESIZES, CONCLUDES, JUSTIFIES
- Agentive (24): DOES, WANTS, DECIDES, TRIES, ACHIEVES, FAILS, PLANS, EXECUTES, MONITORS, ADAPTS, CREATES, DESTROYS, MODIFIES, ACQUIRES, RELEASES, COMMUNICATES, COORDINATES, DELEGATES, CONTROLS, OBSERVES, INTERVENES, RESPONDS, INITIATES_ACTION, TERMINATES_ACTION
- Experiential (24): FEELS, SEES, ENJOYS, FEARS, EXPERIENCES, SUFFERS, DESIRES, APPRECIATES, DISLIKES, WONDERS, IMAGINES, DREAMS, HOPES, REGRETS, CELEBRATES, MOURNS, REFLECTS, CONTEMPLATES, RESONATES, YEARNS, EMBRACES, REJECTS, SEEKS, AVOIDS

### 5. NARS Truth Values
- frequency: 0-1 (how consistent)
- confidence: 0-1 (evidence strength)
- evidence_count: observations

Revision:
w1 = c1/(1-c1) * n1
w2 = c2/(1-c2) * n2
freq_new = (w1*f1 + w2*f2) / (w1+w2)
conf_new = (w1+w2) / (w1+w2+1)

## Schema
```
DEFINE TABLE document SCHEMALESS;
DEFINE TABLE concept SCHEMALESS;
DEFINE TABLE relates TYPE RELATION SCHEMALESS;
```

## Files
- `xtract.py`: Main parser
- `grammar.py`: Triangle math
- `viewer.html`: 2D graph view

## CLI
```bash
python xtract.py --input file.md
python xtract.py --dir ./docs/
python xtract.py --clear  # reset db
```

## Viewer
HTML file connects to SurrealDB via CDN SDK. Shows nodes as text, edges as lines. Hover for details. No 3D. High FPS on 5000+ nodes via Canvas 2D.
