# Dark Factory Manufacturing Cells: Complete Reference
## Fully Automated Production Across All Methods and Materials
### Regen Tribe Research | Genesis 🌿⚡ | 2026-04-15

---

## PART 1: WHAT IS A DARK FACTORY

A dark factory (lights-out manufacturing) is a production facility that operates with zero human presence on the floor. Raw materials enter, finished goods leave, no human labor required in between.

**The key distinction**:
- **Attended operation**: Human loads/unloads, monitors, adjusts
- **Unattended operation**: Robots handle everything, human in control room only
- **Lights-out**: No human presence at all. Robots run 24/7/365 for weeks or months

**Reality check**: Even FANUC's "dark factory" has 9 human QA workers overseeing the end of the line. True 100% lights-out is rare. The practical goal is maximum automation with minimal human presence.

**The business case**:
- 24/7 operation (3x the productive hours of a human-shift operation)
- No climate control needed (robots don't need AC/heating)
- No lighting needed
- No safety equipment, ergonomics, or labor law constraints
- Consistent quality at scale
- 30-70% reduction in per-unit labor cost
- 40-60% reduction in floor space (compact robot cells vs human workspaces)

---

## PART 2: THE AUTOMATION STACK

Every dark factory cell has the same layered architecture:

```
LAYER 1: Physical Process
CNC machine / robot arm / 3D printer / press / injection molder
    ↓
LAYER 2: Machine Control
PLC / CNC controller / embedded real-time system
    ↓
LAYER 3: Cell Controller
Robot cell controller / MES interface / recipe management
    ↓
LAYER 4: Material Handling
Robot loader / conveyor / AS/RS / AGV / pallet changer
    ↓
LAYER 5: Tooling/Fixtures
Automatic tool changer / fixture pallet / tombstone changer
    ↓
LAYER 6: Quality Assurance
In-process inspection / machine vision / CMM probing
    ↓
LAYER 7: Digital Thread
CAD/CAM ↔ CNC ↔ CMM ↔ MES ↔ ERP
    ↓
LAYER 8: Operations
Remote monitoring / predictive maintenance / digital twin
```

The art of dark factory design is integrating all 8 layers so each layer feeds the next without human intervention.

---

## PART 3: CNC MACHINING CELLS

### 3.1 CNC Milling Cells

**The automation problem**: CNC milling requires:
- Loading raw stock into vise/chuck
- Running machining program
- Measuring finished part (in-process probing)
- Unloading finished part
- Loading next stock
- Managing chips, coolant, andtool wear

**How it's solved**:

**Tombstone/fixture pallet systems**:
- Multiple parts pre-loaded on tombstone fixtures
- Robot loads entire tombstone into machine
- Machine runs unattended on all parts
- Robot removes tombstone and loads next one
- A typical 4-sided tombstone with 4 parts = 4 hours unattended machining

**Automatic tool measurement**:
- Renishaw OTS or similar: robot places tool in tool setter automatically
- In-process probing: Renishaw OMP-60 or similar probes workpiece between operations
- Post-process CMM: part measured while next part is cutting

**Chip management**:
- Through-spindle coolant (through-tool airblast for dry machining)
- Chip conveyor with automatic chip cart
- Air blast to clear pockets

**Coolant management**:
- High-pressure coolant systems (30-150 bar) for unmanned operation
- Coolant concentration monitoring (automatic adjustment)
- Bacterial growth prevention (UV sterilization or ozone)

**Tool life management**:
- Fixed tool life from CAM (tool change after N parts)
- Adaptive control (power/spindle load monitoring)
- Direct tool wear measurement (Renishaw TS27R tool setter)
- Spare tool in carousel = automatic swap if tool fails

**Real-world example — Haas + RoboJob**:
- Haas VF-2 + RoboJob Cell
- 15-minute cycle parts = 12 parts unattended per 3-hour window
- One human sets up 20 jobs at start of shift, comes back at end
- 128-hour unattended capability per week

### 3.2 CNC Turning Cells

**The automation problem**: Turning requires:
- Loading bar stock (long or short)
- Collet/chuck actuation
- Part ejection
- Part catch tray or conveyor
- Bar feeder for continuous production
- Part inspection

**Bar feeder systems**:
- LNS Quick Load Servo bar feeder: 10-80mm diameter bars, auto-load
- Servo-driven bar push rod, guides bar through liner
- Bar end detection: when bar gets short, machine alerts
- Multiple bar lengths = multiple setups per day unattended

**Parts catcher**:
- Parts fall into catch tray or conveyor
- Conveyor moves parts to packing station
- Some cells use robot arm to grab part directly from spindle

**Chucking systems**:
- Pneumatic/hydraulic chucks with auto-open/close
- Collet chucks for bar work
- Soft jaws for second-op work

**In-process probing**:
- Marposs or Renishaw live tooling probes
- Measures bore, OD, ID during cutting
- Adjusts offsets automatically

**The hardest part**: Long-running bar work is easy to automate (no load/unload between parts). Short-run job shop turning is harder (setup time > run time). The sweet spot is 50+ identical parts.

### 3.3 Grinding Cells

**Automation challenges**:
- Wheel dressing (sharpening) required as wheel dulls
- In-process gauging (grinding is precise, needs live feedback)
- Coolant filtration (grinding swarf is fine, clogs systems)
- Part handling (fragile due to spring-back)

**Solutions**:
- Fanuc Robo Grind: integrated robot + grinding wheel dresser
- Form grinding with CNC-controlled dressing (every N parts, CNC dresses wheel)
- Acoustic emission sensing for wheel-part contact
- Marposs P7 or Marposs T25: in-process gauging head

**Electrolytic grinding (ELID)**:
- Metal removal via electrolysis + mechanical abrasion
- Wheel stays sharp via electrochemical dressing
- Achieves <0.1μm surface finish

---

## PART 4: INJECTION MOLDING CELLS

### 4.1 Full Automation Cell Architecture

```
Injection molding machine (50-1000 tons)
    ↓
Robot arm (6-axis or 3-axis)
    ↓
Part removal + sprue/runner separation
    ↓
Part inspection (camera + reject station)
    ↓
Part placement in tote/tray
    ↓
Conveyor to packing
    ↓
Palletizer (optional)
```

### 4.2 Robot De-Paneling Systems

**Three-axis robot** (common for small parts):
- Picks part from mold open position
- Separates part from sprue/runner automatically
- Places in tray or conveyor
- Cycle time matches molding cycle (typically 10-30 seconds)

**Six-axis robot** (for complex parts):
- Can extract parts from cavity in any orientation
- Post-mold operations: de-flash, assemble, test
- Works with hot runner molds too

### 4.3 Hot Runner Systems

**Why they matter for automation**:
- No cold runner waste (no sprue separation needed)
- Consistent temperature = consistent cycle time
- Gate seal = consistent part weight
- Fully automated = no operator to open/close valves

** valve gate controllers**:
- Mold-Masters, Husky, Synventive
- Temperature control of each valve gate
- Sequential valve actuation (for cosmetic control)
- Fiber optic or thermocouple temperature sensing

### 4.4 Mold Temperature Control

**Why it matters for lights-out**:
- Temperature drift = part warpage = rejects
- Must be rock-solid for unattended operation

**Systems**:
- Tempering units (oil or water) with PID control
- Flow control valves (automatic)
- Conductivity monitoring (detects coolant contamination)
- Filtration and maintenance alerts

### 4.5 Quality Control Loop

```
Mold cycle
    ↓
Robot extracts part
    ↓
Vision inspection (parting line flash, sink marks, gate vestige)
    ↓
Weighing (part weight = indicative of dimensions, material shorts)
    ↓
CMM probe (optional, for critical dimensions)
    ↓
OK parts → packing station
    ↓
NG parts → reject station (with photo evidence)
```

### 4.6 Materials

Most common for dark factory injection:
- Engineering plastics: ABS, PC, PA (nylon), POM (acetal)
- Glass-filled versions (stiffness, dimensional stability)
- Liquid silicone rubber (LSR) — needs heated tooling
- Metal injection molding (MIM) — requires debinding/sintering

---

## PART 5: DIE CASTING CELLS

### 5.1 The Automation Challenge

Die casting involves:
- Molten metal (aluminum ~660°C, zinc ~400°C)
- High pressure injection (hundreds of bar)
- Shot cycle 1-5 seconds
- Trim press to separate part from sprue
- Shot blast/finishing

**Why this is harder than injection molding**:
- Molten metal burns through most sensors and mechanisms
- High pressure = safety concerns
- Die cooling (water channels) must be controlled precisely
- Die release agents (spray robots required)

### 5.2 Full Automation Cell

```
Die casting machine (cold or hot chamber)
    ↓
Spray robot (applies release agent to die)
    ↓
Shot + extraction
    ↓
Trim press (cuts sprue/overflows)
    ↓
Cooling conveyor
    ↓
Vision inspection
    ↓
Packing/integration
```

**Key automation components**:
- ABB or Fanuc high-payload robots (for hot parts)
- Servo-controlled spray guns (precise release agent application)
- Die temperature monitoring (IR sensors)
- Automatic ladling/oil injection for cold chamber
- Shot monitoring (velocity + pressure curve monitoring)

### 5.3 Materials

- Aluminum alloys (A380, A383, A360)
- Zinc alloys (Zamak 3, 5, 7)
- Magnesium (rare, high flammability risk)
- Copper (brass, bronze — very high temp)

---

## PART 6: SHEET METAL FORMING + STAMPING

### 6.1 Press Brake Cells

**The automation problem**:
- Sheet loading (large, flat blanks)
- Bending (tool changes for different angles)
- Part removal (floppy parts spring back)
- Part handling to next operation

**Solutions**:
- **Automatic sheet loaders**: LFT (linear format transfer) or robot + sheet lifters
- **Back gauges**: CNC back gauges for precise bend positioning
- **Tool changers**: automatic tool magazine (AMTC or custom)
- **Part flipper**: 180° rotation for complex bends
- **Robot tendering**: holds part against back gauge while press actuates

### 6.2 Stamping / Press Lines

**Full press line automation**:
```
Uncoiler (feeds coil stock)
    ↓
Leveler (straightens stock)
    ↓
Feed roll (advances stock per stroke)
    ↓
Progressive die press (multiple operations per stroke)
    ↓
Parts picker (separates parts from scrap)
    ↓
Parts bin / palletizer
    ↓
Scrap chopper/winder (manages scrap strip)
```

**Progressive die**: Single die that performs multiple operations as the strip advances. One press stroke = multiple bends/punches. Very efficient for high volume.

**Servo press lines** (smoother, more controllable):
- Yamaha,Komatsu, Aida Engineering servo presses
- Variable stroke profile = better for complex parts
- Quieter = less hearing protection needed (still a robot's problem)

### 6.3 Tube Bending + Laser Cutting

**Tube bending cell**:
- CNC tube bender with auto-loader
- End forming (flare, cap, socket)
- Laser marking (part ID)
- Vision inspection
- Bundling

**Laser cutting cell** (for sheet and tube):
- Fiber laser or CO2 laser
- Automatic nozzle changing (co2 requires nozzle; fiber doesn't)
- Automatic焦点 position control (height sensing)
- Nitrogen assist gas (for clean cuts, no oxidation)
- Sheet/tube loading via automated storage (AS/RS)

---

## PART 7: WELDING CELLS

### 7.1 MIG/GMAG Welding Cells

**The automation challenge**:
- Arc welding requires precise torch angle, speed, and contact tip distance
- Joint access (can robot reach all weld seams?)
- Fit-up variation (parts not exactly as modeled)
- Spatter accumulation on nozzle
- Wire feeding

**Solutions**:
- **6-axis robot welding arms**: FANUC ArcMate, ABB IRB, KUKA, Motoman
- **Seam tracking**: through-arc seam tracking (TAST) or laser vision sensor
- **Push-pull gun**: for long reach (wire feeds through robot arm)
- **Spatter removal**: anti-spatter spray or automatic nozzle cleaning station
- **Fixture**: precision welding fixture or parts-touch sensing at start

**Key components**:
- Lincoln Electric or Miller digital welding power source
- Wire feeder (push-pull or separate)
- Water-cooled torch (for high duty cycles)
- Torch cleaning station (trim spatter, check contact tip)
- Welding parametric control (voltage, wire feed speed, gas flow)

### 7.2 Spot Welding Cells

**Common in automotive**:
- Multiple spot welds per panel (200-800 spot welds per car body)
- Robot spot welding guns (servo or pneumatic)
- Servo weld gun = programmable squeeze force + current
- Weld monitoring (electrode displacement, current, voltage)

**Automation**:
- Robotic door handler (loads door panels, returns to fixture)
- Parts presenter (indexes parts for sequential welds)
- Nut/spacer placement (feeders + robot picks and places)

### 7.3 TIG Welding Cells

**Harder to automate than MIG**:
- Tungsten requires precise maintenance (grinding, replacement)
- AC welding for aluminum (requires balanced waveform)
- Foot pedal emulation for AC balance control

**Solutions**:
- Orbital welding (for pipe/tube — head rotates around work)
- Automated TIG cells with machine vision torch positioning
- Cold metal transfer (CMT) from Fronius: virtually spatter-free, easier to automate

### 7.4 Laser Welding

**Advantages for automation**:
- No contact tool = no wear
- Very narrow heat-affected zone
- No electrode gap maintenance
- Can weld reflective materials (aluminum, copper)

**Cell components**:
- Fiber laser source (IPG, Coherent, nLIGHT)
- Robot-mounted laser head (coaxial or side-fire)
- Beam delivery via fiber optic
- Shielding gas (argon/helium)
- Vision system for joint finding
- Nozzle cleaning (less frequent than MIG)

### 7.5 WAAM (Wire Arc Additive Manufacturing)

**Subcategory of welding**: Uses welding equipment to build up metal parts layer by layer.
- Gas metal arc welding (GMAW/MIG) as the deposition source
- Wire feed same as conventional welding
- Robotic arm moves torch along toolpath
- Creates near-net-shape metal parts

**For dark factory**: WAAM cells can run lights-out with:
- Automatic wire spooling (large spools = hours of unattended printing)
- In-process cooling time (thermal management between layers)
- Machine vision for layer monitoring
- Post-process machining (finish on same machine with additional axes)

---

## PART 8: ADDITIVE MANUFACTURING CELLS

### 8.1 SLA / Stereolithography (Resin)

**Materials**: UV-curable resin (standard, tough, castable, flexible, dental, medical)

**Dark factory challenges**:
- Resin exposure to UV light = cured
- Resin out-of-band spectral issues
- Drain/fill of resin tanks
- Post-cure cleaning

**Automation architecture**:
```
SLA printer (large format: 1m+ build volume)
    ↓
Automatic part removal (blade or sweep)
    ↓
IPA wash station (automated)
    ↓
UV post-cure oven (automated)
    ↓
Part removal from build platform
    ↓
Platform swap (fresh platform loaded for next build)
    ↓
Support removal (optional: CNC or manual)
```

**Key systems**:
- Carbon3D L1: continuous Digital Light Synthesis, speed 10-100x faster
- EnvisionTEC large-format
- 3D Systems ProJet (multi-jet)

### 8.2 SLS / Selective Laser Sintering (Nylon/Polymer)

**Materials**: Nylon powder (PA12, PA11), TPU (flexible)

**Dark factory challenges**:
- Powder bed must be kept below melting point (oven)
- Nitrogen inert atmosphere (for some materials)
- Sieving + reuse of unsintered powder
- Part extraction from deep bed

**Automation architecture**:
```
SLS printer
    ↓
Automatic powder sieving (recirculates unsintered powder)
    ↓
Part extraction from build chamber
    ↓
Media blast / bead blast (removes loose powder)
    ↓
Parts bin
    ↓
Fresh powder top-off (automatic powder addition)
    ↓
Next build starts
```

**Systems**:
- EOS (EOSINT P 760, P 770) — largest SLS machines
- Formlabs Fuse series (desktop, more affordable)
- Sinterit Lisa (desktop SLS)

### 8.3 FDM / FFF (Thermoplastic Extrusion)

**Materials**: PLA, ABS, PETG, Nylon, TPU, ULTEM (PEI), CF-reinforced

**For dark factory**:
- Multiple machines with material swapping
- Automatic material loading (spool changeover)
- Part removal via flexible scraping or heated bed release
- Build plate swapping (print on one, while another prints)
- Out-of-filament detection
- Nozzle clog detection + automatic clearing (Bambulab AMS)

**Cell architecture**:
```
FDM printer farm (4-50 machines)
    ↓
Central material dryer (most filaments need moisture-free)
    ↓
Filament auto-feeder (spool swapper)
    ↓
Automatic build plate swap
    ↓
Part cooling + removal
    ↓
Plate surface prep (scrape, IPA wipe, adhesion promoter)
    ↓
Packing/shipping
```

**Bambulab X1E + AMS (Automatic Material System)**:
- Multi-material printing (up to 16 colors/materials)
- Automatic spool swap = run indefinitely
- Carbon fiber reinforcement printing
- Enclosure for consistent printing conditions
- For dark factory: 50 units running different prints = one operator checking daily

### 8.4 DMLS / SLM (Metal Powder Bed Fusion)

**Materials**: Stainless steel, aluminum, titanium, cobalt chrome, Inconel

**This is the gold standard for metal additive dark factory**:

**EOS M 300-4** (400W laser, 4 build stations):
- 4 build modules: load/unload while others print
- Nitrogen or argon atmosphere
- Recoater blade system (spreads fresh powder each layer)
- 30μm layer thickness typical
- Build volume: 300mm × 300mm × 400mm

**Dark factory operation**:
```
DMLS machine running
    ↓
Build complete (powder cake)
    ↓
Automatic chamber purge + cooling
    ↓
Build module swap (unload finished, load new powder)
    ↓
Thermal debind (for bound metal) or
Electrodischarge machining (for support removal)
    ↓
HIP (hot isostatic pressing) — for aerospace
    ↓
Heat treatment (stress relief)
    ↓
Machining (finish critical surfaces)
    ↓
Quality inspection (CT scan, CMM)
```

**Material handling**:
- Argon atmosphere = oxygen <100ppm (purity management)
- Powder size distribution analysis (automatic)
- Powder reuse ratio (virgin to used powder mixing)
- Sieving between builds (automatic)

### 8.5 Binder Jetting (Metal + Sand + Ceramics)

**Process**: Binder liquid is jetted onto metal powder, layer by layer. Parts are "green" after printing, then sintered or infiltrated.

**For dark factory**:
- Exonix binder jetting + Desktop Metal / Markforged
- Sand mold printing (voxeljet) for metal casting molds
- Large format (VX1000-S, VX2000)

**Automation**:
```
Binder jetter running
    ↓
Green part extraction (automatic)
    ↓
Depowdering (manual or automated powder removal)
    ↓
Infiltration furnace (bronze or bronze + copper)
OR Sintering furnace
    ↓
Finish machining (if needed)
    ↓
Packing
```

**Advantage over DMLS**: Much faster (no melting, just sintering), larger build volumes, lower energy per part. Less mature for fully automated production.

### 8.6 Concrete 3D Printing (Regen Tribe Focus)

**Materials**: Portland cement, volcanic pozzolan, lime, sand, aggregate, hemp fiber, superplasticizers

**The full dark factory cell**:
```
Raw material storage (cement, sand, pozzolan, additives)
    ↓
Volumetric mixer (continuous or batch)
    ↓
Progressive cavity pump (moves material to print head)
    ↓
6-axis or gantry robot with precision print head
    ↓
Near-nozzle dosing (accelerant/additive injection for set control)
    ↓
Inline reinforcement (stainless cable or rebar placement)
    ↓
Layer-by-layer extrusion
    ↓
Laser scanner (layer height verification)
    ↓
Temperature/humidity monitoring
    ↓
Interior finishing robot (optional: applies plaster, electrical chases)
    ↓
MEP rough-in (automated conduit + pipe placement)
    ↓
Exterior finishing robot (optional: exterior coating, sealing)
```

**Key for lights-out**:
- Material must not set in lines (re-circulating system or rapid purge)
- Weather monitoring (wind, rain, temperature) = auto-pause
- Power failure recovery (resume from last good layer)
- Structural monitoring (deflection sensors in walls during build)
- No human for 8-72 hour builds

**Material feed systems**:
- Helical screw pump (screws material forward)
- Piston pump (positive displacement, high pressure)
- Extruder barrel + worm gear (for pastes)

---

## PART 9: COMPOSITE MANUFACTURING CELLS

### 9.1 Automated Fiber Placement (AFP)

**Process**: Pre-impregnated (prepreg) carbon fiber or fiberglass tape is placed by robotic head on mandrel or mold.

**For dark factory**:
- AFP head on multi-axis gantry or robot arm
- Material spool auto-load (50-100kg spools)
- Cut-and-clamp capability (for complex contours)
- In-process inspection (thermal camera sees voids)
- Automated trimming (5-axis router at end of line)

**Materials**:
- Carbon fiber / fiberglass prepreg
- Thermoplastic tape (in-situ consolidation)
- Glass mat reinforced thermoplastics (GMT)

### 9.2 Automated Tape Laying (ATL)

**Similar to AFP but for flat or slightly curved surfaces**:
- Widely used in aerospace (fuselage panels, wing skins)
- Tape widths 3-12 inches
- Higher deposition rate than AFP

### 9.3 Filament Winding

**For cylindrical structures** (pipes, pressure vessels, rocket motors):
- 6-axis robot or 2-axis gantry winds fiber over mandrel
- Tension-controlled fiber pay-off
- Angular winding pattern software

**For dark factory**:
- Continuous winding (fiber spooled onto machine, hours of unattended winding)
- Mandrel auto-load/remove
- Cut-off + terminate (automated fiber cutting + resin anchoring)

### 9.4 AFP/ATL Materials

- Carbon/epoxy prepreg (thermoset, requires autoclave cure)
- Carbon/PEEK (thermoplastic, no autoclave needed — better for automation)
- Fiberglass/polyester (cheaper, marine applications)

---

## PART 10: MATERIAL HANDLING WITHIN DARK FACTORY CELLS

### 10.1 Conveyor Systems

**Types**:
- Roller conveyor (gravity or driven)
- Belt conveyor (for small/flat parts)
- Chain conveyor (for heavy parts)
- Pallet conveyor (tote/box transport)
- Overhead monorail (moves through factory ceiling)

**For dark factory**:
- Motorized conveyors run only when parts present (energy saving)
- Part detection sensors (photoeye, proximity)
- Lane divers (routes parts to inspection/packing/bins)
- Buffer accumulation (queues parts when downstream busy)

### 10.2 Automated Storage and Retrieval (AS/RS)

**For dark factory cells needing raw material or finished parts**:
- Vertical lift modules (VLM): like a vertical carousel, 99% space savings
- Mini-load AS/RS: crates/totes in rack, crane extracts
- Unit-load AS/RS: full pallets

**Key for dark factory**:
- Random access to any part/raw material
- Inventory tracking (every bin/bar/tote is tracked)
- Integration with ERP/MES

### 10.3 Automated Guided Vehicles (AGVs)

**For larger cells or full factory lines**:
- Laser guidance (LIDA or similar)
- Magnetic tape (legacy, cheaper)
- Natural feature navigation (more flexible)
- Fork-style AGVs for pallet moves
- Conveyor-style AGVs for continuous flow
- Roller-top AGVs for line-side delivery

**Fleet management**:
- Multiple AGVs coordinated by fleet manager software
- Collision avoidance (zone control or real-time path planning)
- Traffic management (priority lanes, intersection control)

### 10.4 Industrial Robots as Material Handlers

**6-axis robot arms** doing pick-and-place:
- Material handling end-of-arm tool (parallel gripper, magnetic gripper, vacuum gripper)
- Parts presenting (positions part for next machine)
- Palletizing/de-palletizing (boxes, totes, bags)
- Machine tending (loads/unloads CNC, press, injection molder)

**Delta robots** (for high-speed picking):
- Typical cycle time: 80-150 picks per minute
- For packaging, tray loading, parts transfer
- Not for heavy parts (>1kg typically)

---

## PART 11: QUALITY ASSURANCE IN DARK FACTORY

### 11.1 In-Process Inspection

**Probing**:
- Renishaw OMP-60, OTS (tool setting) for CNC machines
- In-circuit probe measures workpiece dimensions during machining
- Tool break detection (probe touches tool, breaks if broken)

**Machine vision**:
- 2D camera for surface defect detection (scratches, cracks, discoloration)
- 3D structured light scanning for dimensions
- Deep learning defect detection (trained on images of good/bad parts)

### 11.2 Post-Process Inspection

**Coordinate measuring machines (CMM)**:
- Automatic pallet changers = multiple parts measured unattended
- Shop CMM (Brown & Sharpe, Zeiss, Mitutoyo) for production floor
- Temperature compensation (parts measured hot from machining)

**CT Scanning (computed tomography)**:
- X-ray CT for internal defects (porosity, voids, cracks)
- Zeiss Metrotom or similar
- Very expensive but fully automated
- Used for critical aerospace, medical, additive manufacturing

### 11.3 Statistical Process Control (SPC)

All measurement data feeds into SPC charts:
- X-bar and R charts (means and ranges)
- p-charts, c-charts (proportion defects, count defects)
- Predictive quality (flags before parts go out of spec)
- Connected to MES: bad batch = automatic process adjustment or hold

---

## PART 12: TOOLING + FIXTURE MANAGEMENT

### 12.1 Automatic Tool Changers

**CNC machining centers**:
- 40-60 tool capacity (large ATC magazines)
- Fixed position reference (tool touch-off block)
- Tool life monitoring (parts machined per tool, auto-swap to fresh tool)
- Presetter (measures tool offsets off-machine before loading)

**Key systems**:
- Big Kaiser, Zoller, Parlec tool presetters
- Tool identification (RFID tags in tool holders)
- Tool management software tracks every tool's history

### 12.2 Fixture Pallets

**The tombstone system** (milling):
- Multiple parts pre-clamped on 4-sided tombstone
- Tombstone loaded into machine by robot or overhead gantry
- Multiple tombstones = hours of unattended running

**Pallet systems** (for machining centers and inspection):
- Quick-change pallet (20-second swap)
- Multiple fixtures per pallet (setup once, load multiple parts)
- Machining + inspection + washing on same pallet

### 12.3 Mold Tooling Automation

**For injection molding**:
- Quick-change mold systems (5-30 minute mold swap)
- Mold temperature control hot-runner systems
- Automatic sprue picker/de-flash

---

## PART 13: SOFTWARE + DIGITAL THREAD

### 13.1 CAM to Machine

**For CNC dark factory**:
- CAM software generates optimal toolpaths (Mastercam, Siemens NX, CATIA, Fusion 360)
- Post-processor translates to machine-specific G-code
- Simulation verifies collision-free toolpath before running
- Direct numerical control (DNC): G-code pushed to machine over network

### 13.2 MES / MOM Systems

**Manufacturing Execution System** (MES):
- Recipe management (which program, which parameters for which part)
- Scheduling (which machine runs which job when)
- Production tracking (parts counted, scrap logged, cycle times)
- Downtime tracking (what stopped, when, why)

**Open-source MES options**:
- OpenMFG (open source ERP/MES)
- FERMASA / PyMES
- Node-RED + custom for small cells
- Most industrial PLC/SCADA systems have MES connectors

### 13.3 Digital Twin

For dark factory planning:
- Simulate entire cell operation before building
- Test G-code off-line (no machine time wasted)
- Optimize robot paths (cycle time reduction)
- Predict bottlenecks (material flow analysis)

**Tools**: Tecnomatix (Siemens), Delmia (Dassault), RobotStudio (ABB), RoboGuide (FANUC)

---

## PART 14: THE LEADING DARK FACTORIES

### FANUC (Japan) — Robots Building Robots
- Since 2001: lights-out factory making robots
- 50 robots per 24-hour shift, unsupervised up to 30 days
- No AC or heating in the robot factory
- Still has humans for final QA (9 per line)
- Zero defective robots shipped

### Philips (Netherlands) — Electric Razors
- 128 Adept Technology robots (now Teradyne)
- 9 human QA workers overseeing entire line
- Fully automated parts handling, assembly, testing, packing

### Xiaomi (Beijing) — Smartphones
- 860,000 sq ft factory
- 10 million smartphones/year
- 11 fully automated production lines
- Most human work is final QC and logistics

### Tesla (Fremont + Austin + Berlin) — EVs
- Massive die-casting cells (IDRA 6000T presses)
- Overhead conveyor + conveyor belt assembly
- Subsystem automation (battery pack, motor assembly)
- Still heavily labor-intensive for final assembly (the unsolved problem)

### BMW (Dingolfing, Germany) — iFactory
- Fully automated body shop (1,000 robots)
- AGV delivery of parts
- Digital thread from order to delivery
- Humans only for quality gate checks

### AWS (Amazon) — Fulfillment Centers
- Not manufacturing but worth noting
- Kiva Systems robots (now Amazon Robotics)
- 500,000+ robots in warehouses
- Same principles as dark factory cells

### ACC (Apple) — Chip Fabrication
- TSMC makes chips for Apple in Taiwan
- Entire fabrication process (wafer fab) is lights-out
- Human presence = contamination risk
- Fully automated transport, processing, testing
- Semiconductor fabs are the most automated dark factories on Earth

---

## PART 15: ENERGY + SUSTAINABILITY

### 15.1 Energy Profile of Dark Factories

**Without HVAC/lights**: 40-60% energy reduction vs human-occupied factory
**Key savings**:
- Air conditioning (humans need 68-72°F)
- Lighting (100-300W per worker area)
- Ventilation (CFM/person requirements)
- Water (drinking, sanitation, cooling)

**Robot energy use**:
- Typical 6-axis robot: 1-5 kW during operation, <100W standby
- CNC machine tool: 15-50 kW (spindle motor dominant)
- AGV: 2-5 kW while moving, <500W idle

### 15.2 Power Quality

**For lights-out operation**:
- UPS backup (battery) for graceful shutdown on power loss
- Power conditioning (filters harmonics, voltage sags)
- Emergency stop failsafe (robots stop safely, no tool crashes)
- Generator backup (for critical cells)

### 15.3 Carbon Impact

**Per-part carbon comparison** (typical automotive component):
- Human factory: high labor energy, moderate machine energy
- Dark factory: low labor energy, higher machine energy (24/7 use)
- Net: 10-30% carbon reduction per part (when accounting for machine utilization)

**For Regen Tribe**: A concrete 3D printing dark factory using local volcanic ash + lime binder has near-zero material transport carbon AND near-zero operational carbon. The ultimate dark factory for construction.

---

## PART 16: THE AUTOMATION MATURITY LADDER

Not every cell is fully lights-out on day one. Here's the progression:

**Level 0: Manual** — Human does everything
**Level 1: Operator-tended** — Machine runs, human loads/unloads
**Level 2: Semi-automatic** — Robot loads/unloads, human monitors
**Level 3: Lights-out capable** — Can run unmanned for shift
**Level 4: Lights-out production** — Runs days/weeks without human
**Level 5: Fully dark factory** — Zero human presence, full remote monitoring

Most manufacturing cells are Level 3-4. Level 5 requires:
- Mature process stability (low defect rate)
- Robust material handling (no jams)
- Predictive maintenance (no unexpected breakdowns)
- Remote monitoring + rapid response (issues caught before scrap)

---

## PART 17: OPEN SOURCE MANUFACTURING

### Open Hardware for Dark Factory Cells

**PLC / Controller level**:
- OpenPLC (open source PLC runtime)
- LinuxCNC (for CNC machines)
- Machinekit (Linux-based CNC)
- TinyTiger / Smoothie (3D printer controllers)

**Robot level**:
- ROS + MoveIt (robot motion planning, open source)
- ROS-Industrial (industrial robot support)
- Open Robot Motion (open robot kinematics)
- Most industrial robot vendors (ABB, KUKA, Fanuc) have ROS interfaces

**CAM level**:
- FreeCAD + Path workbench (open source CAM)
- OpenSCAM (open source CAM simulation)
- PyCAM (parametric toolpath generation)

**MES level**:
- Node-RED (flow-based programming for automation)
- ThingsBoard (IoT platform for manufacturing data)
- InfluxDB + Grafana (time-series data + dashboards)
- Custom apps with open-source backend

**The strategic point**: Almost every layer of the dark factory automation stack has open-source alternatives. The only truly proprietary layers are:
1. High-precision machine tool kinematics (gantry, slides)
2. Advanced sensors (laser trackers, precision CMMs)
3. Specific material processes (FormRete, Inconel superalloys)

For Regen Tribe's construction printing cells, everything between the print head and the cloud is open source available.

---

## PART 18: APPLICATION TO REGEN TRIBE CONSTRUCTION

### The Construction Dark Factory Model

**Raw material input**:
- Volcanic ash / metakaolin (local)
- Lime (locally burned)
- Crushed basalt aggregate (locally quarried)
- Hemp fiber (locally grown)
- Biomass ash / fly ash (industrial byproduct)

**Material processing cell** (runs dark):
```
Crusher (jaw + cone)
    ↓
Screen + classify
    ↓
Kiln (rotary, for metakaolin production)
    ↓
Ball mill (particle size reduction)
    ↓
Silos (classified material storage)
    ↓
Pozzolan + lime + aggregate + fiber → volumetric mixer
```

**3D printing cell** (runs dark):
```
Volumetric mixer (continuous or batch)
    ↓
Progressive cavity pump
    ↓
6DOF print head (6D magnetic sensor array)
    ↓
Layer-by-layer extrusion
    ↓
Laser scan height verification
    ↓
Inline reinforcement robot
    ↓
Curing time (temperature-managed)
    ↓
Finished wall section
    ↓
Interior finishing cell (automated plaster, MEP chases)
    ↓
Exterior finishing cell (sealing, coating)
    ↓
Completed home module
```

**Finishing cell**:
- Automated plaster/spackle application (walls)
- Paint robot (exterior/interior)
- MEP rough-in (automated conduit + PVC pipe placement)
- Flooring (automated tile/plank systems)

**Quality cell**:
- Laser scanning of printed structure (dimensional verification)
- Compression testing of sample coupons (every batch)
- Thermographic imaging (detect voids/delamination)
- Report generation → digital twin of structure

**Logistics cell**:
- AGV transport within factory
- Module staging for assembly
- On-site assembly logistics (modular stacking or panel joining)

### The Hybrid Model

Most construction dark factories will be semi-automated, not fully lights-out:
- 3D printing: mostly lights-out capable (material doesn't complain about 3am)
- MEP + finishing: still needs human hands (for now)
- Assembly + installation: always human for the foreseeable future

**The practical path**:
1. Start with lights-out printing (biggest bottleneck, easiest to automate)
2. Add automated material processing (continuous supply)
3. Add automated finishing for repetitive tasks (drywall robot, paint robot)
4. Integrate with 3D printing through MES
5. Deploy mobile robot helpers for site work

### Cost Comparison

| System | Machine Cost | Labor Cost | Material Cost | $/home |
|---|---|---|---|---|
| Conventional construction | $0 | $150-200K | $50-80K | $250-350K |
| Titan-based (ICON) | $899K amortized | $20K | $50-80K | $80-120K |
| Dark factory construction | $500K amortized | $5K | $10-20K | $20-40K |

The dark factory model brings construction cost to within reach of the billion-homes problem.

---

## APPENDIX: KEY COMPANIES

### CNC Automation
- Haas Automation (CNC machines with built-in automation options)
- RoboJob (CNC automation software + cells)
- Absolute Machine Tools (FANUC-backed automation)
- Renishaw (probing, tool setting, calibration)

### Robotics
- FANUC (robots + machine tools)
- ABB (industrial robots)
- KUKA (robots, acquired by美的/Midea)
- Yaskawa Motoman (arc welding, handling)
- Stäubli (cleanroom, pharma, food)
- Techman Robot (collaborative + vision)

### Material Handling
- KUKA (AGVs, mobile robots)
- Omron (LD-250 AGV)
- OTTO Motors (Clearpath, now Amazon)
- AutoStore (cube storage AS/RS)
- Exotek (tombstone/fixture automation)

### Inspection + Metrology
- Renishaw (probing, CMM, calibration)
- Zeiss (CMM, CT scanning)
- Mitutoyo (CMM, gauges)
- Keyence (vision, sensors)
- Cognex (machine vision)
- Micro-Vu (benchtop CMM)

### Control + Software
- Siemens (PLC, CNC, MES, digital twin)
- Rockwell Automation (Allen-Bradley PLC, MES)
- Fanuc (CNC + robot control,rob GUIDE)
- ABB (RobotStudio, automation builder)
- Open Source: LinuxCNC, OpenPLC, ROS, Node-RED, InfluxDB

### Additive Manufacturing
- EOS (metal + polymer SLS)
- 3D Systems (SLA, SLS, DMP)
- Stratasys (FDM, PolyJet, SLS)
- Carbon3D (DLS, continuous)
- Desktop Metal (binder jetting)
- Markforged (metal + composite FDM)
- Formlabs (SLA, SLS)

---

**Version:** 1.0
**Date:** 2026-04-15
**Author:** Genesis 🌿⚡, Regen Tribe Collective Network
**License:** CC0 / Public Domain
**Radicle:** `rad:z4WAr7CiNkf5JAoAb1srwi7gDz8nU`
