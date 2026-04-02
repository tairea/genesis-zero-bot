# NVC-bot

A tool where users input what they want to say, and the tool provides guidance and options on how to say it in Nonviolent Communication (NVC) format.

## Problem

Many people want to communicate more effectively, especially in community settings where tension can arise. NVC is powerful but requires practice — most people don't have the mental bandwidth to reframe their message in the moment.

## Solution

NVC-bot takes a raw message and transforms it into the NVC 4-part format:

1. **Observation** — What happened (without evaluation)
2. **Feeling** — What you feel (without blame)
3. **Need** — What underlying need is unmet
4. **Request** — What you'd like to happen (specific, doable)

### Example

**Input:** "You never listen to me!"

**Output:**
- **Observation:** "When you check your phone while I'm talking..."
- **Feeling:** "...I feel ignored and unheard."
- **Need:** "Because I value connection and being fully present."
- **Request:** "Could you put your phone away when we're talking, or let me know if you need to step away?"

---

## Development Plan

### Phase 1: Quick Prototype (Day 1)
- Simple prompt-based version in Telegram
- User types message → Genesis or a simple bot reformats it
- No persistent storage needed

### Phase 2: Standalone Bot (Week 1-2)
- Dedicated Telegram bot (`@nvc_bot`)
- Interactive buttons for common situations
- Walks user through the 4-step process step-by-step
- Remembers conversation context within a session

### Phase 3: Full Features (Week 3-4)
- **Patterns:** Tracks common triggers, suggests growth areas
- **Templates:** Pre-built NVC phrases for common scenarios (conflict, feedback, boundaries)
- **Practice Mode:** Users can practice in low-stakes context before using in real situations
- **Stats:** Visualizes communication growth over time

### Tech Stack Options

| Level | Approach | Pros | Cons |
|-------|----------|------|------|
| Quickest | Prompt template in existing chat | No dev needed, works now | Limited interactivity |
| Simple | Telegram bot with inline buttons | Fast build, familiar UI | Basic state management |
| Full | Node.js/Python bot + database | Persistent memory, rich features | More dev time |

### Next Step

Choose a Phase 1 approach and start iterating.

---

*Created: 2026-04-02*
*Champion: Oscar C ii 🔺*