"""
cleanup.py — Remove junk/generic concepts from the knowledge graph.

Deletes concepts that are stopwords, too short, contain newlines,
or are generic single-word terms that don't represent meaningful domain entities.
Also cleans up orphaned edges pointing to deleted concepts.

Usage:
    python cleanup.py --dry-run    # See what would be deleted
    python cleanup.py              # Actually delete
"""

from __future__ import annotations

import asyncio
import os
import sys


def _is_junk_concept(name: str) -> bool:
    """Same filter as llm_parser.py — keep in sync."""
    if len(name) <= 2:
        return True
    if "\n" in name:
        return True
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
    if " " not in name and name[0].islower() and len(name) <= 8:
        return True
    return False


async def cleanup(dry_run: bool = True, verbose: bool = True):
    from surrealdb import AsyncSurreal

    db_url = os.environ.get("SURREALDB_URL", "ws://127.0.0.1:8000")
    db = AsyncSurreal(url=db_url)
    await db.connect()
    await db.signin({"username": "root", "password": os.environ.get("SURREAL_PASS", "root")})
    await db.use("semantic_graph", "main")

    # Get all concepts
    concepts = await db.query("SELECT id, name, type FROM concept")
    if not concepts:
        print("No concepts found.")
        return

    total = len(concepts)
    junk = []
    for c in concepts:
        name = c.get("name", "")
        if _is_junk_concept(name):
            junk.append(c)

    print(f"Total concepts: {total}")
    print(f"Junk concepts to remove: {len(junk)} ({100*len(junk)/total:.1f}%)")

    if verbose:
        # Show sample
        print(f"\nSample junk concepts (first 50):")
        for c in junk[:50]:
            print(f"  {c['type']:12s} | {c['name']!r}")

    if dry_run:
        print(f"\n[DRY RUN] Would delete {len(junk)} concepts and their edges.")
        await db.close()
        return

    # Delete junk concepts and their edges
    deleted = 0
    for c in junk:
        cid = c["id"]
        try:
            # Delete edges first
            await db.query("DELETE relates WHERE in = $id OR out = $id", {"id": cid})
            await db.query("DELETE mentions WHERE out = $id", {"id": cid})
            # Delete the concept
            await db.query("DELETE $id", {"id": cid})
            deleted += 1
        except Exception as e:
            print(f"  Error deleting {c['name']!r}: {e}", file=sys.stderr)

    print(f"\nDeleted {deleted}/{len(junk)} junk concepts and their edges.")

    # Stats after cleanup
    result = await db.query("SELECT count() as cnt FROM concept GROUP ALL")
    remaining = 0
    if result and isinstance(result, list) and result:
        first = result[0]
        remaining = first.get("cnt", 0) if isinstance(first, dict) else 0
    print(f"Remaining concepts: {remaining}")

    await db.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Clean junk concepts from the knowledge graph")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be deleted without deleting")
    parser.add_argument("-v", "--verbose", action="store_true", default=True)
    args = parser.parse_args()
    asyncio.run(cleanup(dry_run=args.dry_run, verbose=args.verbose))
