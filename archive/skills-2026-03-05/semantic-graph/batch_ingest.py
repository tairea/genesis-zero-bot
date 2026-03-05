#!/usr/bin/env python3
"""
Simple batch document ingestion script for semantic graph.
Uses rule-based extraction to avoid API dependencies.
"""

import asyncio
import os
import sys
import re
from pathlib import Path

# Add skills path
sys.path.insert(0, str(Path(__file__).parent))

from surrealdb import AsyncSurreal
from grammar_triangle import chunk_text

# Configuration
DB_URL = "ws://127.0.0.1:8000"
DB_NS = "semantic_graph"
DB_NAME = "main"
DB_USER = "root"
DB_PASS = "DLkelAlX8ucXPRUKBVPh5dYp9xZ5Y+IZ"

# Concept type keywords
TYPE_KEYWORDS = {
    "system": ["system", "platform", "framework", "infrastructure", "architecture", "service", "module", "layer", "stack"],
    "process": ["process", "workflow", "pipeline", "method", "procedure", "step", "stage", "phase", "flow"],
    "entity": ["entity", "object", "resource", "file", "document", "data", "record", "item", "node", "edge"],
    "idea": ["idea", "concept", "principle", "value", "belief", "theory", "model", "pattern", "approach"],
    "person": ["person", "user", "admin", "operator", "owner", "developer", "agent", "actor", "role"],
    "event": ["event", "action", "trigger", "signal", "notification", "alert", "change", "update"],
    "attribute": ["attribute", "property", "field", "parameter", "config", "setting", "option", "flag"],
    "place": ["place", "location", "environment", "folder", "directory", "path", "endpoint", "server"],
}

# Relation verbs - more comprehensive list
RELATION_PATTERNS = [
    # A -> B patterns
    (r"(\w+)\s+is\s+a\s+(\w+)", "IS_A"),
    (r"(\w+)\s+is\s+an\s+(\w+)", "IS_A"),
    (r"(\w+)\s+has\s+a\s+(\w+)", "HAS_A"),
    (r"(\w+)\s+has\s+an\s+(\w+)", "HAS_A"),
    (r"(\w+)\s+has\s+(\w+)", "HAS_A"),
    (r"(\w+)\s+contains\s+(\w+)", "CONTAINS"),
    (r"(\w+)\s+includes\s+(\w+)", "CONTAINS"),
    (r"(\w+)\s+depends\s+on\s+(\w+)", "DEPENDS_ON"),
    (r"(\w+)\s+depends\s+upon\s+(\w+)", "DEPENDS_ON"),
    (r"(\w+)\s+relates\s+to\s+(\w+)", "RELATES_TO"),
    (r"(\w+)\s+related\s+to\s+(\w+)", "RELATES_TO"),
    (r"(\w+)\s+connects\s+to\s+(\w+)", "CONNECTED_TO"),
    (r"(\w+)\s+connected\s+to\s+(\w+)", "CONNECTED_TO"),
    (r"(\w+)\s+uses\s+(\w+)", "USES"),
    (r"(\w+)\s+using\s+(\w+)", "USES"),
    (r"(\w+)\s+provides\s+(\w+)", "PROVIDES"),
    (r"(\w+)\s+provides\s+(\w+)\s+for", "PROVIDES"),
    (r"(\w+)\s+requires\s+(\w+)", "REQUIRES"),
    (r"(\w+)\s+required\s+for\s+(\w+)", "REQUIRES"),
    (r"(\w+)\s+enables\s+(\w+)", "ENABLES"),
    (r"(\w+)\s+enables\s+(\w+)\s+to", "ENABLES"),
    (r"(\w+)\s+manages\s+(\w+)", "MANAGES"),
    (r"(\w+)\s+managed\s+by\s+(\w+)", "MANAGED_BY"),
    (r"(\w+)\s+stores\s+(\w+)", "STORES"),
    (r"(\w+)\s+stored\s+in\s+(\w+)", "STORED_IN"),
    (r"(\w+)\s+processes\s+(\w+)", "PROCESSES"),
    (r"(\w+)\s+processed\s+by\s+(\w+)", "PROCESSED_BY"),
    (r"(\w+)\s+generates\s+(\w+)", "GENERATES"),
    (r"(\w+)\s+generated\s+by\s+(\w+)", "GENERATED_BY"),
    (r"(\w+)\s+validates\s+(\w+)", "VALIDATES"),
    (r"(\w+)\s+validated\s+by\s+(\w+)", "VALIDATED_BY"),
    (r"(\w+)\s+extracts\s+(\w+)", "EXTRACTS"),
    (r"(\w+)\s+extracted\s+from\s+(\w+)", "EXTRACTED_FROM"),
    (r"(\w+)\s+transforms\s+(\w+)", "TRANSFORMS"),
    (r"(\w+)\s+transformed\s+into\s+(\w+)", "TRANSFORMED_TO"),
    (r"(\w+)\s+calls\s+(\w+)", "CALLS"),
    (r"(\w+)\s+called\s+by\s+(\w+)", "CALLED_BY"),
    (r"(\w+)\s+imports\s+(\w+)", "IMPORTS"),
    (r"(\w+)\s+exports\s+(\w+)", "EXPORTS"),
    (r"(\w+)\s+implements\s+(\w+)", "IMPLEMENTS"),
    (r"(\w+)\s+implemented\s+by\s+(\w+)", "IMPLEMENTED_BY"),
    (r"(\w+)\s+extends\s+(\w+)", "EXTENDS"),
    (r"(\w+)\s+inherits\s+from\s+(\w+)", "INHERITS_FROM"),
    (r"(\w+)\s+composed\s+of\s+(\w+)", "COMPOSED_OF"),
    (r"(\w+)\s+part\s+of\s+(\w+)", "PART_OF"),
    (r"(\w+)\s+defines\s+(\w+)", "DEFINES"),
    (r"(\w+)\s+defined\s+by\s+(\w+)", "DEFINED_BY"),
    (r"(\w+)\s+configures\s+(\w+)", "CONFIGURED_BY"),
    (r"(\w+)\s+configured\s+by\s+(\w+)", "CONFIGURED_BY"),
    (r"(\w+)\s+loads\s+(\w+)", "LOADS"),
    (r"(\w+)\s+loaded\s+from\s+(\w+)", "LOADED_FROM"),
    (r"(\w+)\s+handles\s+(\w+)", "HANDLES"),
    (r"(\w+)\s+handles\s+(\w+)\s+requests", "HANDLES"),
    (r"(\w+)\s+receives\s+(\w+)", "RECEIVES"),
    (r"(\w+)\s+sends\s+(\w+)", "SENDS"),
    (r"(\w+)\s+creates\s+(\w+)", "CREATES"),
    (r"(\w+)\s+created\s+by\s+(\w+)", "CREATED_BY"),
    (r"(\w+)\s+updates\s+(\w+)", "UPDATES"),
    (r"(\w+)\s+updated\s+by\s+(\w+)", "UPDATED_BY"),
    (r"(\w+)\s+deletes\s+(\w+)", "DELETES"),
    (r"(\w+)\s+deleted\s+by\s+(\w+)", "DELETED_BY"),
    (r"(\w+)\s+queries\s+(\w+)", "QUERIES"),
    (r"(\w+)\s+queried\s+by\s+(\w+)", "QUERIED_BY"),
    (r"(\w+)\s+authenticates\s+(\w+)", "AUTHENTICATES"),
    (r"(\w+)\s+authorized\s+by\s+(\w+)", "AUTHORIZED_BY"),
    (r"(\w+)\s+encrypts\s+(\w+)", "ENCRYPTS"),
    (r"(\w+)\s+decrypts\s+(\w+)", "DECRYPTS"),
    (r"(\w+)\s+caches\s+(\w+)", "CACHES"),
    (r"(\w+)\s+cached\s+in\s+(\w+)", "CACHED_IN"),
    (r"(\w+)\s+indexes\s+(\w+)", "INDEXES"),
    (r"(\w+)\s+indexed\s+by\s+(\w+)", "INDEXED_BY"),
    (r"(\w+)\s+triggers\s+(\w+)", "TRIGGERS"),
    (r"(\w+)\s+triggered\s+by\s+(\w+)", "TRIGGERED_BY"),
    (r"(\w+)\s+subscribes\s+to\s+(\w+)", "SUBSCRIBES_TO"),
    (r"(\w+)\s+publishes\s+(\w+)", "PUBLISHES"),
    (r"(\w+)\s+subscribes\s+to\s+(\w+)", "SUBSCRIBES_TO"),
    (r"(\w+)\s+monitors\s+(\w+)", "MONITORS"),
    (r"(\w+)\s+logs\s+(\w+)", "LOGS"),
    (r"(\w+)\s+recorded\s+in\s+(\w+)", "RECORDED_IN"),
]


def extract_concepts_from_text(text: str) -> list[dict]:
    """Extract concepts from text using pattern matching."""
    concepts = []
    seen = set()
    
    # Find capitalized phrases (potential concepts)
    patterns = [
        r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,4})\b',  # Capitalized words
        r'\b(\w+(?:tion|ing|ment|ness|ity|ance|ence)s)\b',  # Verb/noun forms
        r'\b(\w+(?:er|or|ist|ian)s)\b',  # Agent nouns
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            if len(match) > 3 and match.lower() not in seen:
                seen.add(match.lower())
                
                # Determine type
                concept_type = "entity"
                match_lower = match.lower()
                for t, keywords in TYPE_KEYWORDS.items():
                    if any(kw in match_lower for kw in keywords):
                        concept_type = t
                        break
                
                concepts.append({
                    "name": match,
                    "type": concept_type,
                    "description": f"Extracted from text context",
                    "rung": 1,
                    "nars_frequency": 0.7,
                    "nars_confidence": 0.5,
                    "evidence_count": 1,
                })
    
    return concepts


def extract_relations_from_text(text: str, concepts: list[dict]) -> list[dict]:
    """Extract relations between concepts."""
    relations = []
    concept_names = [c["name"] for c in concepts]
    
    for pattern, verb in RELATION_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            subj, obj = match
            # Check if both are in our concepts
            subj_found = any(subj.lower() in c["name"].lower() for c in concepts)
            obj_found = any(obj.lower() in c["name"].lower() for c in concepts)
            
            if subj_found and obj_found:
                relations.append({
                    "subject": subj,
                    "verb": verb,
                    "object": obj,
                    "evidence": f"Found in text: {subj} {verb.lower()} {obj}",
                    "nars_frequency": 0.7,
                    "nars_confidence": 0.5,
                })
    
    return relations


async def ensure_schema(db):
    """Apply schema if not exists."""
    schema = """
    DEFINE TABLE IF NOT EXISTS document SCHEMALESS;
    DEFINE TABLE IF NOT EXISTS chunk SCHEMALESS;
    DEFINE TABLE IF NOT EXISTS concept SCHEMALESS;
    DEFINE TABLE IF NOT EXISTS contains TYPE RELATION SCHEMALESS;
    DEFINE TABLE IF NOT EXISTS mentions TYPE RELATION SCHEMALESS;
    DEFINE TABLE IF NOT EXISTS relates TYPE RELATION SCHEMALESS;
    """
    for stmt in schema.split(";"):
        stmt = stmt.strip()
        if stmt:
            try:
                await db.query(stmt + ";")
            except:
                pass


async def ingest_file(db, filepath: str) -> str:
    """Ingest a single file."""
    path = Path(filepath)
    if not path.exists():
        return None
    
    text = path.read_text(encoding="utf-8", errors="ignore")
    if not text.strip():
        return None
    
    # Create document
    import hashlib
    doc_id = f"document:{hashlib.sha256(str(path).encode()).hexdigest()[:16]}"
    await db.query(f"""
        UPSERT {doc_id} SET source = '{path}', title = '{path.name}', text = '', created_at = time::now()
    """)
    
    # Chunk text
    chunks = chunk_text(text)
    
    # Process each chunk
    all_concepts = []
    all_relations = []
    
    for i, chunk in enumerate(chunks):
        chunk_text_val = chunk.get("text", "")
        if not chunk_text_val or len(chunk_text_val) < 20:
            continue
        
        # Extract concepts
        concepts = extract_concepts_from_text(chunk_text_val)
        for c in concepts:
            c["source_chunks"] = [f"chunk:{i}"]
        all_concepts.extend(concepts)
        
        # Extract relations
        relations = extract_relations_from_text(chunk_text_val, concepts)
        all_relations.extend(relations)
    
    # Deduplicate concepts by name
    seen_concepts = {}
    unique_concepts = []
    for c in all_concepts:
        key = c["name"].lower()
        if key not in seen_concepts:
            seen_concepts[key] = c
            unique_concepts.append(c)
    
    # Store concepts
    concept_ids = {}
    for c in unique_concepts:
        import hashlib
        cid = f"concept:{hashlib.sha256(c['name'].lower().encode()).hexdigest()[:16]}"
        concept_ids[c['name'].lower()] = cid
        
        await db.query(f"""
            UPSERT {cid} SET 
                name = '{c["name"]}',
                type = '{c["type"]}',
                description = '{c.get("description", "")}',
                rung = {c.get("rung", 1)},
                nars_frequency = {c.get("nars_frequency", 0.7)},
                nars_confidence = {c.get("nars_confidence", 0.5)},
                evidence_count = {c.get("evidence_count", 1)},
                first_seen_in = {doc_id}
        """)
    
    # Store relations
    for r in all_relations:
        subj_key = r["subject"].lower()
        obj_key = r["object"].lower()
        verb = r["verb"]
        
        if subj_key in concept_ids and obj_key in concept_ids:
            rel_key = f"{subj_key}_{verb}_{obj_key}"
            rid = f"relates:{hashlib.sha256(rel_key.encode()).hexdigest()[:16]}"
            
            await db.query(f"""
                UPSERT {rid} SET
                    in = {concept_ids[subj_key]},
                    out = {concept_ids[obj_key]},
                    verb = '{r["verb"]}',
                    weight = {r.get("nars_confidence", 0.5)},
                    nars_frequency = {r.get("nars_frequency", 0.7)},
                    nars_confidence = {r.get("nars_confidence", 0.5)},
                    evidence_count = 1,
                    source_doc = {doc_id}
            """)
    
    return doc_id


async def main():
    # Connect to DB
    db = AsyncSurreal(url=DB_URL)
    await db.connect()
    await db.signin({"username": DB_USER, "password": DB_PASS})
    await db.use(DB_NS, DB_NAME)
    
    print("Connected to SurrealDB")
    
    # Ensure schema
    await ensure_schema(db)
    
    # Find all markdown files in workspace
    workspace = Path.home() / ".openclaw" / "workspace-genesis"
    md_files = []
    
    for pattern in ["**/*.md", "**/*.txt"]:
        md_files.extend(workspace.glob(pattern))
    
    print(f"Found {len(md_files)} files")
    
    # Ingest all files
    ingested = 0
    for f in md_files:
        try:
            doc_id = await ingest_file(db, str(f))
            if doc_id:
                ingested += 1
                print(f"✓ {f.name}")
        except Exception as e:
            print(f"✗ {f.name}: {e}")
    
    # Get counts
    result = await db.query("SELECT count() as cnt FROM concept GROUP ALL")
    concept_count = result[0].get("cnt", 0) if result else 0
    
    result = await db.query("SELECT count() as cnt FROM relates GROUP ALL")
    relation_count = result[0].get("cnt", 0) if result else 0
    
    print(f"\n=== Summary ===")
    print(f"Files ingested: {ingested}")
    print(f"Total concepts: {concept_count}")
    print(f"Total relations: {relation_count}")
    
    await db.close()


if __name__ == "__main__":
    asyncio.run(main())
