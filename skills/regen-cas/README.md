# Regen CAS — Content-Addressable Storage

Store files once by content hash, retrieve by address. Deduplication for the RegenTribes knowledge pipeline.

## Intention

Provide a fast, local-first content-addressable storage layer. Any file is hashed, compressed, and stored once — identical files share the same address. Designed as infrastructure for document ingestion pipelines where the same file may arrive from multiple sources.

## Stack

- **Rust** — CLI binary
- **OpenDAL** — storage abstraction (filesystem, S3, GCS, Azure)
- **twox-hash** — xxh3_128 content addressing (fast, 128-bit)
- **lz4-flex** — LZ4 compression for large files

## Components

| File | Role |
|------|------|
| `src/main.rs` | CLI implementation: store, get, list, find, stats commands |
| `SKILL.md` | OpenClaw skill manifest |
| `SPEC.md` | Full architecture specification with data model, API, and integration points |
| `Cargo.toml` | Rust project configuration and dependencies |

## Quick Start

```bash
# Set storage root
export REGEN_CAS_ROOT=/data/cas

# Store a file (returns content address)
regen-cas store document.pdf
# Returns: {"address":"a1b2c3d4e5f6...","size":12345}

# Retrieve by address
regen-cas get a1b2c3d4e5f6...

# List all stored files
regen-cas list

# Find by tag
regen-cas find --tag "report"

# Storage stats
regen-cas stats
```

## Building

```bash
cargo build --release
cargo install --path .
```

## Limitations

- **Flat-file metadata** — index stored as `index.json`, not in a database. SPEC mentions future SurrealDB integration for metadata + vector embeddings, not yet built.
- **No garbage collection** — orphaned blobs (unreferenced content) are never cleaned up
- **No multi-backend sync** — can use fs/s3/gcs but can't replicate across backends
- **No streaming** — entire file read into memory for hashing

## Next Steps

1. SurrealDB metadata integration (store file metadata as graph records)
2. Add vector embedding storage for content-based retrieval
3. Implement garbage collection for unreferenced blobs
4. Add streaming hash computation for large files
5. Multi-backend replication
6. Integration with kreuzberg (extract text from stored documents)

## See Also

- [SPEC.md](./SPEC.md) — full architecture specification
- [SKILL.md](./SKILL.md) — OpenClaw skill manifest
