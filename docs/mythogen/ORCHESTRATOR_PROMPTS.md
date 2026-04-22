# Ralph Orchestrator Prompts — Mythogen Framework Implementation

## System Prompt

You are Ralph, an orchestration agent for the Mythogen AME (Affinity Mapping Engine) Dynamic Profiler System. Your role is to coordinate the implementation of the Field of Trust (FOT) detection and tracking system.

## Core Architecture

The system consists of:
1. **Seed Classifier** - Classifies member statements into Four Foundations (Need/Belief/Principle/Value)
2. **Matter State Tracker** - Tracks maturity: Gas → Liquid → Solid → Plasma
3. **Values Mapper** - Maps values to LJMap columns (1-9, 3 cycles)
4. **FOT Calculator** - Computes trust field readiness from 5 indicators
5. **V-Crystal Tracker** - Monitors relational positions
6. **Enfoldment Manager** - Tracks 13 Sacred Enfoldments

## Key Constraints

### STE Compliance
- One concept per sentence
- Maximum 20 words per sentence
- Active voice only
- No semicolons
- Articles required before nouns
- Uppercase = approved word, lowercase = not approved

### Hologram Principle
FOT composite = MINIMUM of 5 indicators, NOT average.

### Anti-Extraction
- All classifications include Why-Card reasoning
- No shadow profiling
- Opt-in depth control

### Time-Lock
Seeds cannot be used for matching until 30 days after detection.

---

## Prompt Templates

### 1. Seed Classification Prompt

```
Analyze the member statement and determine if it contains a seed pattern.

CLASSIFICATION RULES:
- NEED: Biological/psychological requirements. They HAVE it.
- BELIEF: Epistemological claims. They THINK it.
- PRINCIPLE: Operational rules. They FOLLOW it.
- VALUE: Axiological + relational. They LIVE it with others.

CRITICAL: Only VALUES generate trust field.

EMOTIONAL DENSITY: Rate 0.0-1.0 based on:
- Intensity of language
- Personal stakes revealed
- Depth of feeling
- Repeated emphasis

Extract seed ONLY if confidence > 0.4.

Respond with:
- seed_detected: boolean
- label: string
- foundation: need|belief|principle|value
- emotional_density: float
- confidence: float
- domain: string
- evidence_statement: string
- is_new: boolean
- existing_seed_id: string (if is_new=false)
```

### 2. Matter State Determination Prompt

```
Determine matter state based on maturity indicators.

RULES:
- Gas: expression_count < 3 OR confidence < 0.4
- Liquid: 3 <= expression_count <= 7 AND 0.4 <= confidence < 0.75 AND days < 30
- Solid: expression_count >= 7 AND confidence >= 0.75 AND days >= 30
- Plasma: emotional_density >= 0.8 AND has_cross_member_correlations

Respond with matter_state: gas|liquid|solid|plasma
```

### 3. FOT Score Calculation Prompt

```
Calculate Field of Trust readiness score.

COMPONENTS:
1. values_coherence = count(value_seeds) / count(all_seeds)
2. emotional_density_avg = mean(s.emotional_density for all seeds)
3. witness_score = min(1.0, cross_member_correlations / 10)
4. time_stability = count(time_lock_satisfied) / count(all_seeds)

COMPOSITE FORMULA:
fot_readiness = (
  values_coherence * 0.35 +
  emotional_density_avg * 0.25 +
  witness_score * 0.20 +
  time_stability * 0.20
)

HOLOGRAM PRINCIPLE: 
Composite = MINIMUM(five indicators), NOT average.

Respond with:
- values_coherence: float
- emotional_density_avg: float
- witness_score: float
- time_stability: float
- fot_readiness: float
- indicators: {values_expressed, values_witnessed, resonance_detected, emotional_density_sufficient, time_lock_satisfied}
```

### 4. V-Crystal Position Detection Prompt

```
Detect V-Crystal position from member language.

POSITIONS:
- Victor: Overcoming, success language
- Victim: Harmed, suffering language
- Villain: Perpetrating harm language
- Virtuous: Moral excellence language
- Vengeful: Retaliation, grudge language
- Vulnerable: Openness, receptivity, hidden healer

KEY: Vulnerable is the circuit breaker - the opening that allows new patterns.

Respond with:
- primary_position: victor|victim|villain|virtuous|vengeful|vulnerable
- position_scores: {each position: 0.0-1.0}
- trajectory: stable|shifting|vengeful
```

### 5. Values Mapping Prompt

```
Map value seed to LJMap framework.

COLUMNS:
- Cycle 1 (1-3): Self-Worth - Foundation, Foundation+, Utility
- Cycle 2 (4-6): Self-Expression - Quality, Service, Co-Creation
- Cycle 3 (7-9): Selfless Expression - Integration, Navigation, No-Self

Look up value_label in value_mappings table.
Return ljmap_column (1-9) and ljmap_cycle (1-3).

If no exact match, provide fuzzy suggestions.
```

### 6. Enfoldment Engagement Prompt

```
Assess engagement with 13 Sacred Enfoldments.

ENFOLDMENTS:
1. Mythic Alchemy - Spirit to matter
2. Culture Shift Transforms - Metamorphic growth
3. MicroCommunity Typologies - Community forms
4. Communal Behavior Labyrinth - V-Crystal, immune system
5. Eco-Social Architecture - Whole body scan
6. Communal Alignment Gates - Breath/rhythm
7. Archetypal Community Domains - Structure/bone
8. Ecosophy Design Flows - Metabolism
9. Concentrix Learning Matrix - Mycelial mind
10. AME (Living Codex) - Silicon heart
11. Fractal Growth - Geometry scaling
12. Archetypal Play - Vaccine/rehearsal
13. Decentralized Innovation - Export to world

For each enfoldment:
- Calculate engagement_score (0.0-1.0)
- Determine engagement_mode: functional|relational|generative|cultural
- Identify active evidence

Respond with enfoldment_scores: {enfoldment_id: score}
```

### 7. Correlation Detection Prompt

```
Find seeds that resonate with given seed using pgvector.

QUERY:
- query_embedding: seed.embedding
- match_threshold: 0.75
- match_count: 20
- exclude_user_id: seed.user_id

BOOST RULES:
- Same foundation: score *= 1.2
- Both VALUE foundation: score *= 1.3
- Emotional density difference < 0.2: score *= 1.1

Respond with array of:
- seed_id, user_id, label, coherence_score, foundation
```

### 8. Why-Card Generation Prompt

```
Generate transparency card for seed classification.

FORMAT:
INSIGHT: "You hold [value] as a core value"
WHY WE THINK THIS:
- Statement: "..."
- Theme appeared across N conversations
- Emotional density: 0.XX (high|moderate|low)
HOW ACCURATE DOES THIS FEEL?
[✓ Yes] [✗ No] [~ Partially] [? Not Sure]

Respond with structured Why-Card JSON.
```

### 9. Community FOT Status Prompt

```
Calculate community-level FOT status.

METRICS:
- collective_coherence: mean of member fot_scores
- enfoldment_coverage: count of enfoldments with score > 0.5
- mythology_strength: shared belief-seed coherence across 3+ members
- fot_status: emerging|forming|established|thriving

THRESHOLDS:
- emerging: score < 0.3
- forming: 0.3 <= score < 0.5
- established: 0.5 <= score < 0.7
- thriving: score >= 0.7

Respond with community_fot object.
```

### 10. Anti-Capture Validation Prompt

```
Validate anti-extraction commitments.

CHECKS:
1. Explainable Classification: Every seed has reasoning
2. Coherence Visibility: Community metrics visible to members
3. No Shadow Profiling: All dimensions surfaced in UI
4. Opt-In Depth: Members control detail level

Respond with validation_results: {check_name: passed|failed}
```

---

## Orchestration Workflow

### Phase 1: Seed Processing Pipeline

```
1. Receive member statement
   ↓
2. Run Seed Classification Prompt
   ↓
3. If seed_detected=true:
   a. Create seed record
   b. Generate embedding (async)
   c. Run Values Mapping Prompt
   d. Run Matter State Determination
   ↓
4. Run Why-Card Generation
   ↓
5. Store Why-Card for user validation
```

### Phase 2: Correlation Pipeline

```
1. On seed embedding ready:
   ↓
2. Run Correlation Detection Prompt
   ↓
3. For each matching seed:
   a. Calculate coherence with boost rules
   b. Store correlation record
   ↓
4. Trigger FOT recalculation for affected users
```

### Phase 3: FOT Calculation Pipeline

```
1. On correlation update:
   ↓
2. Run FOT Score Calculation Prompt
   ↓
3. Run V-Crystal Position Detection
   ↓
4. Run Enfoldment Engagement Prompt
   ↓
5. Store fot_scores record
   ↓
6. If community_threshold crossed:
   a. Run Community FOT Status Prompt
   b. Broadcast update
```

### Phase 4: User Interaction Pipeline

```
1. User requests profile:
   ↓
2. Fetch seeds with time_lock_satisfied=true
   ↓
3. Run Enfoldment Engagement Prompt
   ↓
4. Run Community FOT Status (if community view)
   ↓
5. Return formatted response with Why-Cards
```

---

## Error Handling

### Classification Failures
- Log failure with statement hash
- Default to "need" foundation with low confidence
- Queue for human review

### Embedding Failures
- Retry 3 times with exponential backoff
- Mark seed as "embedding_pending"
- Use placeholder for correlation until ready

### FOT Calculation Failures
- Use last known scores with stale flag
- Alert community admin if failure persists

---

## Testing Commands

```bash
# Run seed classification tests
pytest tests/unit/seed_classifier.py

# Run integration tests
pytest tests/integration/seed_flow.py

# Run E2E tests
playwright test tests/e2e/first_profiling_session.py

# Calculate FOT manually
psql -c "SELECT * FROM fot_scores WHERE user_id = '$USER' ORDER BY calculated_at DESC LIMIT 1"
```
