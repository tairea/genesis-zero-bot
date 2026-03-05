---
name: ref-docs
description: Reference documentation and API lookup skill for development - manages reference repositories and provides instant API lookups
homepage: https://github.com/genesis-zero-bot/ref-docs
metadata:
  emoji: 📚
  requires:
    bins: [git, curl, jq, grep]
  install:
    - kind: clone
      repos:
        - https://github.com/vasturiano/3d-force-graph
        - https://github.com/agentskills/agentskills
        - https://github.com/AdaWorldAPI/ladybug-rs
        - https://github.com/AdaWorldAPI/langextract-rs
        - https://github.com/semanticarts/gist
        - https://github.com/valueflows/valueflows
        - https://github.com/uncefact/spec-untp
---

# ref-docs — Reference Documentation Skill

Manage and query reference repositories for development.

## Setup

Reference repos are cloned to: `skills/ref-docs/repos/`

## Commands

### List Repositories
```bash
ref-docs list
```

### Search in Repository
```bash
ref-docs search <repo> <query>
```

### Get API Reference
```bash
ref-docs api <repo> <method/function>
```

### Find Examples
```bash
ref-docs example <repo> <feature>
```

### Clone All Repositories
```bash
ref-docs sync
```

## Available Repositories

| Repo | Description |
|------|-------------|
| 3d-force-graph | 3D network visualization |
| agentskills | Agent skill patterns |
| ladybug-rs | Rust parsing library |
| langextract-rs | Language extraction |
| gist | Semanticart's gist tools |
| valueflows | Value flows ontology |
| spec-UNTP | UN trade standards |

## Usage Examples

```bash
# List all available repositories
ref-docs list

# Search for nodeColor in 3d-force-graph
ref-docs search 3d-force-graph nodeColor

# Get API for highlight
ref-docs example 3d-force-graph highlight

# Find ForceGraph3D usage
ref-docs api 3d-force-graph ForceGraph3D
```

## Repository Structure

```
ref-docs/
├── SKILL.md
├── bin/
│   └── ref-docs          # CLI script
└── repos/                # Cloned repositories
    ├── 3d-force-graph/
    ├── agentskills/
    ├── ladybug-rs/
    └── ...
```

## Skill Development Best Practices

1. **Local clones** - All repos cloned locally for offline access
2. **Indexed search** - Full-text search across all docs
3. **API extraction** - Parse type definitions and docs
4. **Example extraction** - Find usage patterns

## Updates

- 2026-03-05: Initial setup with 7 reference repositories
