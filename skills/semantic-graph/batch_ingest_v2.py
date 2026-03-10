#!/usr/bin/env python3
"""
Improved batch document ingestion with better relation extraction.
"""

import asyncio
import os
import sys
import re
from pathlib import Path
import hashlib

sys.path.insert(0, str(Path(__file__).parent))

from surrealdb import AsyncSurreal
from grammar_triangle import chunk_text

# Configuration
DB_URL = "ws://127.0.0.1:8000"
DB_NS = "semantic_graph"
DB_NAME = "main"
DB_USER = "root"
DB_PASS = os.environ.get("SURREAL_PASS", "root")

# Extended concept type keywords
TYPE_KEYWORDS = {
    "system": ["system", "platform", "framework", "infrastructure", "architecture", "service", "module", "layer", "stack", "engine", "runtime", "container", "cluster", "network", "api", "sdk", "tool"],
    "process": ["process", "workflow", "pipeline", "method", "procedure", "step", "stage", "phase", "flow", "operation", "task", "job", "batch", "transaction", "session", "execution"],
    "entity": ["entity", "object", "resource", "file", "document", "data", "record", "item", "node", "edge", "table", "index", "key", "token", "credential", "config", "setting"],
    "idea": ["idea", "concept", "principle", "value", "belief", "theory", "model", "pattern", "approach", "strategy", "practice", "standard", "protocol", "specification", "requirement"],
    "person": ["person", "user", "admin", "operator", "owner", "developer", "agent", "actor", "role", "team", "group", "member", "creator", "maintainer", "contributor"],
    "event": ["event", "action", "trigger", "signal", "notification", "alert", "change", "update", "request", "response", "error", "timeout", "exception", "failure", "success"],
    "attribute": ["attribute", "property", "field", "parameter", "config", "setting", "option", "flag", "variable", "constant", "value", "type", "format", "schema", "structure"],
    "place": ["place", "location", "environment", "folder", "directory", "path", "endpoint", "server", "host", "port", "url", "uri", "address", "region", "zone"],
    "specification": ["spec", "specification", "standard", "RFC", "documentation", "guide", "reference", "manual", "API"],
    "project": ["project", "product", "application", "app", "service", "library", "package", "module"],
}

# More comprehensive relation patterns
RELATION_PATTERNS = [
    # Basic relationships
    (r"\b(\w+)\s+is\s+a\s+(\w+)", "IS_A"),
    (r"\b(\w+)\s+is\s+an\s+(\w+)", "IS_A"),
    (r"\b(\w+)\s+is\s+the\s+(\w+)", "IS_A"),
    (r"\b(\w+)\s+are\s+(\w+)", "IS_A"),
    (r"\b(\w+)\s+acts\s+as\s+(\w+)", "ACTS_AS"),
    
    # Containment
    (r"\b(\w+)\s+has\s+a\s+(\w+)", "HAS_A"),
    (r"\b(\w+)\s+has\s+an\s+(\w+)", "HAS_A"),
    (r"\b(\w+)\s+has\s+(\w+)", "HAS_A"),
    (r"\b(\w+)\s+contains\s+(\w+)", "CONTAINS"),
    (r"\b(\w+)\s+includes\s+(\w+)", "INCLUDES"),
    (r"\b(\w+)\s+consists\s+of\s+(\w+)", "CONSISTS_OF"),
    (r"\b(\w+)\s+composed\s+of\s+(\w+)", "COMPOSED_OF"),
    (r"\b(\w+)\s+made\s+of\s+(\w+)", "MADE_OF"),
    (r"\b(\w+)\s+made\s+from\s+(\w+)", "MADE_FROM"),
    
    # Dependencies
    (r"\b(\w+)\s+depends\s+on\s+(\w+)", "DEPENDS_ON"),
    (r"\b(\w+)\s+depends\s+upon\s+(\w+)", "DEPENDS_ON"),
    (r"\b(\w+)\s+requires\s+(\w+)", "REQUIRES"),
    (r"\b(\w+)\s+needs\s+(\w+)", "NEEDS"),
    (r"\b(\w+)\s+needs\s+to\s+(\w+)", "NEEDS"),
    (r"\b(\w+)\s+necessary\s+for\s+(\w+)", "NECESSARY_FOR"),
    (r"\b(\w+)\s+needed\s+for\s+(\w+)", "NEEDED_FOR"),
    
    # Enabling
    (r"\b(\w+)\s+enables\s+(\w+)", "ENABLES"),
    (r"\b(\w+)\s+allows\s+(\w+)", "ALLOWS"),
    (r"\b(\w+)\s+permits\s+(\w+)", "PERMITS"),
    (r"\b(\w+)\s+facilitates\s+(\w+)", "FACILITATES"),
    (r"\b(\w+)\s+supports\s+(\w+)", "SUPPORTS"),
    (r"\b(\w+)\s+provides\s+(\w+)", "PROVIDES"),
    (r"\b(\w+)\s+offers\s+(\w+)", "OFFERS"),
    
    # Usage
    (r"\b(\w+)\s+uses\s+(\w+)", "USES"),
    (r"\b(\w+)\s+using\s+(\w+)", "USES"),
    (r"\b(\w+)\s+utilizes\s+(\w+)", "UTILIZES"),
    (r"\b(\w+)\s+utilizes\s+(\w+)", "UTILIZES"),
    (r"\b(\w+)\s+employs\s+(\w+)", "EMPLOYS"),
    (r"\b(\w+)\s+applies\s+(\w+)", "APPLIES"),
    (r"\b(\w+)\s+implements\s+(\w+)", "IMPLEMENTS"),
    (r"\b(\w+)\s+implements\s+the\s+(\w+)", "IMPLEMENTS"),
    
    # Data flow
    (r"\b(\w+)\s+reads\s+from\s+(\w+)", "READS_FROM"),
    (r"\b(\w+)\s+writes\s+to\s+(\w+)", "WRITES_TO"),
    (r"\b(\w+)\s+stores\s+in\s+(\w+)", "STORES_IN"),
    (r"\b(\w+)\s+stores\s+(\w+)", "STORES"),
    (r"\b(\w+)\s+retrieves\s+from\s+(\w+)", "RETRIEVES_FROM"),
    (r"\b(\w+)\s+loads\s+from\s+(\w+)", "LOADS_FROM"),
    (r"\b(\w+)\s+saves\s+to\s+(\w+)", "SAVES_TO"),
    (r"\b(\w+)\s+caches\s+(\w+)", "CACHES"),
    
    # Processing
    (r"\b(\w+)\s+processes\s+(\w+)", "PROCESSES"),
    (r"\b(\w+)\s+processes\s+the\s+(\w+)", "PROCESSES"),
    (r"\b(\w+)\s+handles\s+(\w+)", "HANDLES"),
    (r"\b(\w+)\s+handles\s+the\s+(\w+)", "HANDLES"),
    (r"\b(\w+)\s+manages\s+(\w+)", "MANAGES"),
    (r"\b(\w+)\s+manages\s+the\s+(\w+)", "MANAGES"),
    (r"\b(\w+)\s+transforms\s+(\w+)", "TRANSFORMS"),
    (r"\b(\w+)\s+transforms\s+into\s+(\w+)", "TRANSFORMS_TO"),
    (r"\b(\w+)\s+converts\s+(\w+)", "CONVERTS"),
    (r"\b(\w+)\s+parses\s+(\w+)", "PARSES"),
    (r"\b(\w+)\s+validates\s+(\w+)", "VALIDATES"),
    (r"\b(\w+)\s+verifies\s+(\w+)", "VERIFIES"),
    
    # Communication
    (r"\b(\w+)\s+calls\s+(\w+)", "CALLS"),
    (r"\b(\w+)\s+calls\s+the\s+(\w+)", "CALLS"),
    (r"\b(\w+)\s+invokes\s+(\w+)", "INVOKES"),
    (r"\b(\w+)\s+sends\s+to\s+(\w+)", "SENDS_TO"),
    (r"\b(\w+)\s+receives\s+from\s+(\w+)", "RECEIVES_FROM"),
    (r"\b(\w+)\s+communicates\s+with\s+(\w+)", "COMMUNICATES_WITH"),
    (r"\b(\w+)\s+connects\s+to\s+(\w+)", "CONNECTS_TO"),
    (r"\b(\w+)\s+connects\s+with\s+(\w+)", "CONNECTS_WITH"),
    
    # Control flow
    (r"\b(\w+)\s+triggers\s+(\w+)", "TRIGGERS"),
    (r"\b(\w+)\s+triggers\s+the\s+(\w+)", "TRIGGERS"),
    (r"\b(\w+)\s+initiates\s+(\w+)", "INITIATES"),
    (r"\b(\w+)\s+starts\s+(\w+)", "STARTS"),
    (r"\b(\w+)\s+stops\s+(\w+)", "STOPS"),
    (r"\b(\w+)\s+pauses\s+(\w+)", "PAUSES"),
    (r"\b(\w+)\s+resumes\s+(\w+)", "RESUMES"),
    
    # Creation/destruction
    (r"\b(\w+)\s+creates\s+(\w+)", "CREATES"),
    (r"\b(\w+)\s+creates\s+the\s+(\w+)", "CREATES"),
    (r"\b(\w+)\s+generates\s+(\w+)", "GENERATES"),
    (r"\b(\w+)\s+produces\s+(\w+)", "PRODUCES"),
    (r"\b(\w+)\s+destroys\s+(\w+)", "DESTROYS"),
    (r"\b(\w+)\s+deletes\s+(\w+)", "DELETES"),
    (r"\b(\w+)\s+removes\s+(\w+)", "REMOVES"),
    
    # Authentication/authorization
    (r"\b(\w+)\s+authenticates\s+(\w+)", "AUTHENTICATES"),
    (r"\b(\w+)\s+authorizes\s+(\w+)", "AUTHORIZES"),
    (r"\b(\w+)\s+encrypts\s+(\w+)", "ENCRYPTS"),
    (r"\b(\w+)\s+decrypts\s+(\w+)", "DECRYPTS"),
    (r"\b(\w+)\s+validates\s+(\w+)", "VALIDATES"),
    
    # Monitoring/logging
    (r"\b(\w+)\s+monitors\s+(\w+)", "MONITORS"),
    (r"\b(\w+)\s+logs\s+(\w+)", "LOGS"),
    (r"\b(\w+)\s+tracks\s+(\w+)", "TRACKS"),
    (r"\b(\w+)\s+measures\s+(\w+)", "MEASURES"),
    
    # Similarity
    (r"\b(\w+)\s+similar\s+to\s+(\w+)", "SIMILAR_TO"),
    (r"\b(\w+)\s+like\s+(\w+)", "LIKE"),
    (r"\b(\w+)\s+related\s+to\s+(\w+)", "RELATED_TO"),
    (r"\b(\w+)\s+relates\s+to\s+(\w+)", "RELATES_TO"),
    (r"\b(\w+)\s+compared\s+to\s+(\w+)", "COMPARED_TO"),
    (r"\b(\w+)\s+compared\s+with\s+(\w+)", "COMPARED_WITH"),
    
    # Conflict/agreement
    (r"\b(\w+)\s+contradicts\s+(\w+)", "CONTRADICTS"),
    (r"\b(\w+)\s+conflicts\s+with\s+(\w+)", "CONFLICTS_WITH"),
    (r"\b(\w+)\s+agrees\s+with\s+(\w+)", "AGREES_WITH"),
    (r"\b(\w+)\s+supports\s+(\w+)", "SUPPORTS"),
    (r"\b(\w+)\s+opposes\s+(\w+)", "OPPOSES"),
    
    # Temporal
    (r"\b(\w+)\s+happens\s+before\s+(\w+)", "HAPPENS_BEFORE"),
    (r"\b(\w+)\s+happens\s+after\s+(\w+)", "HAPPENS_AFTER"),
    (r"\b(\w+)\s+occurs\s+during\s+(\w+)", "OCCURS_DURING"),
    (r"\b(\w+)\s+runs\s+before\s+(\w+)", "RUNS_BEFORE"),
    (r"\b(\w+)\s+runs\s+after\s+(\w+)", "RUNS_AFTER"),
    
    # Ownership
    (r"\b(\w+)\s+owns\s+(\w+)", "OWNS"),
    (r"\b(\w+)\s+owned\s+by\s+(\w+)", "OWNED_BY"),
    (r"\b(\w+)\s+belongs\s+to\s+(\w+)", "BELONGS_TO"),
    (r"\b(\w+)\s+part\s+of\s+(\w+)", "PART_OF"),
    (r"\b(\w+)\s+included\s+in\s+(\w+)", "INCLUDED_IN"),
]


def normalize_text(text: str) -> str:
    """Clean and normalize text for matching."""
    return re.sub(r'[^\w\s]', ' ', text.lower())


def extract_concepts_from_text(text: str) -> list[dict]:
    """Extract concepts from text using pattern matching."""
    concepts = []
    seen = set()
    
    norm_text = normalize_text(text)
    
    # Find potential concepts - capitalized words and technical terms
    patterns = [
        r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,4})\b',  # Capitalized phrases
        r'\b([A-Z][a-z0-9]+(?:-[A-Z][a-z0-9]+)*)\b',  # CamelCase/Kebab-case
        r'\b(\w+(?:tion|ing|ment|ness|ity|ance|ence|er|or|ist|ian|ing)s?)\b',  # Technical terms
        r'\b(\w+_(?:config|handler|manager|factory|provider|service|controller))\b',  # Code patterns
        r'\b(API|SDK|CLI|HTTP|TCP|UDP|JSON|XML|SQL|REST|GraphQL)\b',  # Acronyms
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            if isinstance(match, tuple):
                match = match[0]
            if len(match) > 2 and match.lower() not in seen:
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
                    "description": f"Extracted from documentation",
                    "rung": 1,
                    "nars_frequency": 0.7,
                    "nars_confidence": 0.5,
                    "evidence_count": 1,
                })
    
    return concepts


def extract_relations_from_text(text: str, concepts: list[dict]) -> list[dict]:
    """Extract relations between concepts using comprehensive patterns."""
    relations = []
    concept_names = [c["name"] for c in concepts]
    
    norm_text = normalize_text(text)
    
    for pattern, verb in RELATION_PATTERNS:
        matches = re.findall(pattern, norm_text, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                subj, obj = match
            else:
                continue
            
            # Check if both are in our concepts (fuzzy match)
            subj_found = None
            obj_found = None
            
            for c in concepts:
                c_lower = c["name"].lower()
                if subj.lower() in c_lower or c_lower in subj.lower():
                    subj_found = c["name"]
                if obj.lower() in c_lower or c_lower in obj.lower():
                    obj_found = c["name"]
            
            if subj_found and obj_found and subj_found != obj_found:
                relations.append({
                    "subject": subj_found,
                    "verb": verb,
                    "object": obj_found,
                    "evidence": f"{subj_found} {verb.lower()} {obj_found}",
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
    
    # Store relations (deduplicated)
    seen_relations = set()
    for r in all_relations:
        subj_key = r["subject"].lower()
        obj_key = r["object"].lower()
        verb = r["verb"]
        
        rel_key = f"{subj_key}_{verb}_{obj_key}"
        if rel_key in seen_relations:
            continue
        seen_relations.add(rel_key)
        
        if subj_key in concept_ids and obj_key in concept_ids:
            rid = f"relates:{hashlib.sha256(rel_key.encode()).hexdigest()[:16]}"
            
            await db.query(f"""
                UPSERT {rid} SET
                    in = {concept_ids[subj_key]},
                    out = {concept_ids[obj_key]},
                    verb = '{verb}',
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
