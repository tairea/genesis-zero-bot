# Research Prompt 03: Bridge Between Values Work and Structural Design

## Context

LJMap operates on the individual/group level — stakeholder values, Field of Meaning, Share Meaning Score. Avancier operates on the enterprise level — BDAT domains, architecture decisions, governance. These are parallel universes with no bridge between them. Values mapping tells you what people care about. Architecture design determines what systems people operate within. Causality is contested: does values drive structure, or structure drives values?

## Research Questions

### Core Problem
Build a traceable, operational connection between "what people in a community care about" and "how the community's systems and structures are designed." No existing framework does this.

### Specific Investigations

**Q1: What is the actual direction of causality between values and structure?**
- Literature: structuration theory (Giddens), activity theory (Leontiev), cultural-historical activity theory, critical realism
- Find: NOT "it goes both ways" — a specific mechanism. Under what conditions does values-change precede structure-change, and under what conditions does structure-change precede values-change?
- Deliverable: A DECISION TREE for which comes first in a given community context

**Q2: How do you make governance decisions values-transparent?**
- Avancier: ADRs (Architecture Decision Records) document decisions. But they don't document which values were privileged in the decision and which were marginalized.
- Research: value-sensitive design (Friedman), accountable algorithms, ethics in enterprise architecture, participatory design
- Find: A method for tagging governance decisions with the values in tension
- Deliverable: ADR TEMPLATE WITH VALUES TRACKING — every architecture decision record includes: which stakeholder values were in play, which won, which lost, what the dissent was

**Q3: How do you model conflict as values collision rather than technical disagreement?**
- Avancier treats conflict as "EA is political" — a friction to be managed
- LJMap has Share Meaning Score — can measure alignment between people
- Research: agonistic pluralism (Mouffe), conflict transformation, deep democracy (Isaacs), circle processes
- Find: A STRUCTURED CONFLICT PROTOCOL — when community conflict arises, a process for surfacing the values collision underneath, rather than negotiating technical compromise

**Q4: What is the appropriate lifespan of a structural decision relative to the values that motivated it?**
- Some decisions need to be permanent (physical infrastructure). Some should be provisional (organizational roles). Some should be disposable (policies that can be revised).
- Research: organizational memory (Walsh & Ungson), decision lifecycle management, architecture governance
- Find: A framework for distinguishing between structural decisions that should be sticky vs. those that should be loose
- Deliverable: DECISION PERSISTENCE CRITERIA — questions that determine how long a governance or architectural decision should hold before being revisable

**Q5: How does the coaching relationship and the architecture process share the same structure?**
- LJMap: coaching is a dialogic encounter where meaning is negotiated
- Avancier: architecture workshops are dialogic encounters where system design is negotiated
- Both: the facilitator/coach and the participant are mutually transformed by the encounter
- Research: dialogic organization development (Anderson & Goolishian), interactional coaching (Stober & Grant), large group intervention methods
- Find: The shared structure that makes coaching and architecture governance the SAME PHENOMENON at different scales
- Deliverable: A UNIFIED FACILITATION FRAMEWORK — one set of principles that governs both values coaching and architecture design conversations

## Deliverables

1. **Values-Structure Causality Decision Tree** — When to lead with values work, when to lead with structural change
2. **ADR Template with Values Tracking** — Architecture Decision Record extended with values provenance
3. **Structured Conflict Protocol** — Process for surfacing values collisions in community conflict
4. **Decision Persistence Criteria** — Framework for how long structural decisions should hold
5. **Unified Facilitation Framework** — One set of principles for coaching and architecture conversations

## Execution Instructions

This is the most politically loaded research area. Values-architecture bridges are never neutral — they determine whose values get embedded in systems. Maintain explicit awareness of power dynamics throughout. Do not produce a technical solution that pretends to be apolitical.