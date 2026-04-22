# Inverse Architecture for Correctness-Critical Domains

**Created:** 2026-04-20
**Source:** Vitali's research thread, Zero Trust section

---

## The Core Problem

Generative AI is the wrong tool for domains where correctness matters more than fluency. Medical, legal, financial, safety-critical — generation hallucinations are not acceptable. Yet these are exactly the domains where people try to deploy LLMs most aggressively.

## The Formal Alternative

Three-part architecture:

1. **Explicit knowledge base** — every fact has provenance, every inference is logged. You can trace any output back to its source and verify it independently.

2. **Rule execution, not generation** — problems are formulated as constraint satisfaction (not text generation). The system either finds a solution or reports visible failure. No confabulation.

3. **LLMs as perception only** — used exclusively for OCR, parsing, document extraction. Never making decisions. Never asserting facts directly.

## Tooling

| Approach | Tool | Use Case |
|----------|------|----------|
| Answer Set Programming | Clingo | Constraint satisfaction, planning |
| SAT/SMT solvers | z3, CVC5 | Formal verification, combinatorial problems |
| Formal methods | TLA+, Coq | System specification, correctness proofs |

## Why This Is Hard

LLMs are good at fluent text. Fluency looks like correctness but isn't. In domains where you need correctness, fluent confabulation is more dangerous than explicit ignorance.

The inverse architecture separates: fluency (LLM) from correctness (formal methods). This is architecturally honest but operationally complex — you need two systems instead of one, and they need to be integrated carefully.

## When Generation Is Acceptable

If the output can be cheaply verified and the cost of error is low, generation is fine. Code in a testable codebase (where tests run in 30 seconds) is a reasonable generation target. Code in a medical device (where tests can't fully validate safety) is not.

---

**Tags:** #inverse-architecture #formal-methods #correctness-critical #z3 #clingo #TLA+ #llm-limitations