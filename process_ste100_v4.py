#!/usr/bin/env python3
"""
ASD-STE100 Title Cleanup and Format Revision Script
Processes all markdown files in the regen-tribes-notes repository.
"""

import os
import re
import yaml
from pathlib import Path

REPO_PATH = Path(os.path.expanduser("~/.radicle/regen-tribes-notes"))

# Metaphor replacements for titles (in order of specificity)
TITLE_REPLACEMENTS = [
    (r'\bcell\b', 'unit'),
    (r'\btissue\b', 'group'),
    (r'\becosystem\b', 'network'),
    (r'\borganism\b', 'system'),
    (r'\bmembrane\b', 'boundary'),
    (r'\bneuron\b', 'node'),
    (r'\bsynapse\b', 'connection'),
    (r'\bmetabolism\b', 'operations'),
    (r'\bholistic\b', 'complete'),
    (r'\bholism\b', 'completeness'),
    (r'\bsynergy\b', 'combined effect'),
    (r'\bleverage\b', 'use'),
    (r'\butilize\b', 'use'),
    (r'\boptimize\b', 'improve'),
]

# Banned words replacements for body text
BANNED_WORD_REPLACEMENTS = [
    (r'\butilize\b', 'use'),
    (r'\butilization\b', 'use'),
    (r'\bleveraging\b', 'using'),
    (r'\bleveraged\b', 'used'),
    (r'\bleverage\b', 'use'),
    (r'\boptimizing\b', 'improving'),
    (r'\boptimized\b', 'improved'),
    (r'\boptimize\b', 'improve'),
    (r'\bholistic\b', 'complete'),
    (r'\bholistically\b', 'completely'),
    (r'\bsynergy\b', 'combined effect'),
    (r'\bsynergies\b', 'combined effects'),
]

# Metaphors that need introduction sentences in body text
METAPHORS_REQUIRING_INTRO = [
    ("ecosystem", "system or network"),
    ("organism", "self-sustaining collective"),
    ("cell", "basic unit or module"),
    ("tissue", "connected group or network"),
    ("membrane", "boundary or interface"),
    ("neuron", "node or processing unit"),
    ("synapse", "connection or link"),
    ("metabolism", "operations or processes"),
]

def parse_file(filepath):
    """Parse a markdown file and return (frontmatter_dict, body_str, original_yaml_str)."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            yaml_str = parts[1]
            body = parts[2]
            try:
                frontmatter = yaml.safe_load(yaml_str)
                if isinstance(frontmatter, dict):
                    return frontmatter, body, yaml_str
            except:
                pass
    return {}, content, ""

def extract_number_from_yaml(yaml_str):
    """Extract the number field from the raw YAML string to preserve formatting."""
    if not yaml_str:
        return None
    match = re.search(r'^number:\s*(.+)$', yaml_str, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return None

def update_title(frontmatter, body, yaml_str):
    """Update title if it contains metaphors. Returns (new_frontmatter, new_body, changes, new_filename)."""
    changes = []
    new_filename = None
    
    title = frontmatter.get("title", "")
    if not title:
        return frontmatter, body, changes, new_filename
    
    new_title = title
    for pattern_str, replacement in TITLE_REPLACEMENTS:
        pattern = re.compile(pattern_str, re.IGNORECASE)
        if pattern.search(new_title):
            new_title = pattern.sub(replacement, new_title)
            changes.append(f"Title: '{pattern_str}' -> '{replacement}'")
    
    if new_title != title:
        frontmatter["title"] = new_title
        
        # Update markdown heading
        lines = body.split('\n')
        new_lines = []
        for line in lines:
            if line.startswith('# ') and title in line:
                new_line = "# " + new_title + line[len("# " + title):]
                new_lines.append(new_line)
                changes.append("Heading updated")
            else:
                new_lines.append(line)
        body = '\n'.join(new_lines)
        
        # Generate new filename - preserve original number format from YAML
        num_str = extract_number_from_yaml(yaml_str)
        if num_str:
            # Clean up the number string (remove quotes if present)
            num_str = num_str.strip('"\'')
            # Normalize to 3-digit format
            try:
                num_int = int(num_str)
                num_str = str(num_int).zfill(3)
            except:
                pass
            
            slug = re.sub(r'[^a-z0-9\-]', '', new_title.lower().replace(" ", "-"))
            slug = re.sub(r'-+', '-', slug).strip('-')
            new_filename = f"{num_str}-{slug}.md"
            changes.append(f"Filename: {new_filename}")
    
    return frontmatter, body, changes, new_filename

def replace_banned_words(body):
    """Replace banned words in body text."""
    changes = []
    for pattern_str, replacement in BANNED_WORD_REPLACEMENTS:
        pattern = re.compile(pattern_str, re.IGNORECASE)
        matches = pattern.findall(body)
        if matches:
            body = pattern.sub(replacement, body)
            changes.append(f"Body: '{pattern_str}' -> '{replacement}' ({len(matches)}x)")
    return body, changes

def add_metaphor_intros(body):
    """Add introduction sentences for metaphors in body text."""
    changes = []
    
    for metaphor, description in METAPHORS_REQUIRING_INTRO:
        pattern = re.compile(r'\b' + metaphor + r'\b', re.IGNORECASE)
        
        # Find all occurrences
        matches = list(pattern.finditer(body))
        if not matches:
            continue
        
        first_pos = matches[0].start()
        
        # Check if intro already exists before first occurrence
        context_start = max(0, first_pos - 150)
        context = body[context_start:first_pos]
        
        intro_pattern = re.compile(metaphor + r'\s*\(metaphor', re.IGNORECASE)
        if intro_pattern.search(context):
            continue  # Already has intro
        
        # Find sentence start before first occurrence
        sentence_start = first_pos
        for i in range(first_pos - 1, max(0, first_pos - 200), -1):
            c = body[i]
            if c in '.!?\n':
                sentence_start = i + 1
                # Skip whitespace
                while sentence_start < first_pos and body[sentence_start] in ' \t':
                    sentence_start += 1
                break
            elif c == ' ' and i + 1 < first_pos and body[i + 1].isupper():
                sentence_start = i + 1
                break
        
        # Insert introduction
        intro = f"{metaphor.capitalize()} (metaphor for {description}): "
        body = body[:sentence_start] + intro + body[sentence_start:]
        changes.append(f"Added intro for '{metaphor}'")
    
    return body, changes

def process_file(filepath):
    """Process a single markdown file."""
    try:
        frontmatter, body, yaml_str = parse_file(filepath)
        if not frontmatter:  # No frontmatter, just process body
            body, banned_changes = replace_banned_words(body)
            body, intro_changes = add_metaphor_intros(body)
            if banned_changes or intro_changes:
                with open(filepath, 'w') as f:
                    f.write(body)
            return banned_changes + intro_changes
        
        # Update title
        frontmatter, body, title_changes, new_filename = update_title(frontmatter, body, yaml_str)
        
        # Replace banned words
        body, banned_changes = replace_banned_words(body)
        
        # Add metaphor introductions
        body, intro_changes = add_metaphor_intros(body)
        
        all_changes = title_changes + banned_changes + intro_changes
        
        if all_changes:
            # Rebuild YAML string
            yaml_out = yaml.dump(frontmatter, allow_unicode=True, default_flow_style=False)
            new_content = "---\n" + yaml_out + "---\n" + body
            
            if new_filename:
                new_path = filepath.parent / new_filename
                with open(new_path, 'w') as f:
                    f.write(new_content)
                if filepath.exists():
                    os.remove(filepath)
                all_changes.append(f"Renamed file to {new_filename}")
            else:
                with open(filepath, 'w') as f:
                    f.write(new_content)
        
        return all_changes
    except Exception as e:
        return [f"ERROR: {str(e)}"]

def main():
    """Main processing function."""
    log = ["=" * 60, "ASD-STE100 Title Cleanup and Format Revision", "=" * 60]
    
    md_files = list(REPO_PATH.glob("*.md"))
    log.append(f"\nFound {len(md_files)} markdown files")
    
    total_changes = []
    files_changed = 0
    renamed_files = []
    
    for filepath in sorted(md_files):
        changes = process_file(filepath)
        if changes:
            files_changed += 1
            total_changes.append(f"\n--- {filepath.name} ---")
            total_changes.extend(changes)
            for c in changes:
                if c.startswith("Renamed file") or "Filename:" in c:
                    renamed_files.append(c)
    
    log.append(f"\nFiles with changes: {files_changed}/{len(md_files)}")
    
    if renamed_files:
        log.append("\n=== FILENAME CHANGES ===")
        for r in renamed_files:
            log.append(r)
    
    log.extend(total_changes)
    
    log_path = REPO_PATH / "ste100_revision_log.txt"
    with open(log_path, 'w') as f:
        f.write("\n".join(log))
    
    # Print summary
    print(f"Processed {len(md_files)} files, {files_changed} changed")
    print(f"Renamed files: {len(renamed_files)}")
    print(f"Log written to: {log_path}")

if __name__ == "__main__":
    main()
