---
name: telegram-history
description: Versioned Telegram conversation history manager with JSON query capabilities
homepage: https://github.com/regentribes/genesis-zero-bot
metadata:
  emoji: 📜
  requires:
    bins: [jq, python3]
  media_dir: ./media/inbound
---

# telegram-history — Versioned Chat Archive

Maintain timestamped, versioned archives of Telegram conversation exports for analysis, search, and retrieval.

## File Structure

Telegram exports use this JSON schema:

```json
{
  "name": "Group Name",
  "type": "private_supergroup",
  "id": 123456789,
  "messages": [
    {
      "id": 1,
      "type": "service|message",
      "date": "2023-09-21T11:43:06",
      "date_unixtime": "1695310986",
      "from": "User Name",
      "from_id": "user123456",
      "reply_to_message_id": 42,
      "text": "Message content",
      "text_entities": [
        {"type": "link", "text": "https://example.com"}
      ]
    }
  ]
}
```

## Storage Convention

```
media/inbound/
├── TELEGRAM---{uuid}.json        # Raw export
└── timestamp/                    # Versioned archives
    ├── 2023-09-21--initial.json
    ├── 2023-10-15--update.json
    └── ...
```

Filename format: `{date}--{description}.json`

## Query Operations

### 1. List All Messages by User
```bash
telegram-history query --file export.json --user "Vic Desotelle"
```

### 2. Extract Messages with Links
```bash
telegram-history query --file export.json --links
```

### 3. Find Proposals/Ideas
```bash
telegram-history query --file export.json --ideas
```

### 4. Filter by Date Range
```bash
telegram-history query --file export.json --from 2024-01-01 --to 2024-06-30
```

### 5. Topic Analysis
```bash
telegram-history query --file export.json --topics
```

### 6. Full Text Search
```bash
telegram-history search --file export.json --query "governance"
```

### 7. Extract Member Statistics
```bash
telegram-history stats --file export.json
```

## Demo: Extract Vic's Messages

```bash
# Extract all messages from Vic Desotelle
telegram-history extract --user "Vic" --include links --output vic-messages.json

# Find proposals
telegram-history extract --user "Vic" --proposals --output vic-proposals.json
```

## API Reference

### Query Filters
| Flag | Description |
|------|-------------|
| `--user` | Filter by username |
| `--links` | Include only messages with links |
| `--ideas` | Include proposal/idea/goal keywords |
| `--from` | Start date (YYYY-MM-DD) |
| `--to` | End date (YYYY-MM-DD) |
| `--topic` | Filter by topic ID |
| `--limit` | Max results (default: 1000) |

### JSON Fields
| Field | Type | Description |
|-------|------|-------------|
| `id` | int | Message ID |
| `type` | string | "service" or "message" |
| `date` | string | ISO timestamp |
| `from` | string | Sender name |
| `from_id` | string | Sender ID |
| `text` | string | Message text |
| `text_entities` | array | Formatted content |
| `reply_to_message_id` | int | Reply target |

### Text Entity Types
- `plain` — Regular text
- `link` — URLs
- `mention` — @username
- `hashtag` — #topic
- `code` — Inline code
- `pre` — Code block

## Versioning

To create a new versioned archive:

```bash
# Copy current export to timestamped file
telegram-history archive --source export.json --tag "2024-01-15"
```

This creates: `telegram-history/2024-01-15--export.json`

## Use Cases

1. **Member profiling** — Extract all contributions per member
2. **Proposal tracking** — Find all proposals over time
3. **Link cataloging** — Build resource database from shared links
4. **Topic evolution** — Track how topics develop
5. **Decision logs** — Extract governance decisions
6. **Knowledge extraction** — Build searchable knowledge base
