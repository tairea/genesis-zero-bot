#!/bin/bash
# Rebuild README index from document numbers

REPO="$HOME/.radicle/regen-tribes-notes"
cd "$REPO" || exit 1

# Collect all .md files except README and INTRODUCTION
docs=$(find . -name "*.md" -not -name "README.md" -not -name "INTRODUCTION.md" | \
       grep -v ".git" | sort)

# Extract number and title from frontmatter
python3 << 'PYEOF'
import os
import re
import sys

docs_raw = """DOCLIST""".strip().split('\n')

entries = []
for line in docs_raw:
    path = line.strip()
    if not path or not os.path.exists(path):
        continue
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Extract from frontmatter
        title = re.search(r'^title:\s*(.+)$', content, re.MULTILINE)
        number = re.search(r'^number:\s*(.+)$', content, re.MULTILINE)
        level = re.search(r'^level:\s*(.+)$', content, re.MULTILINE)
        domain = re.search(r'^domain:\s*(.+)$', content, re.MULTILINE)
        
        if title and number:
            entries.append({
                'number': int(number.group(1)),
                'title': title.group(1).strip(),
                'level': level.group(1).strip() if level else '?',
                'domain': domain.group(1).strip() if domain else '?',
                'path': os.path.basename(path)
            })
    except Exception as e:
        pass

entries.sort(key=lambda x: x['number'])

with open('README.md', 'w') as f:
    f.write("""# Regen Tribe Notes — Knowledge Base

## Repository ID
```
rad:z4WAr7CiNkf5JAoAb1srwi7gDz8nU/z6MkhgHUCtE8dW8S89wziVgThbCUDuK5f3A2qdbfiSXDP4Ye
```

## Web UI
https://app.radicle.xyz/nodes/iris.radicle.xyz/rad:z4WAr7CiNkf5JAoAb1srwi7gDz8nU

## The Book Structure

The knowledge base is a book. Numbers are fixed.

Five levels:

```
000  ROOT     Entry point. Defines the whole system.
001-009  Cell   One person. One home. One skill.
010-019  Tissue  Small groups. Trust. Roles.
020-029  Organ   Neighborhoods. Shared infrastructure.
030-039  System  Bioregions. Federation. Trade.
040-049  Body    Planetary. Knowledge commons.
```

Four domains at every level:

```
A  Physical   What you build. Cost. Method. Material.
B  Social     Who does what. How decisions get made.
C  Information  What you know. How you know it.
D  Exchange   Value. Currency. Trade without extraction.
```

## Documents

| N | Level | Domain | Title | File |
|---|-------|--------|-------|------|
""")
    for e in entries:
        f.write(f"| {e['number']:03d} | {e['level']} | {e['domain']} | {e['title']} | `{e['path']}` |\n")
    
    f.write("""
## License

CC0 / Public Domain.

Build with, not for. Open everything. Publish always.
""")

print(f"Wrote {len(entries)} entries to README.md")
PYEOF
