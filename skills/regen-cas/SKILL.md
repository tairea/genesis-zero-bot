---
name: regen-cas
description: Content-Addressable Storage for file deduplication and retrieval
homepage: https://github.com/genesis-zero-bot/regen-cas
metadata:
  emoji: 📦
  requires:
    bins: [cargo, rustc]
  install:
    - kind: cargo
      command: cargo install regen-cas
      bins: [regen-cas]
---

# regen-cas — Content-Addressable Storage Skill

Store files once, retrieve by content hash. Enables deduplication for uploaded files.

## Setup

```bash
# Install Rust if needed
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Clone and build
git clone https://github.com/genesis-zero-bot/regen-cas
cd regen-cas
cargo build --release

# Install binary
cargo install --path .
```

## Configuration

Set environment variable:
```bash
export REGEN_CAS_ROOT=/data/cas
```

## Commands

| Command | Description |
|---------|-------------|
| `regen-cas store <file>` | Store file, returns address |
| `regen-cas get <address>` | Retrieve file by address |
| `regen-cas list` | List all stored files |
| `regen-cas find --tag <tag>` | Find by tag |
| `regen-cas stats` | Show storage stats |

## OpenClaw Integration

Skill interface:
- **store**: Accept file path, return JSON `{"address": "...", "size": N}`
- **get**: Accept address, return file content
- **list**: Return JSON array of entries

## Dependencies

- `opendal` — unified storage (fs/s3/gcs)
- `twox-hash` — fast content addressing
- `lz4-flex` — compression

## See Also

- [SPEC.md](./SPEC.md) — Full specification
- [GitHub](https://github.com/genesis-zero-bot/regen-cas)
