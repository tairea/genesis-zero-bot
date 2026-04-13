#!/usr/bin/env python3
"""Extract Project Glasswing document via Kreuzberg."""

import urllib.request
import tempfile
import os
from kreuzberg import extract_file_sync, ExtractionConfig

url = "https://www.anthropic.com/glasswing"
output_format = "markdown"

config = ExtractionConfig(output_format=output_format)

# Download to temp file
with tempfile.NamedTemporaryFile(mode='wb', suffix='.html', delete=False) as f:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        f.write(resp.read())
    temp_path = f.name

try:
    result = extract_file_sync(temp_path, config=config)
    print("=== CONTENT ===")
    print(result.content)
    print("\n=== METADATA ===")
    for k, v in (result.metadata or {}).items():
        print(f"  {k}: {v}")
    print(f"\n=== LANGUAGES ===")
    print(result.detected_languages)
    print(f"\n=== TABLES ===")
    for i, t in enumerate(result.tables or []):
        print(f"  Table {i}: {t}")
    print(f"\n=== KEYWORDS ===")
    print(result.keywords)
    print(f"\n=== CHUNKS (first 3) ===")
    for i, c in enumerate((result.chunks or [])[:3]):
        print(f"  Chunk {i}: {c[:200]}...")
finally:
    os.unlink(temp_path)
