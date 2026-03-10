# SKILL: Semantic Graph 3D Visualization

## Purpose

Query the semantic graph from SurrealDB and render it as an interactive 3D force-directed graph using 3d-force-graph. Creates self-contained, versioned HTML artifacts.

---

## When to invoke this skill

- "visualize the semantic graph"
- "show me the knowledge graph in 3D"
- "render the concept map"
- "open the graph explorer"
- "create a 3d view of the knowledge graph"
- Any request to see or explore the semantic graph visually

---

## File structure

| File | Role |
|------|------|
| `graph_viz.py` | Main script: queries SurrealDB → generates HTML |
| `template.html` | HTML template with 3d-force-graph embed |
| `SKILL.md` | This file |

---

## Output location

All HTML artifacts are stored in:
```
~/.openclaw/workspace-genesis/artifacts/semantic-graph-viz/
```

Filenames include version and timestamp:
```
semantic-graph-viz-{version}-{timestamp}.html
```

The skill maintains a `latest.html` symlink to the most recent visualization.

---

## Database

- **SurrealDB**: ws://127.0.0.1:8000
- **Namespace**: semantic_graph  
- **Database**: main
- **Credentials**: Uses configured root credentials

---

## Usage

### CLI

```bash
# Generate visualization from default SurrealDB (ws://localhost:8000)
python graph_viz.py

# Custom connection
python graph_viz.py --db ws://localhost:8000 --ns knowledge --db main

# Limit nodes (for large graphs)
python graph_viz.py --limit 500

# Focus on specific concept
python graph_viz.py --focus "Regeneration"

# Export only (don't open browser)
python graph_viz.py --export-only
```

### Python API

```python
from graph_viz import GraphVisualizer

async def main():
    viz = GraphVisualizer()
    await viz.connect()
    
    # Full graph
    html_path = await viz.generate_viz()
    
    # Focused subgraph
    html_path = await viz.generate_viz(focus_concept="Regeneration", depth=3)
    
    print(f"Generated: {html_path}")
```

---

## HTML Features

### Minimalist Design
- Dark theme with high contrast
- Clean typography (system fonts)
- No unnecessary UI chrome

### Node Visualization
- **Size**: Based on evidence_count (more evidence = larger)
- **Color**: Based on concept type (entity, system, process, idea, etc.)
- **Label**: Concept name, always visible, non-overlapping via collision detection

### Edge Visualization
- **Thickness**: Based on nars_confidence
- **Color**: Based on verb_category (Causal, Structural, Temporal, etc.)
- **Label**: Verb name on hover
- **Direction**: Arrow indicators for directed relations

### First-Person Experience
- **Camera**: First-person fly controls (WASD + mouse)
- **Focus mode**: Click a node to center camera and highlight connected nodes
- **Depth control**: Adjust how many neighbor levels to show (1-5)
- **Dimming**: Non-connected nodes dim when focused

### Interaction
- **Click node**: Focus on node, show details panel
- **Hover**: Highlight node + connected edges
- **Scroll**: Zoom in/out
- **Drag**: Move camera (right-click + drag)
- **Double-click**: Zoom to fit selected subgraph

### Visual Effects
- Glow effect on focused node
- Particle flow on high-confidence edges
- Smooth transitions when changing focus

---

## SurrealDB Query

The visualization queries:

```sql
-- All concepts (nodes)
SELECT id, name, type, description, rung, nars_frequency, 
       nars_confidence, evidence_count, tags
FROM concept;

-- All relations (edges)
SELECT in, out, verb, verb_category, weight, 
       nars_frequency, nars_confidence, evidence
FROM relates;
```

For focused mode:
```sql
-- N-hop neighbourhood
SELECT *, ->relates->(concept) AS out_edges,
       <-relates<-(concept) AS in_edges
FROM concept WHERE name = $focus;
```

---

## Dependencies

- `surrealdb` Python package
- Internet access (to load 3d-force-graph from unpkg.com)
- Modern browser with WebGL support

---

## Skill integration

When invoked:
1. Connect to SurrealDB using configured credentials
2. Query all concepts and relations
3. Transform to 3d-force-graph format
4. Generate HTML with embedded data
5. Save versioned artifact
6. Return path to generated HTML

If no data in database, inform user and suggest ingesting documents first.
