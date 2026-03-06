# Regen Viz — 3D Force-Directed Graph Visualizations

Interactive 3D network visualizations of RegenTribes knowledge structures, served as static HTML via GitHub Pages.

## Intention

Render community knowledge graphs as explorable 3D force-directed visualizations. Each visualization is a self-contained HTML file that loads the 3d-force-graph library from CDN — no build step, no server required.

## Stack

- **3d-force-graph** — 3D rendering engine (loaded via CDN, not vendored)
- **Three.js** — WebGL foundation (loaded via CDN)
- **Jekyll** — GitHub Pages static site generation
- **HTML/CSS/JS** — self-contained visualization files

## Components

| Path | Role |
|------|------|
| `SKILL.md` | OpenClaw skill manifest — validation workflow and rendering commands |
| `scripts/test-all.sh` | Pre-publish validation suite: JSON parsing, HTML structure, JS correctness, CDN accessibility (25+ checks) |
| `bin/regen-viz` | CLI binary for generating visualizations |

## Project Output

The generated site files (HTML visualizations, JSON datasets, Jekyll config) live in `projects/regen-viz/` — separate from this skill. This is intended to become its own repo (`regentribes/regen-viz`) for GitHub Pages deployment.

### Datasets (in projects/regen-viz/data/unified/)

| File | Content |
|------|---------|
| `regen-framework.json` | RegenTribes organizational framework |
| `meta-fractal-dao.json` | Meta-fractal DAO governance structure |
| `tree-of-civilization.json` | Civilizational knowledge tree |
| `rgem-regen.json` | RGEM regeneration model |
| `conversation-dag.json` | Conversation directed acyclic graph |

## Visualizations

| Visualization | URL |
|--------------|-----|
| Basic | https://genesis-zero-bot.github.io/regen-viz/html/basic.html |
| Tree | https://genesis-zero-bot.github.io/regen-viz/html/tree.html |
| Highlight | https://genesis-zero-bot.github.io/regen-viz/html/highlight.html |
| Curved Links | https://genesis-zero-bot.github.io/regen-viz/html/curved-links.html |
| Directional Links | https://genesis-zero-bot.github.io/regen-viz/html/directional-links.html |
| Bloom Effect | https://genesis-zero-bot.github.io/regen-viz/html/bloom-effect.html |
| Camera Orbit | https://genesis-zero-bot.github.io/regen-viz/html/camera-orbit.html |
| Controls Orbit | https://genesis-zero-bot.github.io/regen-viz/html/controls-orbit.html |
| Controls Fly | https://genesis-zero-bot.github.io/regen-viz/html/controls-fly.html |
| Responsive | https://genesis-zero-bot.github.io/regen-viz/html/responsive.html |

Plus additional variants: regen-radial, rgem-interactive, rgem-regen, tree-minimal, tree-of-civilization, unified-bloom, unified-meta-fractal, unified-regen-framework, conversation-dag (v2 through v8), conversation-minimal.

## Limitations

- **Manually curated data** — JSON files are hand-crafted, not auto-generated from SurrealDB or any extraction pipeline
- **No pipeline connection** — no export script from semantic-graph or xtract SurrealDB to regen-viz JSON format
- **Redundant variants** — conversation-dag has 7 iterations (v2-v8) that may be superseded by each other
- **CDN dependency** — requires internet access to load 3d-force-graph and Three.js at runtime

## Next Steps

1. Build an export script: SurrealDB (semantic-graph namespace) -> JSON nodes+links -> regen-viz format
2. Prune redundant visualization variants (identify which conversation-dag version is best)
3. Automate publish: extraction -> viz generation -> GitHub Pages deploy
4. Add offline fallback for CDN libraries
