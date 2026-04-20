# Radial Fabrication Chain
## Complete Reverse-Engineering of Construction 3D Printing Ecosystem

*From raw geology to printed building — every system, subsystem, and equipment tier.*

---

## PART 1: RAW MATERIALS — GEOLOGY, EXTRACTION & PROCESSING

Every construction 3D printing system ultimately prints rock — mineral aggregates bound by calcium silicate chemistry. The difference between ICON's Lavacrete and a community using volcanic ash from their local hillside is not the chemistry — it's the engineering precision and the supply chain.

### 1.1 LIMESTONE (CaCO₃)

**Why:** Primary source of calcium oxide (CaO) for cement and lime-based binders.

**Geology:** Sedimentary rock. Ideal purity >90% CaCO₃.

**Extraction:** Open-pit quarrying. Requires excavator + truck. Most regions have a quarry within 50km.

**Processing:** Crushing → calcination at 900-1000°C (kiln) → grinding (ball/roller mill) → cement raw meal.

**Community viability:** Extraction requires heavy equipment. Processing requires industrial kiln. **Buy-in is the path.**

### 1.2 CLAY → METAKAOLIN

**Why:** Calcined clay (650-850°C) becomes metakaolin — high-reactivity pozzolan for geopolymers.

**Geology:** Surface deposits common. Kaolinite, montmorillonite, illite.

**Extraction:** Hand excavation for small batches.

**Processing:** Dry → calcine at 650-850°C (lab kiln) → grind to <45μm.

**Community viability:** ✅ **Achievable.** Most impactful local material a community can produce. Kiln: Nabertherm or Par卡拉 OK (~$3-15k). Batch: 50-200kg.

### 1.3 VOLCANIC ASH / PUMICE

**Why:** Natural pozzolan — reactive silica + alumina WITHOUT calcination. Roman concrete used this.

**Geology:** Within ~50km of volcanoes. Pumice, scoria, pozzolanic tuff.

**Processing:** Crush only. No thermal processing needed.

**Community viability:** ✅ **Best possible case.** If your community is near volcanic geology, you have the world's best binder for free.

### 1.4 SILICA SAND

**Why:** Fine aggregate, refractory molds, input for pozzolan production.

**Sources:** Buy from quarry. $15-50/ton. Wash + classify if needed.

**Community viability:** ✅ Buy locally. Extraction possible with basic screening.

### 1.5 FLY ASH

**Why:** Coal plant waste with pozzolanic properties. Most cost-effective industrial SCM.

**Source:** Coal power plants (400+ in US, declining globally).

**Spec:** Class F: SiO₂+Al₂O₃+Fe₂O₃ ≥ 70%. LOI <6%.

**Cost:** $30-80/ton vs. $120-180 for cement.

**Community viability:** ✅ Source from local coal plant. Transportation dominates beyond 200km. **Warning: coal plants closing globally.**

### 1.6 GGBS (Ground Granulated Blast Furnace Slag)

**Why:** Steel mill byproduct. Exceptional durability, sulfate/chloride resistance.

**Source:** Blast furnace steel plants (Great Lakes US, German Ruhr, etc.).

**Processing:** Grind to 400-600 m²/kg Blaine. Most plants sell pre-ground.

**Cost:** $40-90/ton.

**Community viability:** ✅ Available near steel production regions.

### 1.7 RICE HUSK ASH (RHA)

**Why:** Agricultural waste. Highest pozzolanic reactivity of any ash. Carbon negative if done right.

**Source:** Rice mills (150M tons/year generated globally).

**Critical processing:** Controlled burn at 500-700°C in limited oxygen. Too hot (>900°C): forms cristobalite (hazardous, non-reactive).

**Equipment:** Muffle furnace with temperature control: $3-15k depending on batch size.

**Cost:** Rice husk free (mills pay to dispose). Material cost near zero.

**Community viability:** ✅ In rice-producing regions. **Extremely high value.**

### 1.8 BIOMASS ASH

**Why:** Cheap, local, variable pozzolanic value.

**Sources:** Fireplaces, sawmills, biomass power plants.

**Processing:** Screen + optionally leach (for high alkali types).

**Community viability:** ✅ Essentially free. Variable quality — test before structural use.

### 1.9 BASALT (Aggregate + Fiber)

**Why:** Basalt aggregate is excellent for concrete. Basalt fiber is high-strength reinforcement.

**Geology:** Extrusive volcanic rock. Found globally near volcanic regions.

**Aggregate:** Crush to desired size gradation.

**Fiber:** Requires 1400°C melt + fiberization (industrial process).

**Community viability:** Aggregate ✅. Fiber ❌ (industrial required).

### 1.10 ADMIXTURES

| Type | Commercial Example | Natural Alternative |
|---|---|---|
| Superplasticizer | Glenium 300 | Citrus peel oil (tiny amounts) |
| Retarder | Sikament R | Sugar (0.1-0.5%), citric acid |
| Accelerator | Sika Rapid | Calcium nitrate (1-2%) |
| Viscosity modifier | Viscocrete | Bentonite clay |
| Air entrainer | MB-Air | Pine tar (very small) |

**Critical for 3DCP:** Superplasticizer (workability + pumpability) + thixotropy agent (prevents sagging).

### 1.11 RAW MATERIALS SUMMARY TABLE

| Material | Source | Community Extract? | Processing | Cost/ton | Notes |
|---|---|---|---|---|---|
| Limestone | Quarry | ❌ | Calcination + grinding | $20-40 raw | Buy cement |
| Volcanic ash | Volcanic region | ✅ | Crushing only | $0-30 | **Best binder** |
| Clay (kaolinite) | Surface deposit | ✅ | Calcination 700°C | $0-50 | Metakaolin |
| Silica sand | Quarry/river | ✅ | Washing + class. | $15-50 | |
| Fly ash | Coal plant | ✅ (source) | None | $30-80 | Declining supply |
| GGBS | Steel mill | ✅ (source) | Grinding | $40-90 | |
| Rice husk ash | Rice mill | ✅ (free) | Controlled burn 550°C | $0-30 | Requires kiln |
| Biomass ash | Fireplace | ✅ | Screening | $0-15 | Variable |
| Basalt aggregate | Quarry | ✅ | Crushing | $15-40 | |

---

## PART 2: MATERIALS PROCESSING EQUIPMENT

### 2.1 CRUSHING & GRINDING

| Equipment | Purpose | Budget Options | Cost |
|---|---|---|---|
| Jaw crusher | Primary: boulder → 10-50mm | BICO Badger 5×7 | $3,500 |
| Hammer mill | Secondary: 10mm → 1-3mm | Schutte Buffalo 15 | $3,000-8,000 |
| Ball mill | Fine grind: → <45μm | Sepor 16×32 batch | $8,000 |
| Rod mill | Pre-grinding | Meadows | $2,000-5,000 |

**Community start:** Jaw crusher + ball mill. Capacity: ~100kg/day pozzolan. Budget: $10-20k.

### 2.2 THERMAL PROCESSING

| Process | Temp | Community DIY? | Budget | Throughput |
|---|---|---|---|---|
| Clay calcination (metakaolin) | 700-850°C | ✅ Yes | $2-15k | 50-200kg/batch |
| Limestone calcination | 900-1000°C | ⚠️ Hard | $10-50k | 500kg+/day |
| RHA production | 550-700°C | ✅ Yes | $2-15k | 50kg/batch |
| Basalt melting | 1400°C | ❌ No | Industrial | N/A |

**Small kiln options:** Nabertherm (~$3-10k), Par卡拉 OK 6090 (~$2-3k). DIY firebrick box kiln: $300-500 with welding skills.

### 2.3 CLASSIFICATION & HANDLING

| Equipment | Purpose | Budget | DIY? |
|---|---|---|---|
| Vibrating screen | Size classification | $500-2,000 | ✅ ($100-300) |
| Cyclone classifier | Air-classify fine powder | $1,000-3,000 | ⚠️ Possible |
| Dust collector | 2HP HF | $200 | ✅ |
| Silos | Storage | Food-grade IBC totes | ✅ ($150 each) |
| Pug mill | Continuous mixing | $2-5k DIY | ✅ |

### 2.4 TESTING EQUIPMENT

| Test | Equipment | Budget |
|---|---|---|
| Compressive strength | Forney LC-250 | $2,000-5,000 used |
| Flow table | Vitrified cast iron | $300-800 |
| Vicat apparatus | Set time | $200-500 |
| Sieve set + shaker | Particle size | $1,000-2,000 |
| Blaine apparatus | Fineness | $1-2k |
| XRF chemical analysis | — | Lab service: $50-200/sample |

---

## PART 3: CNC MACHINING ECOSYSTEM

### 3.1 LATHE

| Model | Cost | Use |
|---|---|---|
| Tormach 15Lsl | ~$5,000 | Minimum for functional parts |
| ProTurn 560 | ~$4,000 | Solid entry-level |
| Southbend 10K (used) | ~$15,000 | Industrial quality |
| Manual lathe + DRO | $1-5k used | Slower but capable |

**Critical parts:** Lead screws, ACME threads, nozzle bodies, shaft couplings, bearing housings.

### 3.2 MILL

| Model | Cost | Use |
|---|---|---|
| Tormach 1100MX | ~$12,000 | Full 3-axis, steel capable |
| Carbide 3D XXL | ~$2,500 | Aluminum/soft materials only |
| Haas TM-1 | ~$30,000 | Industrial |

**Critical parts:** Motor mounts, brackets, fixture plates, pump housings.

### 3.3 PLASMA CUTTER

| Model | Cost | Use |
|---|---|---|
| Hypertherm Powermax 45 | ~$2,500 | Manual plate cutting |
| Langmuir MX-1250 (CNC) | ~$4,000 | CNC plate cutting |
| CrossFire Pro (CNC) | ~$2,500 | Budget CNC table |

### 3.4 WELDING (MOST CRITICAL SKILL)

| Welder | Cost | Use |
|---|---|---|
| Miller Multimatic 220 | ~$2,500 | TIG precision — **priority** |
| Miller Multimatic 215 | ~$1,200 | MIG fast structural |
| Lincoln AC/DC 225 | ~$600 | Stick for field repair |

### 3.5 TOOLING

| Item | Budget | Source |
|---|---|---|
| End mills (carbide, 1/4-3/4") | $15-40 each | Lakeshore Carbide |
| Lathe inserts (CNMG/DNMG) | $5-15 | CBTips, YG-1 |
| Drill bit sets (cobalt HSS) | $30-50 | Milwaukee, DeWalt |
| Taps and dies (metric/imperial) | $50-100 | Guhring, Greenfield |

---

## PART 4: METAL 3D PRINTING

| Technology | Budget | Community Viability |
|---|---|---|
| DMLS/SLM | $100k+ | ❌ |
| Binder Jetting | $50-100k used | ⚠️ |
| WAAM (DIY) | $5-15k | ✅ Achievable |
| Ceramic/metal paste extrusion | $5-15k | ✅ For nozzles |

**WAAM:** Most achievable community option. MIG welding + CNC gantry + open-source software. Produces rough parts that need post-machining.

---

## PART 5: ELECTRONICS

### 5.1 MICROCONTROLLERS

| Part | Package | Use | Cost |
|---|---|---|---|
| STM32H743VIT6 | LQFP100 | Main motion controller | $8-12 |
| ESP32-S3-WROOM-1 | Module | WiFi/BT + mesh | $3-5 |
| Raspberry Pi CM4 | Module | Full Linux | $35-75 |
| ATmega328P | TQFP32 | Simple I/O | $2 |

### 5.2 MOTOR DRIVERS

| Part | Spec | Use | Cost |
|---|---|---|---|
| DRV8711 | 50V, 8A, SPI | 3D printer stepper | $5 |
| TMC5161 | 60V, 20A, SPI | High-performance | $10 |
| L6470 | 40V, 3A, SPI | Medium stepper | $4 |
| BTN8982 | 40V, 30A half-bridge | DC/extrusion | $3 |

### 5.3 SENSORS

| Sensor | Use | Cost |
|---|---|---|
| HX711 + 50kg cell | Material flow measurement | $5-15 |
| AS5600 magnetic encoder | Motor position | $2 |
| Linear encoder 1m | Print head position | $20-50/m |
| PT100 RTD | Temperature | $5 |
| Noctua 40mm fan | Cooling | $10 |

### 5.4 PCB FAB

| Equipment | Cost | Use |
|---|---|---|
| Bantan Lab 2.0 | ~$2,500 | Double-sided PCB milling |
| Yihua 936D+ soldering station | $50 | Hand solder |
| T962A reflow oven | ~$200 | SMD reflow |
| KiCad | Free | PCB design |

---

## PART 6: MOTION SYSTEM

### 6.1 LINEAR MOTION

| Grade | Brand | Cost/m | Use |
|---|---|---|---|
| Precision (P) | THK, HIWIN | $50-200 | Z-axis (critical) |
| Standard (N) | SBC, IKU | $15-50 | X/Y axes |
| Budget import | CHG | $5-20 | Non-critical |

### 6.2 LEADScrews

| Spec | Use | Cost |
|---|---|---|
| TR8×8 (8mm lead, 4-start) | Z-axis | $10-20/m |
| TR12×6 (12mm OD, 6mm lead) | X/Y gantry | $15-30/m |
| HIWIN ballscrew 20mm | High precision | $200-400 |

### 6.3 STEPPER MOTORS

| Size | Torque | Use | Cost |
|---|---|---|---|
| NEMA 23 | 1.5-3 Nm | Medium extruder, small gantry | $30-80 |
| NEMA 34 | 3-8 Nm | Large gantry axes | $80-200 |
| NEMA 42 | 10-30 Nm | Industrial heavy gantry | $200-500 |

### 6.4 FRAME MATERIALS

| Material | Spec | Cost/m | Notes |
|---|---|---|---|
| Steel 80×80×5mm tube | Square structural | $8-15 | **Standard choice** |
| 8020 extrusion 40×40 | Aluminum modular | $20-40 | Good for prototype |
| 80/40 vs 40/40 | 80/40 in both dims | +50% | Torsional rigidity |

---

## PART 7: PRINT HEAD & MATERIAL DELIVERY

### 7.1 NOZZLE GEOMETRY

```
Entry angle: 30-60° converging
Land length: 1-3× exit diameter (critical)
Exit diameter: 10-40mm
Exit shape: Round, rectangular, or custom
```

**Wear materials:** Tool steel (H13) → D2 steel → Tungsten carbide (best).

### 7.2 PUMP COMPARISON

| Type | Pros | Cons | Use |
|---|---|---|---|
| Piston | High pressure, precise | Pulsed, complex seals | Industry standard |
| Progressive cavity (Seepex) | Smooth flow, handles abrasive | Wear on stator | Lime/pozzolan mixes |
| Squeeze | Gentle, easy clean | Limited pressure | Multi-material |
| Peristaltic | Precise dosing | Limited flow | Additive dosing |

**Recommendation for Radial:** Progressive cavity (worm pump) — simple, reliable, handles pozzolanic materials well.

### 7.3 SENSORS FOR MATERIAL DELIVERY

| Sensor | Purpose | Budget Solution | Industrial |
|---|---|---|---|
| Load cell | Ground truth flow | HX711 + $50 cell | Zemic L6E ($80) |
| Pressure transducer | Clog detection | Alibaba $20-50 | HBM ($200+) |
| Temperature | Material state | PT100 RTD ($5) | Industrial RTD |
| Linear encoder | Position | Optical $20/m | Renishaw $500/m |

---

## PART 8: SOFTWARE STACK

### 8.1 DESIGN → PRINT PIPELINE

```
FreeCAD (architecture)
    ↓ STEP/OBJ export
radial-path (toolpath engine, Python)
    ↓ G-code + extrusion rates
SD card → STM32H7 firmware (motion control)
    ↓ ESP-NOW mesh
Sensor data → SQLite logger
```

### 8.2 KEY SOFTWARE COMPONENTS

| Layer | Tool | Custom? | Notes |
|---|---|---|---|
| CAD | FreeCAD | No | Parametric architecture |
| BIM | BlenderBIM | No | IFC export |
| Toolpath | Custom (Python) | ✅ YES | Bingham plastic model |
| Firmware | Custom Rust or Marlin fork | ✅ YES | Real-time stepper |
| Mesh | ESP-NOW | ✅ YES | No router needed |
| Logging | SQLite | No | CSV export |
| Safety | Custom | ✅ YES | Interlocks, limits |

### 8.3 MATERIAL PROFILE EXAMPLE (YAML)

```yaml
material:
  name: "volcanic_ash_lime"
  density: 2200  # kg/m³
  yield_stress: 500   # Pa — below this, no flow
  plastic_viscosity: 500  # Pa·s
  open_time: 30   # minutes before stiffening
  set_time: 240   # minutes to structural set
  compressive_strength_7d: 25  # MPa
  compressive_strength_28d: 45  # MPa
  pump_rate: 0.8   # L/min at target pressure
  recommended_layer_height: 12.5  # mm
  recommended_line_width: 40  # mm
```

---

## PART 9: COST TIERS

### Tier 1: Community Lab ($20k-$50k)

**Equipment list:**
- Jaw crusher (BICO Badger): $3,500
- Ball mill (Sepor): $8,000
- Muffle furnace (20L): $5,000
- Miller Multimatic 220 TIG: $2,500
- Manual lathe (Southbend): $3,000
- Manual mill (Enco): $3,000
- CNC router (Shapeoko XXL): $2,500
- HX711 + load cells: $50
- Raspberry Pi + ESP32: $100
- Hand tools, test equipment: $3,000
- Contingency: $5,000

**Can build:** Small-scale printer (~1m³), basic material testing, simple metal parts, basic pozzolan processing

### Tier 2: Maker Space ($50k-$200k)

**Additions over Tier 1:**
- Tormach 1100MX CNC mill: $12,000
- Tormach 15Lmx CNC lathe: $10,000
- Miller MIG welder: $1,200
- Plasma table (Langmuir MX-1250): $4,000
- Used industrial crusher: $10,000
- Larger kiln: $10,000
- Load cell upgrade (Zemic): $200
- Test press upgrade: $3,000

**Can build:** Full-scale community printer (up to 12m × 12m × 4m), functional metal fabrication, pozzolan production at 100kg/day

### Tier 3: Fab Lab ($200k-$1M)

**Includes:** Industrial CNC mill + lathe, waterjet or laser, small crusher, rotary kiln, full materials lab, 3D scanner, 3D printer for plastic patterns

**Can build:** Everything except very large steel fabrication and industrial-scale pozzolan processing

### Tier 4: Micro-Factory ($1M-$5M)

**Includes:** Industrial scale equipment, dedicated facility, engineering team, metrology lab

**Can build:** Complete industrial-grade construction 3D printing ecosystem

---

## PART 10: SUPPLY CHAIN MAP

### From Geology to Building

```
LAYER 0: RAW GEOLOGY
├── Limestone quarry → industrial
├── Clay deposits → community extractable
├── Volcanic ash deposits → community extractable
├── Sand/gravel pits → local quarry
└── Water → municipal/well

LAYER 1: MATERIAL PROCESSING
├── Community lab: crushing, grinding, calcination (Tier 2+)
├── Industrial: cement plant, quarry processor
└── Buy-in: fly ash, GGBS from industrial waste streams

LAYER 2: EQUIPMENT FABRICATION
├── Tier 1-2: Manual machine tools, welding
├── Tier 3+: CNC machining, metal 3D printing
└── Buy-in: precision components (leadscrews, rails, motors)

LAYER 3: ELECTRONICS
├── DIY: PCBs via Bantam/Othermill
├── Buy: microcontrollers, motor drivers (Digikey, Mouser, LCSC)
└── Buy: sensors (industrial grade)

LAYER 4: SYSTEM INTEGRATION
├── Motion: steel frame, linear rails, motors, firmware
├── Print head: pump, nozzle, mixer
├── Software: CAD → path → firmware
└── Test: material characterization, calibration

LAYER 5: OPERATION
├── Material: locally-sourced pozzolan + aggregate + binder
├── Energy: solar + battery for off-grid operation
├── Skills: operators, technicians, mix designers
└── Governance: community decision-making structure
```

---

## PART 11: THE SINGLE MOST IMPORTANT POINT

**The materials science is the moat. Everything else is engineering.**

ICON, COBOD, CyBe, and Wasp all use variations of the same basic chemistry: Portland cement + supplementary cementitious materials (pozzolans) + carefully graded aggregate + admixtures.

**The unlock for community sovereignty is not:**
- Building a fancier machine than COBOD
- Writing better software than ICON
- Copying Titan's gantry system

**The unlock is LOCAL MATERIALS.** If a community can:
1. Identify their local pozzolan source (volcanic ash, calcined clay, rice husk ash, fly ash, GGBS)
2. Characterize its reactivity (7-day test protocol)
3. Develop a mix design that works with it
4. Produce it consistently

Then they have the same essential ingredient as any commercial system — plus something commercial systems can't offer: **near-zero material cost and complete supply chain independence.**

The machine is the easy part. The material is the hard part. The governance is the essential part.

---

*Document: projects/radial/FABRICATION-CHAIN.md*
*Status: Complete draft — Part 1-11*
*For: RegenTribes Radial Project*
