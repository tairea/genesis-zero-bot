---
name: regen-viz
description: 3D Force Graph visualization generator with validation and testing
homepage: https://github.com/genesis-zero-bot/regen-viz
metadata:
  emoji: 🌐
  requires:
    bins: [git, curl, jq, python3]
  env:
    - REGEN_VIZ_REPO (GitHub repo URL)
    - REGEN_VIZ_BRANCH (default: gh-pages)
---

# regen-viz — 3D Visualization Skill

Generate interactive 3D network visualizations from JSON data using 3d-force-graph.

## Quick Start

```bash
# Run full validation before publishing
regen-viz test --path /path/to/regen-viz

# Or use the test script directly
./skills/regen-viz/scripts/test-all.sh /path/to/regen-viz
```

## Pre-Publish Validation

Before publishing artifacts, always run:

```bash
regen-viz test --path ~/.openclaw/workspace-genesis/regen-viz
```

This performs:

### 1. JSON Validation
- All JSON files parse correctly
- Nodes have required fields: id, label
- Links have required fields: source, target

### 2. HTML Validation  
- Valid HTML structure (<html>, <head>, <body>)
- JavaScript syntax correctness
- CDN links accessible (3d-force-graph)

### 3. File Path Checks
- Data file references exist
- Relative paths correct

### 4. Git Repository Checks
- Working tree clean
- Remote configured
- Branch exists

### 5. Dependency Checks
- Required binaries available
- CDN resources accessible

## Commands

### Test (Pre-Publish)
```bash
# Test entire visualization directory
regen-viz test --path /path/to/viz

# Test specific files
regen-viz test --json data/graph.json --html html/graph.html

# Verbose output
regen-viz test --path /path --verbose
```

### Generate JSON
```bash
# Create from comma-separated nodes/links
regen-viz generate-json --nodes node1,node2,node3 --links "node1-node2,node2-node3"

# Output to file
regen-viz generate-json --nodes a,b,c --links a-b --output data/graph.json
```

### Create Visualization
```bash
# Create from JSON file
regen-viz create --data file.json --variant basic --name my-graph

# Create from inline JSON
regen-viz create --json '{"nodes":[{"id":"a"}], "links":[]}' --variant highlight
```

### Publish
```bash
# Publish to GitHub Pages
regen-viz publish --path ~/.openclaw/workspace-genesis/regen-viz
```

## Test Output Example

```
=== regen-viz Validation Report ===
Path: /home/user/regen-viz
Date: 2026-03-05T21:20:00Z

[JSON] Validating 6 JSON files...
  ✓ regen-tribe.json (1458 bytes)
  ✓ meta-fractal-dao.json (14935 bytes)
  ✓ regen-framework.json (6687 bytes)
  ✓ rgem-regen.json (10423 bytes)
  ✓ tree-of-civilization.json (5626 bytes)
  ✓ conversation-dag.json (44721 bytes)
  [PASS] All JSON files valid

[HTML] Validating 19 HTML files...
  ✓ basic.html - valid structure
  ✓ bloom-effect.html - valid structure
  ✓ camera-orbit.html - valid structure
  ✓ controls-fly.html - valid structure
  ✓ controls-orbit.html - valid structure
  ✓ curved-links.html - valid structure
  ✓ directional-links.html - valid structure
  ✓ highlight.html - valid structure
  ✓ index.html - valid structure
  ✓ responsive.html - valid structure
  ✓ tree.html - valid structure
  ✓ unified-bloom.html - valid structure
  ✓ unified-meta-fractal.html - valid structure
  ✓ unified-regen-framework.html - valid structure
  ✓ rgem-regen.html - valid structure
  ✓ rgem-interactive.html - valid structure
  ✓ tree-of-civilization.html - valid structure
  ✓ tree-minimal.html - valid structure
  ✓ regen-radial.html - valid structure
  ✓ conversation-dag.html - valid structure
  ✓ conversation-minimal.html - valid structure
  [PASS] All HTML files valid

[DEPS] Checking dependencies...
  ✓ git available
  ✓ curl available
  ✓ jq available
  ✓ python3 available
  ✓ 3d-force-graph CDN accessible
  [PASS] All dependencies available

[GIT] Checking repository...
  ✓ Git repository initialized
  ✓ Remote configured: https://github.com/genesis-zero-bot/regen-viz
  ✓ Branch exists: gh-pages
  [PASS] Git OK

[PATHS] Checking file references...
  ✓ HTML files reference existing JSON files
  [PASS] Paths OK

=== SUMMARY ===
Files tested: 25
Passed: 25
Failed: 0
Status: ✓ READY TO PUBLISH
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All tests passed |
| 1 | JSON validation failed |
| 2 | HTML validation failed |
| 3 | Dependency missing |
| 4 | Git check failed |
| 5 | Path check failed |

## Available Variants

| Variant | Description | Features |
|---------|-------------|----------|
| `basic` | Simple 3D graph | Auto-color, hover labels |
| `tree` | Tree with text labels | Node labels using SpriteText |
| `highlight` | Interactive highlighting | Hover to highlight connections |
| `curved-links` | Curved edges | Curved link rendering |
| `directional-links` | Arrows + particles | Animated particles on links |
| `bloom-effect` | Post-processing bloom | Glowing nodes |
| `camera-orbit` | Auto-orbiting camera | Continuous rotation |
| `controls-orbit` | Orbit controls | Click-drag to rotate |
| `controls-fly` | Fly controls | WASD navigation |
| `responsive` | Responsive sizing | Auto-resize on window |
| `rgem-regen` | RGEM visualization | Quint mapping |
| `tree-of-civilization` | 5-layer tree | Crown→Leaves→Branches→Trunk→Roots |
| `conversation-dag` | Conversation history | Topics/Actors/Messages DAG |

## 3d-force-graph API Features Covered

### Node Styling
- `nodeColor` - Color by group/custom
- `nodeVal` - Size by value
- `nodeRelSize` - Relative size
- `nodeThreeObject` - Custom 3D objects
- `nodeLabel` - Hover labels
- `nodeAutoColorBy` - Auto-color groups

### Link Styling
- `linkColor` - Custom link colors
- `linkWidth` - Variable width
- `linkCurvature` - Curved links
- `linkDirectionalArrowLength` - Arrow heads
- `linkDirectionalParticles` - Animated particles
- `linkLabel` - Hover labels

### Camera/Controls
- `controlType` - 'orbit' | 'fly' | 'trackball'
- `cameraAutoRotate` - Auto rotation
- `cameraAutoRotateSpeed` - Rotation speed
- `zoomToFit` - Fit to view

### Effects
- `postProcessingComposer` - Bloom, etc.
- `backgroundColor` - Scene background
- `nodeThreeObjectExtend` - Extend nodes

### Interactions
- `onNodeClick` - Click handler
- `onNodeHover` - Hover handler
- `onLinkClick` - Link click
- `onLinkHover` - Link hover

### Data
- `graphData` - Set data
- `jsonUrl` - Load from URL
- `d3Force` - Force simulation control

## Output URLs

After publishing:
- `https://genesis-zero-bot.github.io/regen-viz/html/{name}.html`
- Index: `https://genesis-zero-bot.github.io/regen-viz/`

## See Also

- [3d-force-graph](https://github.com/vasturiano/3d-force-graph)
- [Live Examples](https://vasturiano.github.io/3d-force-graph/)
- [API Reference](https://github.com/vasturiano/3d-force-graph#api-reference)
