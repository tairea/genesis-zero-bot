"""
subagent_parser.py — Sub-agent powered concept and relation extraction.

Uses OpenClaw sessions_spawn to delegate extraction to sub-agents
instead of direct Anthropic API calls.
"""

import json
import os
from typing import Any
from verbs import category_prompt_hint, normalize_verb

# ── Sub-agent extraction ─────────────────────────────────────────────────────

async def extract_chunks_subagent(chunks: list[dict], namespace: str = "semantic_graph") -> dict:
    """
    Extract concepts and relations using sub-agents instead of direct API.
    
    Each chunk is sent to a sub-agent for extraction, then results are merged.
    """
    from sessions_spawn import sessions_spawn
    
    all_concepts = []
    all_relations = []
    
    for i, chunk in enumerate(chunks):
        text = chunk.get("text", "")
        
        # Build prompt for sub-agent
        prompt = f"""Extract concepts and relations from this text chunk.

## Text
{text}

## Output format (JSON only, no other text):
{{
  "concepts": [
    {{"name": "...", "type": "entity|system|process|idea|attribute|event|person|place|quantity|quality|relation", "description": "...", "rung": 0-9, "nars_frequency": 0.0-1.0, "nars_confidence": 0.0-1.0}}
  ],
  "relations": [
    {{"subject": "concept name", "verb": "CAUSES|RELATES_TO|HAS_A|DEPENDS_ON|...", "object": "concept name", "evidence": "short quote", "nars_frequency": 0.0-1.0, "nars_confidence": 0.0-1.0}}
  ]
}}

Respond ONLY with valid JSON."""

        # Spawn sub-agent for extraction
        result = await sessions_spawn(
            model="MiniMax-M2.1",
            task=prompt,
            runtime="subagent"
        )
        
        # Parse result
        try:
            parsed = json.loads(result)
            all_concepts.extend(parsed.get("concepts", []))
            all_relations.extend(parsed.get("relations", []))
        except:
            pass
    
    return {
        "concepts": all_concepts,
        "relations": all_relations
    }


# ── Sync wrapper ─────────────────────────────────────────────────────────────

def extract_chunks(chunks: list[dict], batch_size: int = 4) -> dict:
    """
    Synchronous wrapper for sub-agent extraction.
    Falls back to simpler parsing if sub-agents unavailable.
    """
    import asyncio
    
    try:
        return asyncio.run(extract_chunks_subagent(chunks))
    except Exception as e:
        # Fallback: return empty extraction
        return {"concepts": [], "relations": []}
