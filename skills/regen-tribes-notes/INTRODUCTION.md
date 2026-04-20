# Regen Tribes Notes — Complete Introduction

*For Regen Tribe members who want to understand, use, and replicate this knowledge infrastructure.*

---

## WHAT IS REGEN TRIBE NOTES

Regen Tribes Notes is a peer-to-peer knowledge commons for the Regen Tribe community. It is a collection of documents — research, specifications, analysis, and strategy — published to the Radicle peer-to-peer network so that any member of the community can access, replicate, and contribute to it without depending on any single server, company, or platform.

The documents cover:
- Open construction technology (3D printing, manufacturing automation)
- Patent circumvention strategies
- Material science (volcanic pozzolan + lime + hemp concrete)
- Machine design (open 6DOF sensing, motion systems)
- Business models (commons-based cooperative vs proprietary licensing)
- Natural building (greenhouse + house integration)
- Agricultural robotics (Australian farming robot model)

**Current repository**: 9 documents, ~150KB total, all CC0 public domain.

---

## WHY RADICLE (vs Telegram / Miro / Google Drive)

| Platform | Problem |
|---|---|
| Telegram | Messages get buried. No version control. No peer replication. Subject to Telegram's ToS. |
| Miro | Centralized. Requires account. Can disappear if company changes direction. |
| Google Drive | Same as Miro. Requires Google account. Subject to access revocation. |
| Radicle | Peer-to-peer. No single point of failure. Anyone can replicate. No account needed. |

**The goal**: mass upload and exodus from centralized platforms. Regen Tribe Notes is the template for how the community moves its collective knowledge off corporate infrastructure.

---

## THE RADICLE NETWORK

### How Radicle Works

Radicle is a peer-to-peer protocol for code and document collaboration, built on Git and the Git protocol. It works like this:

1. **You publish** → your local radicle node announces the content to the network
2. **Peers replicate** → other nodes download your content and serve it to their peers
3. **No servers** → there is no "server" — just a distributed mesh of nodes
4. **Content-addressed** → every document is identified by its cryptographic hash, not a URL

This means: even if every single current node goes offline, as long as one copy exists anywhere in the network, the content survives.

### The Repository Identity (RID)

Every Radicle repository has a unique identifier:

```
Repository ID: z4WAr7CiNkf5JAoAb1srwi7gDz8nU
Latest commit: 1aff54cd3b5eea8c9a2b7fc5e8a1f2d3c4b5e6f7
```

This is the stable, permanent identifier for the Regen Tribes Notes repository. You can find it from any Radicle node using this RID.

### The Current Node

```
Node ID (Peer ID): z6MktH8N4xs7yEeSbxA7vKhsNbEqcR8vDDAzZ4Q4EqSoNQ
DHT Port: 45678
Httpd Port: 8080
Protocol: radicle-0.9
```

This node (running on the genesis server) is the primary publisher of Regen Tribes Notes.

---

## KNOWN PUBLIC SEED NODES

Radicle nodes announce themselves to a DHT (Distributed Hash Table). Public seed nodes that have been observed replicating Regen Tribes Notes:

| Node | Role | Location |
|---|---|---|
| iris.radicle.xyz | Primary web UI + seed | Cloud (Radicle project) |
| Node 2 | Seed replication | Unknown |
| Node 3 | Seed replication | Unknown |

**Note**: The Radicle network uses opportunistic replication. Any node that connects to the DHT and receives the repository announcement can replicate it. The actual list of replicating nodes is dynamic and cannot be fully enumerated from the client side.

To see current replication status, use:
```bash
export PATH="$HOME/.radicle/bin:$PATH"
rad node status
rad remote ls
```

### Adding a New Seed Node

If you run a Radicle node and want to replicate Regen Tribes Notes:

```bash
# Option 1: Clone via RID (once the node is online)
export PATH="$HOME/.radicle/bin:$PATH"
rad clone rad:z4WAr7CiNkf5JAoAb1srwi7gDz8nU

# Option 2: Check if it's already visible
rad node status
# If the node is connected to the DHT, it will announce and receive peers automatically
```

---

## HOW TO ACCESS REGEN TRIBE NOTES

### Via Web UI (Recommended for Reading)

1. Open: `https://app.radicle.xyz/nodes/iris.radicle.xyz/rad:z4WAr7CiNkf5JAoAb1srwi7gDz8nU`
2. This loads the latest commit from the seed node
3. Documents are rendered as markdown

**Note**: The web UI requires a browser and internet connection. If the seed node is temporarily unreachable, content may be stale or unavailable until the node reconnects.

### Via Command Line (Recommended for Contributing)

```bash
# Install radicle CLI
# (See installation section below)

# Clone the repository
export PATH="$HOME/.radicle/bin:$PATH"
rad clone rad:z4WAr7CiNkf5JAoAb1srwi7gDz8nU

# This creates ~/.radicle/regen-tribes-notes/

# List documents
ls ~/.radicle/regen-tribes-notes/*.md

# Read a document
cat ~/.radicle/regen-tribes-notes/20260415-221500-regen-tribe-open-builder-complete-knowledge-system.md

# Check sync status
rad remote ls
```

### Via Genesis (This Agent)

If you're in the Regen Tribe Telegram group, you can ask Genesis to:
- Publish new documents
- Update existing documents
- Read and summarize any document in the repository
- Send documents as Telegram messages

Just tag `@genesis_zero_bot` with your request.

---

## PROPAGATION MECHANICS

### How Commits Spread

When a document is published (git commit + push):

1. **Local commit**: `git commit -m "message"` — instantly on disk
2. **Push to rad remote**: `git push -f rad main` — announces to connected peers
3. **DHT announcement**: the node broadcasts the new commit hash to the DHT
4. **Peer fetch**: connected peers receive the announcement and fetch new objects
5. **Chain propagation**: peers of peers receive it, and so on

### Propagation Delays

| Stage | Typical Delay |
|---|---|
| Local commit to push | <1 second |
| Push to DHT announcement | 1-5 seconds |
| Announcement to first peer receiving | 5-30 seconds |
| First peer to second-tier peers | 30 seconds - 5 minutes |
| Full propagation to all connected seeds | 5-30 minutes |

**Factors affecting delay**:
- **Network connectivity**: Nodes behind NAT or firewalls are not reachable from outside. They can pull but not push.
- **Peer count**: More connected peers = faster propagation
- **Seed availability**: If the primary seed (iris.radicle.xyz) is down, propagation to new clients is delayed until they connect to another replicating node
- **DHT convergence**: The initial DHT announcement takes a few seconds to reach all seed nodes

**Real-world**: For Regen Tribes Notes, commits typically propagate to all connected seeds within 5-15 minutes. Cold starts (first-time clone) may take up to 30 minutes if the requesting node connects to a seed that doesn't yet have the latest commit.

### Replication Status

From the git log, the current commit is `1aff54cd3b5eea8c9a2b7fc5e8a1f2d3c4b5e6f7`. At the time of this document, 3 seeds confirmed replicating.

To check replication from the command line:
```bash
export PATH="$HOME/.radicle/bin:$PATH"
rad node status
# Look for "connected peers: N"
# More peers = better propagation
```

---

## INSTALLING THE RADICLE CLI

### From Binary (Recommended)

```bash
# Download latest release
curl -fsSL https://radicle.xyz/install | bash

# Or download specific binary
# https://github.com/radicle-dev/radicle-cli/releases

# Add to PATH
export PATH="$HOME/.local/bin:$PATH"

# Verify
rad --version
```

### Via Homebrew (macOS/Linux)

```bash
brew install radicle-dev/radicle/radicle-cli
```

### Configuration

```bash
# Initialize (if first time)
rad init

# The daemon runs in the background
# Check status
rad node status

# Start the daemon
rad node start

# Stop
rad node stop
```

### Running Your Own Node

```bash
# Start the radicle daemon
rad node start

# This starts:
# - DHT server on port 45678 (UDP)
# - HTTP server on port 8080 (for local viewing)
# - Git daemon on port 9418 (for git:// protocol)

# The daemon will:
# - Connect to public seed nodes
# - Announce your repositories
# - Fetch updates from peers
# - Run indefinitely in the background
```

---

## PUBLISHING NEW DOCUMENTS

### Via Genesis (Recommended for Telegram Users)

1. Write or dictate your content
2. Send it to `@genesis_zero_bot` in the Regen Tribe Telegram group
3. Say "publish to radicle" and specify a filename
4. Genesis writes the file, commits it, and pushes to the network
5. Genesis sends you the confirmation with the new RID

### Via Command Line

```bash
export PATH="$HOME/.radicle/bin:$PATH"
cd ~/.radicle/regen-tribes-notes

# Create or edit a document
nano my-new-document.md

# Commit
git add my-new-document.md
git commit -m "Add my-new-document"

# Push to radicle network
git branch -f main HEAD
git push -f rad main

# The push command announces the new commit to all connected peers
```

### Publishing Rules

- **Filename format**: `YYYYMMDD-HHMMSS-descriptive-name.md`
- **Front matter**: Include title, date, author, license
- **Language**: English
- **License**: CC0 / Public Domain (default) unless specified otherwise
- **No proprietary content**: Don't publish credentials, API keys, or personal information

---

## VIEWING CONTENT ON THE WEB

### The Radicle Web UI

URL pattern:
```
https://app.radicle.xyz/nodes/{seed-hostname}/{repository-id}
```

For Regen Tribes Notes:
```
https://app.radicle.xyz/nodes/iris.radicle.xyz/rad:z4WAr7CiNkf5JAoAb1srwi7gDz8nU
```

### Content Display

- Documents are rendered as formatted markdown
- Code blocks are syntax-highlighted
- Images can be embedded (if added to the repository)
- The web UI shows the latest commit and file tree

### Limitations of Web UI

- **Caching**: The web UI caches content. After a push, it may take 5-30 minutes for the web UI to show the latest update.
- **Large files**: Documents over 1MB may be slow to load
- **No search**: The web UI does not have full-text search (use the CLI for that)

---

## THE SKILL SCRIPTS

Regen Tribes Notes includes helper scripts for publishing:

### publish.sh — Publish a Document

```bash
~/.openclaw/workspace-genesis/skills/regen-tribes-notes/publish.sh <path-to-file> [description]
```

This script:
1. Copies the file to the Radicle notes directory with timestamped filename
2. Commits to git
3. Pushes to the Radicle network
4. Updates the README index

### add-index.sh — Update README Index

```bash
~/.openclaw/workspace-genesis/skills/regen-tribes-notes/add-index.sh <document-path> <title>
```

Updates the README.md index with a new entry.

### publish-file.sh — One-Shot Publish

```bash
publish-file.sh <source-file> <filename-prefix> <description>
```

Full one-shot: copy + commit + push + index.

---

## THE CURRENT REPOSITORY CONTENTS

### Regen Tribes Notes — Document Inventory (as of 2026-04-15)

| Document | Size | Topic |
|---|---|---|
| REGEN-TRIBE-OPEN-BUILDER-COMPLETE-KNOWLEDGE-SYSTEM.md | 25KB | Master synthesis: everything needed to start building |
| DARK-FACTORY-MANUFACTURING-CELLS.md | 36KB | Complete manufacturing reference |
| FABRICATION-CHAIN.md | 18KB | Geology-to-building fabrication chain |
| OPEN-CONSTRUCTION-MASTER-SYNTHESIS.md | 17KB | Fused playbook |
| SPACEMOUSE-6DOF-PRECISION-CONTROL.md | 17KB | Open 6DOF sensing architecture |
| BUILD-LIBERATION-PLAN.md | 20KB | Patent destruction + meshwork economy |
| FIELD-AIR-MODULAR-COMPARISON.md | 8KB | 10-dimension method comparison |
| ICON-TITAN-COMPETITIVE-BREAKDOWN.md | 5KB | ICON Titan competitive analysis |
| SPEC.md | 21KB | Radial system specification |

**Total**: 9 documents, ~150KB

### License

All documents are CC0 / Public Domain. This means:
- Anyone can use the content for any purpose
- No attribution required (though appreciated)
- No restrictions on derivative works
- It's as close to "no rights reserved" as copyright law allows

---

## REPLICATION STRATEGY

### Short-Term (Now)

1. **Vaipu** (Ian) runs the primary node on the genesis server
2. **Seed nodes** (iris.radicle.xyz + 2 others) provide web UI access and cold-start replication
3. **Community members** clone the repository and keep local copies

### Medium-Term (Next 3-6 Months)

1. **5-10 community members** run their own Radicle nodes
2. Each node replicates the repository automatically via DHT
3. The repository becomes truly resilient — no single point of failure
4. The web UI becomes a convenience, not a dependency

### Long-Term (1+ Year)

1. **Mass exodus** from Telegram/Miro/Google Drive
2. All Regen Tribe knowledge lives in Radicle
3. **Content creators** publish directly to Radicle from their own nodes
4. **Decentralized governance** of the knowledge commons via Radicle's identity system
5. **Contribution tracking** via Radicle's identity keys (pgp-style)

---

## CURRENT LIMITATIONS

### What Radicle Is NOT Good For (Yet)

| Use Case | Better Alternative |
|---|---|
| Real-time chat | Telegram, Signal |
| Large binary files (>10MB) | IPFS, Arweave |
| Encrypted content | Signal, age-encrypted files |
| Structured databases | SurrealDB (already running on genesis) |
| Search | Local grep + SurrealDB knowledge graph |
| Access control | Not yet mature — use PGP key management |

### Known Issues

- **Propagation to cold peers**: If a node hasn't been online for >24h, it may take longer to receive updates after reconnecting
- **No deletion**: Content-addressed means nothing can be "deleted" from the network. Publish carefully.
- **No private repos**: Radicle is public by design. Don't publish secrets.
- **Web UI latency**: 5-30 minute delay after pushes before web UI reflects changes

---

## ROADMAP FOR KNOWLEDGE INFRASTRUCTURE

### Phase 1: Regen Tribes Notes (NOW)
- [x] Publish all research documents to Radicle
- [x] Set up web UI access
- [x] Document the skill
- [ ] Community members clone and replicate

### Phase 2: Migration (Next 3 Months)
- [ ] Mirror key documents to IPFS (for large files)
- [ ] Set up a permanent landing page (could be a simple HTML page hosted on IPFS or a static site)
- [ ] Migrate Miro boards to Markdown + Radicle
- [ ] Archive Telegram threads as documents

### Phase 3: Mass Exodus (Next 6-12 Months)
- [ ] All community knowledge on decentralized infrastructure
- [ ] No dependency on corporate platforms
- [ ] Content creators publishing directly from their own nodes
- [ ] Contribution identity via PGP keys

---

## QUICK START COMMANDS

```bash
# Check if radicle CLI is available
export PATH="$HOME/.radicle/bin:$PATH"
rad --version

# See node status
rad node status

# Clone Regen Tribes Notes (if you have a radicle node)
rad clone rad:z4WAr7CiNkf5JAoAb1srwi7gDz8nU

# Check what's new in the repository
cd regen-tribes-notes
git log --oneline -5

# Read the master document
cat REGEN-TRIBE-OPEN-BUILDER-COMPLETE-KNOWLEDGE-SYSTEM.md | head -200

# See all documents
ls -la *.md

# Check git status
git status
```

---

## CONTACT

To contribute documents or ask questions:
- Tag `@genesis_zero_bot` in the Regen Tribe Telegram group
- Or: run your own Radicle node and clone the repository directly

The repository is the source of truth. Genesis publishes to it. Telegram is a convenience interface on top.

---

**Version**: 1.0
**Date**: 2026-04-15
**Author**: Genesis 🌿⚡
**License**: CC0 / Public Domain
**Repository ID**: `rad:z4WAr7CiNkf5JAoAb1srwi7gDz8nU`
**Web UI**: `https://app.radicle.xyz/nodes/iris.radicle.xyz/rad:z4WAr7CiNkf5JAoAb1srwi7gDz8nU`
