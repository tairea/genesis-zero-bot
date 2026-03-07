"""
communities.py — Community detection and summarization for the knowledge graph.

Clusters densely-connected concepts into communities using label propagation,
then generates LLM summaries for each community. Enables "global search" —
answering questions that require synthesizing information across many documents.

Usage:
    python communities.py detect          # Find communities
    python communities.py detect --summarize  # Find + generate summaries
    python communities.py list            # Show existing communities
    python communities.py search "query"  # Search community summaries
"""

from __future__ import annotations

import asyncio
import json
import os
import random
import sys
from collections import defaultdict
from typing import Any

from embeddings import embed_text, embed_texts


# ── Label Propagation (no networkx dependency) ──────────────────────────────

def label_propagation(
    nodes: list[str],
    edges: list[tuple[str, str, float]],
    max_iter: int = 30,
    min_community_size: int = 3,
) -> dict[int, list[str]]:
    """
    Label propagation community detection.

    Args:
        nodes: list of node IDs
        edges: list of (source, target, weight) tuples
        max_iter: maximum iterations
        min_community_size: discard communities smaller than this

    Returns:
        {community_id: [node_id, ...]}
    """
    # Initialize: each node gets its own label
    labels = {n: i for i, n in enumerate(nodes)}

    # Build adjacency with weights
    adj: dict[str, list[tuple[str, float]]] = defaultdict(list)
    for src, tgt, w in edges:
        if src in labels and tgt in labels:
            adj[src].append((tgt, w))
            adj[tgt].append((src, w))

    node_list = list(nodes)

    for iteration in range(max_iter):
        changed = False
        random.shuffle(node_list)

        for node in node_list:
            neighbors = adj.get(node, [])
            if not neighbors:
                continue

            # Count weighted label frequencies among neighbors
            label_weights: dict[int, float] = defaultdict(float)
            for neighbor, weight in neighbors:
                label_weights[labels[neighbor]] += weight

            # Pick the label with highest weight
            best_label = max(label_weights, key=label_weights.get)
            if labels[node] != best_label:
                labels[node] = best_label
                changed = True

        if not changed:
            break

    # Group nodes by label
    communities: dict[int, list[str]] = defaultdict(list)
    for node, label in labels.items():
        communities[label].append(node)

    # Filter by minimum size and re-index
    result = {}
    for i, (_, members) in enumerate(
        sorted(communities.items(), key=lambda x: len(x[1]), reverse=True)
    ):
        if len(members) >= min_community_size:
            result[i] = members

    return result


# ── Build graph from SurrealDB ──────────────────────────────────────────────

async def _build_graph(db) -> tuple[list[dict], list[tuple[str, str, float]]]:
    """Fetch concepts and relations, return as graph structure."""
    concepts = await db.query(
        "SELECT id, name, type, description, rung, nars_confidence FROM concept"
    )
    relations = await db.query(
        "SELECT in.name AS source, out.name AS target, nars_confidence, verb FROM relates"
    )

    if not concepts or not relations:
        return concepts or [], []

    edges = []
    for r in relations:
        src = r.get("source", "")
        tgt = r.get("target", "")
        w = r.get("nars_confidence", 0.5)
        if src and tgt:
            edges.append((str(src), str(tgt), float(w)))

    return concepts, edges


# ── Generate community summaries via LLM ─────────────────────────────────────

def _summarize_community(
    community_id: int,
    members: list[dict],
    internal_relations: list[dict],
) -> str:
    """Generate a natural language summary of a community via LLM."""
    from openai import OpenAI

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        # Fallback: generate a simple summary without LLM
        names = [m["name"] for m in members[:10]]
        types = list(set(m.get("type", "?") for m in members))
        return (
            f"Community of {len(members)} concepts ({', '.join(types)}): "
            f"{', '.join(names)}"
        )

    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
    model = os.environ.get("EXTRACTION_MODEL", "anthropic/claude-sonnet-4")

    # Build context for the LLM
    concept_text = "\n".join(
        f"- {m['name']} ({m.get('type', '?')}): {m.get('description', '') or 'no description'}"
        for m in members[:20]
    )
    relation_text = "\n".join(
        f"- {r['source']} --{r['verb']}--> {r['target']}"
        for r in internal_relations[:15]
    )

    prompt = (
        f"Summarize this cluster of {len(members)} related concepts from a regenerative community knowledge graph.\n"
        f"Write 2-3 sentences describing the main theme, what connects them, and why they matter.\n\n"
        f"Concepts:\n{concept_text}\n\n"
        f"Relationships:\n{relation_text}\n\n"
        f"Summary:"
    )

    try:
        response = client.chat.completions.create(
            model=model,
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"  LLM summary failed for community {community_id}: {e}", file=sys.stderr)
        names = [m["name"] for m in members[:10]]
        return f"Community of {len(members)} concepts: {', '.join(names)}"


# ── Store communities in SurrealDB ───────────────────────────────────────────

async def _store_communities(
    db,
    communities: dict[int, list[str]],
    concept_lookup: dict[str, dict],
    relations: list[dict],
    summarize: bool = True,
):
    """Store detected communities in SurrealDB."""
    from surrealdb import RecordID

    # Ensure community table exists
    await db.query(
        "DEFINE TABLE IF NOT EXISTS community SCHEMALESS "
        "COMMENT 'Cluster of related concepts detected by community detection'"
    )
    await db.query("DEFINE FIELD IF NOT EXISTS name ON community TYPE string")
    await db.query("DEFINE FIELD IF NOT EXISTS summary ON community TYPE option<string>")
    await db.query("DEFINE FIELD IF NOT EXISTS member_count ON community TYPE int")
    await db.query("DEFINE FIELD IF NOT EXISTS member_names ON community TYPE array<string> DEFAULT []")
    await db.query("DEFINE FIELD IF NOT EXISTS top_types ON community TYPE object DEFAULT {}")
    await db.query("DEFINE FIELD IF NOT EXISTS embedding ON community TYPE option<array<float>>")
    await db.query("DEFINE FIELD IF NOT EXISTS created_at ON community TYPE datetime DEFAULT time::now()")

    # Relation table: concept belongs_to community
    await db.query(
        "DEFINE TABLE IF NOT EXISTS belongs_to TYPE RELATION SCHEMALESS "
        "COMMENT 'concept belongs_to community'"
    )

    # Clear old communities
    await db.query("DELETE community")
    await db.query("DELETE belongs_to")

    stored = 0
    for comm_id, member_names in communities.items():
        members = [concept_lookup[n] for n in member_names if n in concept_lookup]
        if not members:
            continue

        # Count types
        type_counts: dict[str, int] = defaultdict(int)
        for m in members:
            type_counts[m.get("type", "?")] += 1
        top_type = max(type_counts, key=type_counts.get)

        # Find internal relations
        name_set = set(member_names)
        internal_rels = [
            r for r in relations
            if r.get("source", "") in name_set and r.get("target", "") in name_set
        ]

        # Generate name from top concepts
        sorted_members = sorted(members, key=lambda m: m.get("nars_confidence", 0), reverse=True)
        comm_name = f"{sorted_members[0]['name']} / {sorted_members[1]['name']}" if len(sorted_members) >= 2 else sorted_members[0]["name"]

        # Generate summary
        summary = None
        if summarize:
            summary = _summarize_community(comm_id, members, internal_rels)

        # Store community node
        comm_record_id = f"community:c{comm_id}"
        await db.query(
            """
            INSERT INTO community {
                id: $id,
                name: $name,
                summary: $summary,
                member_count: $count,
                member_names: $names,
                top_types: $types,
                created_at: time::now()
            } ON DUPLICATE KEY UPDATE
                name = $input.name,
                summary = $input.summary,
                member_count = $input.member_count,
                member_names = $input.member_names,
                top_types = $input.top_types
            """,
            {
                "id": comm_record_id,
                "name": comm_name,
                "summary": summary,
                "count": len(members),
                "names": member_names[:50],
                "types": dict(type_counts),
            },
        )

        # Embed the community summary for search
        comm_rid = RecordID("community", f"c{comm_id}")
        if summary:
            try:
                vec = embed_text(f"{comm_name}: {summary}")
                await db.query("UPDATE $id SET embedding = $vec", {"id": comm_rid, "vec": vec})
            except Exception as e:
                print(f"  Embedding failed for community {comm_id}: {e}", file=sys.stderr)

        # Create belongs_to edges
        for m in members:
            mid = m.get("id")
            if mid:
                try:
                    await db.query(
                        "RELATE $concept->belongs_to->$community",
                        {"concept": mid, "community": comm_rid},
                    )
                except Exception:
                    pass

        stored += 1
        print(f"  Community {comm_id}: {comm_name} ({len(members)} members)", file=sys.stderr)

    return stored


# ── Main entry point ─────────────────────────────────────────────────────────

async def detect_communities(
    db,
    min_size: int = 3,
    max_iter: int = 30,
    summarize: bool = True,
    verbose: bool = True,
) -> dict:
    """
    Detect communities in the knowledge graph.

    Returns: {"communities": N, "total_members": N, "largest": N}
    """
    concepts, edges = await _build_graph(db)

    if not concepts or not edges:
        print("No concepts or relations found.", file=sys.stderr)
        return {"communities": 0, "total_members": 0, "largest": 0}

    # Build lookup
    concept_lookup = {}
    node_names = []
    for c in concepts:
        name = c.get("name", "")
        if name:
            concept_lookup[name] = c
            node_names.append(name)

    if verbose:
        print(f"Graph: {len(node_names)} nodes, {len(edges)} edges", file=sys.stderr)

    # Run label propagation
    communities = label_propagation(node_names, edges, max_iter=max_iter, min_community_size=min_size)

    if verbose:
        print(f"Found {len(communities)} communities (min size {min_size})", file=sys.stderr)

    # Fetch full relations for summary context
    relations = await db.query(
        "SELECT in.name AS source, verb, out.name AS target FROM relates"
    )
    rel_list = []
    for r in (relations or []):
        if isinstance(r, dict):
            rel_list.append({
                "source": str(r.get("source", "")),
                "verb": r.get("verb", ""),
                "target": str(r.get("target", "")),
            })

    # Store in DB
    stored = await _store_communities(db, communities, concept_lookup, rel_list, summarize=summarize)

    total_members = sum(len(m) for m in communities.values())
    largest = max(len(m) for m in communities.values()) if communities else 0

    return {"communities": stored, "total_members": total_members, "largest": largest}


async def search_communities(db, query: str, limit: int = 5) -> list[dict]:
    """Search community summaries by embedding similarity."""
    query_vec = embed_text(query)
    results = await db.query(
        """
        SELECT id, name, summary, member_count, member_names, top_types,
               vector::similarity::cosine(embedding, $vec) AS score
        FROM community
        WHERE embedding IS NOT NONE
        ORDER BY score DESC
        LIMIT $limit
        """,
        {"vec": query_vec, "limit": limit},
    )
    return results or []


# ── CLI ─────────────────────────────────────────────────────────────────────

async def _cli_main():
    import argparse
    parser = argparse.ArgumentParser(description="Community detection for knowledge graph")
    sub = parser.add_subparsers(dest="command", required=True)

    p_detect = sub.add_parser("detect", help="Detect communities")
    p_detect.add_argument("--min-size", type=int, default=3, help="Min community size")
    p_detect.add_argument("--summarize", action="store_true", help="Generate LLM summaries")
    p_detect.add_argument("-v", "--verbose", action="store_true", default=True)

    p_list = sub.add_parser("list", help="List existing communities")

    p_search = sub.add_parser("search", help="Search communities")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("--limit", type=int, default=5)

    args = parser.parse_args()

    from surrealdb import AsyncSurreal
    db_url = os.environ.get("SURREALDB_URL", "ws://127.0.0.1:8000")
    db = AsyncSurreal(url=db_url)
    await db.connect()
    await db.signin({"username": "root", "password": os.environ.get("SURREAL_PASS", "root")})
    await db.use("semantic_graph", "main")

    if args.command == "detect":
        result = await detect_communities(
            db, min_size=args.min_size, summarize=args.summarize, verbose=args.verbose,
        )
        print(json.dumps(result, indent=2))

    elif args.command == "list":
        comms = await db.query("SELECT name, summary, member_count, top_types FROM community ORDER BY member_count DESC")
        for c in (comms or []):
            print(f"\n[{c.get('member_count', 0)} members] {c.get('name', '?')}")
            if c.get("summary"):
                print(f"  {c['summary']}")

    elif args.command == "search":
        results = await search_communities(db, args.query, limit=args.limit)
        for r in results:
            print(f"\n[{r.get('score', 0):.3f}] {r.get('name', '?')} ({r.get('member_count', 0)} members)")
            if r.get("summary"):
                print(f"  {r['summary']}")

    await db.close()


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(__file__))
    asyncio.run(_cli_main())
