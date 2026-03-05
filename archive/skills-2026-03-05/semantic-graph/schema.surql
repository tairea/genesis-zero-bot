-- ============================================================================
-- SurrealDB Schema: Semantic Knowledge Graph
-- Version: 1.0  (evolvable — add fields, never remove)
-- ============================================================================
-- Apply with: surreal import --conn ws://localhost:8000 \
--                             --user root --pass root \
--                             --ns myproject --db knowledge \
--                             schema.surql
-- ============================================================================

-- ── NAMESPACING ──────────────────────────────────────────────────────────────
DEFINE NAMESPACE IF NOT EXISTS myproject;
USE NS myproject;
DEFINE DATABASE IF NOT EXISTS knowledge;
USE DB knowledge;

-- ── DOCUMENT ─────────────────────────────────────────────────────────────────
-- Represents a source document in any format.

DEFINE TABLE document SCHEMALESS
    COMMENT "Source document: PDF, Markdown, DOCX, HTML, plain text, etc.";

DEFINE FIELD IF NOT EXISTS source      ON document TYPE string  COMMENT "File path or URL or 'inline'";
DEFINE FIELD IF NOT EXISTS mime_type   ON document TYPE string  COMMENT "e.g. text/markdown, application/pdf";
DEFINE FIELD IF NOT EXISTS title       ON document TYPE option<string>;
DEFINE FIELD IF NOT EXISTS created_at  ON document TYPE datetime DEFAULT time::now();
DEFINE FIELD IF NOT EXISTS word_count  ON document TYPE option<int>;
DEFINE FIELD IF NOT EXISTS language    ON document TYPE option<string>  COMMENT "BCP-47 code, e.g. en";
DEFINE FIELD IF NOT EXISTS metadata    ON document TYPE object   DEFAULT {};
DEFINE FIELD IF NOT EXISTS quality     ON document TYPE option<float>   COMMENT "Kreuzberg quality_score 0-1";

DEFINE INDEX document_source ON document FIELDS source;
DEFINE INDEX document_title  ON document FIELDS title;

-- ── CHUNK ────────────────────────────────────────────────────────────────────
-- A text segment within a document, with its Grammar Triangle analysis.

DEFINE TABLE chunk SCHEMALESS
    COMMENT "Text segment with Grammar Triangle: NSM + Causality + Qualia";

DEFINE FIELD IF NOT EXISTS text        ON chunk TYPE string;
DEFINE FIELD IF NOT EXISTS index       ON chunk TYPE int   COMMENT "Position in document (0-based)";
DEFINE FIELD IF NOT EXISTS char_start  ON chunk TYPE option<int>;
DEFINE FIELD IF NOT EXISTS char_end    ON chunk TYPE option<int>;
DEFINE FIELD IF NOT EXISTS chunk_type  ON chunk TYPE string DEFAULT "paragraph"
    COMMENT "paragraph | heading | code | table | list | quote";

-- Grammar Triangle (no-LLM, pure signal)
DEFINE FIELD IF NOT EXISTS nsm         ON chunk TYPE object   DEFAULT {}
    COMMENT "NSM primitive weights: {FEEL:0.8, THINK:0.3, ...}";
DEFINE FIELD IF NOT EXISTS qualia      ON chunk TYPE object   DEFAULT {}
    COMMENT "18D qualia: {valence:0.7, arousal:0.4, intimacy:0.6, ...}";
DEFINE FIELD IF NOT EXISTS causality   ON chunk TYPE object   DEFAULT {}
    COMMENT "{temporality:0.0, agency:0.5, past:0.3, present:0.5, future:0.2}";
DEFINE FIELD IF NOT EXISTS dominant_mode ON chunk TYPE option<string>
    COMMENT "emotional | cognitive | existential | emergent | relational";

DEFINE INDEX chunk_document ON chunk FIELDS index;

-- ── CONCEPT ──────────────────────────────────────────────────────────────────
-- A named entity, idea, event, or attribute in the knowledge graph.
-- This is the primary NODE type.

DEFINE TABLE concept SCHEMALESS
    COMMENT "Named node in the knowledge graph: entity, idea, event, attribute, process";

DEFINE FIELD IF NOT EXISTS name        ON concept TYPE string  COMMENT "Canonical name, e.g. 'BindSpace'";
DEFINE FIELD IF NOT EXISTS type        ON concept TYPE string
    COMMENT "entity|system|process|idea|attribute|event|person|place|quantity|quality|relation";
DEFINE FIELD IF NOT EXISTS description ON concept TYPE option<string>;
DEFINE FIELD IF NOT EXISTS aliases     ON concept TYPE array<string> DEFAULT [];
DEFINE FIELD IF NOT EXISTS rung        ON concept TYPE int    DEFAULT 0
    COMMENT "Abstraction depth R0 (surface) to R9 (transcendent)";

-- NARS epistemic state
DEFINE FIELD IF NOT EXISTS nars_frequency   ON concept TYPE float DEFAULT 1.0;
DEFINE FIELD IF NOT EXISTS nars_confidence  ON concept TYPE float DEFAULT 0.5;
DEFINE FIELD IF NOT EXISTS evidence_count   ON concept TYPE int   DEFAULT 1
    COMMENT "Number of times observed (feeds NARS revision)";

-- Qualia (felt character of the concept)
DEFINE FIELD IF NOT EXISTS qualia      ON concept TYPE object DEFAULT {}
    COMMENT "Same 18D qualia as chunks";
DEFINE FIELD IF NOT EXISTS dominant_qualia ON concept TYPE option<string>;

-- Source tracking
DEFINE FIELD IF NOT EXISTS first_seen_in ON concept TYPE option<record<document>>;
DEFINE FIELD IF NOT EXISTS created_at    ON concept TYPE datetime DEFAULT time::now();
DEFINE FIELD IF NOT EXISTS updated_at    ON concept TYPE datetime DEFAULT time::now();

-- Flexible extension bag (anything new goes here before promotion)
DEFINE FIELD IF NOT EXISTS tags        ON concept TYPE array<string>  DEFAULT [];
DEFINE FIELD IF NOT EXISTS properties  ON concept TYPE object          DEFAULT {}
    COMMENT "Arbitrary key-value properties from extraction";

DEFINE INDEX concept_name      ON concept FIELDS name;
DEFINE INDEX concept_type      ON concept FIELDS type;
DEFINE INDEX concept_name_type ON concept FIELDS name, type UNIQUE;
DEFINE INDEX concept_rung      ON concept FIELDS rung;

-- ── CONTAINS (document → chunk) ─────────────────────────────────────────────
DEFINE TABLE contains TYPE RELATION SCHEMALESS
    COMMENT "document → contains → chunk";

-- ── MENTIONS (chunk → concept) ────────────────────────────────────────────
DEFINE TABLE mentions TYPE RELATION SCHEMALESS
    COMMENT "chunk → mentions → concept (provenance link)";

DEFINE FIELD IF NOT EXISTS salience   ON mentions TYPE float DEFAULT 0.5
    COMMENT "How central this concept is to this chunk (0-1)";
DEFINE FIELD IF NOT EXISTS span       ON mentions TYPE option<string>
    COMMENT "Exact text span in the chunk that triggered this link";

-- ── RELATES (concept → concept) ─────────────────────────────────────────────
-- This is the primary EDGE type. verb determines the semantic type.
-- SurrealDB lets us RELATE concept:A ->relates-> concept:B with full metadata.

DEFINE TABLE relates TYPE RELATION SCHEMALESS
    COMMENT "concept [verb] concept — the core semantic edge";

-- Verb taxonomy
DEFINE FIELD IF NOT EXISTS verb          ON relates TYPE string
    COMMENT "One of 144 verbs, e.g. CAUSES, IS_A, BEFORE, KNOWS, DOES, FEELS";
DEFINE FIELD IF NOT EXISTS verb_category ON relates TYPE string
    COMMENT "Structural|Causal|Temporal|Epistemic|Agentive|Experiential";

-- Edge weight & epistemics
DEFINE FIELD IF NOT EXISTS weight        ON relates TYPE float DEFAULT 1.0;
DEFINE FIELD IF NOT EXISTS nars_frequency   ON relates TYPE float DEFAULT 1.0;
DEFINE FIELD IF NOT EXISTS nars_confidence  ON relates TYPE float DEFAULT 0.5;
DEFINE FIELD IF NOT EXISTS evidence_count   ON relates TYPE int   DEFAULT 1;

-- Grounding
DEFINE FIELD IF NOT EXISTS evidence      ON relates TYPE option<string>
    COMMENT "Quoted text snippet that supports this relation";
DEFINE FIELD IF NOT EXISTS source_chunk  ON relates TYPE option<record<chunk>>;
DEFINE FIELD IF NOT EXISTS source_doc    ON relates TYPE option<record<document>>;

-- Temporal validity (optional)
DEFINE FIELD IF NOT EXISTS valid_from    ON relates TYPE option<datetime>;
DEFINE FIELD IF NOT EXISTS valid_until   ON relates TYPE option<datetime>;

DEFINE FIELD IF NOT EXISTS created_at    ON relates TYPE datetime DEFAULT time::now();
DEFINE FIELD IF NOT EXISTS updated_at    ON relates TYPE datetime DEFAULT time::now();

DEFINE INDEX relates_verb     ON relates FIELDS verb;
DEFINE INDEX relates_category ON relates FIELDS verb_category;
DEFINE INDEX relates_key      ON relates FIELDS in, verb, out;

-- ── USEFUL COMPUTED VIEWS ────────────────────────────────────────────────────
-- These are just example queries, not actual views (SurrealDB 2.x supports DEFINE VIEW)

-- High-confidence causal edges:
-- SELECT * FROM relates WHERE verb_category = 'Causal' AND nars_confidence > 0.7

-- Deep concepts (R4+):
-- SELECT name, type, rung, description FROM concept WHERE rung >= 4

-- Full concept subgraph (2 hops):
-- SELECT *, ->relates->(concept)->relates->concept FROM concept WHERE name = 'BindSpace'
