# Information Processing Pipeline

**Purpose:** Ingest documents → Extract entities/relations → Capture semantic meaning → Populate SurrealDB

**Tools:**
- Kreuzberg (document parsing)
- html-to-markdown (HTML conversion)
- langextract-rs (entity/relation extraction)
- ladybug-rs (cognitive fingerprints)
- SurrealDB (storage)

---

## Pipeline Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                         RAW INPUTS                                    │
│   PDF • HTML • DOCX • Images • Markdown • JSON                     │
└──────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    STAGE 1: DOCUMENT PARSING                        │
│  ┌──────────────┐  ┌─────────────────────┐  ┌────────────────────┐   │
│  │   Kreuzberg  │  │  html-to-markdown  │  │  Kreuzberg OCR    │   │
│  │  (PDF/Docx) │  │    (HTML → MD)     │  │  (Image → Text)  │   │
│  └──────────────┘  └─────────────────────┘  └────────────────────┘   │
│                                                                       │
│  Output: Raw text + tables + images + metadata                      │
└──────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    STAGE 2: TEXT PROCESSING                         │
│  ┌──────────────┐  ┌─────────────────────┐  ┌────────────────────┐ │
│  │  Chunking    │  │  Language Detect   │  │  Summary (LLM)  │ │
│  │  (semantic)  │  │  (fasttext/langid) │  │  (optional)      │ │
│  └──────────────┘  └─────────────────────┘  └────────────────────┘ │
│                                                                       │
│  Output: Clean text chunks + metadata                                 │
└──────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    STAGE 3: EXTRACTION                               │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │                    langextract-rs                               │  │
│  │  • Entity recognition (person, project, concept, resource)  │  │
│  │  • Relation extraction (works_on, member_of, knows)          │  │
│  │  • Source grounding (character positions)                       │  │
│  │  • Schema validation                                            │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                                                                       │
│  Output: Raw entities + relations + confidence scores                 │
└──────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    STAGE 4: SEMANTIC FINGERPRINTING                 │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │                    ladybug-rs                                    │  │
│  │  • Generate 10K-bit fingerprints for each entity              │  │
│  │  • Map relations to 144 verbs (IS_A, CAUSES, etc.)            │  │
│  │  • Compute similarity via Hamming distance                      │  │
│  │  • Store in LanceDB (vector index)                             │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                                                                       │
│  Output: Fingerprints + similarity indices                            │
└──────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    STAGE 5: KNOWLEDGE GRAPH                        │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │                      SurrealDB                                  │  │
│  │  • Store entities (with fingerprints)                         │  │
│  │  • Store relations (graph edges)                              │  │
│  │  • HNSW vector index for semantic search                    │  │
│  │  • LIVE SELECT for real-time updates                           │  │
│  │  • Row-level permissions                                        │  │
│  └────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Schema Design (SurrealDB)

```sql
-- Namespaces
DEFINE NAMESPACE regen;

-- Database
DEFINE DATABASE regen_knowledge;

-- Entity table
DEFINE TABLE entity SCHEMAFULL;
DEFINE FIELD id ON entity TYPE string;
DEFINE FIELD name ON entity TYPE string;
DEFINE FIELD type ON entity TYPE enum<'person', 'project', 'concept', 'resource', 'location', 'event'>;
DEFINE FIELD description ON entity TYPE string;
DEFINE FIELD fingerprint ON entity TYPE array<uint>(1250);  -- 10K bits as bytes
DEFINE FIELD source ON entity TYPE string;
DEFINE FIELD source_id ON entity TYPE string;
DEFINE FIELD created_at ON entity TYPE datetime DEFAULT time::now();

-- Relation table (graph edge)
DEFINE TABLE relation SCHEMAFULL TYPE relation;
DEFINE FIELD in ON relation TYPE entity;
DEFINE FIELD out ON relation TYPE entity;
DEFINE FIELD type ON relation TYPE enum<'member_of', 'works_on', 'knows', 'depends_on', 'provides', 'requires', 'discusses', 'authored', 'derived_from', 'similar_to'>;
DEFINE FIELD weight ON relation TYPE float DEFAULT 1.0;
DEFINE FIELD confidence ON relation TYPE float;
DEFINE FIELD source ON relation TYPE string;

-- Indexes
DEFINE INDEX entity_name ON entity FIELDS name SEARCH ANALYZER ascii BM25;
DEFINE INDEX entity_type ON entity FIELDS type;
DEFINE INDEX entity_fingerprint ON entity FIELDS fingerprint HNSW;
```

---

## Implementation

### Stage 1: Document Parsing

```rust
use kreuzberg::{extract_file_sync, ExtractConfig};

pub fn process_document(path: &str) -> Result<ParsedDocument, Error> {
    let config = ExtractConfig::default();
    let result = extract_file_sync(path, config)?;
    
    Ok(ParsedDocument {
        text: result.content,
        tables: result.tables,
        images: result.images,
        metadata: result.metadata,
    })
}
```

### Stage 3: Entity/Relation Extraction

```rust
use langextract_rust::{extract, ExtractConfig, ExampleData, Extraction};

pub async fn extract_entities(text: &str) -> Result<ExtractionResult, Error> {
    let examples = vec![
        ExampleData::new(
            "Alice is leading the solar garden project".to_string(),
            vec![
                Extraction::new("person".to_string(), "Alice".to_string()),
                Extraction::new("project".to_string(), "solar garden".to_string()),
            ],
        )
    ];
    
    let config = ExtractConfig {
        model_id: "qwen3:30b".to_string(),
        model_url: Some("http://localhost:11434".to_string()),
        temperature: 0.3,
        ..Default::default()
    };
    
    extract(text, Some("Extract persons, projects, concepts"), &examples, config).await
}
```

### Stage 4: Semantic Fingerprinting

```rust
use ladybug::core::Fingerprint;

pub fn generate_fingerprint(name: &str, entity_type: &str) -> Vec<u8> {
    let input = format!("{}:{}", entity_type, name);
    let fp = Fingerprint::from_content(&input);
    fp.as_bytes().to_vec()
}
```

### Stage 5: Database Storage

```rust
use surrealdb::Surreal;
use surrealdb::engine::local::RocksDb;

pub async fn store_entity(db: &Surreal<Db>, entity: Entity) -> Result<(), Error> {
    db.create(("entity", &entity.id)).content(entity).await?;
    Ok(())
}
```

---

## Example Queries

```sql
-- Find all projects a person works on
SELECT ->relation->entity as projects 
FROM entity 
WHERE name = 'Alice' AND type = 'person';

-- Semantic search
SELECT * FROM entity 
WHERE vector::similarity::cosine(fingerprint, $query_fp) > 0.8
LIMIT 10;
```

---

## Configuration

```yaml
pipeline:
  extraction:
    model: "qwen3:30b"
    url: "http://localhost:11434"
  storage:
    path: "./data/knowledge.db"
```

---

*See: github.com/regentribes/regen-knowledge-graph*
