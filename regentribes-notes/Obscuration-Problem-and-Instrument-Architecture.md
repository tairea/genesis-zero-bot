# Obscuration Problem & Instrument Architecture

**Created:** 2026-04-20
**Source:** Vitali's research thread, Genesis session

---

## The Problem

Claude Code, Goose, Kilo Code, OpenAI Codex — **all hide what they actually sent to the model**.

This is a business decision, not a missing feature. The product is designed to create dependency through opacity. If you can't see the prompt, you can't reproduce the result, you can't move to a competitor, you can't audit what was done.

**Consequence:** You are building on an oracle you cannot inspect.

---

## Oracle Pattern vs Instrument Pattern

| | Oracle | Instrument |
|---|---|---|
| **Flow** | Ask → Decide → Receive | Specify → Propose → Approve → Verify |
| **User role** | Consumer | Architect |
| **Auditability** | None | Full |
| **Dependency** | Locked in | Portable |
| **Market** | Saturated | Empty |

The market for oracles is saturated. Every AI coding tool is an oracle. You ask, it decides, it returns.

The market for **instruments** is empty. Nobody makes tools where you specify the constraint, the LLM proposes, you approve, it executes, you verify. That is what a good instrument looks like.

Pi (pi.dev, Mario Goul) is the only serious attempt at instrument architecture: minimal core (while loop + tool calling), 4 tools only (retreat, edit, mesh), self-modifying via TypeScript extensions hot-reloaded during session.

---

## Why Oracle Dominates

1. **Lock-in:** If you can't see the prompt, you can't reproduce it elsewhere
2. **Blame deflection:** When oracle fails, it's "the model's fault" not "your tool's fault"
3. **Revenue:** Oracles are subscription products. Instruments are dev tools (lower margin)

---

## What an Instrument Looks Like

- Every prompt you send is a file you can read
- Every model response is a diff you can accept/reject line by line
- The tool chains tool calls into a trace you can replay
- No popup on every action — security is built for your specific use case (YOL = Your Own Leash)
- The spec is the artifact. Code is expendable.

---

## Zero Trust Implication

For correctness-critical work: any agent that cannot be audited at every step cannot be trusted with real work. The audit trail IS the definition of trustworthy. No component trusted by default. All inference steps, tool calls, context retrievals must be verifiable.

This applies to human verification too: if you can't see what the AI did, you can't verify it. Verification requires visibility.

---

**Tags:** #obscuration #instrument-pattern #oracle-pattern #zero-trust #pi #MarioGoul #auditability