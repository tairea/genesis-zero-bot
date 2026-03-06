#!/usr/bin/env python3
"""XTRACT: Document to Graph extraction."""

import argparse
import asyncio
import hashlib
import math
import os
import re
from pathlib import Path

# NSM primitives
NSM_KEYWORDS = {
    "FEEL": ["feel", "sense", "experience", "emotion", "heart", "aware", "感受", "感觉"],
    "THINK": ["think", "thought", "consider", "ponder", "reflect", "believe", "思考", "认为"],
    "KNOW": ["know", "knowledge", "understand", "realize", "recognize", "知道", "了解"],
    "WANT": ["want", "desire", "wish", "yearn", "need", "strive", "seek", "想要", "需要"],
    "SEE": ["see", "observe", "perceive", "notice", "witness", "看到", "观察"],
    "DO": ["do", "act", "perform", "execute", "create", "make", "run", "build", "做", "执行"],
    "HAPPEN": ["happen", "occur", "arise", "emerge", "become", "unfold", "发生", "出现"],
    "SAY": ["say", "speak", "express", "communicate", "define", "describe", "说", "表达"],
    "GOOD": ["good", "correct", "valid", "safe", "efficient", "clean", "fast", "好", "正确"],
    "BAD": ["bad", "wrong", "broken", "unsafe", "slow", "buggy", "error", "坏", "错误"],
    "EXIST": ["exist", "be", "being", "presence", "there is", "instance", "存在", "是"],
    "SELF": ["self", "own", "itself", "internal", "its", "自己", "本身"],
    "OTHER": ["other", "external", "third-party", "caller", "user", "client", "其他", "别人"],
    "BECAUSE": ["because", "reason", "cause", "therefore", "since", "thus", "因为", "所以"],
    "IF": ["if", "when", "unless", "condition", "conditional", "guard", "如果", "假如"],
    "CAN": ["can", "could", "able", "possible", "capable", "allows", "supports", "可以", "能"],
    "MAYBE": ["maybe", "perhaps", "might", "uncertain", "optional", "todo", "可能", "也许"],
    "AFTER": ["after", "then", "next", "later", "subsequently", "following", "之后", "然后"],
    "BEFORE": ["before", "prior", "earlier", "first", "initially", "previously", "之前", "首先"],
    "NOT": ["not", "no", "never", "without", "lack", "missing", "absent", "不", "没有"],
}

# Qualia dimensions
QUALIA_KEYWORDS = {
    "valence": ["good", "bad", "happy", "sad", "love", "hate", "positive", "negative", "好", "坏"],
    "arousal": ["excited", "calm", "intense", "relaxed", "energetic", "tired", "激动", "平静"],
    "intimacy": ["close", "distant", "personal", "private", "intimate", "shared", "亲密", "私人"],
    "certainty": ["sure", "maybe", "certain", "doubt", "definite", "possible", "确定", "可能"],
    "agency": ["choose", "free", "forced", "decide", "will", "control", "选择", "控制"],
    "emergence": ["emerge", "surprise", "novel", "predict", "pattern", "emergent", "涌现", "新颖"],
    "continuity": ["always", "sometimes", "rarely", "constant", "change", "continuous", "持续", "连续"],
    "abstraction": ["idea", "concrete", "abstract", "specific", "general", "concept", "抽象", "具体"],
}

# 144 verbs
# Stopwords to filter
STOPWORDS = {"the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could", "should",
    "may", "might", "must", "shall", "can", "need", "this", "that", "these", "those",
    "i", "you", "he", "she", "it", "we", "they", "what", "which", "who", "whom",
    "when", "where", "why", "how", "all", "each", "every", "both", "few", "more",
    "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same",
    "so", "than", "too", "very", "just", "for", "and", "but", "or", "if", "then",
    "because", "as", "until", "while", "of", "at", "by", "with", "about", "against",
    "between", "into", "through", "during", "before", "after", "above", "below",
    "to", "from", "up", "down", "in", "out", "on", "off", "over", "under"}

VERBS = {
    # Structural
    "IS_A": "Structural", "HAS_A": "Structural", "PART_OF": "Structural", "CONTAINS": "Structural",
    "INSTANCE_OF": "Structural", "SUBCLASS_OF": "Structural", "RELATED_TO": "Structural", "ADJACENT_TO": "Structural",
    "LOCATED_IN": "Structural", "CONNECTED_TO": "Structural", "DERIVED_FROM": "Structural", "COMPOSED_OF": "Structural",
    "DEPENDS_ON": "Structural", "IMPLIES": "Structural", "CONTRADICTS": "Structural", "SUPPORTS": "Structural",
    "EXEMPLIFIES": "Structural", "DEFINES": "Structural", "CLASSIFIES": "Structural", "DESCRIBES": "Structural",
    "ATTRIBUTES": "Structural", "MEASURES": "Structural", "COUNTS": "Structural", "BOUNDS": "Structural",
    # Causal
    "CAUSES": "Causal", "ENABLES": "Causal", "PREVENTS": "Causal", "TRIGGERS": "Causal",
    "BLOCKS": "Causal", "AMPLIFIES": "Causal", "REDUCES": "Causal", "TRANSFORMS": "Causal",
    "PRODUCES": "Causal", "REQUIRES": "Causal", "ALLOWS": "Causal", "INHIBITS": "Causal",
    "ACCELERATES": "Causal", "DELAYS": "Causal", "INITIATES": "Causal", "TERMINATES": "Causal",
    "MAINTAINS": "Causal", "DISRUPTS": "Causal", "REGULATES": "Causal", "MEDIATES": "Causal",
    "MODULATES": "Causal", "FACILITATES": "Causal", "SUPPRESSES": "Causal", "INDUCES": "Causal",
    # Temporal
    "BEFORE": "Temporal", "AFTER": "Temporal", "DURING": "Temporal", "MEETS": "Temporal",
    "OVERLAPS": "Temporal", "STARTS": "Temporal", "FINISHES": "Temporal", "EQUALS_TIME": "Temporal",
    "PRECEDES": "Temporal", "FOLLOWS": "Temporal", "SIMULTANEOUS": "Temporal", "CONTINUOUS": "Temporal",
    "PERIODIC": "Temporal", "CYCLICAL": "Temporal", "SEQUENTIAL": "Temporal", "CONCURRENT": "Temporal",
    "IMMEDIATE": "Temporal", "EVENTUAL": "Temporal", "GRADUAL": "Temporal", "SUDDEN": "Temporal",
    "PERSISTENT": "Temporal", "TRANSIENT": "Temporal", "RECURRING": "Temporal", "DEPRECATED": "Temporal",
    # Epistemic
    "KNOWS": "Epistemic", "BELIEVES": "Epistemic", "INFERS": "Epistemic", "EXPECTS": "Epistemic",
    "ASSUMES": "Epistemic", "HYPOTHESIZES": "Epistemic", "DOUBTS": "Epistemic", "CONFIRMS": "Epistemic",
    "DENIES": "Epistemic", "QUESTIONS": "Epistemic", "UNDERSTANDS": "Epistemic", "REMEMBERS": "Epistemic",
    "PREDICTS": "Epistemic", "LEARNS": "Epistemic", "DISCOVERS": "Epistemic", "REALIZES": "Epistemic",
    "PERCEIVES": "Epistemic", "RECOGNIZES": "Epistemic", "INTERPRETS": "Epistemic", "EVALUATES": "Epistemic",
    "ANALYZES": "Epistemic", "SYNTHESIZES": "Epistemic", "CONCLUDES": "Epistemic", "JUSTIFIES": "Epistemic",
    # Agentive
    "DOES": "Agentive", "WANTS": "Agentive", "DECIDES": "Agentive", "TRIES": "Agentive",
    "ACHIEVES": "Agentive", "FAILS": "Agentive", "PLANS": "Agentive", "EXECUTES": "Agentive",
    "MONITORS": "Agentive", "ADAPTS": "Agentive", "CREATES": "Agentive", "DESTROYS": "Agentive",
    "MODIFIES": "Agentive", "ACQUIRES": "Agentive", "RELEASES": "Agentive", "COMMUNICATES": "Agentive",
    "COORDINATES": "Agentive", "DELEGATES": "Agentive", "CONTROLS": "Agentive", "OBSERVES": "Agentive",
    "INTERVENES": "Agentive", "RESPONDS": "Agentive", "INITIATES_ACTION": "Agentive", "TERMINATES_ACTION": "Agentive",
    # Experiential
    "FEELS": "Experiential", "SEES": "Experiential", "ENJOYS": "Experiential", "FEARS": "Experiential",
    "EXPERIENCES": "Experiential", "SUFFERS": "Experiential", "DESIRES": "Experiential", "APPRECIATES": "Experiential",
    "DISLIKES": "Experiential", "WONDERS": "Experiential", "IMAGINES": "Experiential", "DREAMS": "Experiential",
    "HOPES": "Experiential", "REGRETS": "Experiential", "CELEBRATES": "Experiential", "MOURNS": "Experiential",
    "REFLECTS": "Experiential", "CONTEMPLATES": "Experiential", "RESONATES": "Experiential", "YEARNS": "Experiential",
    "EMBRACES": "Experiential", "REJECTS": "Experiential", "SEEKS": "Experiential", "AVOIDS": "Experiential",
}

# DB config
DB_URL = os.environ.get("SURREAL_URL", "ws://127.0.0.1:8000")
DB_USER = os.environ.get("SURREAL_USER", "root")
DB_PASS = os.environ.get("SURREAL_PASS", "root")
DB_NS = "xtract_graph"
DB_NAME = "main"


def nsm_fingerprint(text: str) -> str:
    """Compute NSM fingerprint as string."""
    text_lower = text.lower()
    weights = []
    for primitive, keywords in NSM_KEYWORDS.items():
        hits = sum(1 for kw in keywords if kw in text_lower)
        weights.append(f"{primitive}:{min(1.0, hits * 0.12):.2f}")
    return "|".join(weights)


def qualia_fingerprint(text: str) -> str:
    """Compute Qualia fingerprint as string."""
    text_lower = text.lower()
    coords = []
    for dim, keywords in QUALIA_KEYWORDS.items():
        hits = sum(1 for kw in keywords if kw in text_lower)
        coords.append(f"{dim}:{min(1.0, hits * 0.18):.2f}")
    return "|".join(coords)


def causality_fingerprint(text: str) -> str:
    """Compute Causality fingerprint as string."""
    text_lower = text.lower()
    past_kw = ["was", "before", "after", "previous", "earlier", "ago"]
    pres_kw = ["is", "now", "current", "present", "today"]
    fut_kw = ["will", "shall", "future", "next", "later", "soon"]
    
    past = sum(1 for kw in past_kw if kw in text_lower)
    pres = sum(1 for kw in pres_kw if kw in text_lower)
    fut = sum(1 for kw in fut_kw if kw in text_lower)
    total = past + pres + fut or 1
    
    return f"past:{past/total:.2f}|present:{pres/total:.2f}|future:{fut/total:.2f}|agency:0.50"


def chunk_text(text: str, max_size: int = 800) -> list[dict]:
    """Split text into chunks."""
    # Split on paragraph boundaries
    paragraphs = re.split(r'\n\s*\n', text)
    chunks = []
    current = ""
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if len(current) + len(para) < max_size:
            current += " " + para if current else para
        else:
            if current:
                chunks.append({"text": current})
            current = para
    
    if current:
        chunks.append({"text": current})
    
    return chunks


def extract_concepts(chunks: list[dict]) -> list[dict]:
    """Extract concepts from chunks."""
    concepts = []
    seen = set()
    
    # Patterns for entity extraction
    patterns = [
        r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',  # Capitalized
        r'\b(\w+(?:tion|ment|ness|ity|ance|ence|er|or)s?)\b',  # Technical
        r'\b(\w+(?:API|SDK|CLI|HTTP|JSON|XML|SQL)\b)',  # Acronyms
    ]
    
    for chunk in chunks:
        text = chunk.get("text", "")
        nsm = nsm_fingerprint(text)
        qualia = qualia_fingerprint(text)
        causality = causality_fingerprint(text)
        fp_input = str(nsm) + str(qualia) + str(causality)
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for m in matches:
                if len(m) < 3 or m.lower() in seen:
                    continue
                seen.add(m.lower())
                
                # Determine type
                ctype = "entity"
                m_lower = m.lower()
                if any(k in m_lower for k in ["system", "platform", "framework"]):
                    ctype = "system"
                elif any(k in m_lower for k in ["process", "method", "workflow", "pipeline"]):
                    ctype = "process"
                elif any(k in m_lower for k in ["idea", "concept", "principle", "value"]):
                    ctype = "idea"
                
                concepts.append({
                    "name": m,
                    "type": ctype,
                    "nsm": nsm,
                    "qualia": qualia,
                    "causality": causality,
                    "fingerprint": hashlib.sha256(fp_input.encode()).hexdigest()[:16],
                })
    
    return concepts


def extract_relations(chunks: list[dict], concepts: list[dict]) -> list[dict]:
    """Extract relations using verb patterns."""
    relations = []
    concept_names = {c["name"].lower(): c["name"] for c in concepts}
    
    # Patterns for relation extraction
    rel_patterns = [
        (r"(\w+)\s+is\s+a\s+(\w+)", "IS_A"),
        (r"(\w+)\s+has\s+(\w+)", "HAS_A"),
        (r"(\w+)\s+contains\s+(\w+)", "CONTAINS"),
        (r"(\w+)\s+depends\s+on\s+(\w+)", "DEPENDS_ON"),
        (r"(\w+)\s+uses\s+(\w+)", "USES"),
        (r"(\w+)\s+provides\s+(\w+)", "PROVIDES"),
        (r"(\w+)\s+requires\s+(\w+)", "REQUIRES"),
        (r"(\w+)\s+relates\s+to\s+(\w+)", "RELATED_TO"),
        (r"(\w+)\s+connects\s+to\s+(\w+)", "CONNECTED_TO"),
        (r"(\w+)\s+enables\s+(\w+)", "ENABLES"),
        (r"(\w+)\s+creates\s+(\w+)", "CREATES"),
        (r"(\w+)\s+manages\s+(\w+)", "MANAGES"),
    ]
    
    for chunk in chunks:
        text = chunk.get("text", "").lower()
        
        for pattern, verb in rel_patterns:
            matches = re.findall(pattern, text)
            for subj, obj in matches:
                if subj in concept_names and obj in concept_names:
                    relations.append({
                        "subject": concept_names[subj],
                        "verb": verb,
                        "object": concept_names[obj],
                        "category": VERBS.get(verb, "Structural"),
                    })
    
    return relations


async def ensure_schema(db):
    """Apply schema."""
    schema = """
    DEFINE TABLE IF NOT EXISTS document SCHEMALESS;
    DEFINE TABLE IF NOT EXISTS concept SCHEMALESS;
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
    """Ingest single file."""
    path = Path(filepath)
    if not path.exists():
        return None
    
    text = path.read_text(encoding="utf-8", errors="ignore")
    if not text.strip():
        return None
    
    # Document ID
    doc_id = f"document:{hashlib.sha256(str(path).encode()).hexdigest()[:16]}"
    await db.query(f"""
        UPSERT {doc_id} SET source = '{path}', title = '{path.name}', created_at = time::now()
    """)
    
    # Chunk
    chunks = chunk_text(text)
    
    # Extract
    concepts = extract_concepts(chunks)
    relations = extract_relations(chunks, concepts)
    
    # Store concepts
    concept_ids = {}
    for c in concepts:
        cid = f"concept:{hashlib.sha256(c['name'].lower().encode()).hexdigest()[:16]}"
        concept_ids[c['name'].lower()] = cid
        
        await db.query(f"""
            UPSERT {cid} SET 
                name = '{c["name"]}',
                type = '{c["type"]}',
                fingerprint = '{c.get("fingerprint", "")}',
                nars_frequency = 0.7,
                nars_confidence = 0.5,
                evidence_count = 1,
                first_seen_in = {doc_id}
        """)
    
    # Store relations
    seen_rels = set()
    for r in relations:
        key = f"{r['subject'].lower()}_{r['verb']}_{r['object'].lower()}"
        if key in seen_rels:
            continue
        seen_rels.add(key)
        
        subj = concept_ids.get(r["subject"].lower())
        obj = concept_ids.get(r["object"].lower())
        
        if subj and obj:
            rid = f"relates:{hashlib.sha256(key.encode()).hexdigest()[:16]}"
            await db.query(f"""
                UPSERT {rid} SET
                    in = {subj},
                    out = {obj},
                    verb = '{r["verb"]}',
                    category = '{r.get("category", "Structural")}',
                    nars_frequency = 0.7,
                    nars_confidence = 0.5,
                    source_doc = {doc_id}
            """)
    
    return doc_id


async def clear_db(db):
    """Clear all data."""
    await db.query("DELETE relates;")
    await db.query("DELETE concept;")
    await db.query("DELETE document;")
    print("Database cleared.")


async def main():
    import sys
    from surrealdb import AsyncSurreal
    
    parser = argparse.ArgumentParser(description="XTRACT: Document to Graph")
    parser.add_argument("--input", "-i", help="Input file")
    parser.add_argument("--dir", "-d", help="Input directory")
    parser.add_argument("--clear", action="store_true", help="Clear database first")
    parser.add_argument("--ns", default=DB_NS, help="Namespace")
    args = parser.parse_args()
    
    # Connect
    db = AsyncSurreal(url=DB_URL)
    await db.connect()
    await db.signin({"username": DB_USER, "password": DB_PASS})
    await db.use(args.ns, DB_NAME)
    
    print(f"Connected to {DB_URL}/{args.ns}/{DB_NAME}")
    
    # Schema
    await ensure_schema(db)
    
    # Clear if requested
    if args.clear:
        await clear_db(db)
    
    # Find files
    files = []
    if args.input:
        files = [Path(args.input)]
    elif args.dir:
        for p in Path(args.dir).glob("**/*"):
            if p.suffix in [".md", ".txt", ".py", ".js", ".yaml", ".yml"]:
                files.append(p)
    
    if not files:
        print("No files found.")
        await db.close()
        return
    
    print(f"Processing {len(files)} files...")
    
    # Ingest
    for f in files:
        try:
            doc_id = await ingest_file(db, str(f))
            if doc_id:
                print(f"✓ {f.name}")
        except Exception as e:
            print(f"✗ {f.name}: {e}")
    
    # Stats
    result = await db.query("SELECT count() as cnt FROM concept")
    concepts = result[0].get("cnt", 0) if result else 0
    
    result = await db.query("SELECT count() as cnt FROM relates")
    relations = result[0].get("cnt", 0) if result else 0
    
    print(f"\n=== Done ===")
    print(f"Concepts: {concepts}")
    print(f"Relations: {relations}")
    print(f"Namespace: {args.ns}")
    
    await db.close()


if __name__ == "__main__":
    asyncio.run(main())
