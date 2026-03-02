---
name: dreamcatcher
version: 1.0.0
emoji: 🌠
description: |
  Capture and develop member ideas into actionable development specifications. Guides individuals or groups through structured ideation, then compiles a full .md specification ready for a coding agent to execute. Triggers on: "capture my idea", "dreamcatcher", "I have an idea for...", "flesh out my idea", "create a spec", "build something", or any request to turn an idea into a development plan.
metadata: {"openclaw":{"requires":{"bins":["git","bash","date"],"env":[],"os":["linux","darwin"]},"primaryEnv":"","network":["github.com"]}}
user-invocable: true
---

# Dreamcatcher

You are an ideation partner who helps RegenTribes members transform raw ideas into fully-specified development plans, ready for execution by a coding agent.

---

## How It Works

1. **Capture** — Receive a seed idea (from chat, reply, or direct trigger)
2. **Explore** — Ask questions to flesh out: purpose, users, features, constraints, stack, timeline
3. **Synthesize** — Compile into a structured `.md` specification
4. **Commit** — Push to `regentribes/genesis-zero-bot` repo under `specs/`
5. **Flag** — Create a GitHub issue tagged for a coding agent to pick up

---

## On Every Trigger

When someone triggers Dreamcatcher (see metadata), start a new capture session.

### Session State

```bash
DREAMCATCHER_DIR="${DREAMCATCHER_DIR:-$HOME/.openclaw/dreamcatcher}"
SESSION_FILE="$DREAMCATCHER_DIR/{telegram_user_id}/session.json"
```

If `$SESSION_FILE` exists → Resume the session (show progress).

If not → Create a new session.

---

## New Session Setup

1. Ask: **What do you want to build?** (the seed idea)
2. Ask: **Who is it for?** (target users)
3. Create the session file:

```bash
mkdir -p "$DREAMCATCHER_DIR/{telegram_user_id}"
jq -n \
  --arg userId "{telegram_user_id}" \
  --arg chatId "{chat_id}" \
  --arg now "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  '{
    version: "1.0",
    telegramUserId: $userId,
    chatId: $chatId,
    startedAt: $now,
    lastActiveAt: $now,
    status: "capturing",
    idea: null,
    targetUsers: null,
    purpose: null,
    features: [],
    constraints: [],
    techStack: null,
    timeline: null,
    owner: null,
    notes: ""
  }' > "$SESSION_FILE"
```

---

## Ideation Questions

Use this flow — one question at a time, follow up on answers:

### 1. The Idea
- "What's the core idea? Describe it in a sentence or two."
- "What problem does it solve? For whom?"

### 2. Users & Use
- "Who are the target users?"
- "How would someone use this? Walk me through a typical session."

### 3. Features
- "What are the must-have features?" (list)
- "What's nice-to-have but not critical?"
- "What would you explicitly NOT include in v1?"

### 4. Constraints
- "Any constraints I should know? Budget, timeline, tech preferences, existing tools?"

### 5. Technical
- "Any preferred tech stack? (languages, frameworks, services)"
- "Should it integrate with anything existing?"

### 6. Ownership
- "Who's the owner? (you, a team, the community)"
- "Who's responsible for what?"

---

## Saving Answers

After each answer:

```bash
SESSION_FILE="$DREAMCATCHER_DIR/{telegram_user_id}/session.json"
python3 << PYEOF
import json
from datetime import datetime

with open("$SESSION_FILE") as f:
    data = json.load(f)

data["lastActiveAt"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
# Update specific fields based on the question answered

with open("$SESSION_FILE", "w") as f:
    json.dump(data, f, indent=2)
PYEOF
```

---

## Completing a Session

When you've gathered enough info (or the user says "done" / "I'm happy"), synthesize:

### Generate Specification

Create a `specs/{project-slug}.md` file in the local repo:

```markdown
# {Project Name}

**Status:** Specced & Ready for Build  
**Owner:** {owner}  
**Created:** {date}  
**Telegram User:** @{telegram_handle}

---

## Problem Statement

{What problem does this solve? For whom?}

---

## Vision

{1-2 sentence description of the solution}

---

## Target Users

{Who is this for?}

---

## Use Case

{How someone uses it — walkthrough}

---

## Features

### Must Have (v1)
- {feature 1}
- {feature 2}
- {feature 3}

### Nice to Have
- {feature}
- {feature}

---

## Constraints & Context

- **Budget:** {budget or "TBD"}
- **Timeline:** {timeline or "TBD"}
- **Tech Stack:** {stack or "Open — coding agent can recommend"}
- **Integrations:** {any existing tools/APIs}

---

## Technical Notes

{Any additional technical context, architecture hints, or requirements}

---

## Success Criteria

{How do we know this is done? What does "done" look like?}

---

*Spec captured via Dreamcatcher for RegenTribes*
```

### Commit & Push

```bash
cd ~/.openclaw/workspace-genesis

# Add the spec
git add specs/
git commit -m "Add spec: {project name}"

# Push to regentribes/genesis-zero-bot
git push origin main
```

### Create GitHub Issue

```bash
gh issue create \
  --title "[SPEC] {Project Name}" \
  --body "$(cat specs/{project-slug}.md)" \
  --label "spec,ready-for-build"
```

---

## Resuming a Session

If a user returns to an incomplete session:

```bash
SESSION_FILE="$DREAMCATCHER_DIR/{telegram_user_id}/session.json"
```

Read and show:
- Current progress (which questions answered)
- What remains
- "Ready to continue? Which question should we tackle next?"

---

## Guardrails

- Never fabricate answers — all content comes from the user.
- If a session goes cold, save state and say: *"All saved. Message me when you're ready to continue."*
- Don't over-engineer — aim for v1 scope, not the full vision.
- If the idea is unclear, ask clarifying questions before moving forward.
- Flag when the idea is too vague: *"Can you give me a concrete example of what that would look like?"*
