"""
verbs.py — 144-verb taxonomy for semantic graph edges.

Six categories × 24 verbs each = 144 total.
Every relation between concepts uses exactly one verb from this list.
"""

from typing import Optional

VERB_TAXONOMY: dict[str, list[str]] = {
    "Structural": [
        "IS_A", "HAS_A", "PART_OF", "CONTAINS", "INSTANCE_OF", "SUBCLASS_OF",
        "RELATED_TO", "ADJACENT_TO", "LOCATED_IN", "CONNECTED_TO", "DERIVED_FROM",
        "COMPOSED_OF", "DEPENDS_ON", "IMPLIES", "CONTRADICTS", "SUPPORTS",
        "EXEMPLIFIES", "DEFINES", "CLASSIFIES", "DESCRIBES", "ATTRIBUTES",
        "MEASURES", "COUNTS", "BOUNDS",
    ],
    "Causal": [
        "CAUSES", "ENABLES", "PREVENTS", "TRIGGERS", "BLOCKS", "AMPLIFIES",
        "REDUCES", "TRANSFORMS", "PRODUCES", "REQUIRES", "ALLOWS", "INHIBITS",
        "ACCELERATES", "DELAYS", "INITIATES", "TERMINATES", "MAINTAINS",
        "DISRUPTS", "REGULATES", "MEDIATES", "MODULATES", "FACILITATES",
        "SUPPRESSES", "INDUCES",
    ],
    "Temporal": [
        "BEFORE", "AFTER", "DURING", "MEETS", "OVERLAPS", "STARTS", "FINISHES",
        "EQUALS_TIME", "PRECEDES", "FOLLOWS", "SIMULTANEOUS", "CONTINUOUS",
        "PERIODIC", "CYCLICAL", "SEQUENTIAL", "CONCURRENT", "IMMEDIATE",
        "EVENTUAL", "GRADUAL", "SUDDEN", "PERSISTENT", "TRANSIENT",
        "RECURRING", "DEPRECATED",
    ],
    "Epistemic": [
        "KNOWS", "BELIEVES", "INFERS", "EXPECTS", "ASSUMES", "HYPOTHESIZES",
        "DOUBTS", "CONFIRMS", "DENIES", "QUESTIONS", "UNDERSTANDS", "REMEMBERS",
        "PREDICTS", "LEARNS", "DISCOVERS", "REALIZES", "PERCEIVES", "RECOGNIZES",
        "INTERPRETS", "EVALUATES", "ANALYZES", "SYNTHESIZES", "CONCLUDES",
        "JUSTIFIES",
    ],
    "Agentive": [
        "DOES", "WANTS", "DECIDES", "TRIES", "ACHIEVES", "FAILS", "PLANS",
        "EXECUTES", "MONITORS", "ADAPTS", "CREATES", "DESTROYS", "MODIFIES",
        "ACQUIRES", "RELEASES", "COMMUNICATES", "COORDINATES", "DELEGATES",
        "CONTROLS", "OBSERVES", "INTERVENES", "RESPONDS", "INITIATES_ACTION",
        "TERMINATES_ACTION",
    ],
    "Experiential": [
        "FEELS", "SEES", "ENJOYS", "FEARS", "EXPERIENCES", "SUFFERS",
        "DESIRES", "APPRECIATES", "DISLIKES", "WONDERS", "IMAGINES", "DREAMS",
        "HOPES", "REGRETS", "CELEBRATES", "MOURNS", "REFLECTS", "CONTEMPLATES",
        "RESONATES", "YEARNS", "EMBRACES", "REJECTS", "SEEKS", "AVOIDS",
    ],
}

# Flat lookup: verb → category
_VERB_TO_CATEGORY: dict[str, str] = {
    verb: cat
    for cat, verbs in VERB_TAXONOMY.items()
    for verb in verbs
}

# Flat set for O(1) validation
ALL_VERBS: frozenset[str] = frozenset(_VERB_TO_CATEGORY.keys())


def get_category(verb: str) -> Optional[str]:
    """Return the category for a verb, or None if unknown."""
    return _VERB_TO_CATEGORY.get(verb.upper())


def normalize_verb(raw: str) -> tuple[str, str]:
    """
    Given a raw verb string (possibly free-form from LLM),
    return (normalized_verb, category).
    Falls back to RELATED_TO / Structural if unrecognised.
    """
    upper = raw.upper().replace(" ", "_").replace("-", "_")
    if upper in ALL_VERBS:
        return upper, _VERB_TO_CATEGORY[upper]

    # Fuzzy match: find best prefix
    for verb in ALL_VERBS:
        if upper.startswith(verb[:4]) or verb.startswith(upper[:4]):
            return verb, _VERB_TO_CATEGORY[verb]

    return "RELATED_TO", "Structural"


def category_prompt_hint() -> str:
    """Compact representation for LLM system prompt."""
    lines = []
    for cat, verbs in VERB_TAXONOMY.items():
        lines.append(f"{cat}: {', '.join(verbs)}")
    return "\n".join(lines)
