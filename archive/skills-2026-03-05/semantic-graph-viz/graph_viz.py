#!/usr/bin/env python3
"""
graph_viz.py — Query SurrealDB semantic graph and render as 3D force-directed graph.

Features:
- Hover to show node details
- Click to focus on node
- Optimized rendering for performance
- Visible labels for focused nodes and edges
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from surrealdb import AsyncSurreal

# Configuration
DEFAULT_DB_URL = os.environ.get("SURREALDB_URL", "ws://127.0.0.1:8000")
DEFAULT_NS = os.environ.get("SURREALDB_NS", "semantic_graph")
DEFAULT_DB = os.environ.get("SURREALDB_NAME", "main")
DEFAULT_USER = os.environ.get("SURREALDB_USER", "root")
DEFAULT_PASS = os.environ.get("SURREALDB_PASS", "DLkelAlX8ucXPRUKBVPh5dYp9xZ5Y+IZ")

ARTIFACTS_DIR = Path(__file__).parent.parent.parent / "artifacts" / "semantic-graph-viz"

# Concept type colors
TYPE_COLORS = {
    "entity": "#00d4ff",
    "system": "#ff6b35",
    "process": "#7b2cbf",
    "idea": "#2ec4b6",
    "event": "#ffbe0b",
    "person": "#e71d36",
    "place": "#06d6a0",
    "attribute": "#9b5de5",
    "quantity": "#f15bb5",
    "quality": "#00bbf9",
    "relation": "#fee440",
    "specification": "#ff9f1c",
    "project": "#80ed99",
    "layer": "#adb5bd",
    "concept": "#ffffff",
}

VERB_COLORS = {
    "IS_A": "#ffd700",
    "HAS_A": "#00ff88",
    "CONTAINS": "#ff6b6b",
    "DEPENDS_ON": "#ff4757",
    "RELATES_TO": "#a29bfe",
    "USES": "#74b9ff",
    "PROVIDES": "#55efc4",
    "REQUIRES": "#fd79a8",
    "ENABLES": "#00cec9",
    "MANAGES": "#fdcb6e",
    "STORES": "#e17055",
    "PROCESSES": "#6c5ce7",
    "GENERATES": "#e84393",
    "CREATES": "#00b894",
    "INCLUDES": "#0984e3",
    "CONNECTED_TO": "#636e72",
    "IMPLEMENTS": "#b2bec3",
    "DEFINES": "#ff7675",
    "TRANSFORMS": "#dfe6e9",
    "CALLS": "#ffeaa7",
    "ACTS_AS": "#81ecec",
}


class GraphVisualizer:
    def __init__(
        self,
        url: str = DEFAULT_DB_URL,
        namespace: str = DEFAULT_NS,
        database: str = DEFAULT_DB,
        username: str = DEFAULT_USER,
        password: str = DEFAULT_PASS,
    ):
        self.url = url
        self.namespace = namespace
        self.database = database
        self.username = username
        self.password = password
        self.db = None

    async def connect(self):
        from surrealdb import AsyncSurreal
        self.db = AsyncSurreal(url=self.url)
        await self.db.connect()
        await self.db.signin({"username": self.username, "password": self.password})
        await self.db.use(self.namespace, self.database)
        print(f"Connected to SurrealDB at {self.url}/{self.namespace}/{self.database}")

    async def close(self):
        if self.db:
            await self.db.close()

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, *_: Any):
        await self.close()

    async def get_full_graph(self, limit: int = 0):
        """Fetch all concepts and relations."""
        concepts_result = await self.db.query("SELECT * FROM concept")
        if isinstance(concepts_result, list):
            concepts = concepts_result
        else:
            concepts = concepts_result[0].get("result", []) if concepts_result else []
        
        if limit > 0:
            concepts = concepts[:limit]

        relations_result = await self.db.query("SELECT * FROM relates")
        if isinstance(relations_result, list):
            relations = relations_result
        else:
            relations = relations_result[0].get("result", []) if relations_result else []

        print(f"Fetched {len(concepts)} concepts, {len(relations)} relations")
        return {"nodes": concepts, "links": relations}


def transform_for_3d_force_graph(nodes, links):
    """Transform SurrealDB graph to 3d-force-graph format."""
    
    graph_nodes = []
    node_map = {}
    
    for node in nodes:
        node_id = str(node.get("id", ""))
        if not node_id:
            continue
            
        if ":" in node_id:
            short_id = node_id.split(":")[-1]
        else:
            short_id = node_id
        
        concept_type = node.get("type", "concept")
        node_data = {
            "id": short_id,
            "fullId": node_id,
            "name": node.get("name", "Unknown"),
            "type": concept_type,
            "description": node.get("description", "") or "",
            "rung": node.get("rung", 0),
            "nars_frequency": node.get("nars_frequency", 0.5),
            "nars_confidence": node.get("nars_confidence", 0.5),
            "evidence_count": node.get("evidence_count", 1),
            "color": TYPE_COLORS.get(concept_type, "#ffffff"),
            "val": max(1, node.get("evidence_count", 1)),
        }
        
        node_map[node_id] = short_id
        node_map[short_id] = short_id
        graph_nodes.append(node_data)
    
    graph_links = []
    for link in links:
        source = link.get("source")
        target = link.get("target")
        
        # Handle both string IDs and object IDs (SurrealDB record IDs)
        if hasattr(source, 'get'):
            source = str(source.get("id", ""))
        elif hasattr(source, 'table_name'):
            source = f"{source.table_name}:{source.record_id}"
            
        if hasattr(target, 'get'):
            target = str(target.get("id", ""))
        elif hasattr(target, 'table_name'):
            target = f"{target.table_name}:{target.record_id}"
        
        # Normalize IDs
        if source and ":" in source:
            source = source.split(":")[-1]
        if target and ":" in target:
            target = target.split(":")[-1]
        
        if not source or not target or source == target:
            continue
        
        verb = link.get("verb", "RELATES_TO")
        link_data = {
            "source": source,
            "target": target,
            "verb": verb,
            "verb_category": link.get("verb_category", "Structural"),
            "weight": link.get("weight", link.get("nars_confidence", 0.5)),
            "evidence": link.get("evidence", ""),
            "color": VERB_COLORS.get(verb, "#666666"),
            "width": max(0.5, link.get("weight", 0.5) * 3),
        }
        
        graph_links.append(link_data)
    
    return {"nodes": graph_nodes, "links": graph_links}


def generate_html(graph_data, version="1.0.0", focus_name=None):
    """Generate optimized HTML with hover details, click focus, and visible labels."""
    
    nodes_json = json.dumps(graph_data.get("nodes", []))
    links_json = json.dumps(graph_data.get("links", []))
    
    type_colors_json = json.dumps(TYPE_COLORS)
    verb_colors_json = json.dumps(VERB_COLORS)
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Semantic Graph — {len(graph_data.get("nodes", []))} Nodes</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            background: #0a0a0f;
            color: #e0e0e0;
            overflow: hidden;
            height: 100vh;
        }}
        
        #graph-container {{
            width: 100vw;
            height: 100vh;
            position: relative;
        }}
        
        /* Info Panel - Top Left */
        #info-panel {{
            position: fixed;
            top: 20px;
            left: 20px;
            background: rgba(15, 15, 25, 0.95);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 16px 20px;
            z-index: 100;
            backdrop-filter: blur(16px);
            min-width: 200px;
        }}
        
        #info-panel h2 {{
            font-size: 11px;
            font-weight: 600;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-bottom: 12px;
        }}
        
        .stat {{
            display: flex;
            justify-content: space-between;
            padding: 6px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }}
        
        .stat:last-child {{ border-bottom: none; }}
        
        .stat .label {{ color: #666; font-size: 12px; }}
        .stat .value {{ color: #fff; font-weight: 500; font-size: 12px; }}
        
        /* Hover Panel - Bottom Left - Shows on hover */
        #hover-panel {{
            position: fixed;
            bottom: 80px;
            left: 20px;
            background: rgba(15, 15, 25, 0.95);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 16px 20px;
            z-index: 100;
            backdrop-filter: blur(16px);
            max-width: 360px;
            display: none;
            transition: opacity 0.2s;
        }}
        
        #hover-panel.visible {{ display: block; }}
        
        #hover-panel h3 {{
            font-size: 16px;
            margin-bottom: 4px;
            color: #fff;
            word-break: break-word;
        }}
        
        #hover-panel .type-badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 10px;
            font-weight: 600;
            text-transform: uppercase;
            margin-bottom: 8px;
        }}
        
        #hover-panel p {{
            font-size: 12px;
            color: #888;
            line-height: 1.5;
            margin-bottom: 8px;
            word-break: break-word;
        }}
        
        #hover-panel .meta {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 6px;
            font-size: 11px;
        }}
        
        #hover-panel .meta-item {{
            background: rgba(255, 255, 255, 0.03);
            padding: 6px 8px;
            border-radius: 4px;
        }}
        
        #hover-panel .meta-item .label {{ color: #555; display: block; margin-bottom: 2px; }}
        #hover-panel .meta-item .val {{ color: #fff; }}
        
        /* Focus Panel - Same as hover but for click */
        #focus-panel {{
            position: fixed;
            bottom: 20px;
            left: 20px;
            background: rgba(15, 15, 25, 0.95);
            border: 1px solid rgba(0, 212, 255, 0.3);
            border-radius: 12px;
            padding: 16px 20px;
            z-index: 100;
            backdrop-filter: blur(16px);
            max-width: 400px;
            display: none;
        }}
        
        #focus-panel.visible {{ display: block; }}
        
        #focus-panel h3 {{
            font-size: 18px;
            margin-bottom: 8px;
            color: #00d4ff;
            word-break: break-word;
        }}
        
        #focus-panel .type-badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 10px;
            font-weight: 600;
            text-transform: uppercase;
            margin-bottom: 12px;
        }}
        
        #focus-panel p {{
            font-size: 13px;
            color: #aaa;
            line-height: 1.6;
            margin-bottom: 12px;
            word-break: break-word;
        }}
        
        #focus-panel .meta {{
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 8px;
            font-size: 12px;
        }}
        
        #focus-panel .meta-item {{
            background: rgba(255, 255, 255, 0.03);
            padding: 8px;
            border-radius: 4px;
        }}
        
        #focus-panel .meta-item .label {{ color: #555; display: block; margin-bottom: 2px; }}
        #focus-panel .meta-item .val {{ color: #fff; }}
        
        #focus-panel .close-btn {{
            position: absolute;
            top: 10px;
            right: 10px;
            background: none;
            border: none;
            color: #666;
            cursor: pointer;
            font-size: 18px;
        }}
        
        #focus-panel .close-btn:hover {{ color: #fff; }}
        
        /* Legend - Top Right */
        .legend {{
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(15, 15, 25, 0.9);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 14px;
            z-index: 100;
            backdrop-filter: blur(12px);
            font-size: 11px;
        }}
        
        .legend h4 {{
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
            font-size: 10px;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            margin-bottom: 4px;
        }}
        
        .legend-color {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 8px;
            flex-shrink: 0;
        }}
        
        /* Controls - Bottom Right */
        #controls {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: rgba(15, 15, 25, 0.9);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 14px;
            z-index: 100;
            backdrop-filter: blur(12px);
        }}
        
        #controls label {{
            display: block;
            font-size: 10px;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }}
        
        #controls select {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 6px;
            color: #fff;
            padding: 6px 10px;
            font-size: 12px;
            margin-bottom: 10px;
            width: 100%;
        }}
        
        #controls button {{
            background: linear-gradient(135deg, #2ec4b6, #00d4ff);
            border: none;
            border-radius: 6px;
            color: #000;
            padding: 8px 14px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            transition: transform 0.2s;
        }}
        
        #controls button:hover {{
            transform: translateY(-1px);
        }}
        
        /* Instructions */
        .instructions {{
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(15, 15, 25, 0.8);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 20px;
            padding: 8px 20px;
            font-size: 11px;
            color: #555;
            z-index: 50;
            backdrop-filter: blur(8px);
        }}
        
        kbd {{
            background: rgba(255, 255, 255, 0.1);
            padding: 2px 6px;
            border-radius: 4px;
            font-family: inherit;
            color: #777;
        }}
        
        /* Loading overlay */
        #loading {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: #0a0a0f;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            transition: opacity 0.5s;
        }}
        
        #loading.hidden {{ opacity: 0; pointer-events: none; }}
        
        #loading span {{
            color: #00d4ff;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div id="loading"><span>Loading graph...</span></div>
    
    <div id="graph-container"></div>
    
    <!-- Stats Panel -->
    <div id="info-panel">
        <h2>Graph Stats</h2>
        <div class="stat">
            <span class="label">Nodes</span>
            <span class="value" id="node-count">0</span>
        </div>
        <div class="stat">
            <span class="label">Edges</span>
            <span class="value" id="link-count">0</span>
        </div>
        <div class="stat">
            <span class="label">Version</span>
            <span class="value">{version}</span>
        </div>
    </div>
    
    <!-- Hover Panel -->
    <div id="hover-panel">
        <h3 id="hover-name">-</h3>
        <span class="type-badge" id="hover-type">-</span>
        <p id="hover-desc">-</p>
        <div class="meta">
            <div class="meta-item">
                <span class="label">Rung</span>
                <span class="val" id="hover-rung">-</span>
            </div>
            <div class="meta-item">
                <span class="label">Confidence</span>
                <span class="val" id="hover-confidence">-</span>
            </div>
            <div class="meta-item">
                <span class="label">Evidence</span>
                <span class="val" id="hover-evidence">-</span>
            </div>
            <div class="meta-item">
                <span class="label">Frequency</span>
                <span class="val" id="hover-frequency">-</span>
            </div>
        </div>
    </div>
    
    <!-- Focus Panel (click) -->
    <div id="focus-panel">
        <button class="close-btn" onclick="unfocusAll()">×</button>
        <h3 id="focus-name">-</h3>
        <span class="type-badge" id="focus-type">-</span>
        <p id="focus-desc">-</p>
        <div class="meta">
            <div class="meta-item">
                <span class="label">Rung</span>
                <span class="val" id="focus-rung">-</span>
            </div>
            <div class="meta-item">
                <span class="label">Confidence</span>
                <span class="val" id="focus-confidence">-</span>
            </div>
            <div class="meta-item">
                <span class="label">Evidence</span>
                <span class="val" id="focus-evidence">-</span>
            </div>
            <div class="meta-item">
                <span class="label">Frequency</span>
                <span class="val" id="focus-frequency">-</span>
            </div>
            <div class="meta-item">
                <span class="label">Connections</span>
                <span class="val" id="focus-connections">-</span>
            </div>
            <div class="meta-item">
                <span class="label">Neighbors</span>
                <span class="val" id="focus-neighbors">-</span>
            </div>
        </div>
    </div>
    
    <!-- Legend -->
    <div class="legend">
        <h4>Node Types</h4>
        <div class="legend-item"><span class="legend-color" style="background:#00d4ff"></span>Entity</div>
        <div class="legend-item"><span class="legend-color" style="background:#ff6b35"></span>System</div>
        <div class="legend-item"><span class="legend-color" style="background:#7b2cbf"></span>Process</div>
        <div class="legend-item"><span class="legend-color" style="background:#2ec4b6"></span>Idea</div>
        <div class="legend-item"><span class="legend-color" style="background:#ffbe0b"></span>Event</div>
        <div class="legend-item"><span class="legend-color" style="background:#e71d36"></span>Person</div>
        <h4 style="margin-top:10px">Relations</h4>
        <div class="legend-item"><span class="legend-color" style="background:#ffd700"></span>IS_A</div>
        <div class="legend-item"><span class="legend-color" style="background:#00ff88"></span>HAS_A</div>
        <div class="legend-item"><span class="legend-color" style="background:#ff6b6b"></span>CONTAINS</div>
        <div class="legend-item"><span class="legend-color" style="background:#a29bfe"></span>RELATES_TO</div>
    </div>
    
    <!-- Controls -->
    <div id="controls">
        <label>Node Size</label>
        <select id="size-select">
            <option value="evidence" selected>Evidence Count</option>
            <option value="confidence">Confidence</option>
            <option value="fixed">Fixed Size</option>
        </select>
        <label>Focus Depth</label>
        <select id="depth-select">
            <option value="1">1 hop</option>
            <option value="2" selected>2 hops</option>
            <option value="3">3 hops</option>
            <option value="4">4 hops</option>
        </select>
        <button onclick="resetView()">Reset View</button>
    </div>
    
    <div class="instructions">
        <kbd>Hover</kbd> node for details · <kbd>Click</kbd> to focus · <kbd>Scroll</kbd> zoom · <kbd>Drag</kbd> rotate
    </div>

    <!-- 3D Force Graph -->
    <script src="https://unpkg.com/three"></script>
    <script src="https://unpkg.com/3d-force-graph"></script>
    
    <script>
        // Embedded graph data
        const graphData = {{
            nodes: {nodes_json},
            links: {links_json}
        }};
        
        // Colors
        const typeColors = {type_colors_json};
        const verbColors = {verb_colors_json};
        
        // State
        let focusedNodeId = null;
        let hoveredNodeId = null;
        let g3d = null;
        let nodeDataMap = {{}};
        
        // Build node lookup
        graphData.nodes.forEach(n => {{ nodeDataMap[n.id] = n; }});
        
        // Count connections per node
        const connectionCount = {{}};
        graphData.links.forEach(l => {{
            connectionCount[l.source] = (connectionCount[l.source] || 0) + 1;
            connectionCount[l.target] = (connectionCount[l.target] || 0) + 1;
        }});
        
        // Initialize
        const elem = document.getElementById('graph-container');
        g3d = ForceGraph3D()(
            document.getElementById('graph-container')
        )
        .graphData(graphData)
        .backgroundColor('#0a0a0f')
        
        // Performance optimizations
        .nodeResolution(12)
        .linkResolution(4)
        
        // Node styling
        .nodeAutoColorBy('type')
        .nodeColor(node => typeColors[node.type] || '#ffffff')
        .nodeVal(node => Math.max(2, Math.sqrt(node.evidence_count || 1) * 2.5))
        .nodeOpacity(0.85)
        
        // Link styling
        .linkWidth(link => Math.max(0.3, link.weight * 2))
        .linkColor(link => verbColors[link.verb] || '#444')
        .linkOpacity(0.5)
        .linkDirectionalArrowLength(3.5)
        .linkDirectionalArrowRelPos(0.95)
        
        // Interaction - HOVER for details
        .onNodeHover(node => {{
            hoveredNodeId = node ? node.id : null;
            
            if (hoveredNodeId && hoveredNodeId !== focusedNodeId) {{
                // Show hover panel
                const panel = document.getElementById('hover-panel');
                panel.classList.add('visible');
                
                document.getElementById('hover-name').textContent = node.name;
                document.getElementById('hover-type').textContent = node.type;
                document.getElementById('hover-type').style.background = typeColors[node.type] || '#666';
                document.getElementById('hover-type').style.color = '#000';
                document.getElementById('hover-desc').textContent = node.description || 'No description';
                document.getElementById('hover-rung').textContent = 'R' + (node.rung || 0);
                document.getElementById('hover-confidence').textContent = (node.nars_confidence || 0).toFixed(2);
                document.getElementById('hover-evidence').textContent = node.evidence_count || 0;
                document.getElementById('hover-frequency').textContent = (node.nars_frequency || 0).toFixed(2);
                
                // Highlight on hover (only if not focused)
                g3d.nodeOpacity(n => n.id === hoveredNodeId ? 1 : 0.4);
            }} else if (!focusedNodeId) {{
                document.getElementById('hover-panel').classList.remove('visible');
                g3d.nodeOpacity(0.85);
            }}
        }})
        
        // Interaction - CLICK for focus
        .onNodeClick(node => {{
            if (focusedNodeId === node.id) {{
                unfocusAll();
            }} else {{
                focusNode(node);
            }}
        }})
        
        .onBackgroundClick(() => {{
            unfocusAll();
        }});
        
        // Focus on node with neighbors
        function focusNode(node) {{
            focusedNodeId = node.id;
            
            // Show focus panel
            const panel = document.getElementById('focus-panel');
            panel.classList.add('visible');
            document.getElementById('hover-panel').classList.remove('visible');
            
            document.getElementById('focus-name').textContent = node.name;
            document.getElementById('focus-type').textContent = node.type;
            document.getElementById('focus-type').style.background = typeColors[node.type] || '#666';
            document.getElementById('focus-type').style.color = '#000';
            document.getElementById('focus-desc').textContent = node.description || 'No description';
            document.getElementById('focus-rung').textContent = 'R' + (node.rung || 0);
            document.getElementById('focus-confidence').textContent = (node.nars_confidence || 0).toFixed(2);
            document.getElementById('focus-evidence').textContent = node.evidence_count || 0;
            document.getElementById('focus-frequency').textContent = (node.nars_frequency || 0).toFixed(2);
            document.getElementById('focus-connections').textContent = connectionCount[node.id] || 0;
            
            // Count neighbors
            const neighbors = new Set();
            graphData.links.forEach(l => {{
                if (l.source.id === node.id) neighbors.add(l.target.id || l.target);
                if (l.target.id === node.id) neighbors.add(l.source.id || l.source);
            }});
            document.getElementById('focus-neighbors').textContent = neighbors.size;
            
            // Dim unfocused nodes, highlight connected
            g3d.nodeOpacity(n => {{
                if (n.id === node.id) return 1;
                return neighbors.has(n.id) ? 0.9 : 0.1;
            }});
            
            // Highlight connected links
            g3d.linkOpacity(l => {{
                const src = l.source.id || l.source;
                const tgt = l.target.id || l.target;
                if (src === node.id || tgt === node.id) return 1;
                return 0.05;
            }});
            
            g3d.linkWidth(l => {{
                const src = l.source.id || l.source;
                const tgt = l.target.id || l.target;
                if (src === node.id || tgt === node.id) return Math.max(1, l.weight * 4);
                return 0.3;
            }});
            
            // Animate camera to node
            const distance = 60;
            g3d.cameraPosition({{
                x: (node.x || 0) + distance,
                y: (node.y || 0) + distance / 2,
                z: (node.z || 0) + distance
            }}, node, 1500);
        }}
        
        function unfocusAll() {{
            focusedNodeId = null;
            document.getElementById('focus-panel').classList.remove('visible');
            document.getElementById('hover-panel').classList.remove('visible');
            
            g3d.nodeOpacity(0.85);
            g3d.linkOpacity(0.5);
            g3d.linkWidth(link => Math.max(0.3, link.weight * 2));
        }}
        
        function resetView() {{
            unfocusAll();
            g3d.zoomToFit(1000);
        }}
        
        // Update stats
        document.getElementById('node-count').textContent = graphData.nodes.length;
        document.getElementById('link-count').textContent = graphData.links.length;
        
        // Size selector
        document.getElementById('size-select').addEventListener('change', (e) => {{
            const mode = e.target.value;
            g3d.nodeVal(node => {{
                if (mode === 'evidence') return Math.max(2, Math.sqrt(node.evidence_count || 1) * 2.5);
                if (mode === 'confidence') return Math.max(2, (node.nars_confidence || 0.5) * 15);
                return 5;
            }});
        }});
        
        // Hide loading
        setTimeout(() => {{
            document.getElementById('loading').classList.add('hidden');
            g3d.zoomToFit(1500);
        }}, 500);
    </script>
</body>
</html>'''
    
    return html


async def generate_viz(
    db_url=DEFAULT_DB_URL,
    namespace=DEFAULT_NS,
    database=DEFAULT_DB,
    focus=None,
    depth=2,
    limit=0,
    export_only=False,
):
    """Main function to generate visualization."""
    
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    
    async with GraphVisualizer(db_url, namespace, database) as viz:
        graph_data = await viz.get_full_graph(limit)
        
        if not graph_data.get("nodes"):
            print("No data found in database.")
            return None
        
        # Transform
        transformed = transform_for_3d_force_graph(
            graph_data["nodes"], 
            graph_data["links"]
        )
        
        # Generate version
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        version = "2.0.0"
        
        # Generate HTML
        html_content = generate_html(transformed, version, focus)
        
        # Save
        filename = f"semantic-graph-viz-{version}-{timestamp}.html"
        filepath = ARTIFACTS_DIR / filename
        filepath.write_text(html_content)
        
        # Update latest symlink
        latest_link = ARTIFACTS_DIR / "latest.html"
        if latest_link.exists() or latest_link.is_symlink():
            latest_link.unlink()
        latest_link.symlink_to(filename)
        
        print(f"Generated: {filepath}")
        print(f"Latest: {latest_link}")
        
        return str(filepath)


def main():
    parser = argparse.ArgumentParser(description="Generate 3D semantic graph visualization")
    parser.add_argument("--db", default=DEFAULT_DB_URL)
    parser.add_argument("--ns", default=DEFAULT_NS)
    parser.add_argument("--database", default=DEFAULT_DB)
    parser.add_argument("--focus")
    parser.add_argument("--depth", type=int, default=2)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--export-only", action="store_true")
    
    args = parser.parse_args()
    
    result = asyncio.run(generate_viz(
        db_url=args.db,
        namespace=args.ns,
        database=args.database,
        focus=args.focus,
        depth=args.depth,
        limit=args.limit,
        export_only=args.export_only,
    ))
    
    if result:
        print(f"\\nVisualization: {result}")
    else:
        print("No visualization generated.")


if __name__ == "__main__":
    main()
