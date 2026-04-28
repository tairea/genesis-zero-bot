#!/usr/bin/env python3
"""Find which document chapters contain a search term."""
import sys, os, re

SECF_DIR = "/home/ian/.openclaw/workspace-genesis/ingested-docs/secf-chapters"
GRCSE_DIR = "/home/ian/.openclaw/workspace-genesis/ingested-docs/grcse-chapters"
NASA_DIR = "/home/ian/.openclaw/workspace-genesis/ingested-docs/nasa-se-handbook-chapters"

def main():
    if len(sys.argv) < 2:
        print("Usage: find_topic.py <search_term>")
        sys.exit(1)

    query = sys.argv[1].lower()
    results = []

    for doc, basedir in [("SECF", SECF_DIR), ("GRCSE", GRCSE_DIR), ("NASA", NASA_DIR)]:
        if not os.path.exists(basedir):
            continue
        for fname in sorted(os.listdir(basedir)):
            if not fname.endswith('.md'):
                continue
            fpath = os.path.join(basedir, fname)
            try:
                with open(fpath, 'r', errors='ignore') as f:
                    content = f.read()
            except:
                continue
            
            search_text = (fname + content[:5000]).lower()
            if query in search_text:
                count = content.lower().count(query)
                results.append((doc, fname, count))

    results.sort(key=lambda x: (x[0], x[1]))
    for doc, fname, count in results:
        title = fname.replace('.md', '').replace('_', ' ')
        print(f"[{doc}] {fname}: {title} ({count} matches)")

if __name__ == "__main__":
    main()
