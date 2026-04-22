# Formation Coding Language (FCL) — Complete Technical Reference

**Created:** 2026-04-20
**Source:** Vitali's research thread, Genesis session
**Status:** Design brief complete, prototyping stage (Manim)

---

## Core Concept

FCL transmits ideas via spatial + temporal encoding across substrate-independent formations. The formation is not a bitmap — it is a **graph traversal instruction** for a shared knowledge graph. Substrate changes, meaning doesn't.

> "FCL doesn't transmit symbols encoding ideas. It transmits graph traversals." — Vitali

---

## Architecture: 4 Layers

### Layer 0 — Knowledge Graph as Shared Reference Frame
Sender and receiver must share graph structure. If the graph isn't pre-shared, the formation can't decode. This is the foundation — everything else assumes both parties have identical reference structure.

### Layer 1 — Spatial Encoding
- **Nodes** → geometric points (x, y, z in formation space)
- **Edges** → vectors between points (direction + magnitude = causal relation)
- **Geometry** → causal structure: how things move through the graph encodes what they mean

### Layer 2 — Temporal Encoding
- Formation sequences (one shape → next shape over time)
- Pulse encoding (timing of light pulses carries information)
- Morphing (smooth transitions between states)
- L-systems for botanical formations: axiom + rewriting rules = infinite compression of plant-growth patterns

### Layer 3 — Meta-formation (Turing-complete)
Formations about formations. A formation can encode instructions for interpreting another formation. Enables recursion, self-interpretation, bootstrapping.

---

## SDF / Fractal Encoding Breakthrough

**Key insight from session:** formation specified as SDF shader (signed distance function), not point cloud.

```
Transmit: parameters (center, scale, animation_time) + shader text
Receiver: renders at their own resolution (pixel density doesn't matter)
```

**SDF raymarching loop:**
```
start at camera position
step along ray direction
evaluate f(point) — the distance to nearest surface
when |f(point)| < epsilon → hit surface
normal = gradient of SDF at hit point
```

**Boolean operations:** union = min(), intersection = max(), subtraction = max(a, -b)

**Fractal encodings:**
- Mandelbrot: `DE = 0.5 * |z| * log|z| / |dz|` (distance estimator for smooth bailout)
- Julia set: same formula, no +1 in dz update
- Both enable infinite detail at any resolution

**Space-filling curves** (Hilbert, Morton): linearize 2D point clouds while preserving spatial locality — critical for encoding formation point data into transmissible signals.

---

## Substrate Mapping

| Substrate | Precision | Node Count | Key Properties |
|-----------|-----------|------------|-----------------|
| Drone swarms | ±0.5–2cm | 100s–1000s | precise 3D, direct visual, full SDF capable |
| Bird flocks | low | natural | stigmergy (indirect coordination), natural |
| Holographic projections | volumetric | abstract | high bandwidth, visual only |
| Digital screens | 2D | ubiquitous | 2D projection loses depth encoding |

**Key constraint:** digital screen is the worst substrate for FCL because it forces 2D projection, losing the depth dimension that carries causal structure.

---

## Hardware Rendering Spectrum

| Device | Price | SDF Capability | Max Dots |
|--------|-------|----------------|----------|
| ESP32-C6 | $5 | none (CPU only) | 500 |
| Raspberry Pi Zero 2 | $15 | software WebGPU (SwiftShader) | 2K |
| Raspberry Pi 4 | $35 | simple SDF stippling | 20K |
| Jetson Nano | $80 | basic SDF raymarching | 100K |
| Intel Iris Xe NUC | $150 | full SDF raymarching | 500K |
| RTX 3060 | $400 | complex SDF + fractal | 5M |
| RTX 4090 | $1600 | real-time Mandelbulb | 20M+ |

**Crossover point: $80–150** — at this threshold, formation becomes a *function* (shader) not a *bitmap* (point cloud). Below this, you're limited to dot fields.

---

## Drone Swarm Cost Architecture

**Per-node RTK breakdown ($685/unit):**
- Frame + motors + ESC: $150
- LEDs: $30
- Flight controller: $40
- RTK GPS (ZED-F9P): $300
- Comms: $50
- Battery: $15
- Frame assembly: $100

**RTK Base Station (covers 5km):** $800
- ZED-F9P: $250
- Survey antenna: $400
- Enclosure: $100

**Precision vs nodes:**
- ±30cm: 500–2000 dots, simple dot field
- ±10cm: 1000–5000, alphabet glyphs
- ±5cm: 5000–20000, human face/sculpture
- ±2cm: 10000–100000, volumetric SDF (RTK required)
- ±1cm: 50000–500000, fine art
- ±0.5cm: 100000–1000000, fractal detail (RTK + IMU required)

**Intel Shooting Star reference:** 300 drones × $1000 = $300K production system.

---

## FCL vs Traditional Encoding

FCL is not compression. It is **graph traversal instruction**. The receiver doesn't reconstruct a message — they execute a traversal of a shared graph structure. The formation *happens to* them, and they interpret it by following the path.

This is fundamentally different from:
- Morse code (symbol → signal → symbol)
- Fourier encoding (signal decomposition)
- Holographic storage (diffraction pattern → reconstruction)

FCL requires pre-shared graph. Morse doesn't. That's the trade-off — and it's intentional. FCL is for communities that have already built shared structure. Morse is for anyone, anywhere.

---

## Status

- Design: complete
- Prototyping: Manim (Python mathematical animation engine) — define graph as mobjects, animate, render, validate encoding before hardware deployment
- Next: prototype SDF formation renderer on available hardware (Pi 4 target for first real-time test)
- Open: bootstrap problem — how do you first share the graph if FCL requires pre-shared graph?

---

**Tags:** #FCL #formation-coding #swarm-communication #spatial-encoding #SDF #fractals #drone-swarms #substrate-independent #graph-traversal