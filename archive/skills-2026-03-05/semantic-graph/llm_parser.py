"""
llm_parser.py — Claude-powered concept and relation extraction.

Sends batches of chunks to Claude and returns structured
concept nodes + semantic relation edges with NARS truth values.
"""

from __future__ import annotations

import json
import os
from typing import Any

import anthropic

from verbs import category_prompt_hint, normalize_verb

# ── Anthropic client ──────────────────────────────────────────────────────────

_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    return _client


# ── Prompts ───────────────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """You are a semantic graph extraction engine.

Given text chunks, extract:
1. CONCEPTS — named entities, systems, processes, ideas, people, places, events
2. RELATIONS — directed semantic edges between concepts

## Concept types
entity | system | process | idea | attribute | event | person | place | quantity | quality | relation

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
      "type": "entity|system|process|idea|attribute|event|person|place|quantity|quality|relation",
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
""".format(verb_hint=category_prompt_hint())


# ── Batch extraction ──────────────────────────────────────────────────────────


def extract_batch(chunks: list[dict], model: str = "claude-sonnet-4-20250514") -> dict:
    """
    Send a batch of chunks to Claude and return raw parsed JSON.

    Returns:
        {"concepts": [...], "relations": [...]}
    """
    # Build user message: numbered chunk texts
    parts = []
    for i, chunk in enumerate(chunks):
        ctype = chunk.get("chunk_type", "paragraph")
        parts.append(f"[CHUNK {i} | {ctype}]\n{chunk['text']}")

    user_msg = "\n\n---\n\n".join(parts)

    client = _get_client()
    response = client.messages.create(
        model=model,
        max_tokens=4096,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_msg}],
    )

    raw = response.content[0].text.strip()

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


def normalize_parsed(parsed: dict, chunk_ids: list[str], doc_id: str) -> dict:
    """
    Post-process raw LLM output:
    - Normalize verb names via taxonomy
    - Add source provenance
    - Fill defaults
    """
    concepts = []
    for c in parsed.get("concepts", []):
        concepts.append({
            "name": str(c.get("name", "")).strip(),
            "type": c.get("type", "entity"),
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
    model: str = "claude-sonnet-4-20250514",
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
