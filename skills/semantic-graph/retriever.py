"""
retriever.py — Hybrid retrieval pipeline combining vector search + graph traversal.

Retrieves structured context for LLM consumption:
1. Vector search for seed concepts (cosine similarity)
2. Graph traversal for connected context (1-2 hop neighbors + relations)
3. Source chunk text for passage-level evidence
4. Reciprocal Rank Fusion to merge and rerank results

Usage:
    from retriever import retrieve
    context = await retrieve(db, "what is permaculture?")
    # context.text -> formatted string for LLM prompt
    # context.concepts -> list of relevant concepts
    # context.relations -> list of relevant relations
    # context.chunks -> list of source text passages

CLI:
    python retriever.py "what is permaculture?" --limit 10
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from dataclasses import dataclass, field
from typing import Any

from embeddings import embed_text, embed_texts


# ── Data classes ────────────────────────────────────────────────────────────

@dataclass
class RetrievalContext:
    """Structured context from hybrid retrieval."""
    query: str
    concepts: list[dict] = field(default_factory=list)
    relations: list[dict] = field(default_factory=list)
    chunks: list[dict] = field(default_factory=list)
    communities: list[dict] = field(default_factory=list)
    scores: dict[str, float] = field(default_factory=dict)  # concept_name -> fused score

    @property
    def text(self) -> str:
        """Format as text context for LLM prompt injection."""
        parts = []

        if self.concepts:
            parts.append("## Relevant Concepts")
            for c in self.concepts[:15]:
                score = self.scores.get(c.get("name", ""), 0)
                conf = c.get("nars_confidence", 0)
                desc = c.get("description", "") or ""
                parts.append(
                    f"- **{c['name']}** ({c.get('type', '?')}, R{c.get('rung', 0)}) "
                    f"[relevance={score:.2f}, confidence={conf:.2f}]: {desc}"
                )

        if self.relations:
            parts.append("\n## Connections")
            for r in self.relations[:20]:
                evidence = f' — "{r["evidence"]}"' if r.get("evidence") else ""
                conf = r.get("nars_confidence", 0)
                parts.append(
                    f"- {r['source']} --{r['verb']}--> {r['target']} "
                    f"[confidence={conf:.2f}]{evidence}"
                )

        if self.communities:
            parts.append("\n## Thematic Clusters")
            for cm in self.communities[:3]:
                members = cm.get("member_count", 0)
                score = cm.get("score", 0)
                parts.append(
                    f"- **{cm.get('name', '?')}** ({members} members) "
                    f"[relevance={score:.2f}]: {cm.get('summary', '')}"
                )

        if self.chunks:
            parts.append("\n## Source Passages")
            for ch in self.chunks[:5]:
                doc = ch.get("doc_title", "unknown")
                parts.append(f"[From: {doc}]\n{ch['text']}\n")

        return "\n".join(parts) if parts else "(No relevant knowledge found)"

    def to_dict(self) -> dict:
        return {
            "query": self.query,
            "concepts": self.concepts,
            "relations": self.relations,
            "chunks": self.chunks,
            "communities": self.communities,
            "scores": self.scores,
            "formatted_text": self.text,
        }


# ── Reciprocal Rank Fusion ─────────────────────────────────────────────────

def reciprocal_rank_fusion(
    *ranked_lists: list[dict],
    key: str = "name",
    k: int = 60,
    weights: list[float] | None = None,
) -> list[tuple[str, float]]:
    """
    Combine multiple ranked lists using RRF.
    Optional weights give more importance to specific lists.
    Returns sorted list of (item_key, fused_score).
    """
    if weights is None:
        weights = [1.0] * len(ranked_lists)

    scores: dict[str, float] = {}
    for ranked, w in zip(ranked_lists, weights):
        for rank, item in enumerate(ranked):
            item_key = item.get(key, str(item.get("id", "")))
            scores[item_key] = scores.get(item_key, 0) + w / (k + rank + 1)

    return sorted(scores.items(), key=lambda x: x[1], reverse=True)


# ── Maximal Marginal Relevance ─────────────────────────────────────────────

def mmr_rerank(
    items: list[dict],
    query_vec: list[float],
    embeddings: list[list[float]],
    lambda_: float = 0.7,
    limit: int = 10,
) -> list[dict]:
    """
    Maximal Marginal Relevance reranking for diversity.

    Balances relevance to query (lambda_) vs novelty relative to already-selected
    items (1 - lambda_). Higher lambda_ = more relevance, lower = more diversity.
    """
    import numpy as np

    if not items or not embeddings:
        return items[:limit]

    q = np.array(query_vec, dtype=np.float32)
    q_norm = q / (np.linalg.norm(q) or 1.0)

    emb_mat = np.array(embeddings, dtype=np.float32)
    norms = np.linalg.norm(emb_mat, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    emb_normed = emb_mat / norms

    # Query similarity for each item
    q_sims = emb_normed @ q_norm

    selected_indices: list[int] = []
    remaining = set(range(len(items)))

    for _ in range(min(limit, len(items))):
        best_idx = -1
        best_score = -float("inf")

        for idx in remaining:
            relevance = q_sims[idx]

            # Max similarity to any already-selected item
            if selected_indices:
                sel_embs = emb_normed[selected_indices]
                redundancy = float(np.max(sel_embs @ emb_normed[idx]))
            else:
                redundancy = 0.0

            score = lambda_ * relevance - (1 - lambda_) * redundancy
            if score > best_score:
                best_score = score
                best_idx = idx

        if best_idx < 0:
            break
        selected_indices.append(best_idx)
        remaining.discard(best_idx)

    return [items[i] for i in selected_indices]


# ── Vector search ───────────────────────────────────────────────────────────

async def _vector_search(db, query: str, limit: int = 20) -> list[dict]:
    """Search concepts by embedding similarity."""
    query_vec = embed_text(query)
    results = await db.query(
        """
        SELECT
            id, name, type, description, rung,
            nars_frequency, nars_confidence, evidence_count,
            embedding,
            vector::similarity::cosine(embedding, $vec) AS score
        FROM concept
        WHERE embedding IS NOT NONE
        ORDER BY score DESC
        LIMIT $limit
        """,
        {"vec": query_vec, "limit": limit},
    )
    return _clean_records(results) if results else []


# ── Name deduplication ──────────────────────────────────────────────────────

def _dedup_by_name(results: list[dict], limit: int = 10) -> list[dict]:
    """
    Deduplicate vector results where multiple concepts have near-identical names.

    Keeps the highest-scoring variant. A name is considered a duplicate if:
    - It's identical (case-insensitive) to a selected name
    - It's a substring of or contains a selected name
    - It shares the same key words (>= 60% word overlap)
    """
    def _stem(w: str) -> str:
        """Minimal stemmer: strip common suffixes for overlap comparison."""
        for suffix in ("tion", "sion", "ment", "ness", "ings", "ing", "ies", "ive", "ed", "ly", "er", "es", "s"):
            if len(w) > len(suffix) + 3 and w.endswith(suffix):
                return w[: -len(suffix)]
        return w

    selected = []
    seen_words: list[set[str]] = []

    for r in results:
        name = r.get("name", "")
        norm = name.lower().strip().replace("-", " ").replace("_", " ")
        words = {_stem(w) for w in norm.split()}

        is_dup = False
        for sw in seen_words:
            # Check word overlap: if most words match, it's a duplicate
            if not words or not sw:
                continue
            overlap = len(words & sw)
            smaller = min(len(words), len(sw))
            if smaller > 0 and overlap / smaller >= 0.75:
                is_dup = True
                break

        if not is_dup:
            selected.append(r)
            seen_words.append(words)
        if len(selected) >= limit:
            break

    return selected


# ── Type-filtered vector search ─────────────────────────────────────────────

async def _type_filtered_search(db, query: str, types: list[str], limit: int = 10) -> list[dict]:
    """Search concepts by embedding similarity, filtered to specific types."""
    query_vec = embed_text(query)
    results = await db.query(
        """
        SELECT
            id, name, type, description, rung,
            nars_frequency, nars_confidence, evidence_count,
            embedding,
            vector::similarity::cosine(embedding, $vec) AS score
        FROM concept
        WHERE embedding IS NOT NONE AND type IN $types
        ORDER BY score DESC
        LIMIT $limit
        """,
        {"vec": query_vec, "types": types, "limit": limit},
    )
    return _clean_records(results) if results else []


# ── Graph traversal ─────────────────────────────────────────────────────────

async def _graph_neighbors(db, concept_names: list[str], hops: int = 1) -> tuple[list[dict], list[dict]]:
    """
    Traverse graph from seed concepts, returning neighbor concepts and relations.
    """
    if not concept_names:
        return [], []

    all_relations = []
    neighbor_names = set()

    for name in concept_names:
        # Outgoing relations
        rels_out = await db.query(
            """
            SELECT in.name AS source, verb, out.name AS target,
                   verb_category, evidence, nars_confidence, nars_frequency
            FROM relates
            WHERE in.name = $name
            ORDER BY nars_confidence DESC
            LIMIT 10
            """,
            {"name": name},
        )
        for r in _clean_records(rels_out or []):
            all_relations.append(r)
            if r.get("target"):
                neighbor_names.add(r["target"])

        # Incoming relations
        rels_in = await db.query(
            """
            SELECT in.name AS source, verb, out.name AS target,
                   verb_category, evidence, nars_confidence, nars_frequency
            FROM relates
            WHERE out.name = $name
            ORDER BY nars_confidence DESC
            LIMIT 10
            """,
            {"name": name},
        )
        for r in _clean_records(rels_in or []):
            all_relations.append(r)
            if r.get("source"):
                neighbor_names.add(r["source"])

    # Second hop if requested
    if hops >= 2 and neighbor_names:
        hop2_names = list(neighbor_names - set(concept_names))[:10]  # Limit expansion
        for name in hop2_names:
            rels = await db.query(
                """
                SELECT in.name AS source, verb, out.name AS target,
                       verb_category, nars_confidence
                FROM relates
                WHERE in.name = $name OR out.name = $name
                ORDER BY nars_confidence DESC
                LIMIT 5
                """,
                {"name": name},
            )
            for r in _clean_records(rels or []):
                all_relations.append(r)

    # Deduplicate relations
    seen = set()
    unique_rels = []
    for r in all_relations:
        key = f"{r.get('source', '')}_{r.get('verb', '')}_{r.get('target', '')}"
        if key not in seen:
            seen.add(key)
            unique_rels.append(r)

    # Fetch neighbor concept details
    all_neighbor_names = list(neighbor_names - set(concept_names))
    neighbors = []
    for name in all_neighbor_names[:20]:
        result = await db.query(
            "SELECT id, name, type, description, rung, nars_confidence, evidence_count, embedding "
            "FROM concept WHERE name = $name LIMIT 1",
            {"name": name},
        )
        if result:
            neighbors.extend(_clean_records(result))

    return neighbors, unique_rels


# ── Chunk vector search ────────────────────────────────────────────────────

async def _chunk_vector_search(db, query: str, limit: int = 5) -> list[dict]:
    """Search chunks by embedding similarity — finds exact passages matching a query."""
    query_vec = embed_text(query)
    results = await db.query(
        """
        SELECT
            id, text, chunk_type, dominant_mode,
            vector::similarity::cosine(embedding, $vec) AS score,
            <-contains<-(document).title AS doc_titles
        FROM chunk
        WHERE embedding IS NOT NONE
        ORDER BY score DESC
        LIMIT $limit
        """,
        {"vec": query_vec, "limit": limit},
    )
    chunks = []
    for r in _clean_records(results or []):
        doc_titles = r.get("doc_titles", [])
        doc_title = "unknown"
        if isinstance(doc_titles, list) and doc_titles:
            doc_title = str(doc_titles[0]) if doc_titles[0] else "unknown"
        chunks.append({
            "text": r.get("text", ""),
            "chunk_type": r.get("chunk_type", "paragraph"),
            "dominant_mode": r.get("dominant_mode", ""),
            "doc_title": doc_title,
            "score": r.get("score", 0),
        })
    return chunks


# ── Source chunk retrieval ──────────────────────────────────────────────────

async def _get_source_chunks(db, concept_names: list[str], limit: int = 5) -> list[dict]:
    """Retrieve source text chunks that mention the given concepts."""
    if not concept_names:
        return []

    chunks = []
    seen_chunks = set()

    for name in concept_names[:5]:  # Limit to top 5 concepts
        result = await db.query(
            """
            SELECT
                <-mentions<-(chunk).{text, chunk_type, dominant_mode, index} AS chunk_data,
                <-mentions<-(chunk)<-contains<-(document).title AS doc_titles
            FROM concept WHERE name = $name LIMIT 1
            """,
            {"name": name},
        )

        if not result:
            continue

        for r in result:
            chunk_data = r.get("chunk_data", [])
            doc_titles = r.get("doc_titles", [])

            if isinstance(chunk_data, list):
                for i, cd in enumerate(chunk_data):
                    if isinstance(cd, dict):
                        text = cd.get("text", "")
                        if text and text not in seen_chunks:
                            seen_chunks.add(text)
                            doc_title = "unknown"
                            if isinstance(doc_titles, list) and i < len(doc_titles):
                                doc_title = doc_titles[i] or "unknown"
                            elif isinstance(doc_titles, list) and doc_titles:
                                doc_title = doc_titles[0] or "unknown"

                            chunks.append({
                                "text": text,
                                "chunk_type": cd.get("chunk_type", "paragraph"),
                                "dominant_mode": cd.get("dominant_mode", ""),
                                "doc_title": str(doc_title),
                            })

    return chunks[:limit]


# ── Helpers ─────────────────────────────────────────────────────────────────

def _clean_records(records: list) -> list[dict]:
    """Convert RecordID objects to strings in query results."""
    clean = []
    for r in records:
        if not isinstance(r, dict):
            continue
        c = {}
        for k, v in r.items():
            if hasattr(v, "table_name"):
                c[k] = str(v)
            elif isinstance(v, list):
                c[k] = [str(x) if hasattr(x, "table_name") else x for x in v]
            else:
                c[k] = v
        clean.append(c)
    return clean


# ── Domain-Aware Type Boosting ────────────────────────────────────────────────

# Maps query keywords → concept types that should be boosted.
# Each domain lists (keyword_set, boosted_types_with_weights).
# When a query matches a domain, matching concept types get a score multiplier.
DOMAIN_BOOSTS: list[tuple[set[str], dict[str, float]]] = [
    # Finance & Funding
    (
        {"fund", "funding", "finance", "financial", "money", "invest", "investment",
         "capital", "revenue", "budget", "cost", "price", "afford", "economic",
         "prospectus", "roi", "return", "profit", "income", "expense", "dues"},
        {"quantity": 2.0, "system": 1.4, "process": 1.3, "organization": 1.2},
    ),
    # Food & Agriculture
    (
        {"food", "farm", "farming", "agriculture", "crop", "grow", "growing",
         "harvest", "permaculture", "aquaponics", "agroforestry", "garden",
         "compost", "soil", "seed", "livestock", "poultry", "mushroom"},
        {"process": 1.8, "system": 1.5, "resource": 1.4, "practice": 1.3},
    ),
    # Energy & Infrastructure
    (
        {"energy", "power", "solar", "wind", "battery", "electric", "grid",
         "infrastructure", "utility", "renewable", "photovoltaic", "turbine",
         "generator", "storage", "microgrid", "off-grid"},
        {"system": 1.8, "resource": 1.5, "quantity": 1.3, "process": 1.2},
    ),
    # Water Systems
    (
        {"water", "irrigation", "rainwater", "greywater", "blackwater",
         "aquifer", "well", "cistern", "filtration", "treatment", "wetland",
         "plumbing", "sewage", "watershed", "hydro"},
        {"system": 1.8, "process": 1.5, "resource": 1.4, "quantity": 1.2},
    ),
    # Governance & Decision-making
    (
        {"govern", "governance", "vote", "voting", "consensus", "decision",
         "policy", "bylaw", "constitution", "board", "council", "authority",
         "democracy", "sociocracy", "holacracy", "facilitation"},
        {"process": 1.8, "system": 1.5, "practice": 1.4, "event": 1.2},
    ),
    # People & Teams
    (
        {"team", "founder", "member", "people", "person", "who", "role",
         "hire", "recruit", "volunteer", "leader", "facilitator", "manager",
         "skill", "expertise", "talent", "workforce"},
        {"person": 2.0, "skill": 1.8, "organization": 1.5, "event": 1.2},
    ),
    # Land & Property
    (
        {"land", "property", "site", "acre", "parcel", "zoning", "deed",
         "title", "survey", "terrain", "soil", "location", "real estate",
         "purchase", "acquire", "lease"},
        {"place": 2.0, "resource": 1.5, "quantity": 1.3, "process": 1.2},
    ),
    # Legal & Compliance
    (
        {"legal", "law", "permit", "license", "compliance", "regulation",
         "llc", "cooperative", "co-op", "trust", "entity", "incorporate",
         "contract", "agreement", "liability", "insurance"},
        {"system": 1.6, "process": 1.5, "organization": 1.4},
    ),
    # Construction & Housing
    (
        {"build", "construction", "house", "housing", "dwelling", "shelter",
         "architect", "design", "blueprint", "floor plan", "structure",
         "foundation", "roof", "wall", "cabin", "tiny home", "earthship"},
        {"system": 1.6, "process": 1.5, "place": 1.4, "resource": 1.3},
    ),
    # Community Building & Culture
    (
        {"community", "culture", "onboard", "welcome", "ritual", "ceremony",
         "conflict", "mediation", "communication", "relationship", "trust",
         "belonging", "inclusion", "diversity", "values"},
        {"practice": 1.8, "process": 1.5, "event": 1.4, "idea": 1.3},
    ),
    # Education & Knowledge
    (
        {"learn", "education", "teach", "training", "workshop", "curriculum",
         "research", "study", "knowledge", "course", "mentor", "apprentice"},
        {"skill": 1.8, "event": 1.5, "process": 1.4, "resource": 1.3},
    ),
    # Technology & Digital
    (
        {"software", "app", "platform", "digital", "tech", "technology",
         "database", "api", "iot", "sensor", "automation", "ai",
         "website", "tool", "system"},
        {"system": 1.6, "skill": 1.4, "resource": 1.3},
    ),
]


def detect_domain_boosts(query: str) -> dict[str, float]:
    """
    Detect which domain(s) a query targets and return type boost weights.

    Returns {concept_type: boost_multiplier} — types not listed get 1.0 (no boost).
    Multiple matching domains are merged (max boost per type wins).
    """
    words = set(query.lower().split())
    # Also check bigrams for multi-word terms
    query_lower = query.lower()

    boosts: dict[str, float] = {}
    for keywords, type_weights in DOMAIN_BOOSTS:
        # Count keyword hits (both word-level and substring for multi-word terms)
        hits = sum(1 for kw in keywords if kw in words or (len(kw) > 4 and kw in query_lower))
        if hits >= 1:
            # Scale boost by number of hits (1 hit = full boost, more = stronger)
            strength = min(hits, 3) / 2.0  # 1 hit=0.5, 2=1.0, 3+=1.5
            for t, w in type_weights.items():
                scaled = 1.0 + (w - 1.0) * max(strength, 0.7)
                boosts[t] = max(boosts.get(t, 1.0), scaled)

    return boosts


# ── Domain query rewriting ────────────────────────────────────────────────────

# Maps detected domain types to focused search terms
_DOMAIN_SEARCH_TERMS: dict[str, str] = {
    "quantity": "financial model revenue cost budget capital investment funding",
    "person": "team member founder role facilitator leader coordinator",
    "skill": "expertise capability training education knowledge workshop",
    "place": "land property site location parcel zoning terrain",
    "event": "meeting workshop gathering ceremony session milestone",
    "practice": "method technique approach ritual process practice protocol",
    "resource": "tool material supply equipment asset infrastructure",
    "organization": "cooperative LLC trust entity association network organization",
}


def _make_domain_query(query: str, boosts: dict[str, float]) -> str:
    """
    Rewrite a query to focus on the dominant domain.

    Appends domain-specific search terms so the embedding captures
    the specific intent rather than just the broad topic.
    """
    if not boosts:
        return query

    # Find the most-boosted type
    top_type = max(boosts, key=boosts.get)
    top_boost = boosts[top_type]

    # Only rewrite if there's a meaningful boost
    if top_boost < 1.3:
        return query

    terms = _DOMAIN_SEARCH_TERMS.get(top_type, "")
    if not terms:
        return query

    return f"{query} {terms}"


# ── Community summary search ──────────────────────────────────────────────────

async def _community_search(db, query: str, limit: int = 3) -> list[dict]:
    """Search community summaries by embedding similarity."""
    query_vec = embed_text(query)
    results = await db.query(
        """
        SELECT
            id, name, summary, member_count, member_names, top_types,
            vector::similarity::cosine(embedding, $vec) AS score
        FROM community
        WHERE embedding IS NOT NONE
        ORDER BY score DESC
        LIMIT $limit
        """,
        {"vec": query_vec, "limit": limit},
    )
    return _clean_records(results) if results else []


# ── Main retrieval function ─────────────────────────────────────────────────

async def retrieve(
    db,
    query: str,
    limit: int = 10,
    hops: int = 1,
    include_chunks: bool = True,
) -> RetrievalContext:
    """
    Hybrid retrieval: vector search + graph traversal + source chunks.

    Args:
        db: Connected AsyncSurreal instance
        query: Natural language query
        limit: Max seed concepts from vector search
        hops: Graph traversal depth (1 or 2)
        include_chunks: Whether to include source text passages

    Returns:
        RetrievalContext with concepts, relations, chunks, and formatted text
    """
    ctx = RetrievalContext(query=query)

    # 1. Vector search for seed concepts
    raw_vector = await _vector_search(db, query, limit=limit * 2)

    if not raw_vector:
        return ctx

    # Deduplicate near-identical names (e.g. "Regenerative Neighborhoods" vs "regenerative neighborhoods")
    vector_results = _dedup_by_name(raw_vector, limit=limit)
    seed_names = [r["name"] for r in vector_results if r.get("name")]

    # 1b. Domain-focused vector search (rewritten query targeting domain terms)
    domain_boosts = detect_domain_boosts(query)
    domain_results = []
    if domain_boosts:
        domain_query = _make_domain_query(query, domain_boosts)
        if domain_query != query:
            raw_domain = await _vector_search(db, domain_query, limit=limit * 2)
            # Keep only results that are NEW (not already in vector_results top hits)
            top_names = {r.get("name", "") for r in vector_results[:8]}
            domain_results = [r for r in raw_domain if r.get("name", "") not in top_names][:limit]
            # Add domain seed concepts to graph traversal
            for r in domain_results[:3]:
                name = r.get("name")
                if name and name not in seed_names:
                    seed_names.append(name)

    # 2. Graph traversal from seed concepts
    graph_neighbors, graph_relations = await _graph_neighbors(db, seed_names[:8], hops=hops)

    # 3. Reciprocal Rank Fusion to combine all result sources
    ranked_lists = [vector_results, graph_neighbors]
    rrf_weights = [1.0, 1.0]
    if domain_results:
        ranked_lists.append(domain_results)
        rrf_weights.append(2.0)  # Domain-focused results get 2x RRF weight
    fused_ranking = reciprocal_rank_fusion(
        *ranked_lists,
        key="name",
        weights=rrf_weights,
    )

    # Build score map
    ctx.scores = dict(fused_ranking)

    # Combine and deduplicate concepts
    all_concepts_by_name: dict[str, dict] = {}
    for c in vector_results + domain_results + graph_neighbors:
        name = c.get("name", "")
        if name and name not in all_concepts_by_name:
            all_concepts_by_name[name] = c

    # Apply domain boosts to fused scores
    if domain_boosts:
        for name, score in ctx.scores.items():
            c = all_concepts_by_name.get(name)
            if c:
                ctype = c.get("type", "")
                boost = domain_boosts.get(ctype, 1.0)
                ctx.scores[name] = score * boost

    # Sort by boosted fused score, then dedup near-identical names
    sorted_concepts = sorted(
        all_concepts_by_name.values(),
        key=lambda c: ctx.scores.get(c.get("name", ""), 0),
        reverse=True,
    )
    fused_concepts = _dedup_by_name(sorted_concepts, limit=limit * 2)

    # Apply MMR for diversity
    if len(fused_concepts) > limit:
        # Fetch embeddings for MMR
        concept_embeddings = []
        for c in fused_concepts:
            emb = c.get("embedding")
            if emb:
                concept_embeddings.append(emb)
            else:
                concept_embeddings.append(None)

        # Only apply MMR if we have embeddings
        has_embs = [e for e in concept_embeddings if e is not None]
        if len(has_embs) >= limit:
            query_vec = embed_text(query)
            # Fill missing embeddings with zeros so indices stay aligned
            dim = len(has_embs[0])
            filled = [e if e is not None else [0.0] * dim for e in concept_embeddings]
            ctx.concepts = mmr_rerank(fused_concepts, query_vec, filled, lambda_=0.7, limit=limit)
        else:
            ctx.concepts = fused_concepts[:limit]
    else:
        ctx.concepts = fused_concepts[:limit]

    # Strip embeddings from output (used internally for MMR only)
    for c in ctx.concepts:
        c.pop("embedding", None)

    # Relations sorted by confidence
    ctx.relations = sorted(
        graph_relations,
        key=lambda r: r.get("nars_confidence", 0),
        reverse=True,
    )

    # 4. Community summaries for thematic context
    ctx.communities = await _community_search(db, query, limit=3)

    # 5. Source chunks — combine graph-based + vector-based chunk retrieval
    if include_chunks:
        top_names = [c["name"] for c in ctx.concepts[:5]]
        graph_chunks = await _get_source_chunks(db, top_names, limit=3)
        vector_chunks = await _chunk_vector_search(db, query, limit=3)

        # Deduplicate by text content, preferring graph chunks
        seen_texts = set()
        combined_chunks = []
        for ch in graph_chunks + vector_chunks:
            text = ch.get("text", "")
            if text and text not in seen_texts:
                seen_texts.add(text)
                combined_chunks.append(ch)
        ctx.chunks = combined_chunks[:5]

    return ctx


# ── CLI ─────────────────────────────────────────────────────────────────────

async def _cli_main():
    import argparse
    parser = argparse.ArgumentParser(description="Hybrid knowledge graph retrieval")
    parser.add_argument("query", help="Natural language query")
    parser.add_argument("--limit", type=int, default=10, help="Max results")
    parser.add_argument("--hops", type=int, default=1, help="Graph traversal depth")
    parser.add_argument("--json", action="store_true", help="Output raw JSON instead of formatted text")
    parser.add_argument("--no-chunks", action="store_true", help="Skip source chunk retrieval")
    args = parser.parse_args()

    sys.path.insert(0, os.path.dirname(__file__))
    from surrealdb import AsyncSurreal

    db_url = os.environ.get("SURREALDB_URL", "ws://127.0.0.1:8000")
    db = AsyncSurreal(url=db_url)
    await db.connect()
    await db.signin({"username": "root", "password": os.environ.get("SURREAL_PASS", "root")})
    await db.use("semantic_graph", "main")

    ctx = await retrieve(
        db, args.query,
        limit=args.limit,
        hops=args.hops,
        include_chunks=not args.no_chunks,
    )

    if args.json:
        print(json.dumps(ctx.to_dict(), indent=2, default=str))
    else:
        print(ctx.text)
        print(f"\n---\n{len(ctx.concepts)} concepts, {len(ctx.relations)} relations, {len(ctx.chunks)} chunks")

    await db.close()


if __name__ == "__main__":
    asyncio.run(_cli_main())
