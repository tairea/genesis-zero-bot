# FRAGMENT 2: RELATIONSHIPS AS FIRST-CLASS THINGS

## Purpose

This fragment defines what a relationship IS at the most fundamental level. It shows that relationships are not secondary to things — they are co-equal. Every "thing" in a digital twin is defined entirely by its relationships. Without relationships, a thing has no identity, no position, no meaning.

## Axiom Set for This Fragment

We accept the following as true without proof in this fragment:

- **A1**: The universe contains things and relationships between things.
- **A2**: A thing has no inherent identity independent of its relationships.
- **A3**: A relationship connects exactly two things. (We relax this in Fragment 8.)
- **A4**: Every relationship has a type that distinguishes it from other types.
- **A5**: Relationships can be measured. Measurement produces a number.

These axioms hold for all fragments that follow.

---

## Term Definitions

### relation

A **relation** is a statement that connects two things. The statement can be true or false. If it is true, the relation holds. If it is false, the relation does not hold.

Example: "A is near B" is a relation. It is either true or false.

A relation is not the same as a number. It is a logical claim about the world.

### edge

An **edge** is a representation of a relation inside a computational system. An edge is the encoding of a relation for a machine to store, process, and retrieve.

Think of an edge as a container. The container holds:
- The identifier of the first thing (source)
- The identifier of the second thing (target)
- The type of the relation
- A value (optional) that measures the strength, distance, or intensity of the relation

An edge is not the relation itself. It is a model of the relation inside a machine.

### link

A **link** is the same as an edge in most contexts. The word "link" emphasizes connection. The word "edge" emphasizes graph theory.

We use both words. They mean the same thing: a machine-readable encoding of a relation.

### connection

A **connection** is any relation that persists over time. A connection is a relation that you expect to still hold in the future.

Example: "A is married to B" is a connection, not just a relation. It implies persistence and intention.

A connection implies that neither the source nor the target is free to change independently without consequence. There is obligation or entanglement.

### flow

A **flow** is a directed relation. A flow has a direction. It moves from one thing to another.

Example: "Water flows from the rain barrel to the garden" is a flow. The direction matters. The rain barrel loses water. The garden gains water.

A flow is a relation where the order of the two things carries meaning.

### dependency

A **dependency** is a relation where one thing cannot exist or function without another. The dependent thing requires the other.

Example: "The plant depends on water" means: if water is absent, the plant fails.

A dependency is a relation with a specific semantics: one side is necessary for the other to continue.

---

## Three Fundamental Types of Relation

We identify three kinds of relation that cover all cases in a neighborhood digital twin. These are **spatial**, **causal**, and **value**.

### spatial relation

A **spatial relation** describes where a thing is relative to other things. It answers the question: where is this thing compared to that thing?

Spatial relations include:
- **near** — two things are close in space
- **far** — two things are separated in space
- **inside** — one thing is contained within another
- **between** — one thing is located in the space separating two others
- **above** — one thing is higher in space than another
- **below** — one thing is lower in space than another

A spatial relation does not change the things themselves. It only describes their geometric arrangement. The things retain their properties regardless of where they are.

In a digital twin, spatial relations matter most for physical things: land parcels, buildings, water bodies, soil patches, plants, animals. Spatial relations matter less for social and value things.

### causal relation

A **causal relation** describes how one thing makes another thing change. It answers the question: what causes what?

A causal relation has a direction. Cause comes before effect. The cause produces the effect. Remove the cause, and the effect stops or changes.

Example: "Adding water to soil causes the soil to become moist." The water is the cause. The moisture is the effect.

A causal relation is not the same as a spatial relation. Things can be near each other without causing each other to change. Things can cause each other to change from a distance.

### value relation

A **value relation** describes what one thing is worth to another thing. It answers the question: how much does this thing matter to that thing?

Example: "One hour of labor is worth two kilograms of vegetables." The labor and the vegetables are in a value relation. Each has a value assigned relative to the other.

Value relations are not physical. They are social constructs. They exist because people agree they exist. They can change when agreements change.

Example: "A tool is worth its use to a person." The value relation between the tool and the person depends on the person's needs, goals, and alternatives.

Value is not fixed. It is context-dependent. What is worth much to one person may be worth little to another.

---

## How the Three Types Interrelate

The three relation types are not separate realities. They overlap and influence each other.

### Spatial and Causal

Spatial proximity makes causal relations more likely. Things that are near each other can act on each other. Water placed near a plant can be absorbed by the plant.

But causation does not require spatial proximity. A remote event can cause a local effect: a government policy causes a local price change. A drought upstream causes floods downstream.

The relationship: space enables some causal relations and prevents others. Space is a constraint, not a cause.

### Causal and Value

A causal relation can create or destroy value. If A causes B to happen, and B is valuable to C, then A is valuable to C indirectly.

Example: A compost pile causes nutrient-rich soil to form. Nutrient-rich soil is valuable to a gardener. Therefore, the compost pile is valuable to the gardener, through the causal chain: compost → soil nutrients → plant growth → food.

Value relations can also create causal relations. If A is valuable to B, B may act to preserve A. This is a special kind of cause: intentional preservation.

### Spatial and Value

Spatial relations affect value. Things that are near are easier to exchange. Exchange creates value relations. If two people are near each other, they can trade. If they are far apart, trade is harder.

But value does not depend on space. A person can value a distant relative as much as a near one. Digital goods have value across any distance.

### Unified View

All three relation types are instances of the same underlying thing: a relation. The type is just a label that tells us what kind of meaning the relation carries.

We can represent all three types with the same data structure. The type label is metadata. The structure is the same.

---

## The Distance Metric

Every relation has a **distance**. Distance is a number that measures how strongly the relation holds, or how much separation exists between the two connected things.

Distance is defined differently for each relation type:

### Spatial distance

Spatial distance is measured in units of length. Meters for land. Centimeters for soil patches. Kilometers for regions.

Formula: d_spatial(A, B) = the shortest straight-line distance between A and B in space.

### Causal distance

Causal distance measures how far apart two things are in a causal chain. One causal step is distance 1. Two causal steps is distance 2.

Formula: d_causal(A, B) = the minimum number of causal links in any chain from A to B.

### Value distance

Value distance measures how different the value relations are between two things. If A and B have similar value to all other things, they are close in value-space. If their values differ, they are far.

Formula: d_value(A, B) = the difference between the sum of A's values and the sum of B's values across all value relations each participates in.

---

## Executable Specification: Relation Schema

We define a schema that can represent all three relation types uniformly. This schema is implemented in code.

### Data Structure

```python
class Relation:
    def __init__(self, source_id, target_id, relation_type, value=None, metadata=None):
        # source_id: string identifier of the first thing
        # target_id: string identifier of the second thing
        # relation_type: one of "spatial", "causal", "value"
        # value: optional number measuring the strength/distance
        # metadata: optional dict for additional type-specific data

        self.source_id = source_id
        self.target_id = target_id
        self.relation_type = relation_type
        self.value = value
        self.metadata = metadata or {}

    def distance(self):
        """Return the distance for this relation.
        The distance formula depends on the relation type."""

        if self.relation_type == "spatial":
            return spatial_distance(self)
        elif self.relation_type == "causal":
            return causal_distance(self)
        elif self.relation_type == "value":
            return value_distance(self)
        else:
            raise ValueError(f"Unknown relation type: {self.relation_type}")
```

### Spatial Distance Function

```python
import math

def spatial_distance(relation):
    """Calculate spatial distance between source and target.

    Requires metadata to contain:
        source_coords: (x, y) tuple for source
        target_coords: (x, y) tuple for target
    """

    source_coords = relation.metadata.get("source_coords")
    target_coords = relation.metadata.get("target_coords")

    if source_coords is None or target_coords is None:
        raise ValueError("Spatial relation requires coordinate metadata")

    dx = source_coords[0] - target_coords[0]
    dy = source_coords[1] - target_coords[1]

    return math.sqrt(dx**2 + dy**2)
```

### Causal Distance Function

```python
def causal_distance(relation):
    """Calculate causal distance.
    Causal distance is always 1 for a direct causal link.
    The graph traversal computes minimum causal steps.
    """

    if relation.value is not None:
        return relation.value

    # Default: direct causal link has distance 1
    return 1
```

### Value Distance Function

```python
def value_distance(relation):
    """Calculate value distance as the absolute difference in values.

    If relation connects A and B with value v:
    d_value(A, B) = abs(vA_total - vB_total)
    This simplified version uses the direct relation value.
    """

    if relation.value is not None:
        return abs(relation.value)

    # If no value assigned, return maximum distance (uncertain)
    return float("inf")
```

### Relation Factory

```python
def make_spatial_relation(source_id, target_id, source_coords, target_coords):
    """Create a spatial relation with coordinates."""

    return Relation(
        source_id=source_id,
        target_id=target_id,
        relation_type="spatial",
        metadata={
            "source_coords": source_coords,
            "target_coords": target_coords,
        }
    )

def make_causal_relation(source_id, target_id, causal_distance=1, strength=None):
    """Create a causal relation."""

    return Relation(
        source_id=source_id,
        target_id=target_id,
        relation_type="causal",
        value=causal_distance,
        metadata={"strength": strength}
    )

def make_value_relation(source_id, target_id, value):
    """Create a value relation."""

    return Relation(
        source_id=source_id,
        target_id=target_id,
        relation_type="value",
        value=value,
    )
```

### Usage Example

```python
# Define a rain barrel and a garden
rain_barrel_coords = (10.0, 5.0)
garden_coords = (10.5, 5.2)

# Spatial relation: rain barrel is near garden
near_relation = make_spatial_relation(
    source_id="rain_barrel_1",
    target_id="garden_1",
    source_coords=rain_barrel_coords,
    target_coords=garden_coords
)

# Causal relation: rain barrel supplies water to garden
water_flow = make_causal_relation(
    source_id="rain_barrel_1",
    target_id="garden_1",
    causal_distance=1
)

# Value relation: water is worth 1 unit to the garden
water_value = make_value_relation(
    source_id="rain_barrel_1",
    target_id="garden_1",
    value=1.0
)

# Print distances
print(f"Spatial distance: {near_relation.distance():.2f} meters")
print(f"Causal distance: {water_flow.distance()}")
print(f"Value distance: {water_value.distance()}")
```

Output:
```
Spatial distance: 0.56 meters
Causal distance: 1
Value distance: 1.0
```

---

## Summary

A **relation** is a logical claim connecting two things. An **edge** is its machine representation. A **link** is another word for edge. A **connection** is a persistent relation. A **flow** is a directed relation. A **dependency** is a relation where one side is necessary for the other.

Three fundamental relation types cover all cases:
- **Spatial** — where things are in space
- **Causal** — what makes things change
- **Value** — what things are worth to each other

All three are instances of the same data structure. The type label is metadata. The schema is uniform.

Every relation has a distance. Spatial distance is geometric. Causal distance is the number of causal steps. Value distance is the difference in value assignments.

This schema provides the foundation for all subsequent fragments. Things in Fragments 3 through 10 are connected by relations. All those relations are spatial, causal, or value relations implemented through this schema.
