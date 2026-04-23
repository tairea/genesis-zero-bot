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
    "utilize": "use",
    "utilization": "use",
    "leveraging": "using",
    "leveraged": "used",
    "leverage": "use",
    "optimizing": "improving",
    "optimized": "improved",
    "optimize": "improve",
    "holistic": "complete",
    "holistically": "completely",
    "synergy": "combined effect",
    "synergies": "combined effects",
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

def extract_frontmatter(content):
    """Extract YAML frontmatter from markdown content."""
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                frontmatter = yaml.safe_load(parts[1])
                body = parts[2]
                return frontmatter, body
            except:
                pass
    return {}, content

def update_frontmatter_title(frontmatter, body, filepath):
    """Update title in frontmatter and body if it contains metaphors."""
    changes = []
    new_filepath = filepath
    
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
            # Update the markdown heading if it matches the title
            heading_pattern = re.compile(r'^#\s+' + re.escape(title) + r'\s*$', re.MULTILINE)
            body = heading_pattern.sub("# " + new_title, body)
            
            # Generate new filename
            filename = filepath.name
            filename_base = filepath.stem
            # Extract number prefix
            match = re.match(r'^(\d+[-_]?)', filename_base)
            if match:
                prefix = match.group(1)
                # Build new filename without the metaphor
                new_filename_base = filename_base
                for metaphor, replacement in TITLE_REPLACEMENTS.items():
                    pattern = re.compile(r'\b' + metaphor + r'\b', re.IGNORECASE)
                    new_filename_base = pattern.sub(replacement, new_filename_base)
                
                if new_filename_base != filename_base:
                    new_filename = new_filename_base + ".md"
                    new_filepath = filepath.parent / new_filename
                    changes.append(f"Filename: '{filename}' -> '{new_filename}'")
    
    # Rebuild content
    new_content = "---\n" + yaml.dump(frontmatter, allow_unicode=True, default_flow_style=False) + "---\n" + body
    
    return new_content, new_filepath, changes

def replace_banned_words(content):
    """Replace banned words in body text."""
    changes = []
    original = content
    
    for banned, replacement in BANNED_WORD_REPLACEMENTS.items():
        pattern = re.compile(r'\b' + banned + r'\b', re.IGNORECASE)
        matches = pattern.findall(content)
        if matches:
            content = pattern.sub(replacement, content)
            changes.append(f"Body: '{banned}' -> '{replacement}' ({len(matches)} occurrences)")
    
    return content, changes

def add_metaphor_introductions(content):
    """Add introduction sentences for metaphors in body text."""
    changes = []
    original = content
    
    for metaphor, description in METAPHORS_REQUIRING_INTRO:
        pattern = re.compile(r'\b' + metaphor + r'\b', re.IGNORECASE)
        matches = list(pattern.finditer(content))
        
        if matches:
            # Find first occurrence
            first_match = matches[0]
            pos = first_match.start()
            
            # Get context before the match
            start = max(0, pos - 100)
            context_before = content[start:pos]
            
            # Check if introduction already exists nearby
            intro_pattern = re.escape(metaphor) + r'\s*\(metaphor'
            if not re.search(intro_pattern, context_before, re.IGNORECASE):
                # Find the start of the sentence
                sentence_start = content.rfind('. ', start, pos) + 2
                if sentence_start == 1:  # Not found
                    sentence_start = content.rfind('\n', start, pos) + 1
                    if sentence_start == 0:
                        sentence_start = 0
                
                # Insert introduction
                intro = f"{metaphor.capitalize()} (metaphor for {description}): "
                content = content[:sentence_start] + intro + content[sentence_start:]
                changes.append(f"Added intro for '{metaphor}' at position {sentence_start}")
    
    return content, changes

def process_file(filepath):
    """Process a single markdown file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        all_changes = []
        
        # Phase 2: Update title and filename
        frontmatter, body = extract_frontmatter(content)
        new_content, new_filepath, title_changes = update_frontmatter_title(frontmatter, body, filepath)
        all_changes.extend(title_changes)
        
        # Phase 3: Replace banned words in body
        new_content, banned_changes = replace_banned_words(new_content)
        all_changes.extend(banned_changes)
        
        # Phase 4: Add metaphor introductions
        new_content, intro_changes = add_metaphor_introductions(new_content)
        all_changes.extend(intro_changes)
        
        # Write changes
        if new_content != original_content:
            with open(new_filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            # Rename file if needed
            if new_filepath != filepath:
                if filepath.exists():
                    os.remove(filepath)
        
        return all_changes
    except Exception as e:
        return [f"ERROR: {str(e)}"]

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
    
    for i, filepath in enumerate(sorted(md_files), 1):
        changes = process_file(filepath)
        if changes:
            files_changed += 1
            total_changes.append(f"\n--- {filepath.name} ---")
            total_changes.extend(changes)
    
    log.append(f"\nFiles with changes: {files_changed}/{len(md_files)}")
    log.extend(total_changes)
    
    # Write log
    log_path = REPO_PATH / "ste100_revision_log.txt"
    with open(log_path, 'w') as f:
        f.write("\n".join(log))
    
    print("\n".join(log))
    print(f"\nLog written to: {log_path}")

if __name__ == "__main__":
    main()
