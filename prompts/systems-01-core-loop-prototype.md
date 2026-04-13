# System Creation Prompt 01: Core Feedback Loop Prototype

## Brief

Build the simplest possible working instance of a regenerative community feedback loop. This is not the full methodology — it is the core operational engine that all five research streams depend on. No technology is specified. The choice of technology is the first design decision.

## What the System Must Do (Behavior Specification)

The system must support this cycle, in order:

**Step 1: Sense**
- Collect signals from the community about what is happening
- Community signals include: conversations, decisions made, conflicts that arose, questions asked, things that changed
- Also: ecological signals from the land (even if just one sensor, even if manual observation)
- Store signals with: source, timestamp, content, sender (if available)

**Step 2: Distill**
- From raw signals, extract: what values are present? what tensions are surfacing? what patterns are emerging?
- This is not interpretation — it is structured observation
- Tag each observation with: values detected, stakeholder group, topic area, emotional tenor

**Step 3: Connect**
- New observations are added to the existing record
- Connect new to existing: is this a continuation of a pattern? A departure? A new cluster?
- Link observations to previous decisions: do these signals confirm or challenge earlier governance choices?

**Step 4: Reflect**
- Present the community with a structured reflection artifact
- Format: what have we observed? what patterns are emerging? what tensions exist? what calls for response?
- This is not a report — it is a prompt for collective sensemaking

**Step 5: Respond**
- Community decides how to respond
- Record the decision AND the values that informed it
- If the decision changes structure, update the structural record
- If the decision reveals new values, update the values record

## What Must Be True of the System (Quality Requirements)

**R1: Signals must not be distorted by the collection process**
- Asking people what they value changes what they report
- Observing the community changes what the community does
- The system must make its own observer effect visible

**R2: The community must be able to see and interrogate the record**
- No black boxes — the community can see every signal, every distillation step, every connection
- If the community cannot read the record, they cannot own the process

**R3: The system must be maintainable by the community without external support**
- If the system requires specialized technical knowledge to run, it creates dependency
- Build for a community member with basic computer literacy

**R4: The system must be able to be abandoned and restarted without losing coherence**
- Communities may pause, restart, or abandon the process and return later
- The data model must survive interruption without corruption or incoherence

**R5: Ecological signals must be first-class inputs, not afterthoughts**
- If the system only processes human conversation, it is incomplete
- Even a single environmental indicator (temperature, water level, observation of species) must be integratable

## Design Decisions to Make

These are intentionally left open. They are the creative work of this prompt:

**1. Data model**
- What is the minimum data structure that can store signals, observations, decisions, and their relationships?
- What is the schema for connecting new observations to existing patterns?
- How do you represent "tension" as a first-class data type?

**2. Collection interface**
- How do community members submit signals? (Telegram bot? Form? Voice note?)
- How are ecological signals ingested? (Manual entry? Automated sensor?)
- How do you prevent the collection interface from becoming a surveillance tool?

**3. Distillation method**
- Who or what does the first-pass distillation? (Community members? Facilitator? AI?)
- How do you prevent distillation from imposing interpretation rather than surfacing observation?
- What is the format for a distillation artifact?

**4. Reflection artifact**
- What does the community see when it's time to reflect?
- How is it delivered? (Document? Presentation? Dashboard?)
- Who presents it? (Facilitator? Rotating community member? The system itself?)

**5. Response recording**
- How is a community decision linked to the signals that informed it?
- How do you record dissent — the values that lost, not just the values that won?
- How do you make the decision record queryable by future community members?

## Deliverable

**A prototype system** that runs the 5-step cycle described above, with:
- A data model (even if minimal)
- A signal collection interface (even if just a form)
- A distillation step (even if just structured observation by a human)
- A reflection artifact template
- A decision recording format that links to prior signals

The prototype must be tested with REAL community data — either from an existing community or constructed from realistic scenarios.

## What to Build vs. What to Specify

If you are an AI agent working this prompt:
- You have the authority to BUILD any software component you can implement
- You have the authority to SPECIFY interfaces and protocols that will be implemented by other systems
- Where you cannot build, specify precisely enough that a competent developer could build it

## Constraints

- Do not introduce technology complexity that isn't justified by the requirements
- Do not defer decisions by saying "it depends on the context" — make a reasonable default choice and document it
- The prototype must actually run, not just be a specification document