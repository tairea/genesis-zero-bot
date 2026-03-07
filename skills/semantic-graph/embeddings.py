"""
embeddings.py — Vector embedding generation and semantic search.

Uses OpenRouter's embedding endpoint (OpenAI text-embedding-3-small, 1536d).
Stores embeddings in SurrealDB with HNSW cosine index for nearest-neighbor search.
"""

from __future__ import annotations

import os
import sys
from typing import Any

from openai import OpenAI

# ── Client ───────────────────────────────────────────────────────────────────

_client: OpenAI | None = None

EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "openai/text-embedding-3-small")
EMBEDDING_DIM = 1536  # text-embedding-3-small dimension
BATCH_SIZE = 100  # OpenAI embedding API supports up to 2048 inputs


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


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a list of texts. Returns list of float vectors."""
    if not texts:
        return []

    client = _get_client()
    all_embeddings = []

    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i : i + BATCH_SIZE]
        response = client.embeddings.create(model=EMBEDDING_MODEL, input=batch)
        # Sort by index to maintain order
        sorted_data = sorted(response.data, key=lambda x: x.index)
        all_embeddings.extend([d.embedding for d in sorted_data])

    return all_embeddings


def embed_text(text: str) -> list[float]:
    """Generate embedding for a single text."""
    return embed_texts([text])[0]


# ── SurrealDB integration ───────────────────────────────────────────────────


async def ensure_vector_schema(db) -> None:
    """Add embedding field and HNSW index to concept table."""
    await db.query(
        'DEFINE FIELD IF NOT EXISTS embedding ON concept TYPE option<array<float>> '
        'COMMENT "Vector embedding (1536d)"'
    )
    await db.query(
        "DEFINE INDEX IF NOT EXISTS concept_embedding ON concept "
        f"FIELDS embedding HNSW DIMENSION {EMBEDDING_DIM} DIST COSINE"
    )


async def embed_concepts(db, batch_size: int = 100, force: bool = False) -> int:
    """
    Generate and store embeddings for all concepts that don't have one yet.

    Returns number of concepts embedded.
    """
    if force:
        concepts = await db.query("SELECT id, name, type, description FROM concept")
    else:
        concepts = await db.query(
            "SELECT id, name, type, description FROM concept WHERE embedding IS NONE"
        )

    if not concepts:
        return 0

    total = len(concepts)
    embedded = 0

    for i in range(0, total, batch_size):
        batch = concepts[i : i + batch_size]

        # Build embedding input: "name (type): description"
        texts = []
        for c in batch:
            name = c.get("name", "")
            ctype = c.get("type", "")
            desc = c.get("description", "") or ""
            texts.append(f"{name} ({ctype}): {desc}" if desc else f"{name} ({ctype})")

        try:
            vectors = embed_texts(texts)
        except Exception as e:
            print(f"  Embedding batch {i//batch_size + 1} failed: {e}", file=sys.stderr)
            continue

        for concept, vector in zip(batch, vectors):
            cid = concept["id"]
            await db.query("UPDATE $id SET embedding = $vec", {"id": cid, "vec": vector})
            embedded += 1

        done = min(i + batch_size, total)
        print(f"  Embedded {done}/{total} concepts", file=sys.stderr)

    return embedded


async def embed_chunks(db, batch_size: int = 50, force: bool = False) -> int:
    """
    Generate and store embeddings for text chunks that don't have one yet.
    Enables passage-level retrieval alongside concept-level search.
    """
    if force:
        chunks = await db.query("SELECT id, text, chunk_type FROM chunk")
    else:
        chunks = await db.query(
            "SELECT id, text, chunk_type FROM chunk WHERE embedding IS NONE"
        )

    if not chunks:
        return 0

    # Ensure chunk embedding schema
    await db.query(
        'DEFINE FIELD IF NOT EXISTS embedding ON chunk TYPE option<array<float>> '
        'COMMENT "Vector embedding (1536d)"'
    )
    await db.query(
        "DEFINE INDEX IF NOT EXISTS chunk_embedding ON chunk "
        f"FIELDS embedding HNSW DIMENSION {EMBEDDING_DIM} DIST COSINE"
    )

    total = len(chunks)
    embedded = 0

    for i in range(0, total, batch_size):
        batch = chunks[i : i + batch_size]
        texts = [c.get("text", "")[:2000] for c in batch]  # Truncate long chunks

        try:
            vectors = embed_texts(texts)
        except Exception as e:
            print(f"  Chunk embedding batch {i//batch_size + 1} failed: {e}", file=sys.stderr)
            continue

        for chunk, vector in zip(batch, vectors):
            cid = chunk["id"]
            await db.query("UPDATE $id SET embedding = $vec", {"id": cid, "vec": vector})
            embedded += 1

        done = min(i + batch_size, total)
        print(f"  Embedded {done}/{total} chunks", file=sys.stderr)

    return embedded


async def search(db, query: str, limit: int = 10, min_score: float = 0.0) -> list[dict]:
    """
    Semantic search: find concepts most similar to a natural language query.

    Returns list of {name, type, description, score, ...} ordered by similarity.
    """
    query_vec = embed_text(query)

    results = await db.query(
        """
        SELECT
            id, name, type, description, rung,
            nars_frequency, nars_confidence, evidence_count,
            vector::similarity::cosine(embedding, $vec) AS score
        FROM concept
        WHERE embedding IS NOT NONE
        ORDER BY score DESC
        LIMIT $limit
        """,
        {"vec": query_vec, "limit": limit},
    )

    if not results:
        return []

    # Filter by minimum score
    return [r for r in results if r.get("score", 0) >= min_score]


async def find_similar(db, concept_id: str, limit: int = 10) -> list[dict]:
    """Find concepts most similar to a given concept by embedding distance."""
    from surrealdb import RecordID

    if isinstance(concept_id, str) and ":" in concept_id:
        table, key = concept_id.split(":", 1)
        concept_id = RecordID(table, key)

    # Get the concept's embedding
    result = await db.query("SELECT embedding FROM $id", {"id": concept_id})
    if not result or not result[0].get("embedding"):
        return []

    vec = result[0]["embedding"]
    results = await db.query(
        """
        SELECT
            id, name, type, description,
            vector::similarity::cosine(embedding, $vec) AS score
        FROM concept
        WHERE embedding IS NOT NONE AND id != $id
        ORDER BY score DESC
        LIMIT $limit
        """,
        {"vec": vec, "id": concept_id, "limit": limit},
    )

    return results if results else []
