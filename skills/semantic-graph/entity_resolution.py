"""
entity_resolution.py — Post-processing entity deduplication.

Finds duplicate concepts via embedding similarity clustering,
confirms merges with LLM, and consolidates graph nodes + edges.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from collections import defaultdict
from typing import Any

from embeddings import embed_texts, embed_text

# ── Configuration ───────────────────────────────────────────────────────────

SIMILARITY_THRESHOLD = float(os.environ.get("ER_SIMILARITY_THRESHOLD", "0.88"))
CLUSTER_BATCH_SIZE = int(os.environ.get("ER_CLUSTER_BATCH", "50"))
SKIP_LLM_ABOVE = float(os.environ.get("ER_AUTO_MERGE_THRESHOLD", "0.96"))


# ── Cosine similarity ──────────────────────────────────────────────────────

def _cosine_sim(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


# ── Find candidate duplicates ──────────────────────────────────────────────

async def find_duplicate_candidates(db, threshold: float = SIMILARITY_THRESHOLD) -> list[tuple[dict, dict, float]]:
    """
    Find pairs of concepts whose embeddings are above the similarity threshold.
    Uses in-memory numpy matrix ops for speed (handles 5000+ concepts in seconds).
    Returns list of (concept_a, concept_b, similarity_score).
    """
    import numpy as np

    # Get all concepts with embeddings
    concepts = await db.query(
        "SELECT id, name, type, description, embedding FROM concept "
        "WHERE embedding IS NOT NONE ORDER BY name"
    )
    if not concepts:
        return []

    print(f"Checking {len(concepts)} concepts for duplicates...", file=sys.stderr)

    # Group concepts by type (only compare within same type)
    type_groups: dict[str, list[int]] = defaultdict(list)
    for i, c in enumerate(concepts):
        type_groups[c.get("type", "entity")].append(i)

    candidates = []
    checked = set()

    for ctype, indices in type_groups.items():
        if len(indices) < 2:
            continue

        # Build embedding matrix for this type group
        group_concepts = [concepts[i] for i in indices]
        embeddings = []
        valid_indices = []
        for gi, c in enumerate(group_concepts):
            emb = c.get("embedding")
            if emb and isinstance(emb, list) and len(emb) > 0:
                embeddings.append(emb)
                valid_indices.append(gi)

        if len(embeddings) < 2:
            continue

        # Compute cosine similarity matrix via numpy
        mat = np.array(embeddings, dtype=np.float32)
        norms = np.linalg.norm(mat, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        mat_normed = mat / norms
        sim_matrix = mat_normed @ mat_normed.T

        # Extract pairs above threshold (upper triangle only)
        rows, cols = np.where(np.triu(sim_matrix, k=1) >= threshold)
        print(f"  Type '{ctype}': {len(valid_indices)} concepts, {len(rows)} candidate pairs", file=sys.stderr)

        for r, c_idx in zip(rows, cols):
            a = group_concepts[valid_indices[r]]
            b = group_concepts[valid_indices[c_idx]]
            pair_key = tuple(sorted([str(a["id"]), str(b["id"])]))
            if pair_key not in checked:
                checked.add(pair_key)
                sim = float(sim_matrix[r, c_idx])
                # Strip embeddings from output (large, not needed downstream)
                a_clean = {k: v for k, v in a.items() if k != "embedding"}
                b_clean = {k: v for k, v in b.items() if k != "embedding"}
                candidates.append((a_clean, b_clean, sim))

    # Sort by similarity descending
    candidates.sort(key=lambda x: x[2], reverse=True)
    return candidates


# ── LLM confirmation ────────────────────────────────────────────────────────

def confirm_merges_llm(candidates: list[tuple[dict, dict, float]]) -> list[tuple[dict, dict, str]]:
    """
    Ask the LLM to confirm which candidates are true duplicates.
    Returns list of (concept_a, concept_b, canonical_name).

    Auto-merges pairs above SKIP_LLM_ABOVE threshold without LLM call.
    """
    from openai import OpenAI

    auto_merges = []
    needs_llm = []

    for a, b, sim in candidates:
        if sim >= SKIP_LLM_ABOVE:
            # Auto-merge: pick the longer/more descriptive name
            canonical = a["name"] if len(a["name"]) >= len(b["name"]) else b["name"]
            auto_merges.append((a, b, canonical))
        else:
            needs_llm.append((a, b, sim))

    if not needs_llm:
        return auto_merges

    # Batch LLM confirmation
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("  No OPENROUTER_API_KEY — skipping LLM confirmation, using auto-merges only", file=sys.stderr)
        return auto_merges

    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
    model = os.environ.get("EXTRACTION_MODEL", "google/gemini-3.1-flash-lite-preview")

    llm_merges = []
    for batch_start in range(0, len(needs_llm), CLUSTER_BATCH_SIZE):
        batch = needs_llm[batch_start:batch_start + CLUSTER_BATCH_SIZE]

        pairs_text = []
        for i, (a, b, sim) in enumerate(batch):
            pairs_text.append(
                f"{i+1}. A: \"{a['name']}\" ({a['type']}) — {a.get('description', '') or 'no description'}\n"
                f"   B: \"{b['name']}\" ({b['type']}) — {b.get('description', '') or 'no description'}\n"
                f"   Similarity: {sim:.3f}"
            )

        prompt = (
            "For each pair below, determine if they refer to the SAME entity/concept.\n"
            "If yes, pick the best canonical name.\n"
            "If no, say NO.\n\n"
            "Respond as JSON array: [{\"pair\": 1, \"same\": true, \"canonical\": \"Best Name\"}, ...]\n\n"
            + "\n".join(pairs_text)
        )

        try:
            response = client.chat.completions.create(
                model=model,
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = response.choices[0].message.content.strip()
            if raw.startswith("```"):
                raw = raw.split("```", 2)[1]
                if raw.startswith("json"):
                    raw = raw[4:]
                raw = raw.rsplit("```", 1)[0].strip()

            decisions = json.loads(raw)
            for d in decisions:
                idx = d["pair"] - 1
                if d.get("same") and 0 <= idx < len(batch):
                    a, b, sim = batch[idx]
                    llm_merges.append((a, b, d.get("canonical", a["name"])))
        except Exception as e:
            print(f"  LLM confirmation failed: {e}", file=sys.stderr)

    return auto_merges + llm_merges


# ── Execute merges in SurrealDB ─────────────────────────────────────────────

async def execute_merges(
    db,
    merges: list[tuple[dict, dict, str]],
    verbose: bool = True,
) -> int:
    """
    For each confirmed merge pair (a, b, canonical_name):
    1. Pick the keeper (a) and the duplicate (b)
    2. Redirect all edges pointing to b → point to a
    3. Merge NARS evidence
    4. Add b's name as alias on a
    5. Delete b

    Returns count of merged concepts.
    """
    merged = 0
    for a, b, canonical in merges:
        keeper_id = a["id"]
        dup_id = b["id"]

        # Ensure keeper has the canonical name
        if a["name"] != canonical:
            keeper_id, dup_id = b["id"], a["id"]
            a, b = b, a

        try:
            # Add duplicate's name as alias
            await db.query(
                "UPDATE $id SET aliases += $alias",
                {"id": keeper_id, "alias": b["name"]},
            )

            # Merge NARS evidence
            keeper_data = await db.query(
                "SELECT nars_frequency, nars_confidence, evidence_count FROM $id",
                {"id": keeper_id},
            )
            dup_data = await db.query(
                "SELECT nars_frequency, nars_confidence, evidence_count FROM $id",
                {"id": dup_id},
            )
            if keeper_data and dup_data:
                k, d = keeper_data[0], dup_data[0]
                if isinstance(k, dict) and isinstance(d, dict):
                    from graph_extract import nars_revise
                    f, c, n = nars_revise(
                        k.get("nars_frequency", 1.0), k.get("nars_confidence", 0.5),
                        k.get("evidence_count", 1),
                        d.get("nars_frequency", 1.0), d.get("nars_confidence", 0.5),
                        d.get("evidence_count", 1),
                    )
                    await db.query(
                        "UPDATE $id SET nars_frequency = $f, nars_confidence = $c, evidence_count = $n",
                        {"id": keeper_id, "f": f, "c": c, "n": n},
                    )

            # Redirect incoming relations (dup as target)
            await db.query(
                "UPDATE relates SET out = $keeper WHERE out = $dup",
                {"keeper": keeper_id, "dup": dup_id},
            )

            # Redirect outgoing relations (dup as source)
            await db.query(
                "UPDATE relates SET in = $keeper WHERE in = $dup",
                {"keeper": keeper_id, "dup": dup_id},
            )

            # Redirect mentions
            await db.query(
                "UPDATE mentions SET out = $keeper WHERE out = $dup",
                {"keeper": keeper_id, "dup": dup_id},
            )

            # Delete duplicate
            await db.query("DELETE $id", {"id": dup_id})

            merged += 1
            if verbose:
                print(f"  Merged: \"{b['name']}\" -> \"{a['name']}\"", file=sys.stderr)

        except Exception as e:
            print(f"  Merge failed ({a['name']} <- {b['name']}): {e}", file=sys.stderr)

    return merged


# ── Main entry point ────────────────────────────────────────────────────────

async def resolve_entities(
    db,
    threshold: float = SIMILARITY_THRESHOLD,
    dry_run: bool = False,
    verbose: bool = True,
) -> dict:
    """
    Full entity resolution pipeline:
    1. Find candidates by embedding similarity
    2. Confirm with LLM
    3. Execute merges

    Returns {"candidates": N, "confirmed": N, "merged": N}
    """
    candidates = await find_duplicate_candidates(db, threshold)
    print(f"Found {len(candidates)} candidate duplicate pairs", file=sys.stderr)

    if not candidates:
        return {"candidates": 0, "confirmed": 0, "merged": 0}

    if verbose:
        print(f"\nTop 20 candidates:", file=sys.stderr)
        for a, b, sim in candidates[:20]:
            print(f"  [{sim:.3f}] \"{a['name']}\" ({a['type']}) <-> \"{b['name']}\" ({b['type']})", file=sys.stderr)

    confirmed = confirm_merges_llm(candidates)
    print(f"Confirmed {len(confirmed)} merges", file=sys.stderr)

    if dry_run:
        if verbose:
            for a, b, canonical in confirmed:
                print(f"  [dry-run] Would merge: \"{b['name']}\" -> \"{canonical}\"", file=sys.stderr)
        return {"candidates": len(candidates), "confirmed": len(confirmed), "merged": 0}

    merged = await execute_merges(db, confirmed, verbose=verbose)
    print(f"Merged {merged} duplicate concepts", file=sys.stderr)

    return {"candidates": len(candidates), "confirmed": len(confirmed), "merged": merged}


# ── CLI ─────────────────────────────────────────────────────────────────────

async def _cli_main():
    import argparse
    parser = argparse.ArgumentParser(description="Resolve duplicate entities in the knowledge graph")
    parser.add_argument("--threshold", type=float, default=SIMILARITY_THRESHOLD,
                        help=f"Similarity threshold (default: {SIMILARITY_THRESHOLD})")
    parser.add_argument("--dry-run", action="store_true", help="Find candidates without merging")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    from surrealdb import AsyncSurreal
    db_url = os.environ.get("SURREALDB_URL", "ws://127.0.0.1:8000")
    db = AsyncSurreal(url=db_url)
    await db.connect()
    await db.signin({"username": "root", "password": os.environ.get("SURREAL_PASS", "root")})
    await db.use("semantic_graph", "main")

    result = await resolve_entities(db, threshold=args.threshold, dry_run=args.dry_run, verbose=args.verbose)
    print(json.dumps(result, indent=2))

    await db.close()


if __name__ == "__main__":
    asyncio.run(_cli_main())
