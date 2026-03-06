# SKILL: Ralph Presets Collection

## Purpose
Create and manage Ralph Orchestrator hat-collection presets for multi-agent AI workflows.

## What is Ralph?
Ralph is an AI agent orchestrator that uses "hats" (specialized agent roles) coordinated via events. Each preset defines:
- Hats (agents with specific responsibilities)
- Triggers (what activates each hat)
- Publications (events emitted when hat completes)
- Instructions (detailed prompts for each role)

## Architecture

```
Event → Hat → Execute → Emit Event → Next Hat → ...
```

## Presets Included

| Preset | Pattern | Best For |
|--------|----------|----------|
| tdd-red-green | Critic-Actor Pipeline | Test-driven development |
| adversarial-review | Red Team/Blue Team | Security-critical code |
| socratic-learning | Socratic Dialogue | Learning new codebases |
| spec-driven | Contract-First | Complex requirements |
| mob-programming | Rotating Roles | Multiple perspectives |
| scientific-method | Hypothesis Testing | Debugging |
| code-archaeology | Archaeological Dig | Legacy code |
| performance-optimization | Measure-Optimize | Performance tuning |
| api-design | Outside-In | API design |
| documentation-first | Docs-First | Clear docs |
| incident-response | OODA Loop | Production incidents |
| migration-safety | Expand-Contract | Safe migrations |
| confession-loop | Confidence Gate | Quality verification |

## Usage

```bash
# List presets
ralph init --list-presets

# Run with preset
ralph run -c ralph.yml -H builtin:feature
```

## File Structure
```
ralph-presets/
├── SKILL.md           # This file
├── presets/            # YAML preset definitions
│   ├── tdd-red-green.yml
│   ├── adversarial-review.yml
│   └── ...
└── prompts/           # PROMPT.md templates
    ├── tdd-red-green.md
    └── ...
```

## Reproduction
1. Install Ralph CLI
2. Select preset
3. Run with prompt
