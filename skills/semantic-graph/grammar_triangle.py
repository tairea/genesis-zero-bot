"""
grammar_triangle.py — NSM + Causality + Qualia computation.

Pure signal, no LLM calls.  Used to annotate every chunk with
a continuous semantic signature before LLM concept extraction.
"""

from __future__ import annotations
from dataclasses import dataclass, field


# ── NSM Primitives (Wierzbicka's semantic primes, key subset) ────────────────

_NSM_ACTIVATIONS: dict[str, list[str]] = {
    "FEEL":    ["feel", "sense", "experience", "emotion", "heart", "soul", "aware", "felt"],
    "THINK":   ["think", "thought", "consider", "ponder", "wonder", "reflect", "believe"],
    "KNOW":    ["know", "knowledge", "understand", "realize", "recognize"],
    "WANT":    ["want", "desire", "wish", "yearn", "need", "strive", "seek"],
    "SEE":     ["see", "observe", "perceive", "notice", "witness"],
    "DO":      ["do", "act", "perform", "execute", "create", "make", "run", "build"],
    "HAPPEN":  ["happen", "occur", "arise", "emerge", "become", "unfold"],
    "SAY":     ["say", "speak", "express", "communicate", "define", "describe"],
    "GOOD":    ["good", "correct", "valid", "safe", "efficient", "clean", "fast"],
    "BAD":     ["bad", "wrong", "broken", "unsafe", "slow", "buggy", "error"],
    "EXIST":   ["exist", "be", "being", "presence", "there is", "instance"],
    "SELF":    ["self", "own", "itself", "internal", "its"],
    "OTHER":   ["other", "external", "third-party", "caller", "user", "client"],
    "BECAUSE": ["because", "reason", "cause", "therefore", "since", "thus", "so"],
    "IF":      ["if", "when", "unless", "condition", "conditional", "guard"],
    "CAN":     ["can", "could", "able", "possible", "capable", "allows", "supports"],
    "MAYBE":   ["maybe", "perhaps", "might", "uncertain", "optional", "todo"],
    "AFTER":   ["after", "then", "next", "later", "subsequently", "following"],
    "BEFORE":  ["before", "prior", "earlier", "first", "initially", "previously"],
    "NOT":     ["not", "no", "never", "without", "lack", "missing", "absent"],
}

# ── Qualia Markers ────────────────────────────────────────────────────────────

_QUALIA_MARKERS: dict[str, dict | list] = {
    "valence": {
        "positive": ["good", "correct", "safe", "clean", "fast", "elegant", "zero",
                     "efficient", "working", "done", "pass", "success"],
        "negative": ["bug", "broken", "error", "crash", "panic", "fail", "dead",
                     "wrong", "issue", "race", "mismatch", "stub", "todo"]
    },
    "arousal":    ["critical", "immediately", "p0", "urgent", "fix", "asap", "!", "severe"],
    "intimacy":   ["internal", "own", "self", "core", "private", "inner", "native"],
    "certainty":  {
        "high": ["always", "guarantee", "proven", "verified", "tested", "stable", "canonical"],
        "low":  ["maybe", "todo", "broken", "wip", "experimental", "aspirational", "draft"]
    },
    "agency":     {
        "active":  ["we", "we've", "ladybug", "the system", "the engine", "the scheduler"],
        "passive": ["it", "this", "the code", "is", "was", "has been"]
    },
    "emergence":  ["emerge", "arise", "become", "evolve", "unfold", "develop", "growing"],
    "continuity": ["persist", "continue", "remain", "stay", "endure", "ongoing", "always"],
    "abstraction":["abstract", "generic", "universal", "generalized", "any", "all", "every"],
}


@dataclass
class GrammarTriangle:
    """
    Continuous semantic signature for a text chunk.
    No LLM — pure keyword activation + heuristics.
    """
    text: str
    nsm: dict[str, float] = field(default_factory=dict)
    qualia: dict[str, float] = field(default_factory=dict)
    causality: dict[str, float] = field(default_factory=dict)
    dominant_mode: str = "cognitive"

    def __post_init__(self) -> None:
        self._compute()

    def _compute(self) -> None:
        t = self.text.lower()

        # ── NSM ───────────────────────────────────────────────────────────────
        for prim, keywords in _NSM_ACTIVATIONS.items():
            count = sum(t.count(kw) for kw in keywords)
            self.nsm[prim] = min(1.0, count * 0.12)

        # ── Qualia ────────────────────────────────────────────────────────────
        # Valence
        pos = sum(t.count(w) for w in _QUALIA_MARKERS["valence"]["positive"])
        neg = sum(t.count(w) for w in _QUALIA_MARKERS["valence"]["negative"])
        self.qualia["valence"] = max(0.0, min(1.0, (pos - neg + 4) / 8))

        # Simple scalar dims
        for dim in ("arousal", "intimacy", "emergence", "continuity", "abstraction"):
            markers = _QUALIA_MARKERS[dim]
            self.qualia[dim] = min(1.0, sum(t.count(w) for w in markers) * 0.18)

        # Bipolar dims
        cert_h = sum(t.count(w) for w in _QUALIA_MARKERS["certainty"]["high"])
        cert_l = sum(t.count(w) for w in _QUALIA_MARKERS["certainty"]["low"])
        self.qualia["certainty"] = max(0.0, min(1.0, (cert_h - cert_l + 3) / 6))

        ag_a = sum(t.count(w) for w in _QUALIA_MARKERS["agency"]["active"])
        ag_p = sum(t.count(w) for w in _QUALIA_MARKERS["agency"]["passive"])
        self.qualia["agency"] = max(0.0, min(1.0, (ag_a - ag_p + 3) / 6))

        # ── Causality flow ────────────────────────────────────────────────────
        past    = sum(t.count(w) for w in ["was", "were", "had", "before", "ago", "previously"])
        present = sum(t.count(w) for w in ["is", "are", "has", "now", "currently", "today"])
        future  = sum(t.count(w) for w in ["will", "shall", "going to", "planned", "next"])
        total = past + present + future + 1
        self.causality["past"]        = past / total
        self.causality["present"]     = present / total
        self.causality["future"]      = future / total
        self.causality["temporality"] = (future - past) / (total + 1)
        self.causality["agency"]      = self.qualia["agency"]

        # ── Dominant mode ─────────────────────────────────────────────────────
        scores = {
            "emotional":   self.nsm.get("FEEL", 0) + self.qualia.get("intimacy", 0),
            "cognitive":   self.nsm.get("THINK", 0) + self.nsm.get("KNOW", 0),
            "existential": self.nsm.get("EXIST", 0) + self.nsm.get("SELF", 0),
            "emergent":    self.qualia.get("emergence", 0) + self.nsm.get("HAPPEN", 0),
            "relational":  self.nsm.get("OTHER", 0) + self.nsm.get("BECAUSE", 0),
            "technical":   self.nsm.get("DO", 0) + self.nsm.get("CAN", 0),
        }
        self.dominant_mode = max(scores, key=scores.__getitem__)

    def to_dict(self) -> dict:
        return {
            "nsm": self.nsm,
            "qualia": self.qualia,
            "causality": self.causality,
            "dominant_mode": self.dominant_mode,
        }


def chunk_text(text: str, max_chars: int = 800, overlap: int = 200) -> list[dict]:
    """
    Split text into overlapping chunks that respect paragraph boundaries.
    Returns list of {text, index, char_start, char_end, chunk_type}.
    """
    chunks: list[dict] = []

    # Detect code blocks and tables first (preserve as-is)
    import re
    code_pattern = re.compile(r'```[\s\S]*?```', re.MULTILINE)
    table_pattern = re.compile(r'^\|.+\|$', re.MULTILINE)

    # Split by double-newline (paragraph boundary)
    paragraphs = re.split(r'\n{2,}', text)

    current_chunk = ""
    current_start = 0
    char_pos = 0
    idx = 0

    for para in paragraphs:
        para_stripped = para.strip()
        if not para_stripped:
            char_pos += len(para) + 2
            continue

        # Detect chunk type
        chunk_type = "paragraph"
        if para_stripped.startswith("```") or para_stripped.startswith("    "):
            chunk_type = "code"
        elif re.match(r'^\|', para_stripped):
            chunk_type = "table"
        elif re.match(r'^#{1,6}\s', para_stripped):
            chunk_type = "heading"
        elif re.match(r'^[-*+]\s', para_stripped):
            chunk_type = "list"
        elif re.match(r'^>', para_stripped):
            chunk_type = "quote"

        # Code and tables always get their own chunk
        if chunk_type in ("code", "table"):
            if current_chunk:
                tri = GrammarTriangle(current_chunk)
                chunks.append({
                    "text": current_chunk,
                    "index": idx,
                    "char_start": current_start,
                    "char_end": char_pos,
                    "chunk_type": "paragraph",
                    **tri.to_dict(),
                })
                idx += 1
                current_chunk = ""
                current_start = char_pos

            tri = GrammarTriangle(para_stripped)
            chunks.append({
                "text": para_stripped,
                "index": idx,
                "char_start": char_pos,
                "char_end": char_pos + len(para),
                "chunk_type": chunk_type,
                **tri.to_dict(),
            })
            idx += 1
            char_pos += len(para) + 2
            current_start = char_pos
            continue

        # Accumulate into current chunk
        if len(current_chunk) + len(para_stripped) > max_chars and current_chunk:
            tri = GrammarTriangle(current_chunk)
            chunks.append({
                "text": current_chunk,
                "index": idx,
                "char_start": current_start,
                "char_end": char_pos,
                "chunk_type": "paragraph",
                **tri.to_dict(),
            })
            idx += 1
            # Overlap: keep tail of previous chunk
            overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
            current_chunk = overlap_text + "\n\n" + para_stripped
            current_start = max(0, char_pos - overlap)
        else:
            current_chunk = (current_chunk + "\n\n" + para_stripped).strip()

        char_pos += len(para) + 2

    # Last chunk
    if current_chunk:
        tri = GrammarTriangle(current_chunk)
        chunks.append({
            "text": current_chunk,
            "index": idx,
            "char_start": current_start,
            "char_end": char_pos,
            "chunk_type": "paragraph",
            **tri.to_dict(),
        })

    return chunks
