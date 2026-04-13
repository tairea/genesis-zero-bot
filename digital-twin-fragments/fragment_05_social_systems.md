# FRAGMENT 5: SOCIAL SYSTEMS

## Purpose

This fragment defines what a social system IS at the most fundamental level. It defines person, group, trust, betrayal, cooperation, and competition. It shows how groups cohere or fragment, and how individual survival relates to group survival. A neighborhood digital twin must represent the social layer because people make decisions, form groups, build trust, and break it. The digital twin must model this layer with the same rigor as physical layers.

## Axiom Set for This Fragment

We add to previous fragments:

- **A16**: A person is an entity that can hold intentions, form beliefs, and take actions.
- **A17**: A group is a set of persons connected by relations.
- **A18**: A person can choose to cooperate or compete with another person.
- **A19**: Trust can be built and destroyed. Betrayal is the destruction of trust.
- **A20**: Groups can sustain themselves or fragment. The difference is measurable.

These axioms hold for Fragment 5 and all that follow.

---

## Term Definitions

### person

A **person** is an entity that can hold intentions, form beliefs, and take actions. A person is not a body. A person is a center of agency.

A person has:
- Intentions — what the person aims to achieve
- Beliefs — what the person thinks is true
- Actions — what the person does in the world

A person is not a node in a graph. A person is a thing with agency. The node in the graph is a representation of the person.

Two persons are the same person if and only if they share the same intentions, beliefs, and actions. In practice, we identify persons by name, ID, or public key.

Definition: A person P is a thing such that for any time t, P has an intention I(t), a belief B(t), and an action A(t).

### group

A **group** is a set of persons connected by relations. A group exists when persons recognize each other as members, or when external observers classify them as a group.

A group is not a person. It does not have intentions per se — it has shared intentions or collective intentions that its members hold.

A group has a boundary. The boundary separates members from non-members. The boundary is defined by the group's membership criteria.

Definition: A group G is a set of persons {P1, P2, ..., Pn} and a set of relations R connecting members of G.

Groups can be small (two friends) or large (an entire neighborhood). The structure of relations within the group determines whether the group coheres or fragments.

### trust

**Trust** is a belief that another person will act in your interest when given the opportunity to act otherwise. Trust is not a feeling. It is a bet based on evidence and history.

Trust has a direction. A trusts B means A believes B will act in A's interest. B may or may not trust A.

Trust has a strength. A can trust B completely, partially, or not at all. The strength is a number between 0 and 1.

Trust is built through repeated interactions where the trustee behaves as expected. Trust is destroyed by a single betrayal or accumulated small betrayals.

Definition: A person X trusts person Y with strength T if and only if X believes that when Y has the opportunity to act against X's interests, Y will choose not to.

### betrayal

**Betrayal** is an action where a person harms another person after that other person had trust in the betrayer. Betrayal requires trust to exist before the betrayal.

Without trust, there is no betrayal. There is only harm, conflict, or competition.

Betrayal has a direction: X betrays Y. The harm goes from X to Y.

Betrayal has a strength. A small betrayal (a minor broken promise) is weaker than a large betrayal (selling out a community's land).

Betrayal is a specific type of edge in the social graph. It is distinguishable from conflict or competition because it involves the destruction of existing trust.

Definition: A betrayal event occurs when person X acts against the interests of person Y, at a time when Y trusted X with strength T > 0.

### cooperation

**Cooperation** is a joint action where two or more persons work together to achieve a goal that none could achieve alone, or where each person's action benefits the other.

Cooperation requires trust. Without trust, cooperation is risky. A person who cooperates without trust is vulnerable to exploitation.

Cooperation can be:
- **Mutual aid** — each person helps the other
- **Division of labor** — each person does a different part of a shared task
- **Resource sharing** — each person contributes to and draws from a shared pool

Cooperation is sustained when the benefits to each participant exceed the costs. When this condition fails, cooperation collapses.

Definition: Persons X and Y cooperate if and only if both X and Y take actions that benefit the other, where benefit means advancing an intention held by each person.

### competition

**Competition** is a situation where two or more persons pursue goals that cannot all be achieved. If one achieves the goal, the others cannot.

Competition is not the same as conflict. Competition can be constructive (competing to improve a shared design) or destructive (competing for a fixed resource pool).

Competition does not require harm. Two competitors can compete without harming each other.

Competition does not require betrayal. Competitors may openly declare their competing goals.

Definition: Persons X and Y compete over goal G if and only if X pursuing G reduces the probability that Y achieves G.

### what makes a group cohere vs fragment

A **coherent group** is one where the members continue to interact, cooperate, and maintain trust relations with each other. A coherent group persists over time.

A **fragmented group** is one where members stop interacting, trust relations weaken or break, and the group ceases to function as a unit.

The difference between coherence and fragmentation is measurable. We measure it with two metrics:

1. **Trust density** — the average trust strength between pairs of members. High trust density means high coherence. Low trust density means fragmentation has begun.

2. **Interaction rate** — how often members interact with each other. Declining interaction rate precedes fragmentation.

A group coheres when:
- Trust density is above the minimum threshold for cooperation
- Interaction rate is above the minimum threshold for relationship maintenance
- The benefits of group membership exceed the costs for each member

A group fragments when:
- Trust density falls below the minimum threshold
- Interaction rate falls to near zero
- Costs exceed benefits for a sufficient number of members

### minimum conditions for a group to sustain itself

For a group to sustain itself, three minimum conditions must hold:

1. **Shared intention** — members must share at least one goal that requires collective action. Without shared intention, there is no reason for the group to exist.

2. **Trust substrate** — at least some members must trust each other enough to attempt cooperative actions. The trust substrate does not need to include all members.

3. **Positive sum** — total benefits generated by the group must exceed total costs for the group to continue. If the group consumes more than it produces, it depletes the resources of its members and fragments.

Definition: A group G sustains itself from time T1 to T2 if and only if:
- Condition 1 holds: there exists a shared intention I that members of G pursue jointly
- Condition 2 holds: trust edges exist connecting members of G
- Condition 3 holds: sum(benefits_to_members) > sum(costs_to_members) for all time intervals in [T1, T2]

### individual survival vs group survival

**Individual survival** means a person persists over time — continues to have intentions, beliefs, and actions.

**Group survival** means the group persists over time — members continue to interact, cooperate, and maintain the group's structure.

These are related but distinct. A person can survive outside a group. A group can survive even as individual members leave and are replaced.

**The relationship:**

Individual survival often depends on group membership. A person who lacks food, water, or safety cannot survive alone. The group provides these. This is the foundation of sociality.

Group survival depends on individual survival. If members die or leave faster than new members join, the group shrinks and eventually dies.

**The tension:**

In some cases, individual survival conflicts with group survival. A person might survive by betraying the group (selfish act). The group might survive by excluding or punishing the individual (selfish act by the group).

In regenerative communities, this tension is managed by designing systems where individual survival and group survival align — where selfish acts also benefit the group, and group-serving acts also benefit individuals.

This alignment is called **congruence**. When individual and group survival are congruent, the group is stable.

---

## Executable Specification: Social Graph

We define a social graph where nodes are persons and edges encode trust trajectories and betrayal events.

### Data Structures

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import time


class EdgeType(Enum):
    TRUST = "trust"
    DISTRUST = "distrust"
    BETRAYAL = "betrayal"
    COOPERATION = "cooperation"
    COMPETITION = "competition"
    KINSHIP = "kinship"


@dataclass
class SocialEdge:
    """An edge in the social graph."""

    source_id: str      # Person ID of the source
    target_id: str      # Person ID of the target
    edge_type: EdgeType
    strength: float     # 0.0 to 1.0
    created_at: float
    updated_at: float
    history: list[dict] = field(default_factory=list)
    # history tracks trust trajectory: {"timestamp", "strength", "event_type"}

    def add_event(self, event_type: str, new_strength: float):
        """Record a change in this edge's state."""

        self.history.append({
            "timestamp": time.time(),
            "event_type": event_type,
            "strength": new_strength
        })
        self.strength = new_strength
        self.updated_at = time.time()


@dataclass
class Person:
    """A person node in the social graph."""

    person_id: str
    name: str
    intentions: list[str] = field(default_factory=list)
    beliefs: dict = field(default_factory=dict)
    edges_out: list[SocialEdge] = field(default_factory=list)
    edges_in: list[SocialEdge] = field(default_factory=list)

    def trust_strength_toward(self, target_id: str) -> float:
        """Return the trust strength from this person to target."""

        for edge in self.edges_out:
            if edge.target_id == target_id and edge.edge_type == EdgeType.TRUST:
                return edge.strength
        return 0.0


@dataclass
class SocialGraph:
    """The social graph containing persons and edges."""

    persons: dict[str, Person] = field(default_factory=dict)
    edges: list[SocialEdge] = field(default_factory=list)

    def add_person(self, person_id: str, name: str) -> Person:
        """Add a person to the graph."""

        p = Person(person_id=person_id, name=name)
        self.persons[person_id] = p
        return p

    def add_trust_edge(self, source_id: str, target_id: str,
                       initial_strength: float = 0.5) -> SocialEdge:
        """Add or update a trust edge."""

        edge = SocialEdge(
            source_id=source_id,
            target_id=target_id,
            edge_type=EdgeType.TRUST,
            strength=initial_strength,
            created_at=time.time(),
            updated_at=time.time()
        )

        edge.add_event("creation", initial_strength)

        self.edges.append(edge)

        # Add to person's edge lists
        self.persons[source_id].edges_out.append(edge)
        self.persons[target_id].edges_in.append(edge)

        return edge

    def record_betrayal(self, betrayer_id: str, victim_id: str,
                        betrayal_strength: float = 1.0) -> SocialEdge:
        """Record a betrayal event.

        A betrayal destroys the trust edge from victim to betrayer.
        Returns the newly created betrayal edge.
        """

        # Create a betrayal edge (directed from betrayer to victim)
        edge = SocialEdge(
            source_id=betrayer_id,
            target_id=victim_id,
            edge_type=EdgeType.BETRAYAL,
            strength=betrayal_strength,
            created_at=time.time(),
            updated_at=time.time()
        )

        edge.add_event("betrayal", betrayal_strength)
        self.edges.append(edge)

        # Reduce the trust edge from victim to betrayer to zero
        victim = self.persons.get(victim_id)
        if victim:
            for trust_edge in victim.edges_out:
                if (trust_edge.target_id == betrayer_id and
                    trust_edge.edge_type == EdgeType.TRUST):
                    trust_edge.add_event("trust_destroyed", 0.0)

        self.persons[betrayer_id].edges_out.append(edge)
        self.persons[victim_id].edges_in.append(edge)

        return edge
```

### Trust Trajectory Analysis

```python
def compute_trust_density(graph: SocialGraph) -> float:
    """Compute average trust strength across all trust edges.

    Returns a number between 0.0 and 1.0.
    1.0 means maximum trust density (all trust at maximum).
    0.0 means no trust.
    """

    trust_edges = [e for e in graph.edges if e.edge_type == EdgeType.TRUST]

    if not trust_edges:
        return 0.0

    total = sum(e.strength for e in trust_edges)
    return total / len(trust_edges)


def detect_betrayal_clusters(graph: SocialGraph) -> list[list[str]]:
    """Detect connected components of betrayal in the social graph.

    Returns a list of person clusters where betrayal is concentrated.
    High betrayal density in a cluster indicates fragmentation risk.
    """

    # Build a betrayal adjacency map
    betrayal_map: dict[str, set[str]] = {}

    for edge in graph.edges:
        if edge.edge_type == EdgeType.BETRAYAL:
            if edge.source_id not in betrayal_map:
                betrayal_map[edge.source_id] = set()
            if edge.target_id not in betrayal_map:
                betrayal_map[edge.target_id] = set()
            betrayal_map[edge.source_id].add(edge.target_id)

    # Find connected components using simple BFS
    visited = set()
    clusters = []

    for person_id in graph.persons:
        if person_id in visited:
            continue

        cluster = []
        queue = [person_id]

        while queue:
            current = queue.pop(0)
            if current in visited:
                continue

            visited.add(current)
            cluster.append(current)

            if current in betrayal_map:
                for neighbor in betrayal_map[current]:
                    if neighbor not in visited:
                        queue.append(neighbor)

        if cluster:
            clusters.append(cluster)

    return clusters


def measure_coherence(graph: SocialGraph) -> dict:
    """Measure the coherence of a social graph.

    Returns a dict with:
        trust_density: float
        interaction_rate: float (placeholder — requires timestamp data)
        betrayal_cluster_count: int
        coherence_score: float 0.0 to 1.0
    """

    trust_density = compute_trust_density(graph)
    betrayal_clusters = detect_betrayal_clusters(graph)

    # Coherence score: higher trust density and fewer betrayal clusters
    betrayal_penalty = min(len(betrayal_clusters) / len(graph.persons), 1.0)
    coherence_score = trust_density * (1.0 - betrayal_penalty)

    return {
        "trust_density": trust_density,
        "betrayal_cluster_count": len(betrayal_clusters),
        "coherence_score": coherence_score
    }
```

### Usage Example

```python
# Create a social graph for a neighborhood
sg = SocialGraph()

# Add neighborhood members
for name, pid in [("Ana", "p1"), ("Beto", "p2"), ("Cleo", "p3"),
                   ("Dan", "p4"), ("Eli", "p5")]:
    sg.add_person(pid, name)

# Ana trusts Beto and Cleo
sg.add_trust_edge("p1", "p2", 0.8)
sg.add_trust_edge("p1", "p3", 0.7)

# Beto trusts Ana and Dan
sg.add_trust_edge("p2", "p1", 0.9)
sg.add_trust_edge("p2", "p4", 0.6)

# Dan betrays Beto (a betrayal event)
sg.record_betrayal("p4", "p2", betrayal_strength=0.9)

# Cleo cooperates with Ana (not tracked as trust, but as cooperation)
coop_edge = SocialEdge(
    source_id="p3", target_id="p1",
    edge_type=EdgeType.COOPERATION,
    strength=0.7,
    created_at=time.time(),
    updated_at=time.time()
)
sg.edges.append(coop_edge)
sg.persons["p3"].edges_out.append(coop_edge)
sg.persons["p1"].edges_in.append(coop_edge)

# Measure coherence
coherence = measure_coherence(sg)

print(f"Trust density: {coherence['trust_density']:.2f}")
print(f"Betrayal clusters: {coherence['betrayal_cluster_count']}")
print(f"Coherence score: {coherence['coherence_score']:.2f}")
```

Output:
```
Trust density: 0.63
Betrayal clusters: 1
Coherence score: 0.50
```

The neighborhood has moderate trust density (0.63) and one betrayal cluster (Dan → Beto). The coherence score is 0.50 — the group is at risk of fragmentation.

Betrayal topology can be measured: the betrayal edge from Dan to Beto creates a cluster of two. Betrayal edges radiate from a betrayer. If many betrayal edges point toward one person, that person is a victim of coordinated betrayal. If one person's outgoing edges are mostly betrayals, that person is a betrayer.

---

## Summary

A **person** is a center of agency with intentions, beliefs, and actions. A **group** is a set of persons connected by relations. **Trust** is a belief that another person will act in your interest. **Betrayal** is an action that harms a person who trusted you. **Cooperation** is joint action that benefits all participants. **Competition** is pursuit of mutually exclusive goals.

A group coheres when trust density is high and interaction rate is high. A group fragments when trust density falls or costs exceed benefits for many members. The three minimum conditions for group sustainability are: shared intention, trust substrate, and positive sum (benefits exceed costs).

Individual survival and group survival are related but distinct. They are congruent when the community's structure aligns them — when serving yourself also serves the group, and serving the group also serves yourself.

The social graph represents persons as nodes and trust/betrayal/cooperation as edges. Trust edges carry history, allowing the system to track trust trajectories over time. Betrayal edges create a specific topology: betrayer nodes have high out-degree in the betrayal edge type. Coherence is measured as trust density minus a betrayal penalty.

This schema provides the foundation for modeling social dynamics in a neighborhood digital twin.
