# Genesis Workspace — Repository Catalog
# Radicle RID: rad:z2GNG6Nt3c7NWPge18xTRKZkkxSTy
# GitHub:    github.com/regentribes/genesis-zero-bot
# Generated: 2026-04-30

## Workspace Backup URLs

| Remote | URL |
|--------|-----|
| **GitHub** | https://github.com/regentribes/genesis-zero-bot/tree/e471af5 |
| **Radicle** | https://app.radicle.xyz/nodes/iris.radicle.xyz/rad:z2GNG6Nt3c7NWPge18xTRKZkkxSTy/tree/e471af5 |

Commit: `e471af5` ("backup: workspace cleanup — exclude large repos, venvs, tmp, radicle node data")

---

## 🏛️ Genesis / RegenTribes Org Repos

| Repo | URL | Path in Workspace |
|------|-----|------------------|
| genesis-zero-bot | https://github.com/regentribes/genesis-zero-bot | . (workspace itself) |
| mythogen-ame | https://github.com/regentribes/mythogen-ame | mythogen-ame/ |
| regen-neighborhood-framework | https://github.com/regentribes/regen-neighborhood-framework | projects/framework/ |
| regen-vision | https://github.com/regentribes/regen-vision | projects/regen-vision/ |
| regen-viz | https://github.com/genesis-zero-bot/regen-viz | regen-viz/ |

---

## 📚 All Cloned Reference Repos

### Regenerative Community / Ecocapital

| Repo | URL | Last Commit |
|------|-----|-------------|
| ecohubs-website | https://github.com/ecohubs-community/ecohubs-website | 2026-04-19 |
| RCOS-ecohubs | https://github.com/ecohubs-community/RCOS-ecohubs | 2026-04-27 |
| ecohubs-community-blueprint | https://github.com/ecohubs-community/regenerative-community-blueprint | — |

### Systems Engineering / Complexity

| Repo | URL | Last Commit |
|------|-----|-------------|
| ComplexityMeasures.jl | https://github.com/JuliaDynamics/ComplexityMeasures.jl | 2026-04-26 |
| DynamicalSystems.jl | https://github.com/JuliaDynamics/DynamicalSystems.jl | 2026-01-30 |
| DS-ecosystem-development | https://github.com/aisystant/DS-ecosystem-development | 2026-04-28 |
| S1000D-STE100-Tool-Suite | https://github.com/HendrikLuedemann/S1000D-STE100-Tool-Suite | 2025-08-28 |
| archi-scripts | https://github.com/ThomasRohde/archi-scripts | 2024-08-22 |

### Integral / Philosophy / Governance

| Repo | URL | Last Commit |
|------|-----|-------------|
| integral-whitepaper | https://github.com/Integral-Collective/integral-whitepaper | 2026-03-20 |
| integral-devguide | https://github.com/Integral-Collective/integral-devguide | 2026-03-20 |
| mythogen-ame | https://github.com/regentribes/mythogen-ame | 2026-03-30 |

### UN / Trade / Specification

| Repo | URL | Last Commit |
|------|-----|-------------|
| spec-untp | https://opensource.unicc.org/un/unece/uncefact/spec-untp | 2026-04-23 |
| spec-unvtd | https://opensource.unicc.org/un/unece/uncefact/spec-unvtd | 2026-04-21 |
| gtr | https://opensource.unicc.org/un/unece/uncefact/gtr | 2026-04-21 |

### AI / Agents / Prompt Engineering

| Repo | URL | Last Commit |
|------|-----|-------------|
| fpf-problem-solving-skill | https://github.com/CodeAlive-AI/fpf-problem-solving-skill | 2026-04-07 |
| triz-prompt-engineering | https://github.com/jenson500/triz-prompt-engineering | — |
| aisystant-docs | https://github.com/aisystant/docs | — |
| FPF-agent | https://github.com/pokrovskiyv/FPF-agent | — |

### Web / Graphics / Simulation

| Repo | URL | Last Commit |
|------|-----|-------------|
| alien.js | https://github.com/alienkitty/alien.js.git | 2026-01-06 |
| big_space | https://github.com/aevyrie/big_space.git | 2026-03-27 |

### Valueflows / Open Enterprise

| Repo | URL | Last Commit |
|------|-----|-------------|
| valueflows | https://codeberg.org/valueflows/valueflows | — |
| valueflows pages | https://codeberg.org/valueflows/pages | 2026-02-24 |

### SurrealDB / Data

| Repo | URL | Last Commit |
|------|-----|-------------|
| surreal-skills | https://github.com/24601/surreal-skills.git | 2026-03-03 |

---

## 🔑 How to Reclone Any Excluded Repo

Every excluded `.git/` directory is tracked in `REPO-MANIFEST.json` with:
- `path` — where it lives in the workspace
- `url` — the upstream Git URL
- `branch` — current branch
- `last_commit` — last commit hash, timestamp, and message

```bash
# Example: reclone any excluded repo
git clone https://github.com/regentribes/mythogen-ame.git
git clone https://github.com/ecohubs-community/RCOS-ecohubs.git
git clone https://github.com/JuliaDynamics/ComplexityMeasures.jl.git
```

---

## 📦 What's in the Backup (~116 MB)

- `radicle-notes/` — 32M of knowledge base notes
- `skills/` — 32M (all skills, semantic-graph/.venv excluded)
- `ingested-docs/` — 18M of SEBoK, GRCSE, SECF, INCOSE, NASA SE Handbook
- `memory/` — 13M of daily session notes, gap analysis, corpus
- `3d-force-graph/`, `artifacts/`, `deepwiki_exports/`, `ame-pc-export/` — ~10M reference materials
- All `*.md` synthesis docs, civilization stacks, reports
- `REPO-CATALOG.md` — this file

### Excluded from Backup
- All `.git/` dirs (34 repos — re-clonable via manifest)
- `synthesis-prime/`, `valueflows/`, `genesis-zero-bot/` (large upstream clones)
- `skills/semantic-graph/.venv/` (227M — `pip install` reinstallable)
- `tmp/` (153M generated images)
- SurrealDB `brain.db` (separate service backup)
- `.radicle/node/` (368M radicle node metadata — not repo content)
