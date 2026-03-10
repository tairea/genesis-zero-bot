# Telegram History — Versioned Chat Archive

Manage and query versioned Telegram conversation exports for the Regen Tribes community.

## Intention

Archive Telegram group exports with timestamped versioning, then query them for member profiling, topic extraction, link cataloging, proposal tracking, and full-text search. Serves as the raw data source for community knowledge analysis.

## Stack

- **Python** — query engine
- **jq** — JSON processing
- **Telegram JSON exports** — raw data format

## Components

| File | Role |
|------|------|
| `SKILL.md` | Skill manifest with query examples and file structure documentation |
| `query.py` | Query implementation — filter, search, extract, and analyze conversation data |

## Data Format

Raw exports stored as `TELEGRAM---{uuid}.json`, versioned at `timestamp/{date}--{description}.json`.

Each export contains: group name, type, ID, and messages array with sender, date, text, reply chains, media references, and message types.

## Query Operations

- Filter by user / date range
- Full-text search across messages
- Extract links and URLs
- Find ideas, proposals, decisions
- Topic analysis and evolution tracking
- Member statistics and activity profiling

## Limitations

- **Manual export required** — Telegram exports must be manually created and placed in the skill folder
- **No real-time sync** — operates on static export snapshots, not live Telegram API
- **Single group format** — assumes Telegram Desktop JSON export format

## Next Steps

1. Add automated export via Telegram API (tdlib or pyrogram)
2. Incremental updates instead of full re-export
3. Connect to genesis-brain for automatic knowledge capture from history
4. Add structured output formats (CSV, JSON summary) for analysis pipelines
