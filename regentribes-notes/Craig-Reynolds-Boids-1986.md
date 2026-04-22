# Craig Reynolds / Boids (1986) — Emergent Coordination from Local Rules

**Created:** 2026-04-20
**Source:** Vitali's research thread, Genesis session

---

## The Discovery

Craig Reynolds created boids in 1986 as a crowd simulation algorithm. Three rules only:

1. **Separation** — steer to avoid crowding local flockmates
2. **Alignment** — steer toward average heading of local flockmates
3. **Cohesion** — steer toward average position of local flockmates

That's it. No central controller. No master plan. The flock emerges from the local geometry of these rules.

---

## Why It Matters

**Coordination can be purely structural.** The emergent behavior is a consequence of local rule geometry, not explicit planning. This is the foundational insight for swarm intelligence — it demonstrates that complex coordinated behavior doesn't require a coordinator.

This changed:
- **VFX/crowd simulation:** Hollywood used it for The Lord of the Rings, every crowd scene since
- **Swarm robotics:** the entire field of drone swarm coordination traces back to this
- **Game AI:** NPCs following local rules produce emergent group behavior that looks alive

---

## Key Properties Demonstrated

1. **Continuous simulation** — no discrete events, just continuous rule evaluation
2. **Emergent system debugging** — you can't debug the behavior directly, only the rules
3. **Parameter sensitivity** — small changes to rule weights produce dramatically different behavior
4. **Validation without ground truth** — there's no "correct" flock shape to compare against, only criteria like "looks natural" or "doesn't collide"

---

## Connection to FCL

FCL (Formation Coding Language) is the inverse of boids. Boids: local rules → emergent global formation. FCL: desired global formation → distributed local instructions that produce it.

Both are about eliminating the central controller. Boids showed how emergence works. FCL asks: can we encode the *target formation* as a set of local constraints and let the formation self-assemble?

The answer is yes — which is exactly why drone swarms using FCL can be substrate-independent. The formation doesn't need a choreographer; it needs shared graph structure and local rules.

---

## Historical Note

Reynolds' original 1986 paper is still taught because the demo is so clean. You can implement boids in 50 lines of code and immediately see the phenomenon. The simplicity of the rules is the point — complexity is not designed, it emerges.

---

**Tags:** #boids #CraigReynolds #emergent-coordination #swarm-intelligence #local-rules #FCL #flocking