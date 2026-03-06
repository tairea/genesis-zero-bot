# SPEC.md — Extraction Tool Evaluation

## Objective
Evaluate extraction tools for converting unstructured text into structured entities/relations.

---

## Scope
- langextract-rs (Rust)
- xtr (Rust)
- DSPy (Python) / DSRs (Rust)

---

## Evaluation Criteria

### Must Have
- [ ] Entity precision > 0.85
- [ ] Relation precision > 0.80
- [ ] Source alignment > 0.90
- [ ] Latency p95 < 2s

### Should Have
- [ ] Multi-pass extraction
- [ ] Cost < $0.01 per message

---

## Alternative Implementations

### Option A: langextract-rs
Rust library with LLM-based extraction, character-level alignment, schema validation.

### Option B: xtr
GEPA-based prompt optimization, schema-driven extraction, multi-model fallback.

### Option C: DSRs
DSPy Rust rewrite, signature-based modules, performance-centered.

---

## Timeline
- Week 1: Setup + test data
- Week 2: Run evaluation
- Week 3: Analyze results
- Week 4: Document and finalize
