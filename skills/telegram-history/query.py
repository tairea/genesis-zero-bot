#!/usr/bin/env python3
"""
Telegram History Query Tool
Extract, filter, and analyze Telegram conversation exports
"""

import json
import sys
import os
import re
from datetime import datetime
from pathlib import Path
from collections import defaultdict

def load_export(filepath):
    """Load Telegram export JSON"""
    with open(filepath, 'r', encoding='utf-8') as f:
        # Try JSON first, then YAML
        try:
            return json.load(f)
        except json.JSONDecodeError:
            print("Error: Not valid JSON. Try converting from YAML export format.")
            sys.exit(1)

def filter_messages(messages, user=None, links_only=False, ideas_only=False, 
                   date_from=None, date_to=None, topic_id=None, limit=1000):
    """Filter messages based on criteria"""
    results = []
    
    # Keywords for idea/proposal detection
    idea_keywords = [
        'proposal', 'idea', 'vision', 'goal', 'objective', 'mission',
        'should', 'could', 'would be good', 'recommend', 'suggest',
        'want to', 'working on', 'building', 'creating', 'developing',
        'designing', 'implementing', 'plan', 'initiative', 'project',
        'dream', 'hope', 'envision', 'imagine', 'future'
    ]
    
    for msg in messages:
        # Skip service messages unless filtering for them
        if msg.get('type') == 'service':
            continue
        
        # User filter - 'from' for regular messages, 'actor' for service
        sender = ''
        if msg.get('type') == 'message':
            sender = msg.get('from', '') or ''
        else:
            sender = msg.get('actor', '') or ''
        
        if user:
            if sender and user.lower() not in sender.lower():
                continue
        
        # Links filter
        if links_only:
            text = msg.get('text', '')
            if isinstance(text, list):
                has_link = any(e.get('type') == 'link' for e in text if isinstance(e, dict))
            else:
                has_link = 'http://' in text or 'https://' in text
            if not has_link:
                continue
        
        # Ideas filter
        if ideas_only:
            text = msg.get('text', '')
            if isinstance(text, list):
                text = ' '.join([t if isinstance(t, str) else str(t) for t in text])
            text_lower = text.lower()
            if not any(kw in text_lower for kw in idea_keywords):
                continue
        
        # Date filters
        msg_date = msg.get('date', '')[:10]  # Get YYYY-MM-DD
        if date_from and msg_date < date_from:
            continue
        if date_to and msg_date > date_to:
            continue
        
        results.append(msg)
        
        if len(results) >= limit:
            break
    
    return results

def extract_text(msg):
    """Extract clean text from message"""
    text = msg.get('text', '')
    if isinstance(text, list):
        parts = []
        for t in text:
            if isinstance(t, str):
                parts.append(t)
            elif isinstance(t, dict):
                parts.append(t.get('text', ''))
        return ''.join(parts)
    return str(text) if text else ''

def get_sender(msg):
    """Get sender name from message"""
    return msg.get('from', '') or msg.get('actor', 'Unknown')

def extract_links(msg):
    """Extract links from message"""
    text = msg.get('text', [])
    links = []
    if isinstance(text, list):
        for t in text:
            if isinstance(t, dict) and t.get('type') == 'link':
                links.append(t.get('text', ''))
    return links

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Telegram History Query Tool')
    parser.add_argument('--file', '-f', required=True, help='Export JSON file')
    parser.add_argument('--user', '-u', help='Filter by username')
    parser.add_argument('--links', action='store_true', help='Include only messages with links')
    parser.add_argument('--ideas', action='store_true', help='Include only messages with proposals/ideas')
    parser.add_argument('--from', dest='date_from', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--to', dest='date_to', help='End date (YYYY-MM-DD)')
    parser.add_argument('--topic', help='Filter by topic ID')
    parser.add_argument('--limit', type=int, default=1000, help='Max results')
    parser.add_argument('--output', '-o', help='Output file')
    parser.add_argument('--format', choices=['json', 'text', 'summary'], default='json', help='Output format')
    
    args = parser.parse_args()
    
    # Load export
    if not os.path.exists(args.file):
        print(f"Error: File not found: {args.file}")
        sys.exit(1)
    
    print(f"Loading {args.file}...")
    data = load_export(args.file)
    messages = data.get('messages', [])
    print(f"Loaded {len(messages)} messages")
    
    # Filter
    print(f"Filtering messages...")
    results = filter_messages(
        messages,
        user=args.user,
        links_only=args.links,
        ideas_only=args.ideas,
        date_from=args.date_from,
        date_to=args.date_to,
        topic_id=args.topic,
        limit=args.limit
    )
    
    print(f"Found {len(results)} matching messages")
    
    # Output
    if args.format == 'json':
        output = json.dumps(results, indent=2, ensure_ascii=False)
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"Saved to {args.output}")
        else:
            print(output)
    
    elif args.format == 'text':
        for msg in results:
            date = msg.get('date', '')[:19]
            sender = msg.get('from', '') or msg.get('actor', 'Unknown')
            text = extract_text(msg)[:200]
            print(f"[{date}] {sender}: {text}...")
            print()
    
    elif args.format == 'summary':
        # Count by user
        user_counts = defaultdict(int)
        for msg in results:
            sender = msg.get('from', '') or msg.get('actor', 'Unknown')
            user_counts[sender] += 1
        
        print("\n=== SUMMARY ===")
        for user, count in sorted(user_counts.items(), key=lambda x: -x[1]):
            print(f"  {user}: {count} messages")

if __name__ == '__main__':
    main()
