#!/usr/bin/env python3
"""
pipeline.py — End-to-end knowledge graph pipeline.

Ingest documents, extract concepts+relations via LLM, store in SurrealDB,
generate embeddings for semantic search, and produce 3D visualizations.

Usage:
    # Ingest a single file
    python pipeline.py ingest path/to/file.pdf

    # Ingest a directory
    python pipeline.py ingest ./docs/

    # Generate embeddings for all concepts
    python pipeline.py embed

    # Semantic search
    python pipeline.py search "regenerative agriculture"

    # Find similar concepts
    python pipeline.py similar "concept:abc123"

    # Generate visualization from current DB
    python pipeline.py viz

    # Export graph as JSON
    python pipeline.py export --output graph.json

    # Full pipeline: ingest + embed + viz
    python pipeline.py ingest path/to/file.pdf --embed --viz

    # Stats: show what's in the DB
    python pipeline.py stats

    # Embed text chunks for passage-level retrieval
    python pipeline.py embed-chunks

    # Community detection
    python pipeline.py communities detect --summarize
    python pipeline.py communities list
    python pipeline.py communities search "regenerative design"

    # Hybrid retrieval (vector + graph + chunks)
    python pipeline.py retrieve "what is permaculture?" --hops 2

    # Entity resolution
    python pipeline.py resolve --dry-run

    # Cleanup junk concepts
    python pipeline.py cleanup --dry-run

    # Evaluation
    python pipeline.py evaluate health
    python pipeline.py evaluate retrieval
    python pipeline.py evaluate extraction --ground-truth eval_gt.json
    python pipeline.py evaluate generate-ground-truth "Quick_Reference_One_Pager.md"
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

# Add skill dir to path
sys.path.insert(0, str(Path(__file__).parent))

DB_URL = os.environ.get("SURREALDB_URL", "ws://127.0.0.1:8000")
DB_NS = "semantic_graph"
DB_DB = "main"
DB_USER = "root"
DB_PASS = os.environ.get("SURREAL_PASS", "root")


async def cmd_ingest(args):
    """Ingest documents into the knowledge graph."""
    from graph_extract import GraphExtractor

    gx = await GraphExtractor.connect(
        url=DB_URL, namespace=DB_NS, database=DB_DB,
        username=DB_USER, password=DB_PASS,
    )
    await gx.ensure_schema()

    target = Path(args.path)
    if target.is_file():
        sources = [target]
    elif target.is_dir():
        sources = [f for f in target.rglob("*") if f.is_file() and not f.name.startswith(".")]
    else:
        print(f"Error: {target} not found")
        return

    print(f"Ingesting {len(sources)} file(s)...\n")
    success = 0
    
    # Parse extra metadata from --meta JSON string
    extra_meta = None
    if getattr(args, "meta", None):
        import json
        try:
            extra_meta = json.loads(args.meta)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in --meta: {e}")
            return
    
    for src in sources:
        try:
            doc_id = await gx.ingest(src, verbose=args.verbose, batch_size=args.batch_size, extra_metadata=extra_meta)
            print(f"  + {src.name} -> {doc_id}")
            success += 1
        except Exception as e:
            print(f"  x {src.name}: {e}")

    await gx._db.close()
    print(f"\nIngested {success}/{len(sources)} files")

    if getattr(args, "embed", False):
        print("\nGenerating embeddings...")
        await cmd_embed(args)

    if args.viz:
        print("\nGenerating visualization...")
        await cmd_viz(args)


async def cmd_viz(args):
    """Generate 3D visualization from current DB state."""
    from viz.graph_viz import generate_viz
    result = await generate_viz(
        db_url=DB_URL, namespace=DB_NS, database=DB_DB,
        limit=getattr(args, "limit", 0),
        export_json_path=getattr(args, "export_json", None),
    )
    if result:
        print(f"Visualization: {result}")


async def cmd_export(args):
    """Export graph as JSON."""
    from viz.graph_viz import export_json
    output = args.output or str(Path(__file__).parent / "artifacts" / "semantic-graph.json")
    result = await export_json(
        db_url=DB_URL, namespace=DB_NS, database=DB_DB,
        limit=getattr(args, "limit", 0),
        output_path=output,
    )


async def _connect_db():
    """Helper to get a connected AsyncSurreal instance."""
    from surrealdb import AsyncSurreal
    db = AsyncSurreal(url=DB_URL)
    await db.connect()
    await db.signin({"username": DB_USER, "password": DB_PASS})
    await db.use(DB_NS, DB_DB)
    return db


async def cmd_embed(args):
    """Generate vector embeddings for all concepts missing them."""
    from embeddings import embed_concepts, ensure_vector_schema

    db = await _connect_db()
    await ensure_vector_schema(db)

    force = getattr(args, "force", False)
    count = await embed_concepts(db, batch_size=getattr(args, "batch_size", 100), force=force)
    print(f"\nEmbedded {count} concepts")
    await db.close()


async def cmd_search(args):
    """Semantic search across the knowledge graph."""
    from embeddings import search

    db = await _connect_db()
    results = await search(db, args.query, limit=args.limit)

    if not results:
        print("No results found.")
    else:
        print(f"Top {len(results)} results for: \"{args.query}\"\n")
        for i, r in enumerate(results, 1):
            score = r.get("score", 0)
            name = r.get("name", "?")
            ctype = r.get("type", "?")
            desc = r.get("description", "") or ""
            conf = r.get("nars_confidence", 0)
            print(f"  {i:2d}. [{score:.3f}] {name} ({ctype})")
            if desc:
                print(f"      {desc[:80]}")
            print(f"      confidence={conf:.2f}  evidence={r.get('evidence_count', 0)}  rung=R{r.get('rung', 0)}")

    await db.close()


async def cmd_similar(args):
    """Find concepts similar to a given concept."""
    from embeddings import find_similar

    db = await _connect_db()
    results = await find_similar(db, args.concept_id, limit=args.limit)

    if not results:
        print("No similar concepts found (concept may not have an embedding).")
    else:
        print(f"Similar to {args.concept_id}:\n")
        for i, r in enumerate(results, 1):
            score = r.get("score", 0)
            name = r.get("name", "?")
            ctype = r.get("type", "?")
            print(f"  {i:2d}. [{score:.3f}] {name} ({ctype})")

    await db.close()


async def cmd_stats(args):
    """Show database statistics."""
    from surrealdb import AsyncSurreal
    db = AsyncSurreal(url=DB_URL)
    await db.connect()
    await db.signin({"username": DB_USER, "password": DB_PASS})
    await db.use(DB_NS, DB_DB)

    tables = ["document", "chunk", "concept", "contains", "mentions", "relates", "community", "belongs_to"]
    print(f"Database: {DB_NS}/{DB_DB}\n")
    for table in tables:
        result = await db.query(f"SELECT count() as cnt FROM {table} GROUP ALL")
        cnt = result[0].get("cnt", 0) if result and isinstance(result, list) and result else 0
        if isinstance(result, list) and result:
            first = result[0]
            if isinstance(first, dict) and "result" in first:
                cnt = first["result"][0].get("cnt", 0) if first["result"] else 0
            elif isinstance(first, dict) and "cnt" in first:
                cnt = first["cnt"]
        print(f"  {table:12s} {cnt:>6}")

    # Embedding coverage
    result = await db.query("SELECT count() as cnt FROM concept WHERE embedding IS NOT NONE GROUP ALL")
    emb_cnt = 0
    if result and isinstance(result, list) and result:
        first = result[0]
        if isinstance(first, dict):
            emb_cnt = first.get("cnt", first.get("result", [{}])[0].get("cnt", 0) if "result" in first else 0)
    total_concepts = 0
    result2 = await db.query("SELECT count() as cnt FROM concept GROUP ALL")
    if result2 and isinstance(result2, list) and result2:
        first = result2[0]
        if isinstance(first, dict):
            total_concepts = first.get("cnt", 0)
    print(f"\n  Embeddings: {emb_cnt}/{total_concepts} concepts")

    # Show top concept types
    result = await db.query("SELECT type, count() as cnt FROM concept GROUP BY type ORDER BY cnt DESC LIMIT 10")
    types = result[0].get("result", result) if isinstance(result, list) and result else []
    if isinstance(types, list) and types and isinstance(types[0], dict) and "result" in types[0]:
        types = types[0]["result"]
    if types:
        print(f"\nTop concept types:")
        for t in types:
            if isinstance(t, dict):
                print(f"  {t.get('type', '?'):15s} {t.get('cnt', 0):>5}")

    # Show verb distribution
    result = await db.query("SELECT verb, count() as cnt FROM relates GROUP BY verb ORDER BY cnt DESC LIMIT 10")
    verbs = result[0].get("result", result) if isinstance(result, list) and result else []
    if isinstance(verbs, list) and verbs and isinstance(verbs[0], dict) and "result" in verbs[0]:
        verbs = verbs[0]["result"]
    if verbs:
        print(f"\nTop relation verbs:")
        for v in verbs:
            if isinstance(v, dict):
                print(f"  {v.get('verb', '?'):15s} {v.get('cnt', 0):>5}")

    await db.close()


async def cmd_resolve(args):
    """Find and merge duplicate entities."""
    from entity_resolution import resolve_entities

    db = await _connect_db()
    result = await resolve_entities(
        db,
        threshold=args.threshold,
        dry_run=args.dry_run,
        verbose=args.verbose,
    )
    import json
    print(json.dumps(result, indent=2))
    await db.close()


async def cmd_retrieve(args):
    """Hybrid graph+vector retrieval."""
    from retriever import retrieve
    import json

    db = await _connect_db()
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
        print(f"\n---\n{len(ctx.concepts)} concepts, {len(ctx.relations)} relations, {len(ctx.communities)} communities, {len(ctx.chunks)} chunks")

    await db.close()


async def cmd_embed_chunks(args):
    """Generate vector embeddings for text chunks."""
    from embeddings import embed_chunks

    db = await _connect_db()
    force = getattr(args, "force", False)
    count = await embed_chunks(db, batch_size=getattr(args, "batch_size", 50), force=force)
    print(f"\nEmbedded {count} chunks")
    await db.close()


async def cmd_communities(args):
    """Community detection and search."""
    import json
    from communities import detect_communities, search_communities

    db = await _connect_db()

    if args.subcmd == "detect":
        result = await detect_communities(
            db,
            min_size=args.min_size,
            summarize=args.summarize,
            verbose=True,
        )
        print(json.dumps(result, indent=2))

    elif args.subcmd == "list":
        comms = await db.query(
            "SELECT name, summary, member_count, top_types FROM community ORDER BY member_count DESC"
        )
        for c in (comms or []):
            print(f"\n[{c.get('member_count', 0)} members] {c.get('name', '?')}")
            if c.get("summary"):
                print(f"  {c['summary']}")

    elif args.subcmd == "search":
        results = await search_communities(db, args.query, limit=args.limit)
        for r in results:
            print(f"\n[{r.get('score', 0):.3f}] {r.get('name', '?')} ({r.get('member_count', 0)} members)")
            if r.get("summary"):
                print(f"  {r['summary']}")

    await db.close()


async def cmd_cleanup(args):
    """Remove junk concepts from the graph."""
    from cleanup import cleanup
    await cleanup(dry_run=args.dry_run, verbose=True)


async def cmd_evaluate(args):
    """Run evaluation metrics."""
    from evaluate import graph_health, eval_retrieval, eval_extraction, generate_ground_truth_template
    import json

    db = await _connect_db()

    if args.subcmd == "health":
        result = await graph_health(db)
        clean = {k: v for k, v in result.items() if k not in ("type_distribution", "verb_distribution")}
        print(f"\n{json.dumps(clean, indent=2)}")

    elif args.subcmd == "retrieval":
        result = await eval_retrieval(db, verbose=not args.json)
        if args.json:
            print(json.dumps(result, indent=2))

    elif args.subcmd == "extraction":
        result = await eval_extraction(db, args.ground_truth, verbose=not args.json)
        if args.json:
            print(json.dumps(result, indent=2))

    elif args.subcmd == "generate-ground-truth":
        await generate_ground_truth_template(db, args.doc_title, args.output)

    await db.close()


def main():
    parser = argparse.ArgumentParser(
        prog="pipeline",
        description="Semantic Graph Knowledge Pipeline",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # ingest
    p_ingest = sub.add_parser("ingest", help="Ingest documents")
    p_ingest.add_argument("path", help="File or directory to ingest")
    p_ingest.add_argument("--viz", action="store_true", help="Generate viz after ingest")
    p_ingest.add_argument("--embed", action="store_true", help="Generate embeddings after ingest")
    p_ingest.add_argument("--batch-size", type=int, default=4, help="Chunks per LLM batch")
    p_ingest.add_argument("--meta", type=str, default=None, help="Extra metadata as JSON string (e.g. '{\"author\":\"Ian\"}')")
    p_ingest.add_argument("-v", "--verbose", action="store_true")

    # embed
    p_embed = sub.add_parser("embed", help="Generate embeddings for concepts")
    p_embed.add_argument("--force", action="store_true", help="Re-embed all concepts")
    p_embed.add_argument("--batch-size", type=int, default=100)

    # search
    p_search = sub.add_parser("search", help="Semantic search")
    p_search.add_argument("query", help="Natural language query")
    p_search.add_argument("--limit", type=int, default=10, help="Max results")

    # similar
    p_similar = sub.add_parser("similar", help="Find similar concepts")
    p_similar.add_argument("concept_id", help="Concept ID (e.g. concept:abc123)")
    p_similar.add_argument("--limit", type=int, default=10)

    # viz
    p_viz = sub.add_parser("viz", help="Generate 3D visualization")
    p_viz.add_argument("--limit", type=int, default=0, help="Max nodes (0=all)")
    p_viz.add_argument("--export-json", metavar="PATH", help="Also export JSON")

    # export
    p_export = sub.add_parser("export", help="Export graph as JSON")
    p_export.add_argument("--output", "-o", help="Output file path")
    p_export.add_argument("--limit", type=int, default=0)

    # stats
    sub.add_parser("stats", help="Show database statistics")

    # resolve — entity deduplication
    p_resolve = sub.add_parser("resolve", help="Find and merge duplicate entities")
    p_resolve.add_argument("--threshold", type=float, default=0.88,
                           help="Similarity threshold (default: 0.88)")
    p_resolve.add_argument("--dry-run", action="store_true", help="Find candidates without merging")
    p_resolve.add_argument("-v", "--verbose", action="store_true")

    # retrieve — hybrid search
    p_retrieve = sub.add_parser("retrieve", help="Hybrid graph+vector retrieval")
    p_retrieve.add_argument("query", help="Natural language query")
    p_retrieve.add_argument("--limit", type=int, default=10, help="Max results")
    p_retrieve.add_argument("--hops", type=int, default=1, help="Graph traversal depth (1 or 2)")
    p_retrieve.add_argument("--json", action="store_true", help="Output raw JSON")
    p_retrieve.add_argument("--no-chunks", action="store_true", help="Skip source chunk retrieval")

    # embed-chunks — chunk-level embeddings
    p_echunks = sub.add_parser("embed-chunks", help="Generate embeddings for text chunks")
    p_echunks.add_argument("--force", action="store_true", help="Re-embed all chunks")
    p_echunks.add_argument("--batch-size", type=int, default=50)

    # communities — community detection + search
    p_comm = sub.add_parser("communities", help="Community detection and search")
    comm_sub = p_comm.add_subparsers(dest="subcmd", required=True)
    p_comm_detect = comm_sub.add_parser("detect", help="Detect communities via label propagation")
    p_comm_detect.add_argument("--min-size", type=int, default=3, help="Min community size")
    p_comm_detect.add_argument("--summarize", action="store_true", help="Generate LLM summaries")
    p_comm_list = comm_sub.add_parser("list", help="List existing communities")
    p_comm_search = comm_sub.add_parser("search", help="Search community summaries")
    p_comm_search.add_argument("query", help="Search query")
    p_comm_search.add_argument("--limit", type=int, default=5)

    # cleanup — remove junk concepts
    p_cleanup = sub.add_parser("cleanup", help="Remove junk concepts from the graph")
    p_cleanup.add_argument("--dry-run", action="store_true", help="Preview without deleting")

    # evaluate — quality metrics
    p_eval = sub.add_parser("evaluate", help="Evaluation and quality metrics")
    eval_sub = p_eval.add_subparsers(dest="subcmd", required=True)
    eval_sub.add_parser("health", help="Graph health metrics")
    p_eval_ret = eval_sub.add_parser("retrieval", help="Evaluate retrieval quality")
    p_eval_ret.add_argument("--json", action="store_true", help="Output raw JSON")
    p_eval_ext = eval_sub.add_parser("extraction", help="Evaluate extraction against ground truth")
    p_eval_ext.add_argument("--ground-truth", required=True, help="Path to ground truth JSON")
    p_eval_ext.add_argument("--json", action="store_true")
    p_eval_gt = eval_sub.add_parser("generate-ground-truth", help="Generate ground truth template")
    p_eval_gt.add_argument("doc_title", help="Document title")
    p_eval_gt.add_argument("--output", "-o", help="Output file path")

    args = parser.parse_args()

    cmd_map = {
        "ingest": cmd_ingest,
        "embed": cmd_embed,
        "embed-chunks": cmd_embed_chunks,
        "search": cmd_search,
        "similar": cmd_similar,
        "viz": cmd_viz,
        "export": cmd_export,
        "stats": cmd_stats,
        "resolve": cmd_resolve,
        "retrieve": cmd_retrieve,
        "communities": cmd_communities,
        "cleanup": cmd_cleanup,
        "evaluate": cmd_evaluate,
    }

    asyncio.run(cmd_map[args.command](args))


if __name__ == "__main__":
    main()
