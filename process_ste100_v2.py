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

# Metaphor replacements for titles
TITLE_REPLACEMENTS = {
    "ecosystem": "network",
    "organism": "system",
    "cell": "unit",
    "tissue": "group",
    "membrane": "boundary",
    "neuron": "node",
    "synapse": "connection",
    "metabolism": "operations",
    "holistic": "complete",
    "holism": "completeness",
    "synergy": "combined effect",
    "leverage": "use",
    "utilize": "use",
    "optimize": "improve",
}

# Banned words replacements for body text
BANNED_WORD_REPLACEMENTS = {
    r"\butilize\b": "use",
    r"\butilization\b": "use",
    r"\bleveraging\b": "using",
    r"\bleveraged\b": "used",
    r"\bleverage\b": "use",
    r"\boptimizing\b": "improving",
    r"\boptimized\b": "improved",
    r"\boptimize\b": "improve",
    r"\bholistic\b": "complete",
    r"\bholistically\b": "completely",
    r"\bsynergy\b": "combined effect",
    r"\bsynergies\b": "combined effects",
}

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

def process_frontmatter_and_body(content):
    """Split content into frontmatter and body, return tuple (frontmatter_dict, body, yaml_str)."""
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                yaml_str = parts[1]
                frontmatter = yaml.safe_load(yaml_str)
                body = parts[2]
                return frontmatter, body, yaml_str
            except:
                pass
    return {}, content, ""

def update_title_in_content(frontmatter, body, yaml_str):
    """Update title in frontmatter and body if it contains metaphors."""
    changes = []
    new_filename_base = None
    
    title = frontmatter.get("title", "")
    original_title = title
    
    if title:
        new_title = title
        for metaphor, replacement in TITLE_REPLACEMENTS.items():
            pattern = re.compile(r'\b' + metaphor + r'\b', re.IGNORECASE)
            if pattern.search(new_title):
                new_title = pattern.sub(replacement, new_title)
                changes.append(f"Title: '{metaphor}' -> '{replacement}'")
        
        if new_title != title:
            frontmatter["title"] = new_title
            # Rebuild yaml_str
            yaml_str = yaml.dump(frontmatter, allow_unicode=True, default_flow_style=False)
            
            # Update the markdown heading
            # First, find the heading line
            heading_pattern = re.compile(r'^#\s+.+$', re.MULTILINE)
            lines = body.split('\n')
            new_lines = []
            for line in lines:
                if line.startswith('# ') and original_title in line:
                    new_lines.append("# " + new_title + line[len("# " + original_title):])
                    changes.append(f"Heading updated")
                else:
                    new_lines.append(line)
            body = '\n'.join(new_lines)
            
            # Generate new filename
            filename_base = None
            for metaphor, replacement in TITLE_REPLACEMENTS.items():
                if filename_base is None:
                    # Build pattern to match current filename
                    pattern = re.compile(r'\b' + metaphor + r'\b', re.IGNORECASE)
                    if pattern.search(frontmatter.get("number", "")):
                        continue
                else:
                    pattern = re.compile(r'\b' + metaphor + r'\b', re.IGNORECASE)
                    filename_base = pattern.sub(replacement, filename_base)
            
            # We need to track the new filename base from the title changes
            # Actually, let's just track if any title word changed
            orig_words = set(original_title.lower().split())
            new_words = set(new_title.lower().split())
            changed_words = orig_words - new_words
            
            if changed_words:
                # Get the number prefix from frontmatter
                num = frontmatter.get("number", "")
                if num:
                    # Construct new filename base
                    new_filename_base = num + "-" + new_title.lower().replace(" ", "-").replace("---", "").replace("-", "-")
                    new_filename_base = re.sub(r'[^a-z0-9\-]', '', new_filename_base)
                    changes.append(f"Filename will change based on title")
    
    return frontmatter, body, yaml_str, changes

def replace_banned_words_in_body(body):
    """Replace banned words in body text only (not frontmatter)."""
    changes = []
    original = body
    
    for pattern_str, replacement in BANNED_WORD_REPLACEMENTS.items():
        pattern = re.compile(pattern_str, re.IGNORECASE)
        matches = pattern.findall(body)
        if matches:
            body = pattern.sub(replacement, body)
            changes.append(f"Body: '{pattern_str}' -> '{replacement}' ({len(matches)} occurrences)")
    
    return body, changes

def add_metaphor_introductions(body):
    """Add introduction sentences for metaphors in body text only."""
    changes = []
    original = body
    
    # Find the start of the actual body content (after frontmatter)
    body_start = 0
    
    for metaphor, description in METAPHORS_REQUIRING_INTRO:
        pattern = re.compile(r'\b' + metaphor + r'\b', re.IGNORECASE)
        matches = list(pattern.finditer(body))
        
        if matches:
            first_match = matches[0]
            pos = first_match.start()
            
            # Check if introduction already exists nearby (within 50 chars before)
            nearby_text = body[max(0, pos-100):pos]
            intro_pattern = re.compile(metaphor + r'\s*\(metaphor', re.IGNORECASE)
            if intro_pattern.search(nearby_text):
                continue  # Already has intro
            
            # Find the start of the sentence (go back to find period + space or start of line)
            sentence_start = pos
            for i in range(pos - 1, max(0, pos - 200), -1):
                if body[i] in '.!?\n':
                    sentence_start = i + 1
                    break
                elif body[i] == ' ' and i < pos - 1 and body[i+1].isupper():
                    sentence_start = i + 1
                    break
            
            # Make sure we're not inside a word
            while sentence_start < pos and not body[sentence_start].isalnum() and body[sentence_start] not in '\n':
                sentence_start += 1
            
            # Insert introduction
            intro = f"{metaphor.capitalize()} (metaphor for {description}): "
            body = body[:sentence_start] + intro + body[sentence_start:]
            changes.append(f"Added intro for '{metaphor}'")
    
    return body, changes

def process_file(filepath):
    """Process a single markdown file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        all_changes = []
        
        # Split into frontmatter and body
        frontmatter, body, yaml_str = process_frontmatter_and_body(content)
        
        if not yaml_str:
            # No frontmatter, just process body
            body, banned_changes = replace_banned_words_in_body(body)
            all_changes.extend(banned_changes)
            body, intro_changes = add_metaphor_introductions(body)
            all_changes.extend(intro_changes)
            
            if body != original_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(body)
            return all_changes
        
        # Phase 2: Update title if needed
        frontmatter, body, new_yaml_str, title_changes = update_title_in_content(frontmatter, body, yaml_str)
        all_changes.extend(title_changes)
        
        # Phase 3: Replace banned words in body
        body, banned_changes = replace_banned_words_in_body(body)
        all_changes.extend(banned_changes)
        
        # Phase 4: Add metaphor introductions
        body, intro_changes = add_metaphor_introductions(body)
        all_changes.extend(intro_changes)
        
        # Rebuild content
        new_content = "---\n" + new_yaml_str + "---\n" + body
        
        # Handle filename change
        new_filepath = filepath
        if title_changes and any("Filename will change" in c for c in title_changes):
            title = frontmatter.get("title", "")
            num = frontmatter.get("number", "")
            if num and title:
                # Create new filename
                new_title_slug = re.sub(r'[^a-z0-9\-]', '', title.lower().replace(" ", "-").replace("---", "-"))
                new_filename = f"{num}-{new_title_slug}.md"
                new_filepath = filepath.parent / new_filename
                all_changes.append(f"Filename: '{filepath.name}' -> '{new_filename}'")
        
        # Write changes
        if new_content != original_content or new_filepath != filepath:
            with open(new_filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            # Remove old file if renamed
            if new_filepath != filepath and filepath.exists():
                os.remove(filepath)
        
        return all_changes
    except Exception as e:
        return [f"ERROR processing {filepath}: {str(e)}"]

def main():
    """Main processing function."""
    log = []
    log.append("=" * 60)
    log.append("ASD-STE100 Title Cleanup and Format Revision")
    log.append("=" * 60)
    
    # Find all markdown files
    md_files = list(REPO_PATH.glob("*.md"))
    log.append(f"\nFound {len(md_files)} markdown files")
    
    # Process each file
    total_changes = []
    files_changed = 0
    renamed_files = []
    
    for i, filepath in enumerate(sorted(md_files), 1):
        changes = process_file(filepath)
        if changes:
            files_changed += 1
            total_changes.append(f"\n--- {filepath.name} ---")
            total_changes.extend(changes)
            
            # Track renames
            for c in changes:
                if c.startswith("Filename:"):
                    renamed_files.append(c)
    
    log.append(f"\nFiles with changes: {files_changed}/{len(md_files)}")
    
    if renamed_files:
        log.append("\n=== FILENAME CHANGES ===")
        for r in renamed_files:
            log.append(r)
    
    log.extend(total_changes)
    
    # Write log
    log_path = REPO_PATH / "ste100_revision_log.txt"
    with open(log_path, 'w') as f:
        f.write("\n".join(log))
    
    print("\n".join(log[:200]))  # Print first 200 lines
    print(f"\n... (full log written to {log_path})")
    print(f"\nRenamed files: {len(renamed_files)}")

if __name__ == "__main__":
    main()
