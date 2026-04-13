# System Creation Prompt 02: Values-Architecture Bridge Prototype

## Brief

Build the prototype for the most structurally novel component of the five-stream methodology: the operational bridge between what a community values and how its systems are designed. This is the gap that no existing framework fills.

## What This Bridge Must Do

**The problem it solves:**
A community makes a governance decision. Six months later, nobody remembers why that decision was made. The decision becomes "how things are done." New community members inherit a structure without knowing the values that created it. Over time, the community drifts from its own values because the connection between decisions and values was never recorded.

**What the bridge does:**
1. When a governance decision is made, explicitly record: which stakeholder VALUES were in play
2. When those values conflict, record WHICH values won and WHICH were marginalized
3. When the community evaluates a structure (a role, a process, a physical arrangement), trace it back: what values originally justified this?
4. When the community considers a new decision, surfacing existing structures that embody the competing values — so the community can see what they are choosing between

## Core Data Model (Design This)

The minimum viable data model must support these relationships:

```
STAKEHOLDER ←→ VALUES ←→ DECISION ←→ STRUCTURE

stakeholder: a person, group, or entity (human or ecological) that has values
values: what matters to this stakeholder (from the relational values framework)
decision: a governance choice made by the community
structure: an enacted role, process, agreement, or physical arrangement
```

Each edge in this graph must be TIME-TAGGED and REVISABLE.

**Critical fields on the DECISION node:**
- decision_text: what was decided
- decision_date: when
- values_in_tension: [list of values that were in conflict]
- values_that_won: [list — may be one or many]
- values_that_lost: [list — including dissent]
- stakeholder_positions: {stakeholder: which values they held}
- dissenting_view: what was the dissent, who held it

**Critical fields on the STRUCTURE node:**
- structure_type: role | process | agreement | physical
- structure_name: name
- originating_decision_id: link to the decision that created this
- current_status: active | suspended | dissolved | evolved
- carries_values: [list of values this structure currently embodies]
- began_date: when it became active
- review_triggers: what events or cadence should prompt review

## The Conflict Surfacing Protocol

When the system detects a new governance decision is needed:
1. Query existing STRUCTURE nodes that are relevant to this decision domain
2. For each structure, trace its originating_decision and extract values_that_won
3. Present: "Here are the structures that currently exist in this domain, and the values that created them"
4. This surfaces: the community is not starting fresh — they are choosing whether to maintain or disrupt existing values-embodied-in-structure

When conflict arises:
1. Each party articulates their position as VALUES (not as arguments)
2. The system maps: which structures would embody which values if this decision goes which way
3. The system presents: "If Party A wins, this existing structure is reinforced. If Party B wins, that structure is changed."
4. This converts abstract values conflict into concrete structural consequence

## Reflection Questions the System Must Support

**For individuals:**
- What values do I hold that the community's current structures do not reflect?
- What structures am I regularly bumping against?

**For the community:**
- What values have we been privileging in our decisions?
- What values have we been marginalizing?
- What structures are we maintaining that no longer reflect our current values?
- Where are we choosing between values and not realizing it?

**For ecological integration:**
- What ecological carrying capacity constraints does this decision approach?
- Which structures embody our ecological values and which are in tension with ecosystem health?

## User Interface (Design This)

The system needs interfaces for:

**1. Decision Recording** (when a decision is made)
- Who is recording? (facilitator, community member)
- Decision text (free form)
- Values in tension (select from community values vocabulary + free entry)
- Values won/lost (selection + dissent recording)
- Link to existing structures affected

**2. Structure Tracing** (when reviewing structures)
- Select structure
- See: originating decision, values it carries, review history
- See: all decisions that touched this structure

**3. Values Health Dashboard** (periodic community reflection)
- Word cloud or graph of values that have won in recent decisions
- Word cloud or graph of values that have been marginalized in recent decisions
- Structures that have not been reviewed in X months (review triggers)
- Ecological indicator readings overlaid on relevant decisions

**4. Conflict Navigator** (when conflict arises)
- Enter conflict description
- System maps: which existing structures are in competition
- System presents: the values embodied in each competing structure
- System outputs: a structured conversation guide, not a resolution

## Deliverable

**A prototype values-architecture bridge** that:
1. Has the data model described above (implemented in any reasonable database)
2. Has the four interfaces described above (even if rough)
3. Has a test case: take an existing community governance decision and trace it through the bridge — does it reveal what values created the structure?
4. Documents: what works, what breaks down, what assumptions are embedded

## What Counts as "Working"

The prototype works if:
- A community member who has never used the system can understand what it does within 5 minutes
- A facilitator can use it in a real meeting without extensive preparation
- The system surfaces values tensions that the community did not already know were there
- The system makes structural consequences of values choices visible, not just abstract

## Constraints

- No black boxes — every recommendation must be traceable to explicit inputs
- No AI magic — the surfacing and connecting can be assisted by AI, but the logic must be explicable to a community member
- No permanent records — the community can revise or erase any record (data sovereignty)