"""
llm_parser.py — Claude-powered concept and relation extraction.

Sends batches of chunks to Claude and returns structured
concept nodes + semantic relation edges with NARS truth values.
"""

from __future__ import annotations

import json
import os
from typing import Any

from openai import OpenAI

from verbs import category_prompt_hint, normalize_verb

# ── LLM client (OpenRouter-compatible) ───────────────────────────────────────

_client: OpenAI | None = None

# Default model — can be overridden via EXTRACTION_MODEL env var
DEFAULT_MODEL = os.environ.get("EXTRACTION_MODEL", "google/gemini-3.1-flash-lite-preview")


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            raise RuntimeError("OPENROUTER_API_KEY env var is required")
        _client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
    return _client


# ── Prompts ───────────────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """You are a semantic graph extraction engine for RegenTribes, a regenerative community platform.

Given text chunks, extract:
1. CONCEPTS — named entities, systems, processes, ideas, people, places, events, skills, resources, organizations, practices
2. RELATIONS — directed semantic edges between concepts

## Concept types (choose the MOST SPECIFIC type)
person         — named individuals, community members, roles (e.g. "Ian", "Local Coordinator", "Facilitator")
organization   — groups, companies, cooperatives, DAOs, collectives (e.g. "RegenTribes", "Sunrise Labs")
project        — initiatives, programs, ventures, campaigns (e.g. "Eco-Housing Project", "Regen Week")
skill          — capabilities, competencies, expertise areas (e.g. "Permaculture Design", "Facilitation", "Composting")
resource       — tangible or intangible assets: land, tools, funding, materials, data (e.g. "Community Land", "Seed Library", "Grant Funding")
place          — physical locations, neighborhoods, regions, sites (e.g. "Auckland", "Site A", "Food Forest")
event          — gatherings, meetings, workshops, milestones (e.g. "Weekly Circle", "Regen Week 2026", "Buildathon")
system         — frameworks, platforms, architectures, methodologies (e.g. "Meta-Fractal DAO", "SurrealDB", "RGEM")
process        — workflows, procedures, sequences, pipelines (e.g. "Community Alchemy", "Spiral Development", "Consensus Building")
practice       — techniques, methods, traditions, design patterns (e.g. "Companion Planting", "Sociocracy", "Seed Saving")
idea           — principles, values, theories, visions (e.g. "Food Sovereignty", "Regenerative Development", "Commons")
attribute      — properties, measurements, specifications, metrics (e.g. "Carbon Footprint", "Member Count", "Budget")
quantity       — specific numbers, amounts, thresholds (e.g. "70% Agreement Target", "$200K Budget")

## Rung levels (abstraction depth)
R0=literal name  R1=shallow inference  R2=contextual  R3=analogical
R4=abstract pattern  R5=structural schema  R6=counterfactual  R7=meta  R8=recursive  R9=transcendent

## Relation verbs (use EXACTLY one per edge)
{verb_hint}

## NARS truth values
- frequency (0.0–1.0): how consistently true is this statement?
- confidence (0.0–1.0): how much evidence supports it?
  - Direct statement → confidence 0.8–0.95
  - Implied/inferred → confidence 0.4–0.7
  - Speculative → confidence 0.1–0.4

## Output format
Return ONLY valid JSON matching this schema exactly:
{{
  "concepts": [
    {{
      "name": "string",
      "type": "person|organization|project|skill|resource|place|event|system|process|practice|idea|attribute|quantity",
      "description": "one-sentence description",
      "rung": 0,
      "aliases": [],
      "tags": [],
      "qualia": {{"valence": 0.5, "certainty": 0.5, "abstraction": 0.0}},
      "nars_frequency": 1.0,
      "nars_confidence": 0.9
    }}
  ],
  "relations": [
    {{
      "subject": "concept name",
      "verb": "VERB_NAME",
      "object": "concept name",
      "evidence": "exact quote from text supporting this",
      "nars_frequency": 1.0,
      "nars_confidence": 0.8,
      "valid_from": null,
      "valid_until": null
    }}
  ]
}}

Rules:
- Both subject and object must appear in the concepts list
- Prefer specific verbs over RELATED_TO
- Extract 3–15 concepts per chunk batch; 2–20 relations
- Aliases: include acronyms, alternate names, camelCase variants
- Evidence: quote ≤50 chars from the source text
- Do NOT invent facts not present in the text

## CRITICAL: What makes a good concept
- GOOD concepts: named entities, proper nouns, domain-specific terms, tools, frameworks, techniques, organizations, named processes
  Examples: "Permaculture", "SurrealDB", "Composting", "Community Land Trust", "Biomass Gasification"
- BAD concepts: generic verbs, adjectives, common words, function words, pronouns, articles
  DO NOT extract: "Add", "Remove", "Table", "following", "using", "Active", "New", "Try", "Are", "Does", "Get"
- Concept names must be CLEAN: no newlines, no trailing fragments like "\\nSee" or "\\nThe", no partial sentences
- Descriptions must be specific to the source text, not just "Extracted from documentation"
- If a chunk is mostly code or config syntax, extract the TOOLS and FRAMEWORKS, not code tokens
""".format(verb_hint=category_prompt_hint())


# ── Batch extraction ──────────────────────────────────────────────────────────


def extract_batch(chunks: list[dict], model: str | None = None) -> dict:
    """
    Send a batch of chunks to the LLM via OpenRouter and return raw parsed JSON.

    Returns:
        {"concepts": [...], "relations": [...]}
    """
    model = model or DEFAULT_MODEL

    # Build user message: numbered chunk texts
    parts = []
    for i, chunk in enumerate(chunks):
        ctype = chunk.get("chunk_type", "paragraph")
        parts.append(f"[CHUNK {i} | {ctype}]\n{chunk['text']}")

    user_msg = "\n\n---\n\n".join(parts)

    client = _get_client()
    response = client.chat.completions.create(
        model=model,
        max_tokens=4096,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
    )

    raw = response.choices[0].message.content.strip()

    # Strip markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("```", 2)[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.rsplit("```", 1)[0].strip()

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM returned invalid JSON: {e}\n---\n{raw[:500]}") from e

    return parsed


def _is_junk_concept(name: str) -> bool:
    """Filter out generic/stopword concepts that aren't meaningful graph nodes."""
    # Too short to be meaningful
    if len(name) <= 2:
        return True
    # Contains newlines (parsing artifact)
    if "\n" in name:
        return True
    # Common stopwords that should never be concepts
    STOP_CONCEPTS = {
        "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "shall", "can", "need", "must",
        "for", "and", "but", "or", "nor", "not", "no", "yes", "yet",
        "if", "then", "else", "when", "where", "how", "what", "which", "who",
        "this", "that", "these", "those", "it", "its", "they", "them", "we",
        "add", "get", "set", "put", "run", "let", "try", "use", "see", "new",
        "old", "big", "top", "end", "ask", "say", "go", "all", "any", "few",
        "most", "some", "each", "every", "both", "many", "much", "more",
        "other", "same", "such", "also", "just", "only", "very", "too",
        "now", "here", "there", "why", "often", "never", "always",
        "true", "false", "none", "null", "ok", "done", "found", "made",
        "show", "hide", "move", "call", "take", "give", "keep", "make",
        "come", "know", "think", "want", "look", "find", "tell", "turn",
        "start", "begin", "stop", "close", "open", "read", "write",
        "actual", "active", "added", "adjust", "allow", "better", "built",
        "clear", "common", "currently", "default", "final", "following",
        "general", "good", "great", "initial", "last", "main", "next",
        "present", "primary", "related", "required", "similar", "simple",
        "specific", "standard", "using", "various", "without",
    }
    if name.lower() in STOP_CONCEPTS:
        return True
    # Single generic word (lowercase, no spaces) — likely not a domain concept
    if " " not in name and name[0].islower() and len(name) <= 8:
        return True
    return False


_VALID_TYPES = {
    "person", "organization", "project", "skill", "resource", "place", "event",
    "system", "process", "practice", "idea", "attribute", "quantity",
}
# Map old/variant types to new ontology
_TYPE_MAP = {
    "entity": "system",  # generic fallback
    "quality": "attribute",
    "relation": "idea",
    "concept": "idea",
    "specification": "system",
}


def _normalize_type(raw_type: str) -> str:
    """Map concept types to the RegenTribes ontology."""
    t = raw_type.lower().strip()
    if t in _VALID_TYPES:
        return t
    return _TYPE_MAP.get(t, "system")


def normalize_parsed(parsed: dict, chunk_ids: list[str], doc_id: str) -> dict:
    """
    Post-process raw LLM output:
    - Filter junk/generic concepts
    - Normalize verb names via taxonomy
    - Clean concept names (strip newlines, fragments)
    - Add source provenance
    - Fill defaults
    """
    concepts = []
    for c in parsed.get("concepts", []):
        name = str(c.get("name", "")).strip()
        # Clean newlines from names
        name = name.split("\n")[0].strip()
        if not name or _is_junk_concept(name):
            continue
        concepts.append({
            "name": name,
            "type": _normalize_type(c.get("type", "entity")),
            "description": c.get("description", ""),
            "rung": int(c.get("rung", 0)),
            "aliases": c.get("aliases", []),
            "tags": c.get("tags", []),
            "qualia": c.get("qualia", {}),
            "nars_frequency": float(c.get("nars_frequency", 1.0)),
            "nars_confidence": float(c.get("nars_confidence", 0.9)),
            "evidence_count": 1,
            "source_doc": doc_id,
        })

    relations = []
    for r in parsed.get("relations", []):
        raw_verb = str(r.get("verb", "RELATED_TO"))
        verb, verb_category = normalize_verb(raw_verb)
        relations.append({
            "subject": str(r.get("subject", "")).strip(),
            "verb": verb,
            "verb_category": verb_category,
            "object": str(r.get("object", "")).strip(),
            "evidence": r.get("evidence", ""),
            "nars_frequency": float(r.get("nars_frequency", 1.0)),
            "nars_confidence": float(r.get("nars_confidence", 0.8)),
            "evidence_count": 1,
            "valid_from": r.get("valid_from"),
            "valid_until": r.get("valid_until"),
            "source_chunks": chunk_ids,
            "source_doc": doc_id,
        })

    return {"concepts": concepts, "relations": relations}


def extract_chunks(
    chunks: list[dict],
    doc_id: str,
    batch_size: int = 4,
    model: str | None = None,
) -> dict:
    """
    Extract concepts and relations from all chunks, batched.

    Returns merged {"concepts": [...], "relations": [...]}
    """
    all_concepts: list[dict] = []
    all_relations: list[dict] = []

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        chunk_ids = [c.get("id", f"chunk:{i+j}") for j, c in enumerate(batch)]

        raw = extract_batch(batch, model=model)
        normalized = normalize_parsed(raw, chunk_ids, doc_id)

        all_concepts.extend(normalized["concepts"])
        all_relations.extend(normalized["relations"])

    return {"concepts": all_concepts, "relations": all_relations}
