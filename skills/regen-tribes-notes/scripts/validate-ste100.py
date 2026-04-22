#!/usr/bin/env python3
"""Validate ASD-STE100 compliance for a markdown file."""

import sys
import re

BANNED = {
    'leverage', 'utilize', 'optimize', 'holistic', 'synergy',
    'very', 'really', 'quite', 'extremely', 'incredibly', 'basically', 'simply'
}

def check_file(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    errors = []
    warnings = []
    em_dash_count = content.count('\u2014') + content.count('--')
    
    if em_dash_count > 0:
        errors.append(f"Em-dash found: {em_dash_count} occurrences")
    
    # Check frontmatter
    in_frontmatter = False
    body_started = False
    sentence_count = 0
    word_counts = []
    
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        
        if stripped == '---':
            if not body_started:
                in_frontmatter = not in_frontmatter
            continue
        
        if not in_frontmatter and not body_started and stripped.startswith('#'):
            body_started = True
            continue
        
        if body_started and stripped:
            words = stripped.split()
            word_counts.append(len(words))
            
            # Check for banned words
            lower_line = stripped.lower()
            for word in BANNED:
                if re.search(r'\b' + word + r'\b', lower_line):
                    errors.append(f"Line {i}: banned word '{word}'")
    
    if word_counts:
        avg = sum(word_counts) / len(word_counts)
        max_len = max(word_counts)
        sentence_count = len(word_counts)
        
        if max_len > 20:
            errors.append(f"Sentence > 20 words found. Max: {max_len}")
        
        print(f"Words per sentence: avg={avg:.1f}, max={max_len}, sentences={sentence_count}")
    
    if em_dash_count > 0:
        print(f"Em-dashes: {em_dash_count}")
    
    if errors:
        print("\nERRORS:")
        for e in errors:
            print(f"  {e}")
        return 1
    
    print("PASS: ASD-STE100 compliance OK")
    return 0

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: validate-ste100.py <file.md>")
        sys.exit(1)
    sys.exit(check_file(sys.argv[1]))
