# Closed-Loop Life Support: Regenerative Habitat Core

## Guiding Principle
Every joule, every liter, every molecule counts. Eliminate status signaling, optimize for survival density.

---

## 1. AIR

Requirements per person/day:
- O2 consumption: ~550L (≈0.7kg)
- CO2 production: ~0.9kg
- Air volume needed: 3-5m³ minimum (habitat volume)

| Sub-system | Technology | Specs | Power |
|------------|-----------|-------|-------|
| **CO2 Scrubbing** | Solid amine ( amine scrubber) or LiOH canisters | Regenerable vs one-shot | 30-50W (regenerable) |
| **O2 Generation** | Electrolysis (water) or O2 concentrator | 0.5-1 kg/day | 3-5 kWh/kg O2 |
| **Air Filtration** | HEPA + activated carbon | 99.97% @ 0.3μm | 10-20W continuous |
| **Humidity Control** | Condensate collection / desiccant | Target: 40-60% RH | 20-40W |

Closed-loop trick: Plants (hydroponic/aeroponic) naturally scrub CO2 → produce O2. 50-100m² of leafy greens per person handles most O2/CO2 balance.

---

## 2. WATER

Requirements per person/day:
- Drinking: 2-3L
- Hygiene: 5-10L
- Total loop: 15-25L (including all outputs)

| Sub-system | Technology | Specs | Recovery Rate |
|------------|-----------|-------|---------------|
| **Greywater Filter** | Membrane + UV | <10ppm TSS | 85-90% |
| **Urine Treatment** | Struvite precipitation + nitrification | N/P recovery | 95% |
| **Feces → Compost** | Vermicomposting or black soldier fly | Pathogen kill in 48h | 100% |
| **Atmospheric Condensate** | Cold surfaces + drainage | 2-5 L/day per person | — |
| **Rainwater/Source** | First-flush diverter + filtration | 5000+ mm catch | — |
| **Final Purification** | UV + activated carbon + RO (sparingly) | Potable std | 99.9% |

Budget: ~20-30L/person/day total throughput

---

## 3. FOOD

Caloric requirement: ~2000-2500 kcal/person/day

| System | Yield | Space | Notes |
|--------|-------|-------|-------|
| **Hydroponic Greens** | 20-50 kg/m²/year | 2-3 m²/person | Fast turnover, high nutrition density |
| **Sprouts/Microgreens** | 5-10 kg/m²/batch | 0.5 m² | 7-10 day cycles |
| **Mushrooms (oyster)** | 10-20 kg/m²/year | 1 m² | Decomposes waste, high protein |
| **Insect farming** (BSF larvae) | 100+ kg/m²/year | 0.5 m² | 25-50% protein, recycles waste |
| **Aquaponics** (tilapia/crayfish) | 10-20 kg/m²/year | 5-10 m² | Nitrates → plants, protein |
| **Staples** (wheat, rice, potatoes) | 200-400 kg/m²/year | 10-20 m² | Grain storage, processing |

Minimum viable: 15-25 m²/person for caloric + nutritional diversity

Optimization: Stack functions — aquaponics does protein + filtration in one loop.

---

## 4. WASTE

| Stream | Processing | Output | Recovery |
|--------|-----------|--------|----------|
| **Humanure** | Thermophilic composting (55-70°C, 2-3 weeks) | Compost → food crops | N, P, K |
| **Greywater** | Membrane filtration + UV | Irrigation water | H2O |
| **Urine** | Storage (6mo) or struvite reactor | Fertilizer | N, P |
| **Food scraps** | BSF larvae or vermicompost | Animal feed + compost | Biomass |
| **Inorganics** | Metal recycling, glass crushing | Raw materials | ~80% recyclable |
| **Atmospheric CO2** | Algae bioreactor (optional) | Biofuel + O2 | Carbon |

---

## 5. POWER

Budget per person: 150-250W continuous (residential), 500W peak

| Source | Capacity | Notes |
|--------|----------|-------|
| **Solar PV** | 3-5 m²/person | 200-300 W/m², batteries essential |
| **Wind** (if viable) | 100-500W depending on site | Must be reliable |
| **Battery Storage** | 3-5 kWh/person | LiFePO4 recommended (long life) |
| **Thermal Storage** | Phase-change or water tank | 50-100 L hot + cold |
| **Backup Generator** | Propane/biogas | Emergency only |

Critical loads: Air circulation, water pumping, UV sterilization, communications — must run 24/7.

---

## 6. THERMAL

| Need | Solution |
|------|----------|
| **Heating** | Solar thermal + heat pump recovery from waste heat |
| **Cooling** | Evaporative + nocturnal radiation + ground coupling |
| **Thermal Mass** | Water containers, PCM (paraffin salts), stone/concrete |
| **Cooking** | Solar cooker + induction (battery) — avoid gas dependency |
| **Temperature Target** | 18-24°C interior, 5-15°C for cold storage |

Key insight: Thermal inertia beats active HVAC. 500L water tank = ~500 Wh/°C thermal buffer.

---

## Automation Architecture

```
+-------------------------------------------------------------+
|                    CENTRAL CONTROLLER                       |
|         (PLC / Industrial Raspberry Pi / Arduino)           |
+-------------------------------------------------------------+
          |            |            |            |
    +-----+-----+ +----+----+ +----+----+ +----+-----+
    |  SENSORS  | | SENSORS | | SENSORS | | SENSORS  |
    | (Air)     | | (Water) | | (Power) | | (Thermal)|
    +-----+-----+ +----+----+ +----+----+ +----+-----+
          |            |            |            |
    +-----+-----+ +----+----+ +----+----+ +----+-----+
    | ACTUATORS | |ACTUATORS| |ACTUATORS| | ACTUATORS|
    | (Fans,    | |(Pumps,  | |(Inverters| |(Valves, |
    | Valves)   | | Valves) | | Breakers)| | Heaters)|
    +-----------+ +---------+ +----------+ +----------+
```

### Sensor Network (per person)
- Air: CO2 (NDIR), O2 (electrochemical), VOCs, temperature, humidity, pressure
- Water: pH, ORP, turbidity, conductivity, flow meters
- Power: Voltage, current, wattage, battery SOC
- Thermal: Temp sensors (10-20 points), flow sensors
- Food: Soil moisture, pH, EC, light PAR, water temp (aquaponics)

### Communication
- Wired: RS-485 / CAN bus (reliable, industrial)
- Wireless: LoRa for sensors, WiFi for high-bandwidth
- Local dashboard: Grafana + InfluxDB on local server

### Control Philosophy
- Reactive: Simple threshold logic (if CO2 > 1200ppm → scrubber on)
- Predictive: Forecast weather, occupancy, adjust buffers
- Alert hierarchy: Warning (log) → Alert (notify) → Critical (actuate safety)

---

## Failure Modes & Redundancy

| System | Failure Mode | Mitigation | Priority |
|--------|--------------|------------|----------|
| **Air → CO2** | Scrubber fails | Redundant canisters + natural ventilation | CRITICAL |
| **Air → O2** | Plants die | Emergency O2 storage (cylinders) | CRITICAL |
| **Water** | Filtration fails | 3-day water reserve, backup purification | HIGH |
| **Power** | Solar down 3+ days | Battery buffer + backup generator + reduced load mode | CRITICAL |
| **Food** | Crop failure | Seed bank + multiple systems (aquaponics, mushrooms, insects) | HIGH |
| **Thermal** | Heating/cooling fails | Thermal mass buys time, passive survivability design | MEDIUM |
| **Automation** | Controller dies | Manual overrides on all critical valves/pumps | HIGH |

Rule: 2N-1 redundancy on anything that kills you in <4 hours.

---

## Resource Budget Summary (per person/day)

| Resource | Input | Output | Loop Efficiency |
|----------|-------|--------|-----------------|
| **Water** | 25L (all sources) | 20L recoverable | 80% |
| **Calories** | 0 (self-produced) | 2500 kcal | — |
| **Power** | 150-250W avg | — | — |
| **Air** | Makeup O2 + scrubber regen | CO2 for plants | 95%+ |
| **Heat** | Solar + waste recovery | Radiated/vented | Variable |

---

## "Parasitic Bullshit" to Flag for Deletion

| Item | Why | Replacement |
|------|-----|-------------|
| Decorative landscaping | Water/space sink | Food-producing plants only |
| Individual climate control per room | Energy waste | Zoned thermal mass |
| Fast fashion imports | Waste stream | Local textile production |
| Entertainment electronics | Power sink | Books, games, communal activities |
| Personal vehicles | Resource hog | Communal tools, bikes |
| Imported luxury foods | Supply chain fragility | Local seasonal diet |
| Planned obsolescence | Waste | Repairable, modular design |

---

## Execution Priorities

### Phase 1: Survival Critical (Week 1-4)
1. Air: CO2 scrubber + backup O2
2. Water: Filtration + 3-day reserve
3. Power: Solar + battery
4. Thermal: Basic heating/cooling + thermal mass
5. Food: 3-day reserve + sprout system

### Phase 2: Stabilization (Month 1-3)
1. Install hydroponics/aquaponics
2. Set up greywater reclamation
3. Automate sensor monitoring
4. Build compost systems
5. Establish seed bank + multiple crops

### Phase 3: Optimization (Month 3-12)
1. Tune automation loops
2. Maximize closure rates
3. Add redundancy where budget allows
4. Reduce external dependencies
5. Expand food diversity

### Phase 4: Scaling (Year 1+)
- Duplicate modules per 10 people
- Centralize utilities (power plant, water treatment)
- Distributed food production
- Build community skills matrix

---

## Scaling Formula

For N people:
- Water: 20L/person/day × N + 20% buffer → treatment capacity
- Power: 200W × N average, 500W × N peak → solar + battery
- Food: 25m² × N minimum (intensive)
- Air: 5m³ × N volume minimum, scrubber scales ~50W/10 people
- Automation: One controller per 20 people, networked

---

Generated by Genesis for Regen Tribe Collective Network
