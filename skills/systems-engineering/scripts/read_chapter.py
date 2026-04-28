#!/usr/bin/env python3
"""Read a specific chapter from the SE knowledge base."""
import sys, os, re

SECF_DIR = "/home/ian/.openclaw/workspace-genesis/ingested-docs/secf-chapters"
GRCSE_DIR = "/home/ian/.openclaw/workspace-genesis/ingested-docs/grcse-chapters"
NASA_DIR = "/home/ian/.openclaw/workspace-genesis/ingested-docs/nasa-se-handbook-chapters"

def main():
    if len(sys.argv) < 3:
        print("Usage: read_chapter.py <doc> <topic>")
        print("  doc: SECF | GRCSE | NASA")
        print("  topic: chapter name (partial match, case-insensitive)")
        print("\nExamples:")
        print("  read_chapter.py SECF Systems_Thinking")
        print("  read_chapter.py NASA Verification")
        print("  read_chapter.py GRCSE Introduction")
        sys.exit(1)

    doc = sys.argv[1].upper()
    topic = sys.argv[2].lower()

    doc_dirs = {
        "SECF": SECF_DIR,
        "GRCSE": GRCSE_DIR,
        "NASA": NASA_DIR
    }

    basedir = doc_dirs.get(doc)
    if not basedir or not os.path.exists(basedir):
        print(f"Unknown doc: {doc}")
        sys.exit(1)

    # Find matching file (try exact match first, then partial)
    for fname in sorted(os.listdir(basedir)):
        if not fname.endswith('.md'):
            continue
        base = fname.replace('.md', '').lower()
        if base == topic.lower().replace(' ', '_') or topic.lower() in base:
            path = os.path.join(basedir, fname)
            with open(path, 'r', errors='ignore') as f:
                content = f.read()
            # Print header line + first 2000 chars
            lines = content.split('\n')
            header = lines[0] if lines else ''
            body = '\n'.join(lines[1:min(100, len(lines))])
            print(f"# {fname}\n")
            print(body[:2000])
            print(f"\n[... {len(content)} total chars in this chapter ...]")
            return

    print(f"No chapter found matching '{topic}' in {doc}")
    print("\nAvailable chapters in {doc}:")
    for fname in sorted(os.listdir(basedir)):
        if fname.endswith('.md'):
            print(f"  {fname.replace('.md','').replace('_',' ')}")

if __name__ == "__main__":
    main()
