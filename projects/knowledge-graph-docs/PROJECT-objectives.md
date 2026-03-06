# Project Overview

**Name:** RegenTribes Knowledge Graph & AI Brain
**Vision:** Transform RegenTribes community knowledge into a queryable, visualizable intelligence system
**Classification:** Safety-critical

---

## Core Objectives

### 1. Knowledge Capture & Structuring
Transform raw inputs (Telegram, Miro, Drive) into structured entities and relations.

### 2. Semantic Understanding
Implement the 4-stage understanding algorithm:
- Stage 1 → Literal Stripping (flag ambiguity)
- Stage 2 → Multi-meaning Expansion (all possibilities)
- Stage 3 → Chain Formation (connect interpretations)
- Stage 4 → Memory Validation (filter against existing knowledge)

### 3. Knowledge Graph Operations
- Graph traversal <50ms (p95)
- Vector similarity search (recall @10 >0.90)
- Hybrid queries <200ms (p95)
- RDF export via SPARQL

### 4. Intelligence Visualization
- 3D force graph rendering
- 10,000+ nodes @ 30fps
- Interactive navigation

### 5. Security & Resilience
- Zero-trust architecture
- RBAC + audit logging
- Input sanitization

---

## Information Pipeline

```
RAW INPUTS → INGESTION → EXTRACTION → MEANING → VALIDATION → KG
                                    (4-stage)                │
                        ┌────────────────┴────────────────┐   │
                        ▼                                 ▼
                  RAG QUERIES                   3D VISUALIZATION
```

---

## Success Criteria

| Metric | Target |
|--------|--------|
| Entity extraction F1 | >0.85 |
| Relation extraction F1 | >0.80 |
| Query latency (p95) | <200ms |
| Visualization (10k nodes) | 30+ FPS |

---

## Recommended Stack
```
Kreuzberg → langextract-rs → 4-Stage → SurrealDB + Oxigraph → Three.js
```
