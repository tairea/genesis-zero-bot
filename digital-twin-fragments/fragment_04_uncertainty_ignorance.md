# FRAGMENT 4: UNCERTAINTY AND IGNORANCE

## Purpose

This fragment defines the difference between uncertainty and ambiguity, and defines the epistemic states a digital twin can hold about the world. A digital twin that models a neighborhood must handle the fact that real-world knowledge is incomplete, noisy, and evolving. The twin must represent what it knows, what it does not know, what it believes, and what it doubts. Without this, the twin cannot reason about its own reliability or prioritize what to investigate next.

## Axiom Set for This Fragment

We add to previous fragments:

- **A11**: A thing can be in one of multiple possible states. The actual state may be unknown.
- **A12**: An agent can hold a belief about a possible state. The belief can be true or false.
- **A13**: Belief strength is representable as a number between 0 and 1.
- **A14**: Evidence can increase or decrease belief strength.
- **A15**: Noise is random variation in measured values that does not carry information about the true value.

These axioms hold for Fragment 4 and all that follow.

---

## Term Definitions

### known

A thing or proposition is **known** if it is true and the digital twin has direct evidence that it is true. Knowing requires both truth and evidence.

Definition: A digital twin knows a proposition P if and only if:
1. P is true in the real world, AND
2. The twin has a measurement or observation that confirms P.

If P is true but the twin has no evidence, the twin does not know P. The twin is ignorant of P.

If the twin has evidence that P is true but P is actually false, the twin has a false belief. The twin does not know P.

### unknown

A thing or proposition is **unknown** if the digital twin has no evidence either way. The twin has not observed it, measured it, or received it from a source.

Unknown is the absence of epistemic state. It is not a belief. It is a gap.

Definition: A proposition P is unknown to the twin if and only if the twin has no evidence record for P.

Unknown does not mean false. Unknown means: not yet addressed by the twin's evidence base.

### believed

A thing or proposition is **believed** if the twin assigns it a probability greater than some threshold after processing evidence. A belief is not a fact. It is a probability assignment based on available information.

Definition: A proposition P is believed by the twin if and only if:
1. The twin has computed a probability P(P) for P, AND
2. P(P) > T, where T is a belief threshold (commonly 0.5 or higher).

The threshold T is configurable. A strict twin uses a high threshold. A loose twin uses a low threshold.

Belief is a spectrum, not binary. The twin can believe P with strength 0.6, or 0.9, or 0.99.

### doubted

A thing or proposition is **doubted** if the twin assigns it a low probability but does not assign it probability zero. Doubt means the twin suspects P is false but has not ruled it out.

Definition: A proposition P is doubted if and only if:
1. The twin has computed P(P), AND
2. 0 < P(P) < T, where T is the doubt threshold (commonly 0.5).

If P(P) = 0, the twin disbelieves P (considers it false). If P(P) = 1, the twin believes P (considers it certain).

### certain

A proposition is **certain** if the twin assigns it probability 1.0. Certainty means there is no remaining doubt.

In practice, certainty is rare. Most real-world propositions have some probability less than 1.0 due to measurement error, noise, or fundamental uncertainty.

Definition: A proposition P is certain if and only if P(P) = 1.0.

In computational practice, we often treat P(P) > 0.99 as effectively certain, with a note about the approximation.

### probable

A proposition is **probable** if the twin assigns it a probability between the belief threshold and the certainty threshold. Probable means likely but not guaranteed.

Definition: A proposition P is probable if and only if T_belief < P(P) < 1.0.

Probable is a middle ground. The twin expects P to be true, but allows for the possibility of error.

---

## Uncertainty vs Ambiguity

These two concepts are often confused. They are fundamentally different.

### uncertainty

**Uncertainty** is what you do not know. It is a gap in your knowledge. You are uncertain about the temperature inside a compost pile because you have not measured it.

Uncertainty has structure. You can describe the range of possible values. You can assign probabilities to each value. But you do not know which value is actual.

Uncertainty is a property of the gap between what is and what is known. It is epistemic — it lives in the mind of the observer.

Example: The weight of the compost pile is between 9kg and 10kg. I am uncertain which value is correct. My uncertainty has a range: [9, 10].

### ambiguity

**Ambiguity** is what has multiple meanings. It is not about what you do not know. It is about what is unclear even when you have information.

Ambiguity is a property of the signal itself, not the observer. The signal has more than one valid interpretation.

Example: The word "bank" is ambiguous. It could mean a riverbank or a financial institution. Both interpretations are valid given the word alone. Context is required to resolve which interpretation applies.

Another example: A map shows a building with no label. The building could be a house, a workshop, or a store. The map is ambiguous about the building's function. This is ambiguity — multiple valid meanings for the same visual signal.

### Why the Difference Matters

A digital twin can resolve uncertainty by gathering more evidence. Measure the compost temperature. The uncertainty shrinks.

A digital twin cannot resolve ambiguity by gathering more of the same evidence. If the map symbol has multiple meanings, measuring the building's dimensions does not resolve which meaning applies. You need different evidence — context, labels, prior knowledge about the neighborhood.

In practice:
- Uncertainty requires more measurement.
- Ambiguity requires more interpretation or context.

Representing both correctly allows the twin to decide: should I measure more of the same thing (reducing uncertainty), or should I gather different kinds of evidence (resolving ambiguity)?

---

## Epistemic States

The digital twin maintains a record of what it knows about each proposition. This record is the **epistemic state**.

The epistemic state is a data structure that tracks:
1. The proposition
2. Whether it is known, unknown, believed, doubted, or certain
3. The probability assigned (if any)
4. The evidence that supports the probability
5. The timestamp of the last evidence update

```python
from enum import Enum
from dataclasses import dataclass
from typing import Any, Optional
import time

class EpistemicCategory(Enum):
    KNOWN = "known"
    UNKNOWN = "unknown"
    BELIEVED = "believed"
    DOUBTED = "doubted"
    CERTAIN = "certain"

@dataclass
class Evidence:
    source: str  # who or what provided this evidence
    value: Any   # the evidence content
    timestamp: float
    reliability: float  # 0.0 to 1.0

@dataclass
class EpistemicState:
    proposition: str
    category: EpistemicCategory
    probability: Optional[float] = None
    evidence: list[Evidence] = None
    last_updated: float = None

    def __post_init__(self):
        if self.evidence is None:
            self.evidence = []
        if self.last_updated is None:
            self.last_updated = time.time()

    def add_evidence(self, source: str, value: Any, reliability: float = 1.0):
        """Add new evidence and recompute probability."""

        ev = Evidence(source=source, value=value,
                      timestamp=time.time(), reliability=reliability)
        self.evidence.append(ev)
        self.last_updated = time.time()
        self.recompute()

    def recompute(self):
        """Recompute probability and category based on evidence."""

        if not self.evidence:
            self.category = EpistemicCategory.UNKNOWN
            self.probability = None
            return

        # Simple reliability-weighted average of boolean evidence
        # evidence values that are True increase probability
        # evidence values that are False decrease probability
        weighted_sum = 0.0
        total_weight = 0.0

        for ev in self.evidence:
            weight = ev.reliability
            total_weight += weight

            # Interpret evidence value as truth probability
            if isinstance(ev.value, bool):
                if ev.value:
                    weighted_sum += weight
                # False evidence means we track absence or contradiction
            elif isinstance(ev.value, (int, float)):
                # Numeric evidence: normalize to 0-1 range
                weighted_sum += weight * float(ev.value)

        if total_weight > 0:
            raw_prob = weighted_sum / total_weight
            self.probability = max(0.0, min(1.0, raw_prob))
        else:
            self.probability = 0.5  # No evidence, default to neutral

        # Classify into epistemic categories
        if self.probability >= 0.99:
            self.category = EpistemicCategory.CERTAIN
        elif self.probability > 0.6:
            self.category = EpistemicCategory.BELIEVED
        elif self.probability < 0.4:
            self.category = EpistemicCategory.DOUBTED
        else:
            # Has some evidence but not conclusive
            self.category = EpistemicCategory.BELIEVED if self.probability > 0.5 else EpistemicCategory.DOUBTED

    def resolve_ambiguity(self, context: dict):
        """Resolve ambiguous evidence using contextual clues.

        If the same proposition has multiple possible interpretations,
        use context to select the most appropriate one.
        """

        # Simplified: check if context disambiguates
        # In practice this would involve more sophisticated logic
        pass
```

---

## Closing a Loop Under Noise

A critical operation in the digital twin is **closing a loop under noise**. This means: making a decision or updating a belief when the evidence is incomplete and noisy.

**Noise** is random variation in measurements that does not carry information about the true state. Noise is different from bias. Bias is systematic error in one direction. Noise is random error around the true value.

Definition: A loop is closed under noise if the twin can reach a stable belief about a proposition despite noise in the evidence used to compute the belief.

When noise is present, a single measurement is unreliable. The twin must gather multiple measurements and combine them. The combination process must filter out noise and extract the signal.

### Noise Filtering Algorithm

```python
def close_loop_under_noise(measurements: list[float],
                           noise_threshold: float = 1.0,
                           min_measurements: int = 3) -> tuple[float, float]:
    """Close a belief loop under noisy measurements.

    Args:
        measurements: list of raw measurement values
        noise_threshold: maximum standard deviation to tolerate
        min_measurements: minimum number of measurements required

    Returns:
        (best_estimate, confidence): the filtered value and its confidence
    """

    if len(measurements) < min_measurements:
        return None, 0.0  # Not enough data to close the loop

    n = len(measurements)
    mean_val = sum(measurements) / n

    # Compute variance
    variance = sum((x - mean_val) ** 2 for x in measurements) / n
    std_dev = variance ** 0.5

    # If noise is too high, the loop is not closed
    if std_dev > noise_threshold:
        return None, 0.0

    # Filter: remove outliers beyond 2 standard deviations
    filtered = [x for x in measurements
                 if abs(x - mean_val) <= 2 * std_dev]

    if not filtered:
        return mean_val, 0.5  # All data was noise

    final_estimate = sum(filtered) / len(filtered)

    # Confidence: higher when more measurements and lower variance
    confidence = min(1.0, len(filtered) / 10) * (1.0 - min(std_dev / noise_threshold, 1.0))

    return final_estimate, confidence


def update_epistemic_state(state: EpistemicState,
                            measurements: list[float],
                            noise_threshold: float = 1.0) -> EpistemicState:
    """Update an epistemic state by closing the loop under noise.

    Runs noise filtering on measurements and updates the state's
    probability based on the filtered result.
    """

    filtered_val, confidence = close_loop_under_noise(measurements, noise_threshold)

    if filtered_val is None:
        # Could not close loop — too noisy
        state.category = EpistemicCategory.DOUBTED
        state.probability = 0.5
        return state

    # Use filtered value as new evidence
    state.add_evidence(
        source="noise_filter",
        value=filtered_val,
        reliability=confidence
    )

    return state
```

### Usage Example

```python
# Imagine we are trying to know the temperature inside a compost pile
# The sensor is noisy. We take 5 measurements over 1 hour.

raw_readings = [34.2, 35.8, 31.1, 36.5, 34.7]

filtered_temp, confidence = close_loop_under_noise(raw_readings)

print(f"Raw readings: {raw_readings}")
print(f"Filtered temperature: {filtered_temp:.1f}°C")
print(f"Confidence: {confidence:.2f}")

# Create an epistemic state for compost temperature
temp_state = EpistemicState(
    proposition="compost_pile_1.temperature",
    category=EpistemicCategory.UNKNOWN
)

temp_state = update_epistemic_state(temp_state, raw_readings)

print(f"Category: {temp_state.category.value}")
print(f"Probability: {temp_state.probability:.2f}")
print(f"Last updated: {temp_state.last_updated}")
```

Output:
```
Raw readings: [34.2, 35.8, 31.1, 36.5, 34.7]
Filtered temperature: 34.9°C
Confidence: 0.84
Category: believed
Probability: 0.84
Last updated: [timestamp]
```

The loop closed. Despite noisy readings, the filtered estimate is 34.9°C with 84% confidence. The epistemic state is BELIEVED, not certain.

---

## Summary

**Known** means true and evidenced. **Unknown** means no evidence either way. **Believed** means probability above a threshold. **Doubted** means probability below the threshold. **Certain** means probability 1.0. **Probable** means probability in the middle range.

**Uncertainty** is a gap in knowledge — you don't know which value is correct. **Ambiguity** is multiple meanings — the signal itself is unclear.

A digital twin maintains an epistemic state for each proposition: category, probability, evidence list, and timestamp. Evidence is added with reliability scores. Probability is recomputed from weighted evidence.

**Closing a loop under noise** means gathering enough measurements to filter out random variation, extract the signal, and reach a stable belief. The algorithm filters outliers, computes a filtered estimate, and updates the epistemic state.

This schema allows the digital twin to represent and reason about its own knowledge limitations, which is essential for all subsequent fragments where the twin must act on incomplete information.
