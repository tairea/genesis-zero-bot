# Parallel Agentic Loops Playbook

## Overview
This playbook enables running multiple Ralph orchestrator agents in parallel across different project domains, with coordination and result synthesis.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    MASTER ORCHESTRATOR                          │
│              (coordinates all parallel agents)                   │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│  ECOLOGY      │   │  HARDWARE     │   │  HUMAN SYSTEMS│
│  Agent        │   │  Agent         │   │  Agent        │
│  (research)   │   │  (spec)       │   │  (docs)       │
└───────────────┘   └───────────────┘   └───────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RESULT SYNTHESIS                              │
│            (aggregates all outputs into unified plan)           │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

```bash
# Run all parallel agents for a full regenerative neighborhood analysis
ralph parallel \
  --config ralph.yml \
  --agents ecology,hardware,human-systems,economy,software \
  --prompt tasks/master-playbook/PROMPT.md \
  --output results/

# Run specific domain agents
ralph parallel \
  --config ralph.yml \
  --agents governance,community \
  --prompt tasks/governance/PROMPT.md
```

## Preset Mapping by Domain

| Domain | Primary Preset | Secondary Preset | Use Case |
|--------|---------------|------------------|----------|
| ECOLOGY | `research` | `gap-analysis` | Environmental analysis |
| HARDWARE | `spec-driven` | `feature` | Infrastructure design |
| HUMAN SYSTEMS | `documentation` | `research` | Policy/Governance docs |
| ECONOMY | `research` | `spec-driven` | Financial models |
| SOFTWARE | `feature` | `debug` | Implementation |
| GOVERNANCE | `spec-driven` | `documentation` | Decision frameworks |

## Parallel Execution Examples

### Example 1: Full Framework Analysis
```bash
# Spawn 5 parallel agents, one for each main domain
ralph spawn --name ecology-agent \
  --preset research \
  --prompt tasks/ecology/climate/PROMPT.md \
  --model minimax-m2.1

ralph spawn --name hardware-agent \
  --preset spec-driven \
  --prompt tasks/hardware/housing/PROMPT.md \
  --model minimax-m2.1

ralph spawn --name humansystems-agent \
  --preset documentation \
  --prompt tasks/human-systems/governance/PROMPT.md \
  --model minimax-m2.1

ralph spawn --name economy-agent \
  --preset research \
  --prompt tasks/economy/currency/PROMPT.md \
  --model minimax-m2.1

ralph spawn --name software-agent \
  --preset feature \
  --prompt tasks/software/ai-ml/PROMPT.md \
  --model minimax-m2.1
```

### Example 2: Governance Deep-Dive
```bash
# Run parallel agents on governance subdomains
ralph parallel \
  --preset documentation \
  --domain governance \
  --subdomains decision-making,legal,roles,conflict-resolution
```

## Agent Configuration Presets

### Research Agent (for ECOLOGY, ECONOMY)
```yaml
agent:
  model: minimax-m2.1
  temperature: 0.7
  max_tokens: 8000
  
workflow:
  - observe: Gather initial data
  - orient: Contextualize findings
  - decide: Prioritize insights
  - act: Produce research output

output:
  format: markdown
  structure: summary_findings_recommendations
```

### Spec-Driven Agent (for HARDWARE, GOVERNANCE)
```yaml
agent:
  model: minimax-m2.1
  temperature: 0.3
  max_tokens: 12000
  
workflow:
  - analyze: Requirements analysis
  - design: Create specifications
  - validate: Cross-reference constraints
  - document: Produce spec document

output:
  format: markdown
  structure: requirements_specifications_implementation_notes
```

### Documentation Agent (for HUMAN SYSTEMS)
```yaml
agent:
  model: minimax-m2.1
  temperature: 0.5
  max_tokens: 10000
  
workflow:
  - gather: Collect existing docs
  - synthesize: Combine sources
  - structure: Organize logically
  - write: Produce final guide

output:
  format: markdown
  structure: overview_details_examples_references
```

## Coordination Patterns

### Pattern 1: Sequential Handoff
```
Agent A → Agent B → Agent C
```
Use when: Output of one feeds into next

### Pattern 2: Parallel + Merge
```
    ┌─ Agent A ─┐
    │           │
Master ─┼─ Agent B ─┼─→ Merge → Final Output
    │           │
    └─ Agent C ─┘
```
Use when: Independent analysis, unified output

### Pattern 3: Supervisor Pattern
```
Supervisor Agent
    │
    ├──→ Sub-Agent A (delegate)
    ├──→ Sub-Agent B (delegate)  
    └──→ Sub-Agent C (delegate)
```
Use when: Complex multi-domain coordination

## Result Synthesis

After parallel execution, run synthesis:

```bash
ralph synthesize \
  --inputs results/ecology.md,results/hardware.md,results/humansystems.md \
  --output results/full-framework.md \
  --mode cross-reference
```

## Monitoring Parallel Runs

```bash
# Check status of all parallel agents
ralph status --all

# Get output from specific agent
ralph output --agent ecology-agent

# Kill stuck agent
ralph kill --agent hardware-agent
```

## Best Practices

1. **Use consistent model** across parallel agents for coherent output
2. **Set appropriate timeouts** - research takes longer than documentation
3. **Monitor token usage** - parallel agents can consume quickly
4. **Always synthesize** - individual outputs need cross-referencing
5. **Version control** - commit results after each parallel run

## Playbook Files

Each project folder should contain:
- `PROMPT.md` - Task definition
- `preset.yml` - Agent configuration  
- `expected-output.md` - What success looks like
- `synthesis-guide.md` - How to merge with other domains
