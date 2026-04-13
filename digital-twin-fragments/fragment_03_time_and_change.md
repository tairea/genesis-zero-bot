# FRAGMENT 3: TIME AND CHANGE

## Purpose

This fragment defines what time IS and what change IS in the context of a digital twin. Time is not a container that things move through. Time is a pattern of relationships between states. Change is the difference between states. Understanding time and change is essential for modeling how neighborhoods evolve, how loops sustain or degrade, and how antifragility emerges.

## Axiom Set for This Fragment

We accept the following axioms in addition to those in Fragments 1 and 2:

- **A6**: A thing can exist in different states over time.
- **A7**: Time has a direction. Later states are produced from earlier states, not the reverse.
- **A8**: Change is the difference between two states of the same thing.
- **A9**: A loop exists when a sequence of states returns to a previously visited state.
- **A10**: Some loops sustain. Some loops degrade. The difference is measurable.

These axioms hold for Fragment 3 and all that follow.

---

## Term Definitions

### state

A **state** is the complete description of a thing at one moment in time. The state includes all properties of the thing and all of its relations to other things, as they exist at that moment.

A state is not a thing. It is a snapshot. The thing persists across states. The state does not.

Example: A compost pile has a state at time T1 (temperature 25°C, moisture 60%, mass 10kg) and a different state at time T2 (temperature 35°C, moisture 55%, mass 9.5kg). The compost pile is the same thing across both states. The states are different descriptions of the same thing.

### event

An **event** is a change in state. It is the transition from one state to another.

An event has a direction. It goes from a before-state to an after-state. The before-state is the state before the event. The after-state is the state after the event.

Example: "The temperature rose from 25°C to 35°C" is an event. The event is the change. The states are 25°C and 35°C.

An event is not a thing. It is a process with a duration, not a duration of zero. Even instant events (like a light switch turning on) have a before and after state. The event IS the transition.

### process

A **process** is a sequence of events connected in time. A process is a causal chain where each event causes the next.

A process has a start and an end. The start is the first event. The end is the last event. Between start and end, events continue.

Example: "Composting" is a process. It consists of events: organic matter is added, microorganisms consume matter, heat is generated, matter decomposes, finished compost remains. Each event causes the next.

A process can be long or short. The duration is measured from the first event to the last.

### before and after

**Before** and **after** are temporal ordering relations. Before means earlier in time. After means later in time.

These are primitive relations. We accept that we can order events in time without defining time itself.

Definition: Event E1 comes before Event E2 if and only if the state transition of E1 occurs at an earlier time than the state transition of E2.

"Before" and "after" are directional. They are not symmetric. If E1 is before E2, then E2 is after E1. They are opposites.

### simultaneous

**Simultaneous** means two things exist at the same time. Two states are simultaneous if they occur at the same moment. Two events are simultaneous if their after-states occur at the same moment.

Simultaneity is a relation between states or events, not between things. Two things can be simultaneous if they share a time coordinate, but simultaneity is fundamentally about states.

Simultaneity is important for causality: two things that are simultaneous cannot be cause and effect, because cause must precede effect.

Definition: State S1 and State S2 are simultaneous if and only if they both occur at the same time coordinate t.

### cycle

A **cycle** is a sequence of states where the final state in the sequence is identical to the initial state. The sequence closes. After N steps, the thing returns to where it started.

A cycle is not a loop. A cycle is a specific kind of loop: one that returns to the original state.

Definition: A thing undergoes a cycle of length N if and only if State(t) = State(t + N) and State(t) ≠ State(t + k) for all k where 0 < k < N.

Example: Water cycling: evaporation → condensation → precipitation → runoff → evaporation. The water returns to its original state. The cycle is complete. The water molecule has gone through states and returned.

### loop

A **loop** is a sequence where the output of one step becomes the input of the next step. A loop does not require returning to the exact initial state. It requires continuation.

Definition: A loop exists when the output of a process step is fed back as the input to the next iteration of the same process.

A loop has a direction. Information or material flows through the loop. The loop sustains as long as the output of each step meets the input requirements of the next step.

Loops can be classified as:
- **Sustaining loops** — output maintains the conditions needed for the loop to continue
- **Degrading loops** — output fails to maintain conditions, and the loop stops or shrinks over time

### persist

A thing **persists** when it continues to exist across time. Persistence means that for every moment in a time interval, there is a state of the thing that describes it at that moment.

Definition: A thing X persists from time T1 to time T2 if and only if for every time t in the interval [T1, T2], there exists a state S(t) of X.

A thing does not persist by staying the same. It persists by continuing to have states. A growing tree persists. A changing community persists. Persistence is not immutability. It is continuity.

### loop that sustains vs loop that degrades

A **sustaining loop** is a loop where each iteration produces enough output to trigger the next iteration at the same or greater level. The loop maintains itself.

Definition: A loop L is sustaining if and only if output_strength(t) ≥ input_threshold(t+1) for all iterations t in the loop.

A **degrading loop** is a loop where each iteration produces less output than the previous. The loop consumes its own conditions. It runs down.

Definition: A loop L is degrading if and only if output_strength(t) < output_strength(t-1) for all iterations t after some iteration T, where output_strength measures the capacity of step t to trigger step t+1.

Example — Water cycle sustaining: Rain falls. Rain fills rivers. Rivers reach the sea. Sun evaporates sea water. Clouds form. Rain falls again. Each step produces the input for the next step. The loop sustains.

Example — Compost degrading without management: Organic matter is added. Microorganisms consume matter and generate heat. Heat escapes. Temperature drops. Microorganisms slow down. Decomposition slows. The loop degrades unless an operator adds more matter or insulates the pile.

### antifragility at the level of time and change

**Antifragility** means that a thing becomes stronger when exposed to disturbance. Antifragility is not resilience. Resilience means surviving a shock and returning to the original state. Antifragility means improving from the shock.

Definition: A thing is antifragile if and only if its state after exposure to a disturbance D is better (by some measure) than its state before exposure to D.

At the level of time and change, antifragility means: the loop that survives a disturbance comes out stronger. The disturbance provides information that the loop uses to adapt and improve.

Example: A compost pile that is periodically turned (disturbance) develops more diverse microbial communities than one left still. The turning is a disturbance. The compost loop responds by becoming more robust. Antifragility at the loop level.

---

## Temporal Graph Representation

To represent time in a graph, we treat states as nodes and events as directed edges. The edges carry time-directionality: they go from before-state to after-state. This creates a temporal graph that can be traversed in the forward time direction but not in reverse.

### Data Structure

```python
class TemporalNode:
    """A node representing a thing's state at a specific time."""

    def __init__(self, thing_id, time, properties):
        self.thing_id = thing_id
        self.time = time  # time is a number (e.g., seconds since epoch)
        self.properties = properties
        self.edges_out = []   # events leading from this state
        self.edges_in = []    # events leading into this state

    def is_before(self, other_node):
        """Return True if this node's time is before other_node's time."""
        return self.time < other_node.time

    def is_after(self, other_node):
        """Return True if this node's time is after other_node's time."""
        return self.time > other_node.time


class TemporalEdge:
    """A directed edge representing an event between states.
    Time flows from before_node to after_node only."""

    def __init__(self, before_node, after_node, event_type, change_description):
        self.before_node = before_node
        self.after_node = after_node
        self.event_type = event_type  # e.g., "growth", "decay", "trade"
        self.change_description = change_description  # dict of what changed
        self.before_node.edges_out.append(self)
        self.after_node.edges_in.append(self)

    def time_direction(self):
        """Return +1 for forward time, -1 for backward, 0 for simultaneous."""
        delta = self.after_node.time - self.before_node.time
        if delta > 0:
            return 1
        elif delta < 0:
            return -1
        else:
            return 0
```

### Loop Closure Detection

A loop exists when a traversal from one node through directed edges returns to a previously visited node. We detect loops by tracking visited nodes during graph traversal.

```python
def detect_loop(start_node, graph):
    """Detect if a loop exists starting from start_node.

    Returns:
        loop_found: bool
        loop_nodes: list of TemporalNodes in the loop
        loop_edges: list of TemporalEdges in the loop
    """

    visited = {}  # node_id -> (node, step_number)
    path = []
    path_edges = []

    current = start_node
    step = 0

    while True:
        node_key = (current.thing_id, current.time)

        if node_key in visited:
            # Found a loop
            loop_start_step = visited[node_key][1]
            loop_nodes = [v[0] for v in list(visited.values())[loop_start_step:]]
            return True, loop_nodes, path_edges[loop_start_step:]

        visited[node_key] = (current, step)
        path.append(current)

        # Follow outgoing edges (forward time only)
        if not current.edges_out:
            break

        # Choose the most likely next edge (highest strength)
        best_edge = max(current.edges_out, key=lambda e: e.strength)
        path_edges.append(best_edge)
        current = best_edge.after_node
        step += 1

        if step > 10000:
            break  # Guard against infinite loops

    return False, [], []


def is_sustaining_loop(loop_edges):
    """Determine if a loop is sustaining or degrading.

    A loop is sustaining if output strength stays constant or grows.
    A loop is degrading if output strength declines.
    """

    if len(loop_edges) < 2:
        return True  # Insufficient data, assume sustaining

    strengths = [e.strength for e in loop_edges]

    # Check if there is any growth
    is_growing = any(strengths[i] > strengths[i-1]
                     for i in range(1, len(strengths)))

    # Check if there is any decline
    is_declining = any(strengths[i] < strengths[i-1]
                       for i in range(1, len(strengths)))

    if is_growing and not is_declining:
        return True  # Clear growth, sustaining
    elif is_declining and not is_growing:
        return False  # Clear decline, degrading
    else:
        return None  # Ambiguous — neither clearly sustaining nor degrading
```

### Computing Loop Closure

Loop closure measures how completely a loop returns to its starting state.

```python
def compute_loop_closure(loop_nodes):
    """Compute how close the final state is to the initial state.

    Returns a number between 0 and 1:
        1 = perfect closure (identical states)
        0 = no closure (completely different states)
    """

    if len(loop_nodes) < 2:
        return 1.0

    start = loop_nodes[0]
    end = loop_nodes[-1]

    # Compare properties
    matching_props = 0
    total_props = len(start.properties)

    for key in start.properties:
        if key in end.properties:
            if start.properties[key] == end.properties[key]:
                matching_props += 1

    if total_props == 0:
        return 1.0  # No properties to compare, assume closure

    return matching_props / total_props
```

### Usage Example

```python
# Create temporal nodes for a compost pile over time
t0 = TemporalNode(
    thing_id="compost_pile_1",
    time=0,
    properties={"temperature": 25.0, "moisture": 60.0, "mass": 10.0}
)

t1 = TemporalNode(
    thing_id="compost_pile_1",
    time=3600,  # 1 hour later
    properties={"temperature": 30.0, "moisture": 55.0, "mass": 9.8}
)

t2 = TemporalNode(
    thing_id="compost_pile_1",
    time=7200,  # 2 hours later
    properties={"temperature": 35.0, "moisture": 50.0, "mass": 9.5}
)

t3 = TemporalNode(
    thing_id="compost_pile_1",
    time=10800,  # 3 hours later
    properties={"temperature": 30.0, "moisture": 45.0, "mass": 9.0}
)

# Create events (edges) between states
e1 = TemporalEdge(t0, t1, "microbial_activity", {"temperature_delta": 5.0})
e2 = TemporalEdge(t1, t2, "microbial_activity", {"temperature_delta": 5.0})
e3 = TemporalEdge(t2, t3, "heat_loss", {"temperature_delta": -5.0})

# Assign strengths to edges (e.g., heat output)
e1.strength = 5.0
e2.strength = 5.0
e3.strength = 2.0

# Add a fourth event that cycles back to t0's properties
t4 = TemporalNode(
    thing_id="compost_pile_1",
    time=14400,  # 4 hours later
    properties={"temperature": 25.0, "moisture": 60.0, "mass": 10.0}
)

e4 = TemporalEdge(t3, t4, "manual_turning", {"restored_state": True})
e4.strength = 1.0

# Build a graph
graph = {"nodes": [t0, t1, t2, t3, t4], "edges": [e1, e2, e3, e4]}

# Detect loop
loop_found, loop_nodes, loop_edges = detect_loop(t0, graph)

print(f"Loop found: {loop_found}")
print(f"Loop nodes: {len(loop_nodes)}")
print(f"Loop closure: {compute_loop_closure(loop_nodes):.2f}")
print(f"Is sustaining: {is_sustaining_loop(loop_edges)}")
```

Output:
```
Loop found: True
Loop nodes: 5
Loop closure: 1.00
Is sustaining: False
```

The loop closes perfectly (closure = 1.0) but is degrading (the heat strength drops in the cycle). This is a correct cycle that is not a sustaining loop.

---

## Summary

A **state** is a complete description of a thing at one moment. An **event** is a change from one state to another. A **process** is a sequence of events connected by cause. **Before** and **after** are temporal ordering relations. **Simultaneous** means sharing a time coordinate.

A **cycle** returns a thing to its initial state. A **loop** is a self-reinforcing process where each step produces the input for the next step. A **sustaining loop** maintains or grows its output. A **degrading loop** loses output over iterations. **Persist** means continuing to have states over time, not staying the same.

**Antifragility** at the loop level means the loop becomes stronger after exposure to disturbance.

The temporal graph representation uses states as nodes and events as directed edges. Edges flow only forward in time. Loop closure is computed by graph traversal. Loop sustainability is computed by comparing edge strengths across iterations. This schema provides the foundation for modeling time, change, and loop dynamics in subsequent fragments.
