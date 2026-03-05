# regen-cas

Content-Addressable Storage for Regen Tribe — store files once, retrieve by content hash.

## Quick Start

```bash
# Set storage root
export REGEN_CAS_ROOT=/data/cas

# Store a file
regen-cas store document.pdf
# Returns: {"address":"a1b2c3d4e5f6...","size":12345}

# Retrieve by address
regen-cas get a1b2c3d4e5f6...

# List all
regen-cas list

# Stats
regen-cas stats
```

## Building

```bash
cargo build --release
cargo install --path .
```

## Dependencies

- `opendal` — Storage abstraction (fs/s3/gcs)
- `twox-hash` — Fast content addressing (xxh3)
- `lz4-flex` — LZ4 compression

## See Also

- [SPEC.md](./SPEC.md) — Full specification
- [SKILL.md](./SKILL.md) — OpenClaw skill manifest
