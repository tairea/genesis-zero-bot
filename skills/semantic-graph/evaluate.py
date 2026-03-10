"""
evaluate.py — Evaluation framework for knowledge graph extraction and retrieval quality.

Measures:
1. Extraction quality: concept precision/recall against labeled ground truth
2. Retrieval quality: answer relevance via LLM-as-judge scoring
3. Graph health: structural metrics (density, connectivity, type distribution)

Usage:
    python evaluate.py health                      # Graph health metrics
    python evaluate.py retrieval                   # Run retrieval eval on built-in queries
    python evaluate.py extraction --ground-truth eval_ground_truth.json
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))


# ── Graph Health Metrics ────────────────────────────────────────────────────

async def graph_health(db, verbose: bool = True) -> dict:
    """
    Structural health metrics for the knowledge graph.

    Returns dict with density, connectivity, type balance, etc.
    """
    metrics: dict[str, Any] = {}

    # Basic counts
    tables = ["document", "chunk", "concept", "relates", "mentions", "community"]
    for table in tables:
        result = await db.query(f"SELECT count() as cnt FROM {table} GROUP ALL")
        cnt = 0
        if result and isinstance(result, list) and result:
            first = result[0]
            cnt = first.get("cnt", 0) if isinstance(first, dict) else 0
        metrics[f"count_{table}"] = cnt

    n_concepts = metrics["count_concept"]
    n_relations = metrics["count_relates"]
    n_chunks = metrics["count_chunk"]

    # ── Density ──
    # For a directed graph: density = edges / (nodes * (nodes - 1))
    if n_concepts > 1:
        metrics["graph_density"] = round(n_relations / (n_concepts * (n_concepts - 1)), 6)
    else:
        metrics["graph_density"] = 0.0

    # Edge-to-node ratio (healthy: 1.0-5.0)
    metrics["edge_node_ratio"] = round(n_relations / max(n_concepts, 1), 2)

    # ── Embedding coverage ──
    emb_result = await db.query(
        "SELECT count() as cnt FROM concept WHERE embedding IS NOT NONE GROUP ALL"
    )
    emb_cnt = 0
    if emb_result and isinstance(emb_result, list) and emb_result:
        emb_cnt = emb_result[0].get("cnt", 0) if isinstance(emb_result[0], dict) else 0
    metrics["concept_embedding_coverage"] = round(emb_cnt / max(n_concepts, 1), 3)

    chunk_emb = await db.query(
        "SELECT count() as cnt FROM chunk WHERE embedding IS NOT NONE GROUP ALL"
    )
    chunk_emb_cnt = 0
    if chunk_emb and isinstance(chunk_emb, list) and chunk_emb:
        chunk_emb_cnt = chunk_emb[0].get("cnt", 0) if isinstance(chunk_emb[0], dict) else 0
    metrics["chunk_embedding_coverage"] = round(chunk_emb_cnt / max(n_chunks, 1), 3)

    # ── Type distribution ──
    type_result = await db.query(
        "SELECT type, count() as cnt FROM concept GROUP BY type ORDER BY cnt DESC"
    )
    type_dist = {}
    if type_result:
        for t in type_result:
            if isinstance(t, dict) and t.get("type"):
                type_dist[t["type"]] = t["cnt"]
    metrics["type_distribution"] = type_dist

    # Type entropy (higher = more balanced)
    if type_dist:
        import math
        total = sum(type_dist.values())
        entropy = -sum((c / total) * math.log2(c / total) for c in type_dist.values() if c > 0)
        max_entropy = math.log2(len(type_dist)) if len(type_dist) > 1 else 1.0
        metrics["type_entropy"] = round(entropy, 3)
        metrics["type_balance"] = round(entropy / max_entropy, 3)  # 0-1, higher is more balanced

    # ── Verb distribution ──
    verb_result = await db.query(
        "SELECT verb, count() as cnt FROM relates GROUP BY verb ORDER BY cnt DESC"
    )
    verb_dist = {}
    if verb_result:
        for v in verb_result:
            if isinstance(v, dict) and v.get("verb"):
                verb_dist[v["verb"]] = v["cnt"]
    metrics["verb_distribution"] = verb_dist
    metrics["unique_verbs"] = len(verb_dist)

    # ── Orphan concepts (no edges) ──
    rel_sources = await db.query("SELECT VALUE in FROM relates")
    rel_targets = await db.query("SELECT VALUE out FROM relates")
    related_ids = set()
    for rid in (rel_sources or []) + (rel_targets or []):
        related_ids.add(str(rid))

    all_concept_ids = await db.query("SELECT VALUE id FROM concept")
    all_ids = set(str(i) for i in (all_concept_ids or []))
    orphan_count = len(all_ids - related_ids)
    metrics["orphan_concepts"] = orphan_count
    metrics["orphan_ratio"] = round(orphan_count / max(n_concepts, 1), 3)

    # ── Confidence distribution ──
    conf_result = await db.query("""
        SELECT
            math::mean(nars_confidence) AS mean_conf,
            math::min(nars_confidence) AS min_conf,
            math::max(nars_confidence) AS max_conf
        FROM concept
    """)
    if conf_result and isinstance(conf_result, list) and conf_result:
        cr = conf_result[0]
        metrics["concept_confidence_mean"] = round(cr.get("mean_conf", 0), 3)
        metrics["concept_confidence_range"] = [
            round(cr.get("min_conf", 0), 3),
            round(cr.get("max_conf", 0), 3),
        ]

    # ── Temporal edges ──
    temporal_result = await db.query(
        "SELECT count() as cnt FROM relates WHERE valid_until IS NOT NONE GROUP ALL"
    )
    temporal_cnt = 0
    if temporal_result and isinstance(temporal_result, list) and temporal_result:
        temporal_cnt = temporal_result[0].get("cnt", 0) if isinstance(temporal_result[0], dict) else 0
    metrics["invalidated_edges"] = temporal_cnt

    if verbose:
        print("=== Graph Health Report ===\n")
        print(f"Documents:    {metrics['count_document']}")
        print(f"Chunks:       {metrics['count_chunk']}")
        print(f"Concepts:     {n_concepts}")
        print(f"Relations:    {n_relations}")
        print(f"Communities:  {metrics['count_community']}")
        print(f"\nEdge/Node:    {metrics['edge_node_ratio']}  (healthy: 1.0-5.0)")
        print(f"Density:      {metrics['graph_density']}")
        print(f"Orphans:      {metrics['orphan_concepts']} ({metrics['orphan_ratio']:.1%})")
        print(f"Invalidated:  {metrics['invalidated_edges']} edges")
        print(f"\nEmbeddings:   concepts={metrics['concept_embedding_coverage']:.1%}  chunks={metrics['chunk_embedding_coverage']:.1%}")
        print(f"Type balance: {metrics.get('type_balance', 0):.2f}  (1.0 = perfectly even)")
        print(f"Unique verbs: {metrics['unique_verbs']}")
        print(f"Confidence:   mean={metrics.get('concept_confidence_mean', 0):.2f}  range={metrics.get('concept_confidence_range', [0,0])}")
        print(f"\nType distribution:")
        for t, c in sorted(type_dist.items(), key=lambda x: x[1], reverse=True):
            bar = "#" * (c * 40 // max(type_dist.values()))
            print(f"  {t:15s} {c:>5}  {bar}")
        print(f"\nTop 10 verbs:")
        for v, c in list(verb_dist.items())[:10]:
            print(f"  {v:15s} {c:>5}")

    return metrics


# ── Retrieval Evaluation ────────────────────────────────────────────────────

# Built-in evaluation queries with expected properties
EVAL_QUERIES = [
    {
        "query": "How does water management work in regenerative communities?",
        "expected_concepts": ["Water", "Rainwater", "Greywater", "Treatment"],
        "expected_themes": ["water", "irrigation", "recycling", "treatment"],
    },
    {
        "query": "What governance models are used for intentional communities?",
        "expected_concepts": ["Governance", "Consensus", "Community Agreements", "Decision"],
        "expected_themes": ["governance", "decision", "consensus", "voting"],
    },
    {
        "query": "How do you fund a regenerative neighborhood?",
        "expected_concepts": ["Capital", "Revenue", "Financial", "Investment"],
        "expected_themes": ["funding", "investment", "capital", "revenue", "financial"],
    },
    {
        "query": "What renewable energy systems are appropriate for eco-villages?",
        "expected_concepts": ["Solar", "Battery", "Wind", "Energy"],
        "expected_themes": ["solar", "energy", "battery", "wind", "renewable"],
    },
    {
        "query": "What is the RNF Hybrid Sequencing Model?",
        "expected_concepts": ["RNF", "Spiral", "Gate"],
        "expected_themes": ["spiral", "gate", "sequencing", "phase", "development"],
    },
    {
        "query": "How do you build a founding team for a regenerative community?",
        "expected_concepts": ["Founding", "Team", "Founder"],
        "expected_themes": ["founder", "team", "vision", "alignment", "commitment"],
    },
    {
        "query": "What food production systems work in regenerative neighborhoods?",
        "expected_concepts": ["Aquaponics", "Agroforestry", "Food Production"],
        "expected_themes": ["food", "farming", "agriculture", "production", "growing"],
    },
    {
        "query": "How does the Community Alchemy Playbook work?",
        "expected_concepts": ["Community Alchemy Playbook", "Community Alchemy"],
        "expected_themes": ["alchemy", "playbook", "facilitation", "community building"],
    },
]


async def eval_retrieval(db, queries: list[dict] | None = None, verbose: bool = True) -> dict:
    """
    Evaluate retrieval quality on a set of test queries.

    Metrics:
    - concept_recall: fraction of expected concepts found in results
    - theme_coverage: fraction of expected themes mentioned in returned text
    - avg_result_count: average concepts/relations/chunks returned
    - latency_p50/p95: retrieval speed
    """
    from retriever import retrieve

    queries = queries or EVAL_QUERIES
    results = []

    for i, q in enumerate(queries):
        t0 = time.perf_counter()
        ctx = await retrieve(db, q["query"], limit=10, hops=1, include_chunks=True)
        latency = time.perf_counter() - t0

        # Concept recall (fuzzy: expected name appears as substring in any returned name, or vice versa)
        returned_names = [c.get("name", "").lower() for c in ctx.concepts]
        expected = q.get("expected_concepts", [])

        def _fuzzy_match(expected_name: str, returned: list[str]) -> bool:
            e = expected_name.lower()
            for r in returned:
                if e in r or r in e or e.split()[0] in r:
                    return True
            return False

        found = sum(1 for e in expected if _fuzzy_match(e, returned_names))
        concept_recall = found / len(expected) if expected else 1.0

        # Theme coverage: check if expected themes appear in the formatted text
        text_lower = ctx.text.lower()
        themes = q.get("expected_themes", [])
        theme_hits = sum(1 for t in themes if t in text_lower)
        theme_coverage = theme_hits / len(themes) if themes else 1.0

        result = {
            "query": q["query"],
            "concept_recall": round(concept_recall, 3),
            "theme_coverage": round(theme_coverage, 3),
            "n_concepts": len(ctx.concepts),
            "n_relations": len(ctx.relations),
            "n_communities": len(ctx.communities),
            "n_chunks": len(ctx.chunks),
            "latency_ms": round(latency * 1000, 1),
            "found_concepts": [e for e in expected if _fuzzy_match(e, returned_names)],
            "missed_concepts": [e for e in expected if not _fuzzy_match(e, returned_names)],
        }
        results.append(result)

        if verbose:
            status = "PASS" if concept_recall >= 0.5 and theme_coverage >= 0.5 else "WEAK"
            print(f"  [{status}] Q{i+1}: {q['query'][:60]}...")
            print(f"       recall={concept_recall:.0%}  themes={theme_coverage:.0%}  "
                  f"concepts={len(ctx.concepts)}  latency={latency*1000:.0f}ms")
            if result["missed_concepts"]:
                print(f"       missed: {', '.join(result['missed_concepts'])}")

    # Aggregate
    n = len(results)
    latencies = sorted(r["latency_ms"] for r in results)
    summary = {
        "n_queries": n,
        "avg_concept_recall": round(sum(r["concept_recall"] for r in results) / n, 3),
        "avg_theme_coverage": round(sum(r["theme_coverage"] for r in results) / n, 3),
        "avg_concepts": round(sum(r["n_concepts"] for r in results) / n, 1),
        "avg_relations": round(sum(r["n_relations"] for r in results) / n, 1),
        "avg_communities": round(sum(r["n_communities"] for r in results) / n, 1),
        "avg_chunks": round(sum(r["n_chunks"] for r in results) / n, 1),
        "latency_p50_ms": round(latencies[n // 2], 1),
        "latency_p95_ms": round(latencies[int(n * 0.95)], 1),
        "pass_rate": round(sum(1 for r in results if r["concept_recall"] >= 0.5 and r["theme_coverage"] >= 0.5) / n, 3),
        "details": results,
    }

    if verbose:
        print(f"\n=== Retrieval Evaluation Summary ===")
        print(f"Queries:        {n}")
        print(f"Pass rate:      {summary['pass_rate']:.0%}")
        print(f"Concept recall: {summary['avg_concept_recall']:.1%}")
        print(f"Theme coverage: {summary['avg_theme_coverage']:.1%}")
        print(f"Avg results:    {summary['avg_concepts']:.0f} concepts, {summary['avg_relations']:.0f} relations, {summary['avg_chunks']:.0f} chunks")
        print(f"Latency:        p50={summary['latency_p50_ms']:.0f}ms  p95={summary['latency_p95_ms']:.0f}ms")

    return summary


# ── Extraction Evaluation ──────────────────────────────────────────────────

async def eval_extraction(db, ground_truth_path: str, verbose: bool = True) -> dict:
    """
    Evaluate extraction quality against a manually labeled ground truth file.

    Ground truth JSON format:
    {
        "document_title": {
            "expected_concepts": [{"name": "...", "type": "..."}],
            "expected_relations": [{"source": "...", "verb": "...", "target": "..."}]
        }
    }

    Metrics:
    - concept_precision: fraction of extracted concepts that are in ground truth
    - concept_recall: fraction of ground truth concepts that were extracted
    - concept_f1: harmonic mean
    - relation_recall: fraction of expected relations found (fuzzy match)
    """
    gt_path = Path(ground_truth_path)
    if not gt_path.exists():
        print(f"Ground truth file not found: {gt_path}")
        print("Create one with: python evaluate.py generate-ground-truth <doc_title>")
        return {}

    with open(gt_path) as f:
        ground_truth = json.load(f)

    all_results = []

    for doc_title, expected in ground_truth.items():
        # Get extracted concepts for this document
        extracted_concepts = await db.query(
            "SELECT name, type FROM concept WHERE first_seen_in.title = $title",
            {"title": doc_title},
        )
        if not extracted_concepts:
            # Fallback: find by document → chunks → mentions → concepts
            extracted_concepts = await db.query("""
                SELECT name, type FROM concept
                WHERE ->mentions<-chunk<-contains<-document[WHERE title = $title]
            """, {"title": doc_title})

        extracted_names = {c.get("name", "").lower() for c in (extracted_concepts or []) if isinstance(c, dict)}

        expected_concepts = expected.get("expected_concepts", [])
        expected_names = {c["name"].lower() for c in expected_concepts}

        # Concept precision/recall (case-insensitive exact match)
        if extracted_names and expected_names:
            true_positives = extracted_names & expected_names
            precision = len(true_positives) / len(extracted_names) if extracted_names else 0
            recall = len(true_positives) / len(expected_names) if expected_names else 0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        else:
            precision = recall = f1 = 0.0

        # Relation recall (fuzzy: source and target match, verb is flexible)
        expected_rels = expected.get("expected_relations", [])
        extracted_rels = await db.query("""
            SELECT in.name AS source, verb, out.name AS target
            FROM relates
            WHERE in.first_seen_in.title = $title OR out.first_seen_in.title = $title
        """, {"title": doc_title})

        rel_recall = 0.0
        if expected_rels:
            extracted_rel_pairs = set()
            for r in (extracted_rels or []):
                if isinstance(r, dict):
                    s = str(r.get("source", "")).lower()
                    t = str(r.get("target", "")).lower()
                    extracted_rel_pairs.add((s, t))

            found_rels = 0
            for er in expected_rels:
                s = er["source"].lower()
                t = er["target"].lower()
                if (s, t) in extracted_rel_pairs or (t, s) in extracted_rel_pairs:
                    found_rels += 1
            rel_recall = found_rels / len(expected_rels)

        result = {
            "document": doc_title,
            "extracted_count": len(extracted_names),
            "expected_count": len(expected_names),
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "f1": round(f1, 3),
            "relation_recall": round(rel_recall, 3),
        }
        all_results.append(result)

        if verbose:
            print(f"  [{doc_title}]")
            print(f"    Extracted: {len(extracted_names)} concepts  Expected: {len(expected_names)}")
            print(f"    P={precision:.2f}  R={recall:.2f}  F1={f1:.2f}  RelR={rel_recall:.2f}")

    # Aggregate
    n = len(all_results)
    summary = {
        "n_documents": n,
        "avg_precision": round(sum(r["precision"] for r in all_results) / max(n, 1), 3),
        "avg_recall": round(sum(r["recall"] for r in all_results) / max(n, 1), 3),
        "avg_f1": round(sum(r["f1"] for r in all_results) / max(n, 1), 3),
        "avg_relation_recall": round(sum(r["relation_recall"] for r in all_results) / max(n, 1), 3),
        "details": all_results,
    }

    if verbose:
        print(f"\n=== Extraction Evaluation Summary ===")
        print(f"Documents:       {n}")
        print(f"Avg Precision:   {summary['avg_precision']:.1%}")
        print(f"Avg Recall:      {summary['avg_recall']:.1%}")
        print(f"Avg F1:          {summary['avg_f1']:.1%}")
        print(f"Avg Rel Recall:  {summary['avg_relation_recall']:.1%}")

    return summary


async def generate_ground_truth_template(db, doc_title: str, output: str | None = None) -> dict:
    """
    Generate a ground truth template from existing extraction for manual review.

    Extracts current concepts and relations for a document so you can
    review, correct, and use as ground truth.
    """
    concepts = await db.query("""
        SELECT DISTINCT name, type FROM concept
        WHERE <-mentions<-chunk<-contains<-document[WHERE title = $title]
    """, {"title": doc_title})

    relations = await db.query("""
        SELECT in.name AS source, verb, out.name AS target
        FROM relates
        WHERE source_doc.title = $title
    """, {"title": doc_title})

    template = {
        doc_title: {
            "expected_concepts": [
                {"name": c.get("name", ""), "type": c.get("type", "")}
                for c in (concepts or []) if isinstance(c, dict)
            ],
            "expected_relations": [
                {"source": str(r.get("source", "")), "verb": r.get("verb", ""), "target": str(r.get("target", ""))}
                for r in (relations or []) if isinstance(r, dict)
            ],
        }
    }

    out_path = output or f"eval_gt_{doc_title.replace(' ', '_').replace('.', '_')}.json"
    with open(out_path, "w") as f:
        json.dump(template, f, indent=2, default=str)

    print(f"Ground truth template written to {out_path}")
    print(f"  {len(template[doc_title]['expected_concepts'])} concepts, "
          f"{len(template[doc_title]['expected_relations'])} relations")
    print("Review and correct this file, then use: python evaluate.py extraction --ground-truth", out_path)

    return template


# ── CLI ─────────────────────────────────────────────────────────────────────

async def _cli_main():
    import argparse
    parser = argparse.ArgumentParser(description="Knowledge graph evaluation framework")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("health", help="Graph health metrics")

    p_ret = sub.add_parser("retrieval", help="Evaluate retrieval quality")
    p_ret.add_argument("--json", action="store_true", help="Output raw JSON")

    p_ext = sub.add_parser("extraction", help="Evaluate extraction against ground truth")
    p_ext.add_argument("--ground-truth", required=True, help="Path to ground truth JSON")
    p_ext.add_argument("--json", action="store_true")

    p_gt = sub.add_parser("generate-ground-truth", help="Generate ground truth template from existing data")
    p_gt.add_argument("doc_title", help="Document title to generate template for")
    p_gt.add_argument("--output", "-o", help="Output file path")

    args = parser.parse_args()

    from surrealdb import AsyncSurreal
    db_url = os.environ.get("SURREALDB_URL", "ws://127.0.0.1:8000")
    db = AsyncSurreal(url=db_url)
    await db.connect()
    await db.signin({"username": "root", "password": os.environ.get("SURREAL_PASS", "root")})
    await db.use("semantic_graph", "main")

    if args.command == "health":
        result = await graph_health(db)
        # Also print as JSON for machine consumption
        clean = {k: v for k, v in result.items() if k not in ("type_distribution", "verb_distribution")}
        print(f"\n{json.dumps(clean, indent=2)}")

    elif args.command == "retrieval":
        result = await eval_retrieval(db, verbose=not args.json)
        if args.json:
            print(json.dumps(result, indent=2))

    elif args.command == "extraction":
        result = await eval_extraction(db, args.ground_truth, verbose=not args.json)
        if args.json:
            print(json.dumps(result, indent=2))

    elif args.command == "generate-ground-truth":
        await generate_ground_truth_template(db, args.doc_title, args.output)

    await db.close()


if __name__ == "__main__":
    asyncio.run(_cli_main())
