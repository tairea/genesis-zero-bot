# Ben Goertzel — Three Gaps in Current ML Learning

**Created:** 2026-04-20
**Source:** Vitali's research thread, Genesis session

---

## The Three Gaps

Current neural networks fail at three kinds of learning that humans do effortlessly:

### 1. Continual Learning
Humans learn without forgetting. You learn a new language and you don't lose your ability to walk. Current neural nets experience **catastrophic forgetting** — learning new information overwrites old information completely.

**Why it matters for regen communities:** If an AI system helping manage a farm learns new irrigation techniques, it currently can't do that without risking the agricultural knowledge it already had. Every update is a full replacement, not an addition.

### 2. Transfer Learning
Humans leap out-of-distribution. You understand a new situation by relating it to completely different experiences. LLMs *appear* to transfer, but in reality they just saw both domains in their training data. The "transfer" is retrieval, not reasoning.

**The distinction:** If you trained on all of Wikipedia and then solved a math problem, did you transfer knowledge or just recall? Current ML does the latter. Real transfer would work even on problems whose answer wasn't in any training data.

### 3. Developmental/Lifeless Learning
Humans restructure *how they represent knowledge* over a lifetime. You don't just add facts — you change the framework the facts fit into. Your concept of "time" at age 5 is different from age 30, not just fuller. Current neural networks don't do this restructuring. They add layers but don't change the representational structure.

---

## The Architecture Fix

Goertzel's analysis points to a specific architectural need:

- **Neural nets** for perception (vision, audio, raw data)
- **Symbolic/logic systems** for reasoning (planning, constraint satisfaction)
- **Knowledge graph** as the unified representation layer that both can interface with

This is the Hyperon/Atomspace architecture — programs as subgraphs in a hypergraph, with PLN (Probabilistic Logic Networks) doing reasoning on top.

**Alternative approaches:**
- Predictive coding (different from backpropagation)
- Causal coding (instead of statistical correlation)

---

## Why This Is Hard

Logic systems scale well to reasoning but not to perceptual data. Neural nets handle perception but don't scale to reasoning. Hybrid systems are architecturally correct but operationally complex — you need two working systems that can talk to each other, and debugging is harder because failures can happen in either component.

---

## Connection to Regen Community Design

A regenerative community needs an AI system that:
- Continually learns new local conditions (soil, water, weather) without forgetting previous years
- Transfers insights across completely different problem domains (water management → food forest design → energy systems)
- Restructures its knowledge representation as the community grows and evolves

None of this is possible with current LLMs alone. It requires the hybrid architecture Goertzel describes.

---

**Tags:** #BenGoertzel #continual-learning #transfer-learning #developmental-learning #Hyperon #Atomspace #hybrid-architecture #PLN