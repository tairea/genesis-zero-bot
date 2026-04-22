# Resource Ecosystem — Complete Self-Taught Stack

**Created:** 2026-04-20
**Source:** Vitali's research thread, Genesis session

---

## Why This Matters

A complete self-taught path from zero to research-level knowledge in the domains required for FCL, simulation, and regenerative systems design. This is the educational backbone for someone who wants to understand AI, physics, control systems, and formal methods without going through university.

---

## The Complete Path

### Graphics / Rendering
1. **Ray Tracing in a Weekend** (Peter Shirley) — entry point, complete working ray tracer in a weekend
2. **PBRT** (Physically Based Rendering) — the rigorous textbook
3. **NVIDIA RTR research** — stay current with real-time rendering advances

### Mathematics
1. **Khan Academy** — foundation building
2. **3Blue1Brown** (Grant Sanderson) — develop intuition for linear algebra, calculus, neural networks
3. **Gilbert Strang 18.06** (MIT OpenCourseWare) — linear algebra at university depth
4. **ULAFF** (Urban Lab for Linear Algebra) — complementary to Strang
5. **Harvard Stat 110** — probability theory (Joe Blitzstein)
6. **Boyd Convex Optimization** — Stanford EE364a, the math of optimization problems

### Physics
1. **Physicsgraph AP Physics 1** — high school physics foundation
2. **MIT 18.01** (Calculus I) — single variable
3. **MIT 18.02** (Calculus II) — multivariable
4. **MIT 18.03** (Differential Equations) — the language of physical systems

### Computer Science Theory
1. **Levin Discrete Math** (榆) — introduction via algorithmic lens
2. **CLRS** (Cormen, Leiserson, Rivest, Stein) — the algorithms bible
3. **O'Donnell Complexity** (CMSC 451) — computational complexity
4. **Sipser Theory of Computation** — formal languages, automata
5. **Software Foundations** (Coq) — verified programming, functional correctness

### Control Systems
1. **Åstrøm Feedback Systems** — the control theory bible
2. **Brian Douglas YouTube** — intuitive control theory explanations
3. **Eigensteve** — state-space control, observer design
4. **Brunton Data-Driven Control** — machine learning meets control

### Formal Methods
1. **TLA+ Hyperbook** (Leslie Lamport) — formal specification
2. **Learn TLA+** (Hillel Wayne) — practical TLA+
3. **Coq Software Foundations** — proof assistants

### Complexity Science
1. **Santa Fe Institute Complexity Explorer** — complexity theory introduction
2. **Strogatz** — nonlinear dynamics and chaos
3. **Wolfram Physics** — computational physics program

### Machine Learning / AI
1. **Goodfellow Deep Learning** — the Deep Learning book (the "ianzag book")
2. **Fast.ai** — practical deep learning, top-down learning
3. **Stanford CS229** — machine learning (Andrew Ng)
4. **Deep-ML.com** — advanced topics

### Natural Language Processing
1. **Stanford CS224N** — deep learning for NLP
2. **Hugging Face Course** — practical transformers

### Procedural Graphics
1. **Scratchapixel** — rendering and math foundations
2. **Inigo Quilez blog** — SDF, rendering, signed distance functions (essential for FCL)
3. **Sebastian Lague YouTube** — procedural generation, coding challenges
4. **Kurt Kuehnert YouTube** — creative coding, shader art

### Animation / FCL Prototyping
1. **Manim (3blue1brown/manim)** — mathematical animation engine
   - Everything is a mobject (VMobject, FunctionGraph, ParametricCurve, etc.)
   - LaTeX integration for equations
   - Animation system: play(write), play(transform), wait
   - Camera can be animated (pan, zoom, rotate)
   - Slow render — not real-time
   - Use case: prototype FCL formations — define graph as mobjects, animate, render, validate encoding before hardware deployment

---

## How This Connects to FCL

The FCL pipeline requires:
- **Geometry/algebra** for spatial encoding (Strang 18.06 + Boyd)
- **SDF rendering** (Inigo Quilez + Scratchapixel)
- **Control systems** for swarm dynamics (Åstrøm + Brian Douglas)
- **Formal methods** for graph encoding correctness (TLA+)
- **Complexity science** for emergence analysis (SFI + Strogatz)
- **Animation** for encoding validation (Manim)

This stack is not decorative. Every part is load-bearing for FCL development.

---

**Tags:** #self-taught #education #FCL #graphics #control-systems #formal-methods #ML #Manim