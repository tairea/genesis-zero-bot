"""
graph_extract.py — Full pipeline: input → Kreuzberg → chunks → LLM → SurrealDB.

Usage (CLI):
    python graph_extract.py --input path/to/file.pdf --db ws://localhost:8000
    python graph_extract.py --stdin --mime text/markdown < README.md
    python graph_extract.py --dir ./docs/ --db ws://localhost:8000

Usage (Python API):
    from graph_extract import GraphExtractor

    async with GraphExtractor.connect("ws://localhost:8000") as gx:
        doc_id = await gx.ingest("README.md")
        print(f"Stored as {doc_id}")
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import mimetypes
import os
import sys
import time
from pathlib import Path
from typing import Any

import kreuzberg
from surrealdb import Surreal

from grammar_triangle import chunk_text
from subagent_parser import extract_chunks

# ── NARS revision formula ─────────────────────────────────────────────────────


def nars_revise(f1: float, c1: float, n1: int, f2: float, c2: float, n2: int) -> tuple[float, float, int]:
    """
    Merge two NARS truth values via the revision rule.
    Returns (frequency, confidence, evidence_count).
    """
    w1 = c1 / (1.0 - c1 + 1e-9) * n1
    w2 = c2 / (1.0 - c2 + 1e-9) * n2
    w_total = w1 + w2
    freq_new = (w1 * f1 + w2 * f2) / (w_total + 1e-9)
    conf_new = w_total / (w_total + 1.0)
    return round(freq_new, 4), round(conf_new, 4), n1 + n2


# ── GraphExtractor ────────────────────────────────────────────────────────────


class GraphExtractor:
    """
    Stateful extractor that maintains a SurrealDB connection.

    Use as async context manager:
        async with GraphExtractor.connect(...) as gx:
            doc_id = await gx.ingest("myfile.pdf")
    """

    def __init__(self, db: Surreal, namespace: str, database: str) -> None:
        self._db = db
        self._ns = namespace
        self._database = database

    # ── Factory ────────────────────────────────────────────────────────────

    @classmethod
    async def connect(
        cls,
        url: str = "ws://127.0.0.1:8000",
        namespace: str = "semantic_graph",
        database: str = "main",
        username: str = "root",
        password: str = os.environ.get("SURREAL_PASS", "root"),
    ) -> "GraphExtractor":
        from surrealdb import AsyncSurreal
        db = AsyncSurreal(url=url)
        await db.connect()
        await db.signin({"username": username, "password": password})
        await db.use(namespace, database)
        return cls(db, namespace, database)

    async def __aenter__(self) -> "GraphExtractor":
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self._db.close()

    # ── Schema bootstrap ───────────────────────────────────────────────────

    async def ensure_schema(self) -> None:
        """Apply schema.surql if not already applied."""
        schema_path = Path(__file__).parent / "schema.surql"
        if schema_path.exists():
            sql = schema_path.read_text()
            # Execute statement by statement
            statements = [s.strip() for s in sql.split(";") if s.strip()]
            for stmt in statements:
                try:
                    await self._db.query(stmt + ";")
                except Exception:
                    pass  # Already defined is fine

    # ── Ingestion pipeline ─────────────────────────────────────────────────

    async def ingest(
        self,
        source: str | Path | bytes,
        mime_type: str | None = None,
        title: str | None = None,
        batch_size: int = 4,
        verbose: bool = False,
    ) -> str:
        """
        Full pipeline: extract text → chunk → LLM parse → store graph.

        Returns the SurrealDB document record ID (e.g. "document:abc123").
        """
        t0 = time.perf_counter()

        # ── Step 1: Extract text via Kreuzberg ────────────────────────────
        if isinstance(source, (str, Path)):
            path = Path(source)
            raw_bytes = path.read_bytes()
            if mime_type is None:
                mime_type, _ = mimetypes.guess_type(str(path))
                mime_type = mime_type or "text/plain"
            if title is None:
                title = path.name
        else:
            raw_bytes = source
            mime_type = mime_type or "text/plain"
            title = title or "stdin"

        if verbose:
            print(f"[1/4] Extracting text from {title} ({mime_type})…", file=sys.stderr)

        extraction = kreuzberg.extract_bytes_sync(raw_bytes, mime_type=mime_type)
        text = extraction.content or ""
        doc_metadata = dict(extraction.metadata or {})
        quality = getattr(extraction, "quality_score", None) or doc_metadata.pop("quality_score", None)

        if not text.strip():
            raise ValueError(f"No text extracted from {title}")

        word_count = len(text.split())
        language = doc_metadata.pop("language", "en")

        # ── Step 2: Store document node ───────────────────────────────────
        doc_hash = hashlib.sha256(raw_bytes).hexdigest()[:16]
        doc_id = f"document:{doc_hash}"

        if verbose:
            print(f"[2/4] Storing document node {doc_id}…", file=sys.stderr)

        await self._db.query(
            """
            UPSERT $id MERGE {
                source: $source,
                mime_type: $mime_type,
                title: $title,
                word_count: $word_count,
                language: $language,
                quality: $quality,
                metadata: $metadata,
                created_at: time::now()
            };
            """,
            {
                "id": doc_id,
                "source": str(title),
                "mime_type": mime_type,
                "title": title,
                "word_count": word_count,
                "language": language,
                "quality": quality,
                "metadata": doc_metadata,
            },
        )

        # ── Step 3: Chunk + Grammar Triangle ─────────────────────────────
        if verbose:
            print(f"[3/4] Chunking {word_count} words…", file=sys.stderr)

        chunks = chunk_text(text)

        # Store chunks and collect their IDs
        chunk_ids: list[str] = []
        for chunk in chunks:
            chunk_hash = hashlib.sha256(chunk["text"].encode()).hexdigest()[:12]
            chunk_id = f"chunk:{doc_hash}_{chunk_hash}"
            chunk["id"] = chunk_id

            await self._db.query(
                """
                UPSERT $id MERGE {
                    text: $text,
                    index: $index,
                    char_start: $char_start,
                    char_end: $char_end,
                    chunk_type: $chunk_type,
                    nsm: $nsm,
                    qualia: $qualia,
                    causality: $causality,
                    dominant_mode: $dominant_mode
                };
                """,
                {
                    "id": chunk_id,
                    "text": chunk["text"],
                    "index": chunk["index"],
                    "char_start": chunk["char_start"],
                    "char_end": chunk["char_end"],
                    "chunk_type": chunk["chunk_type"],
                    "nsm": chunk["nsm"],
                    "qualia": chunk["qualia"],
                    "causality": chunk["causality"],
                    "dominant_mode": chunk["dominant_mode"],
                },
            )

            # document → chunk edge
            await self._db.query(
                "RELATE $doc_id->contains->$chunk_id;",
                {"doc_id": doc_id, "chunk_id": chunk_id},
            )

            chunk_ids.append(chunk_id)

        # ── Step 4: LLM concept + relation extraction ─────────────────────
        if verbose:
            n_batches = (len(chunks) + batch_size - 1) // batch_size
            print(
                f"[4/4] Extracting concepts from {len(chunks)} chunks "
                f"in {n_batches} batches…",
                file=sys.stderr,
            )

        parsed = extract_chunks(chunks, batch_size=batch_size)

        # ── Step 5: Store concepts (with NARS deduplication) ──────────────
        concept_id_map: dict[str, str] = {}  # name → SurrealDB ID

        for concept in parsed["concepts"]:
            name = concept["name"]
            if not name:
                continue

            # Stable ID from (doc, normalised name, type)
            key = f"{name.lower().replace(' ', '_')}_{concept['type']}"
            cid = f"concept:{hashlib.sha256(key.encode()).hexdigest()[:16]}"
            concept_id_map[name] = cid

            # Fetch existing for NARS merge
            existing = await self._db.query(
                "SELECT nars_frequency, nars_confidence, evidence_count FROM $id;",
                {"id": cid},
            )
            ex = None
            if existing and existing[0].get("result"):
                ex = existing[0]["result"][0]

            if ex:
                f, c, n = nars_revise(
                    ex["nars_frequency"], ex["nars_confidence"], ex.get("evidence_count", 1),
                    concept["nars_frequency"], concept["nars_confidence"], 1,
                )
            else:
                f, c, n = concept["nars_frequency"], concept["nars_confidence"], 1

            await self._db.query(
                """
                UPSERT $id MERGE {
                    name: $name,
                    type: $type,
                    description: $description,
                    rung: $rung,
                    aliases: $aliases,
                    tags: $tags,
                    qualia: $qualia,
                    nars_frequency: $nars_frequency,
                    nars_confidence: $nars_confidence,
                    evidence_count: $evidence_count,
                    source_doc: $source_doc,
                    first_seen_in: $source_doc
                };
                """,
                {
                    "id": cid,
                    "name": name,
                    "type": concept["type"],
                    "description": concept["description"],
                    "rung": concept["rung"],
                    "aliases": concept["aliases"],
                    "tags": concept["tags"],
                    "qualia": concept["qualia"],
                    "nars_frequency": f,
                    "nars_confidence": c,
                    "evidence_count": n,
                    "source_doc": doc_id,
                },
            )

            # chunk → concept mention edges
            for chunk_id in concept.get("source_chunks", chunk_ids[:1]):
                await self._db.query(
                    "RELATE $chunk_id->mentions->$concept_id SET weight = $conf;",
                    {"chunk_id": chunk_id, "concept_id": cid, "conf": c},
                )

        # ── Step 6: Store relations ───────────────────────────────────────
        rel_count = 0
        for rel in parsed["relations"]:
            subj_name = rel["subject"]
            obj_name = rel["object"]

            if subj_name not in concept_id_map or obj_name not in concept_id_map:
                continue  # Skip dangling edges

            subj_id = concept_id_map[subj_name]
            obj_id = concept_id_map[obj_name]
            verb = rel["verb"]

            # Composite key for deduplication
            rel_key = f"{subj_id}_{verb}_{obj_id}"
            rel_hash = hashlib.sha256(rel_key.encode()).hexdigest()[:16]
            rel_id = f"relates:{rel_hash}"

            # NARS merge for existing relation
            ex_rel = await self._db.query(
                "SELECT nars_frequency, nars_confidence, evidence_count FROM $id;",
                {"id": rel_id},
            )
            ex = None
            if ex_rel and ex_rel[0].get("result"):
                ex = ex_rel[0]["result"][0]

            if ex:
                f, c, n = nars_revise(
                    ex["nars_frequency"], ex["nars_confidence"], ex.get("evidence_count", 1),
                    rel["nars_frequency"], rel["nars_confidence"], 1,
                )
            else:
                f, c, n = rel["nars_frequency"], rel["nars_confidence"], 1

            await self._db.query(
                """
                UPSERT $id MERGE {
                    in: $subj,
                    out: $obj,
                    verb: $verb,
                    verb_category: $verb_category,
                    weight: $weight,
                    evidence: $evidence,
                    nars_frequency: $f,
                    nars_confidence: $c,
                    evidence_count: $n,
                    source_doc: $source_doc,
                    valid_from: $valid_from,
                    valid_until: $valid_until
                };
                """,
                {
                    "id": rel_id,
                    "subj": subj_id,
                    "obj": obj_id,
                    "verb": verb,
                    "verb_category": rel["verb_category"],
                    "weight": c,
                    "evidence": rel.get("evidence", ""),
                    "f": f,
                    "c": c,
                    "n": n,
                    "source_doc": doc_id,
                    "valid_from": rel.get("valid_from"),
                    "valid_until": rel.get("valid_until"),
                },
            )
            rel_count += 1

        elapsed = time.perf_counter() - t0
        if verbose:
            print(
                f"\n✓ Done in {elapsed:.1f}s  |  "
                f"chunks={len(chunks)}  concepts={len(concept_id_map)}  "
                f"relations={rel_count}  doc={doc_id}",
                file=sys.stderr,
            )

        return doc_id

    # ── Query helpers ──────────────────────────────────────────────────────

    async def concepts_for_doc(self, doc_id: str) -> list[dict]:
        """All concepts referenced in a document."""
        result = await self._db.query(
            """
            SELECT ->contains->(chunk)->mentions->(concept).*
            FROM $doc_id;
            """,
            {"doc_id": doc_id},
        )
        return result[0].get("result", []) if result else []

    async def relations_for_concept(self, concept_id: str, depth: int = 1) -> list[dict]:
        """Relations emanating from a concept up to `depth` hops."""
        # Simple 1-hop for now; extend with recursive query for deeper
        result = await self._db.query(
            "SELECT *, ->relates.* FROM $id;",
            {"id": concept_id},
        )
        return result[0].get("result", []) if result else []

    async def subgraph(self, concept_name: str) -> dict:
        """Return subgraph (nodes + edges) centred on a concept name."""
        result = await self._db.query(
            """
            LET $c = (SELECT id FROM concept WHERE name = $name LIMIT 1)[0].id;
            SELECT *, ->relates->(concept).* AS neighbours FROM $c;
            """,
            {"name": concept_name},
        )
        return result[0].get("result", {}) if result else {}


# ── CLI ───────────────────────────────────────────────────────────────────────


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="graph_extract",
        description="Extract semantic knowledge graph from arbitrary documents into SurrealDB.",
    )
    # Input
    inp = p.add_mutually_exclusive_group(required=True)
    inp.add_argument("--input", "-i", metavar="FILE", help="Input file path")
    inp.add_argument("--stdin", action="store_true", help="Read from stdin")
    inp.add_argument("--dir", "-d", metavar="DIR", help="Process all files in directory")

    # SurrealDB
    p.add_argument("--db", default="ws://localhost:8000", help="SurrealDB WebSocket URL")
    p.add_argument("--ns", default="knowledge", help="SurrealDB namespace")
    p.add_argument("--database", default="main", help="SurrealDB database name")
    p.add_argument("--user", default="root", help="SurrealDB username")
    p.add_argument("--pass", dest="password", default="root", help="SurrealDB password")

    # Options
    p.add_argument("--mime", metavar="TYPE", help="Force MIME type (for --stdin)")
    p.add_argument("--title", metavar="NAME", help="Override document title")
    p.add_argument("--batch-size", type=int, default=4, help="Chunks per LLM call (default: 4)")
    p.add_argument("--skip-schema", action="store_true", help="Skip schema bootstrap")
    p.add_argument("-v", "--verbose", action="store_true", help="Verbose progress output")
    p.add_argument("--dry-run", action="store_true", help="Parse only, skip SurrealDB write")

    return p


async def _run_cli(args: argparse.Namespace) -> None:
    if args.dry_run:
        print("[dry-run] Schema and DB writes skipped.", file=sys.stderr)
        gx = None
    else:
        gx = await GraphExtractor.connect(
            url=args.db,
            namespace=args.ns,
            database=args.database,
            username=args.user,
            password=args.password,
        )
        if not args.skip_schema:
            await gx.ensure_schema()

    try:
        if args.input:
            sources = [Path(args.input)]
        elif args.dir:
            d = Path(args.dir)
            sources = [f for f in d.rglob("*") if f.is_file()]
        else:
            # stdin
            raw = sys.stdin.buffer.read()
            if gx:
                doc_id = await gx.ingest(
                    raw,
                    mime_type=args.mime or "text/plain",
                    title=args.title or "stdin",
                    batch_size=args.batch_size,
                    verbose=args.verbose,
                )
            else:
                doc_id = "<dry-run>"
            print(doc_id)
            return

        for path in sources:
            if args.verbose:
                print(f"\n── Processing {path} ──", file=sys.stderr)
            if gx:
                doc_id = await gx.ingest(
                    path,
                    mime_type=args.mime,
                    title=args.title or path.name,
                    batch_size=args.batch_size,
                    verbose=args.verbose,
                )
                print(doc_id)
    finally:
        if gx:
            await gx._db.close()


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    asyncio.run(_run_cli(args))


if __name__ == "__main__":
    main()
