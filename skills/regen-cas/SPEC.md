# CAS Skill Specification — Regen Tribe

## Overview

**Purpose**: OpenClaw skill for content-addressable file storage with deduplication

**Core Function**: Accept file → compute hash → store once → return address → reuse on identical input

---

## Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Upload    │───▶│   Hash      │───▶│  Store     │
│   (any)    │    │ (twox-hash) │    │ (OpenDAL)  │
└─────────────┘    └─────────────┘    └─────────────┘
                                           │
       ┌───────────────────────────────────┘
       ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Index     │◀───│   Query     │◀───│   Agent    │
│  (metadata) │    │  (address)  │    │   request  │
└─────────────┘    └─────────────┘    └─────────────┘
```

---

## Dependencies

| Library | Role | Notes |
|---------|------|-------|
| `opendal` | Storage abstraction | FS, S3, GCS, Azure — pick one |
| `twox-hash` | Content addressing | xxh3_128 (fast, 128-bit) |
| `lz4-flex` | Compression | Optional, for large files |
| `sha2` | Integrity | Optional, for verification |

### Redundant / Skip
- ❌ `rustfs` — superseded by opendal's fs backend
- ❌ `IPFS` — overkill for local-first use case
- ❌ `xxhash-rust` — twox-hash is faster

---

## Data Model

```rust
struct CasEntry {
    address: String,        // hex(xxh3_128(content))
    original_name: String,  // preserved for display
    mime_type: String,      // from magic bytes
    size_original: u64,     // bytes before compression
    size_stored: u64,       // bytes after compression
    created_at: i64,        // Unix timestamp
    tags: Vec<String>,      // user-defined
}
```

---

## API Surface

### CLI Commands
```bash
# Store file, get address
cas store /path/to/file.txt

# Retrieve by address
cas get a1b2c3d4...

# List all stored
cas list --format json

# Query by tag
cas find --tag "regen-tribe"

# Check deduplication stats
cas stats
```

### OpenClaw Skill Interface
```
skill: regen-cas
commands:
  - store <file_path>
  - get <address>
  - list
  - find --tag <tag>
  - stats
```

---

## Implementation

### Step 1: Core CAS
```rust
// cas_core.rs
use twox_hash::{xxh3::xxh3_128, Twox128};
use lz4_flex::compress_prepend_size;
use std::path::Path;

pub fn compute_address(data: &[u8]) -> String {
    hex::encode(xxh3_128(data))
}

pub fn store(data: &[u8], path: &Path) -> std::io::Result<String> {
    let address = compute_address(data);
    let compressed = compress_prepend_size(data);
    let full_path = path.join(&address);
    std::fs::write(full_path, compressed)?;
    Ok(address)
}
```

### Step 2: OpenDAL Layer
```rust
// cas_store.rs
use opendal::Operator;
use opendal::services::Fs;

pub fn new_operator(root: &str) -> Operator {
    let mut fs = Fs::default();
    fs.root(root);
    Operator::new(fs).finish()
}
```

### Step 3: Metadata Index
```rust
// Simple JSON index (upgrade to SurrealDB later)
struct Index {
    entries: HashMap<String, CasEntry>,
}
```

---

## Integration Points

| Existing Skill | Integration |
|----------------|-------------|
| `kreuzberg` | Extract text → CAS store → return address |
| `surrealdb` | Store metadata with vector embeddings |
| `gog` | Download from Drive → CAS store |
| `web-search` | Crawl results → CAS store |

---

## File Structure

```
skills/
└── regen-cas/
    ├── SKILL.md
    ├── Cargo.toml
    ├── src/
    │   ├── main.rs      # CLI entry
    │   ├── lib.rs       # Core CAS logic
    │   ├── store.rs     # OpenDAL storage
    │   └── index.rs     # Metadata
    └── README.md
```

---

## Config

```yaml
# config.yaml
storage:
  backend: fs  # or s3, gcs
  root: /data/cas

compression:
  enabled: true
  threshold_kb: 10  # skip if smaller

deduplication:
  hash: xxh3_128
  verify: sha256  # optional
```

---

## Usage Flow

1. **Agent receives file** (upload or Drive)
2. **Agent calls**: `cas store /tmp/upload.bin`
3. **CAS computes**: `address = xxh3_128(content)`
4. **CAS stores**: compressed at `/{root}/{address}`
5. **CAS returns**: `{"address": "a1b2c3...", "size": 12345}`
6. **Future same file**: instant dedup hit, returns existing address

---

## Deliverables

| Item | Description |
|------|-------------|
| `SKILL.md` | OpenClaw skill manifest |
| `Cargo.toml` | Rust dependencies |
| `src/lib.rs` | Core CAS (50-100 lines) |
| `src/store.rs` | OpenDAL integration |
| `src/main.rs` | CLI + skill interface |
| `config.yaml` | Configuration |
| `README.md` | Setup + usage |

---

## Status

- [x] Research complete
- [ ] Specification (this doc)
- [ ] Core implementation
- [ ] OpenClaw skill wrapper
- [ ] Integration tests
