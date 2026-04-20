# Radial — Open Regenerative Construction System
## Full Trajectory Map & Gap Analysis

---

## 1. Core Design Philosophy (Stated)

**Problem:** ICON Titan solves "cheaper buildings for sale." It creates dependency on proprietary material, software, and supply chain.

**Solution:** Radial solves "community-owned construction sovereignty." Every component is fab-able, repairable, and improvable by the community that uses it.

**Design axioms:**
- No dependency on systems you don't own
- Material choices driven by local abundance, not global supply chain
- Software must be inspectable, modifiable, reproducible by anyone with basic skills
- The machine should outlast any single manufacturer
- Regeneration is the output — carbon-negative walls, water harvesting, thermal mass

---

## 2. Trajectory Map

### 2.1 Technical Trajectories

#### 2.1.1 Motion System Variants

**Baseline (Gantry):**
- Bolted steel tube frame (S235JR structural steel)
- NEMA 34 stepper motors, closed-loop with rotary encoders
- Rack and pinion for X/Y, lead screw for Z
- Print volume: 12m × 12m × 4m (adjustable via modular frame additions)
- Cost target: $18-25k for motion system alone

**Variant A — Radial Arm (for tight sites):**
- Rotating arm on central mast (like a tower crane)
- Reduces footprint by 60% on small lots
- Print radius limited to 8m from center
- Higher complexity in arm structural analysis

**Variant B — Suspended (for uneven terrain):**
- Print head suspended from overhead gantry (no floor contact)
- Ideal for hillside construction, flood-prone areas
- Requires site-built support towers ( timber or steel)
- Cost: similar to baseline, but terrain adaptability higher

**Variant C — Mobile Platform:**
- Self-propelled tracked platform
- Can print foundations and slabs before setting walls
- Hydraulic outriggers with auto-leveling
- Adds $8-12k and significant complexity

**Gap identified:** Which variant for which site type needs a decision matrix. None exists.

#### 2.1.2 Material Science Trajectories

**The core moat.** Titan's lavaite is proprietary. The question isn't "what's the proprietary mix" — it's "what can any community make from local inputs?"

**Pozzolan spectrum (viable local binders):**

| Source | Location | Binder Efficiency | Cost | Notes |
|---|---|---|---|---|
| Volcanic ash | Volcanic regions | High | Very low | Best performance, nearly free in many regions |
| Rice husk ash | Southeast Asia, California | Medium-high | Low | Requires controlled burning (550°C) |
| Fly ash | Coal plant proximity | High | Very low | Waste stream; availability declining |
| Meta-kaolin | Refined from kaolin clay | Very high | Medium | Requires processing; not truly local |
| GGBS (ground granulated blast furnace slag) | Steel mills | High | Low | Waste stream |
| Biomass ash | Wood stoves, agriculture | Low-medium | Very low | Highly variable; requires testing |
| Calcined clay | Broadly available | Medium-high | Medium | Requires kiln to 800°C |

**Aggregate spectrum:**

| Type | Source | Structural | Insulation | Notes |
|---|---|---|---|---|
| Crushed granite | Quarry waste | ✓ | | High compressive strength |
| Volcanic pumice | Volcanic regions | ✓ | ✓ | Lightweight, insulating |
| Recycled concrete | Demolition | ✓ | | Must be crushed + sorted |
| Expanded perlite | Volcanic glass | | ✓ | High insulation, low strength |
| Hemp hurd | Agricultural waste | | ✓ | Carbon negative, breathable |
| Bio-char | Pyrolysis | | ✓ | Carbon sequestration + insulation |
| Glass cullet | Recycling | ✓ | | Requires sorting by color |

**Gap identified:** No comprehensive field testing protocol exists for community-level material characterization. Need a standardized 7-day test that any community can run with $200 in equipment.

**The mix design math:**
- Target compressive strength: 40 MPa (structural), 5 MPa (insulation layer)
- Water-to-binder ratio: 0.35-0.45 (too wet = weak, too dry = poor adhesion)
- Aggregate-to-binder ratio: 3:1 to 6:1 depending on aggregate type
- Workability: measured by slump test, adjusted with plasticizers (natural options: citrus peel oil, pine resin)

**Critical gap — rheology control:**
Concrete printing requires the material to be non-Newtonian: it must flow under pressure but hold shape when extruded. This is achieved through:
- Viscosity modifiers (natural: cellulose, starch)
- Thixotropy agents (natural: bentonite clay)
- Set acceleration (natural: sugar, vinegar — delays set; calcium nitrate — accelerates)

#### 2.1.3 Electronics & Control

**Baseline:**
- STM32H7 main controller (480MHz, real-time capable)
- DRV8711 stepper drivers (or TMC5161 for silence)
- Raspberry Pi 5 as host (runs toolpath engine)
- All KiCad files open source
- Estimated controller cost: $350 for 3-axis system

**Variant A — Full Offline:**
- All toolpaths on SD card
- No network capability at all
- Paranoid security model
- Limitation: toolpath files must be generated elsewhere

**Variant B — Mesh Network:**
- ESP-NOW protocol for multi-machine coordination
- Enables 3-4 printers working on one building simultaneously
- Low bandwidth, no internet dependency
- Range: 1km line-of-sight with external antenna

**Variant C — Solar + Battery:**
- 48V bus from 4× 200W panels
- 2× repurposed EV battery modules (15kWh total)
- MPPT charge controller (open source: Victron or equivalente)
- Run time: 8 hours full print, 3 days standby

**Gap identified:** No open-source real-time motion controller that handles both stepper + fluid pump synchronization. Currently requires custom firmware (Rust or C). Marlin is too slow for fluid pump coordination.

#### 2.1.4 Software Stack

| Layer | Baseline | Alternative A | Alternative B |
|---|---|---|---|
| Architectural design | FreeCAD + BlenderBIM | Sweet Home 3D | OpenSCAD (parametric) |
| Toolpath generation | Custom Python (based on Cura) | Slic3r fork | PrusaSlicer fork |
| Machine control | Custom Rust firmware | Marlin 2.x + extension | LinuxCNC + FPGA |
| Material profiling | JSON-based profiles | Community wiki database | On-device neural network |
| Monitoring | Local dashboard (Raspberry Pi) | Mobile app (offline-capable) | Web interface (local only) |

**Gap identified:** Toolpath generation for non-Newtonian materials is fundamentally different from FDM/Concrete. Existing slicers assume Newtonian fluid dynamics. A new slicing algorithm is needed.

---

### 2.2 Social & Economic Trajectories

#### 2.2.1 Manufacturing Pathways

**Who fabs what — the distributed manufacturing question:**

| Component | Fab Method | Minimum Equipment | Cost to Set Up | Regional Feasibility |
|---|---|---|---|---|
| Steel frame | Angle grinder + drill + welder | Fab shop or mobile welder | $3-5k tooling | Universal |
| Drive system | Bolt-together purchased parts | None (assembled from kits) | $8-12k kits | Universal via mail-order |
| Print head | Machined aluminum (CNC) | Access to CNC mill | $500 tooling + $2k machine time | Urban areas; shared |
| Electronics | PCB fab + assembly | Soldering station + microscope | $300 tooling | Urban areas; community fab lab |
| Software | Open source development | Developer time | Near zero | Distributed |
| Frame bolts | Off-the-shelf | Hardware store | $200 | Universal |

**Gap identified:** A single community cannot afford to set up all fab capability. The model must be "some communities fab frames, others fab heads, others develop software, all trade."

**The Fab Lab Network trajectory:**
1. Phase 1: 3 pilot communities source from centralized kit (~$40k/community)
2. Phase 2: Pilot communities begin fabbing frames for nearby communities
3. Phase 3: Regional "fab clusters" emerge (5-10 communities sharing specialized equipment)
4. Phase 4: Full distributed manufacturing with no central supply chain

#### 2.2.2 Training & Skill Pathways

**Operator training (2-week intensive):**
- Week 1: Materials science (mix design, testing, rheology)
- Week 2: Machine operation, calibration, basic troubleshooting

**Gap identified:** No training curriculum exists. Must be developed.

**Community skill ladder:**

```
Level 0: Awareness — what is Radial, what can it build
Level 1: Operator — can run machine, change materials, basic maintenance
Level 2: Technician — can diagnose faults, replace modules, recalibrate
Level 3: Mix Designer — can develop local material formulations
Level 4: Fabber — can fabricate frame and print head components
Level 5: Trainer — can teach Levels 0-4
Level 6: Developer — can modify firmware and software stack
```

**Gap identified:** Who trains the trainers? Need a "master trainer" program linking pilot communities.

#### 2.2.3 Business Model Trajectories

**Model A — Cooperative Ownership:**
- Community cooperative owns the machine
- Membership fee + per-build fee
- Revenue covers maintenance, upgrades, training

**Model B — Tool Library:**
- Machine circulates like a library book
- Community pays per-use fee
- Low individual commitment, high coordination cost

**Model C — Construction Cooperative:**
- Machine + operator + technician = construction service
- Community pays for build service
- Operator/technician employed by cooperative
- Enables skill specialization

**Model D — Community Investment:**
- Community bonds or shares sold to fund machine purchase
- Machine owned by community trust
- Builds for any member at cost + maintenance reserve

**Gap identified:** No economic model is proven for community-owned construction equipment at this scale. Need pilot data from 3+ communities over 18 months.

#### 2.2.4 Governance Trajectories

**The commons problem:**
Who decides:
- What gets printed and what doesn't?
- Who gets priority access when multiple communities want builds?
- How upgrades to the design are adopted or rejected?
- How shared fab resources are allocated?

**Governance options:**

**Option A — Federated Cooperative:**
- Each community has one vote in Radial Federation
- Federation sets standards, maintains shared IP
- Local chapters have autonomy on local decisions
- Consensus or 2/3 majority for major decisions

**Option B — Open Source with Trademark Commons:**
- All design files open (AGPL or CC-BY-SA)
- "Radial" trademark licensed royalty-free to communities that meet certification standards
- Certification replaces governance — it's a quality seal, not a governing body
- No collective decision-making; individual community choices

**Option C — Charter Colony Model:**
- Founding communities write a charter defining governance
- Charter includes material commons agreements, dispute resolution
- New communities join by adopting charter
- Governance enforced through mutual dependency (fab supply, training)

**Gap identified:** Governance is the most underspecified trajectory. The choice here shapes everything else. Need a structured decision process.

---

### 2.3 Regenerative Design Trajectories

#### 2.3.1 Carbon Trajectory

**Carbon math:**
- 1m³ lavaite concrete ≈ 300-400 kg CO2 emitted (cement production)
- 1m³ hempcrete ≈ -150 to -300 kg CO2 sequestered (net negative)
- 1m³ rammed earth ≈ 30-50 kg CO2 (minimal cement)
- 1m³ volcanic ash aggregate concrete ≈ 100-150 kg CO2 (low cement, local aggregate)

**Building carbon comparison (200m² single-story home):**
- Titan (lavaite): ~30 tonnes CO2 emitted
- Radial with hempcrete: ~-15 tonnes CO2 (net negative)
- Radial with volcanic aggregate: ~10 tonnes CO2 (90% reduction vs Titan)

**Gap identified:** No standardized carbon accounting for community-built regenerative homes. Need a simple calculator that communities can use before/during/after build.

#### 2.3.2 Water Trajectory

**Print process water use:**
- ~50-80 liters per m³ of concrete printed
- Hempcrete mixing: ~40 liters per m³
- Water recycling system: captures 60-70% of runoff for reuse

**In-use water:**
- Rainwater harvesting integration: roof design includes channeling for water collection
- Greywater filtration: plaster layers can incorporate bio-filter media

**Gap identified:** No integrated design protocol for water management in printed structures. Need plumbing routed through wall cavities.

#### 2.3.3 Thermal Mass Trajectory

**Wall section options:**

```
Option A — Single material (simple):
[=== Concrete/Lavaite 300mm ===]

Option B — Structural + insulation (full thermal):
[=== 150mm structural ===]
[=== 100mm hempcrete insulation ===]
[=== 50mm lime plaster ===]

Option C — Hollow core (material saving):
[=== Outer shell 75mm ===]
[--- Air gap 150mm ---]
[=== Inner shell 75mm ===]
(Fills with vermiculite or bio-char for R-30)
```

**Gap identified:** Multi-material printing requires simultaneous dual-extruder coordination. Current firmware doesn't support it. Highest technical gap.

#### 2.3.4 End-of-Life / Deconstruction

**Titan's buildings:** Permanent. Demolition generates waste.

**Radial's buildings:**
- Structural connections designed for disassembly (bolted, not glued)
- Lime-based mortars are water-soluble (can be soaked and separated)
- Hempcrete is compostable (entire wall can be ground and returned to soil)
- Bio-char infill can be land-applied as soil amendment

**Gap identified:** No deconstruction protocol exists. Need to design for it from day one, not retrofit.

---

### 2.4 Community Deployment Trajectories

#### 2.4.1 Readiness Assessment

**Community readiness criteria:**

| Dimension | Indicators | Assessment Method |
|---|---|---|
| Technical | Has machine shop access; has basic fabrication skills | Survey + site visit |
| Social | Governance structure exists; conflict resolution mechanisms in place | Community inventory |
| Economic | 3+ years operating budget; diverse income streams | Financial review |
| Material | Local aggregate survey; pozzolan source identified | Materials testing |
| Land | Secure land tenure; permits for construction | Legal review |
| Training | At least 2 people committed to Level 4 training | Commitment letters |

**Gap identified:** No readiness assessment tool exists. Need to develop and validate.

#### 2.4.2 Site Preparation Trajectory

**Standard site prep for Radial:**
1. Survey and boundary demarcation
2. Perimeter drainage + footer (standard concrete strip, not printed)
3. Compact and level pad (machine self-levels but substrate must be stable)
4. Temporary power + water hookup (machine has onboard power eventually)
5. Material staging area (aggregate storage, covered)
6. Operator shelter (basic 3-sided structure for control station)

**Timeline:** 2-3 weeks for typical residential lot

**Gap identified:** No site prep manual exists. Standard construction site practices apply but need to be adapted for printed structures.

#### 2.4.3 Pilot Program (First 3 Communities)

**Recommended pilot structure:**
- 3 communities, geographically distributed
- Each receives 1 machine, 2 trained operators, 1 technician
- 18-month pilot with shared learning
- Quarterly "learning exchanges" (site visits + virtual)
- Independent evaluation at month 18

**Success metrics:**
- Builds completed: 3-5 homes per community
- Cost per m² vs local conventional construction
- Operator skill progression
- Material characterization reports from each community
- Machine uptime rate

**Gap identified:** No pilot program design exists. Need funders for 3-machine pilot + evaluation budget.

---

### 2.5 Open Source Governance Trajectories

#### 2.5.1 License Choice

**Option A — AGPL + Commons Clause:**
- AGPL: ensures all modifications to software stay open
- Commons Clause: prevents commercial hosting as a service (like MongoDB)
- Maintains open source but limits competition from commercial brokers
- **Recommended starting point**

**Option B — CC-BY-SA 4.0 for documentation + hardware:**
- Hardware designs, manuals, training materials under CC-BY-SA
- Allows commercial use as long as attribution + share-alike
- Software under AGPL

**Option C — Public Domain (unlicense):**
- Maximum adoption potential
- No protection against capture
- Not recommended for this project

#### 2.5.2 Trademark Strategy

**"Radial" trademark held by foundation:**
- Anyone using "Radial" in good standing gets royalty-free license
- Certification requirements: meet build standards, contribute back improvements
- Losing certification: must stop using "Radial" name (but keep design files)

**Gap identified:** Trademark strategy needs legal design. Not yet started.

#### 2.5.3 Contribution Model

**Baseline:** GitHub pull requests + issue tracker

**Tier 1 — User:**
- Downloads designs, builds, files issues
- No formal commitment

**Tier 2 — Contributor:**
- Submits improvements via PR
- Community review required
- Becomes recognized contributor

**Tier 3 — Core Team:**
- Merges PRs in area of expertise
- Voting rights on major design decisions
- Maintainership of specific subsystems

**Tier 4 — Steering Committee:**
- Sets strategic direction
- 1 seat per major subsystem (motion, materials, electronics, software)
- 2-year rotating seats

**Gap identified:** Contribution model is aspirational. No actual governance body exists yet.

---

### 2.6 Failure Mode Analysis

#### Technical Failure Modes

| Failure | Likelihood | Mitigation |
|---|---|---|
| Print head clogging | High (new material) | Dual-nozzle purge; quick-swap design; purge protocols |
| Frame deflection under load | Medium | Load calculations published; no-skip bolting spec |
| Stepper motor stall | Medium | Closed-loop encoders; stall detection; force limiting |
| Material bond failure between layers | High | Inter-layer roughness spec; set-time calibration |
| Thermal cracking | Medium | Shrinkage testing before full build; rebar integration |
| Pump cavitation | Low-Medium | Venting protocol; material settling time |

#### Social Failure Modes

| Failure | Likelihood | Mitigation |
|---|---|---|
| Community cannot afford $40k | High | Staged investment model; cooperative purchasing |
| Skills gap too large | High | Training curriculum + apprenticeship |
| Governance collapse | Medium | Clear charter before machine arrives |
| Social conflict over priority | Medium | Queue system + transparent criteria |
| One community dominates federation | Low | One-vote-per-community governance |

#### Economic Failure Modes

| Failure | Likelihood | Mitigation |
|---|---|---|
| Material costs higher than projected | Medium | Local aggregate survey before commitment |
| Machine downtime too high | Unknown | Pilot data needed; reliability targets not set |
| Cannot attract maintenance technician | Medium | Career pathway + compensation framework |
| Captured by early adopters as status symbol | Low | Certification requires community service commitment |

---

## 3. Gap Summary — Priority Stack

Ranked by dependency (things that block other things):

**Tier 1 — Must exist before anything else:**
1. [ ] Material testing protocol (7-day, $200, community-run)
2. [ ] Mix design calculator (spreadsheet or simple app)
3. [ ] Basic motion controller firmware (STM32 + stepper coordination)

**Tier 2 — Needed for first pilot:**
4. [ ] Training curriculum (2-week operator + technician)
5. [ ] Frame fabrication manual
6. [ ] Toolpath generator (even rough version)
7. [ ] Community readiness assessment

**Tier 3 — Needed for scale:**
8. [ ] Dual-extruder firmware
9. [ ] Multi-material wall section designs
10. [ ] Governance charter template
11. [ ] Fab cluster formation guide
12. [ ] Carbon/water accounting tools

**Tier 4 — Competitive moat (if Radial succeeds):**
13. [ ] Trademark + certification system
14. [ ] Distributed supply chain infrastructure
15. [ ] Inter-community machine sharing protocol

---

## 4. Open Questions

1. **Who funds the first pilot?** Estimated: $180k for 3 machines + training + evaluation
2. **What is the minimum viable community size?** Hypothesis: 50-200 households with shared land intent
3. **Can lime-based materials achieve 40 MPa compressive strength?** Current literature says yes with volcanic aggregate, but needs community-level validation
4. **Who holds the trademark during the bootstrap phase?** Needs a legal entity — could be a dedicated foundation or fiscal sponsor
5. **How does Radial interact with existing building codes?** Most codes were not written for 3D printed walls. Advocacy or code改装 path needed
6. **What is the minimum training budget per operator?** Hypothesis: $5k/person for 2-week intensive + 3-month apprenticeship

---

## 5. Suggested Next Actions

**Immediate (this week):**
- Identify 3-5 potential pilot communities (land-linked, fabrication-capable, governance experience)
- Survey local aggregate sources in each community
- Run first material test with local aggregate

**Short-term (next 3 months):**
- Build v0 motion controller (electronics + firmware)
- Develop training curriculum (first draft)
- Establish legal entity for trademark + pilot contracts

**Medium-term (6-18 months):**
- First 3-community pilot deployment
- Independent evaluation at month 18
- Iterate on design based on pilot learnings

**Long-term (2-5 years):**
- 20+ community network
- Regional fab clusters operational
- Open source construction ecosystem mature
- Advocacy for building code updates

---

*This document is a living specification. Every section marked [ ] is an open task. Every table is a hypothesis that needs testing. The most important sentence in this document is the failure mode analysis — we are not building a dream, we are building a system that must survive contact with reality.*
