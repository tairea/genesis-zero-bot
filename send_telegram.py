#!/usr/bin/env python3
import json
import subprocess

# Get bot token
result = subprocess.run(
    ["jq", "-r", ".channels.telegram.accounts.genesis.botToken",
     "/home/ian/.openclaw/openclaw.json"],
    capture_output=True, text=True
)
BOT_TOKEN = result.stdout.strip()
CHAT_ID = "-1001921904187"
THREAD_ID = 1958

def send_message(text, chunk_num=0):
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "message_thread_id": THREAD_ID,
        "link_preview_options": {"is_disabled": True}
    }
    result = subprocess.run(
        ["curl", "-s", "-X", "POST",
         f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
         "-H", "Content-Type: application/json",
         "-d", json.dumps(payload)],
        capture_output=True, text=True
    )
    print(f"Chunk {chunk_num}: {result.stdout}")

# Chunk 1: Header + BIM Tooling
msg1 = """👤 <b>LOUISTRUE — FULL PROFILE</b>

<b>Louis True</b> — Swiss developer at the intersection of BIM, sustainability, embedded systems, and AI.

<b>Focus:</b> Open-source BIM tools · Life Cycle Assessment (LCA) · Swiss cadastre/zoning · AI/ML on edge devices · Embedded Rust

<b>License:</b> Mostly Apache-2.0 or AGPL-3.0 · <b>Lang:</b> TypeScript/Python/Rust/C++

🏗️ <b>BIM / IFC TOOLING</b>

<b>ifc5cad ⭐ 11 (AGPL-3.0)</b>
Full browser-based 3D CAD for authoring IFC5/IFCX building models.
<b>Stack:</b> TypeScript + Three.js + OpenCascade (WASM) + Rspack
<b>16 packages:</b> chili-core, chili, chili-three, chili-wasm, chili-ui, chili-geo, chili-vis, chili-i18n, chili-storage, ifcx-core, ifcx-schemas + more
<b>Features:</b> 2D sketching (lines, arcs, circles, ellipses, rects, polygons, Bézier curves) · 3D (boxes, cylinders, cones, spheres, pyramids) · Boolean ops · Advanced (extrusion, revolution, sweep, loft, offset, sections) · Editing (chamfer, fillet, trim, break, split, move, rotate, mirror) · Object snapping · IFCX export · Swiss BIM (SIA 416, eBKP-H, KBOB LCA)

<b>ifc-lite — WebGPU BIM Viewer</b>
Lightweight WebGPU-based IFC viewer. Loads IFC files directly in browser. AGPL-3.0.

<b>ifc-data-browser ⭐ 10 (AGPL-3.0)</b>
Browse and query IFC building models as SQLite databases — 100% client-side. IFC → SQLite conversion in-browser · Table browser · Entity inspector · Custom SQL queries · Privacy: zero bytes uploaded

<b>ifc-flow ⭐ 5 (AGPL-3.0)</b>
Drag-and-drop workflow for IFC data manipulation. 15+ node types. Stack: Next.js + React Flow + Pyodide (IfcOpenShell WASM).

<b>ifcclash ⭐ 4 (AGPL-3.0)</b>
Detect geometric conflicts in building models. REST API + React 3D viewer.

<b>ifc-site ⭐ 3 (AGPL-3.0)</b>
Convert Swiss cadastral parcels into georeferenced 3D IFC models.
<b>Data:</b> geo.admin.ch APIs · CityGML (LOD2) · swissTLM3D · SWISSIMAGE
<b>Output:</b> IFC4 (EPSG:2056) + GLB

<b>model-checker ⭐ 3 (Apache-2.0)</b>
Web-based IFC validator with IDS validation, BCF export, multi-language (EN/DE/FR/IT/RM).

<b>ids-flow ⭐ 3 (AGPL-3.0)</b>
Visual drag-and-drop editor for buildingSMART IDS. Real-time validation via IfcTester-Service API."""

msg2 = """<i>(continued)</i>

<b>ifc-rules-demo ⭐ 2 (Apache-2.0)</b>
Query IFC elements by semantic rules instead of GUIDs. JSON rules → express IDs.

<b>ifc-view-gen ⭐ 3 (AGPL-3.0)</b>
2D technical drawings from IFC with camera presets, section planes, SVG export, door swing arc viz.

<b>ifc-classifier</b>
Visual editor for IFC element classification systems.

🌱 <b>ENVIRONMENTAL / LCA</b>

<b>llm-lca-material-match ⭐ 4 (Apache-2.0)</b>
Match IFC building materials to LCA databases using hybrid embedding + LLM reranking.
<b>The problem:</b> BIM models use noisy, multilingual material names (e.g. "_Beton_C30-37_wg") matched to KBOB or ÖKOBAUDAT for embodied carbon.
<b>5-stage pipeline:</b> Preprocessing · Embedding (BGE-M3) · Retrieval · LLM Reranking · Hybrid retrieve-then-rerank
<b>Benchmark (56 test cases, 7 IFC files, 3 languages):</b>
• Baseline: 29% (KBOB) / 7% (ÖKOBAUDAT)
• + Embedding + preprocessing: 50% / 88%
• + LLM reranking: 54%

<b>lignum-dpp-bsdd ⭐ 2 (AGPL-3.0)</b>
Digital Product Passports in IFC using buildingSMART Data Dictionary.
<b>Demo:</b> bsdd-dpp.dev (100% client-side)
<b>EU standards:</b> prEN 18216–18223 + ISO 22057:2022
Whole-building LCA tool: Upload IFC → configure EN 15804+A2 modules → environmental impact results.

<b>swiss-zoning-api ⭐ 1 (AGPL-3.0)</b>
API for Swiss zoning codes, building regulations, cadastral data.
<b>Features:</b> Address geocoding · EGRID parcel data · Zoning codes · Building params (max height, FAR, setbacks) · ÖREB restrictions"""

msg3 = """🐦 <b>AI / EMBEDDED</b>

<b>birdwatch-ai ⭐ 2 (AGPL-3.0)</b>
Hybrid AI bird identification on Raspberry Pi 5.
<b>Pipeline:</b> Camera (RTSP) → YOLOv8m → MobileNet V2 → Fusion ← BirdNET v2.4 (Hailo-8 NPU, 26 TOPS)
Visual: 30 FPS → YOLOv8 detection (33ms) → TFLite species classification (70ms)
Audio: BirdNET 1.2s every 3 seconds.
<b>Hardware:</b> RPi 5 4GB+ · Hailo AI HAT+ · IP camera 1080p RTSP · USB mic 48kHz
<b>Use:</b> Biodiversity monitoring for regenerative land management.

<b>family-calendar ⭐ 1 (AGPL-3.0)</b>
Multi-calendar aggregator with touchscreen display (ESP32 or Raspberry Pi).
4 calendars · 3 views (Day/Week/Month) · Touch navigation · Auto-refresh.
ESP32: Makerfabs MaTouch ESP32-S3 7" via PlatformIO + LVGL.
Pi: Next.js API on Vercel + browser kiosk.

<b>T-Display-S3-Long ⭐ 1 (MIT)</b>
LVGL examples for LilyGo T-Display-S3-Long (ESP32-S3 + 180×640 touch display).

🛠️ <b>DEVELOPER TOOLS</b>

<b>gh-describer ⭐ 1 (MIT)</b>
Auto-generate GitHub repository descriptions using AI.
Multi-LLM comparison (GPT-4, Claude Sonnet, Gemini) · Deep repo analysis · Batch processing."""

msg4 = """📊 <b>PROJECT MAP</b>

<b>ifc5cad ⭐ 11</b> Browser 3D CAD (IFC5) · AGPL-3.0
<b>ifc-data-browser ⭐ 10</b> IFC → SQLite browser · AGPL-3.0
<b>llm-lca-material-match ⭐ 4</b> IFC → LCA matching · Apache-2.0
<b>ifcclash ⭐ 4</b> BIM clash detection · AGPL-3.0
<b>ifc-flow ⭐ 5</b> Visual IFC workflow · AGPL-3.0
<b>model-checker ⭐ 3</b> IFC validator (IDS) · Apache-2.0
<b>ifc-view-gen ⭐ 3</b> 2D drawings from IFC · AGPL-3.0
<b>ifc-site ⭐ 3</b> Swiss cadastre → IFC · AGPL-3.0
<b>ids-flow ⭐ 3</b> Visual IDS editor · AGPL-3.0
<b>lignum-dpp-bsdd ⭐ 2</b> Digital Product Passports in IFC · AGPL-3.0
<b>birdwatch-ai ⭐ 2</b> AI bird ID (RPi + Hailo) · AGPL-3.0
<b>ifc-rules-demo ⭐ 2</b> Semantic IFC querying · Apache-2.0
<b>swiss-zoning-api ⭐ 1</b> Swiss zoning API · AGPL-3.0
<b>family-calendar ⭐ 1</b> Multi-calendar touchscreen · AGPL-3.0
<b>gh-describer ⭐ 1</b> AI GitHub describer · MIT
<b>llm-lca-demo ⭐ 1</b> LLM + LCA demo · MPL-2.0
<b>T-Display-S3-Long ⭐ 1</b> ESP32-S3 LVGL examples · MIT

🌱 <b>REGEN TECH ANGLE</b>

Louis bridges built environment + ecology + open hardware:

🌿 <b>Biodiversity:</b> birdwatch-ai automates species tracking on RPi+Hailo, cross-referenced visual+audio AI

🏗️ <b>Sustainable construction:</b> llm-lca-material-match bridges BIM → LCA → embodied carbon. lignum-dpp-bsdd handles Digital Product Passports (EU regulatory wave). ifc-site enables cadastre → BIM for land use planning.

📋 <b>Land governance:</b> swiss-zoning-api surfaces building params, FAR, setbacks, ÖREB restrictions

🔧 <b>Open hardware:</b> family-calendar, T-Display-S3-Long, RPi 5 + Hailo AI HAT+

<blockquote>Regenerative neighborhoods need to track both natural systems (biodiversity, water, carbon) AND built systems (buildings, materials, energy). Louis's tooling bridges BIM (built) with LCA/environmental databases (impact) — the missing link for true regenerative design.</blockquote>

<a href="https://github.com/louistrue">github.com/louistrue</a> · Swiss-based"""

send_message(msg1, 1)
import time
time.sleep(1)
send_message(msg2, 2)
time.sleep(1)
send_message(msg3, 3)
time.sleep(1)
send_message(msg4, 4)
