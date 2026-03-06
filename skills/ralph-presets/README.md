# Ralph Presets — Regen Tribe Framework

Collection of Ralph Orchestrator presets and task templates for regenerative neighborhood development.

## Quick Start

```bash
# Clone repository
git clone https://github.com/genesis-zero-bot/ralph-presets
cd ralph-presets

# Run a task
ralph run -c ralph.yml -H presets/research.yml -p "tasks/ecology/climate/PROMPT.md"
```

## Project Structure

```
ralph-presets/
├── README.md                    # This file
├── ralph.yml                   # Main config
├── presets/                     # Ralph preset configs
│   ├── research.yml           # Research workflows
│   ├── documentation.yml      # Doc creation
│   ├── spec-driven.yml        # Specification-first
│   └── minimal/               # Lightweight configs
├── tasks/                      # Task prompts (categorized)
│   ├── ecology/               # Environmental systems
│   ├── hardware/              # Physical infrastructure
│   ├── human-systems/         # Social systems
│   ├── economy/               # Economic systems
│   ├── software/              # Technology
│   ├── governance/            # Decision-making
│   └── master-planning/      # Planning
├── playbooks/                  # Orchestration guides
│   └── parallel-agentic-loops.md  # Parallel execution playbook
└── docs/                      # Generated documentation
```

## Preset Mapping

| Domain | Preset | Purpose |
|--------|--------|---------|
| ECOLOGY | `research` | Environmental analysis |
| HARDWARE | `spec-driven` | Infrastructure specs |
| HUMAN SYSTEMS | `documentation` | Policy guides |
| ECONOMY | `research` | Financial models |
| SOFTWARE | `feature` | Implementation |
| GOVERNANCE | `spec-driven` | Decision frameworks |

## Usage

```bash
# Single domain research
ralph run -c ralph.yml -H presets/research.yml -p "tasks/ecology/climate/PROMPT.md"

# Documentation task
ralph run -c ralph.yml -H presets/documentation.yml -p "tasks/hardware/housing/PROMPT.md"

# Parallel execution (see playbooks/parallel-agentic-loops.md)
ralph parallel --config ralph.yml --agents ecology,hardware,human-systems
```

## GitHub
https://github.com/genesis-zero-bot/ralph-presets
