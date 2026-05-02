# ERC-3643 Alternatives + Rust-Native Stack Analysis
**Compiled:** 2026-05-02 | **Sources:** GitHub API, Polymesh, Centrifuge, Holochain, Solana RWA Program

## ERC-3643 Introduction

**What it is:** Ethereum standard for permissioned security tokens. Originally T-REX (Token for Regulated EXchanges).

**Active canonical repo:** github.com/ERC-3643/ERC-3643 (133 stars, last push Apr 17 2026)
**T-REX (TokenySolutions):** ARCHIVED since Oct 2025 (267 stars, no longer maintained)

### Architecture - 6 Components
1. **ONCHAINID** - Self-sovereign identity contract, W3C DID compatible
2. **Trusted Issuers Registry** - Authorized claim issuers
3. **Claim Topics Registry** - Claim types (KYC, AML, etc.)
4. **Identity Registry** - Eligible user identity contracts
5. **Compliance Smart Contract** - Transfer rule verification
6. **Security Token Contract** - ERC-20 compatible, identity-aware

### Key Difference from ERC-20
- ERC-20: Anyone can hold, transfer freely
- ERC-3643: Only verified identities, conditional transfers, built for securities

## T-REX is Obsolete
- **Status:** Archived (Oct 2025)
- **Source:** github.com API verified
- **Replacement:** ERC-3643/ERC-3643 (active)

## Rust-Native Alternatives for Permissioned Tokens

### 1. Polymesh (BEST FOR ITC)
- **Language:** Rust/Substrate
- **Purpose:** Public permissioned blockchain for regulated assets
- **Key:** Protocol-level asset standard (not smart contract), compliance built into base layer
- **Identity, compliance, confidentiality, settlement** at runtime level
- Node operators are licensed financial entities
- **Source:** polymesh.network whitepaper

### 2. Solana RWA Token Program
- **Language:** Rust-equivalent (SPL Token-2022)
- **Purpose:** Permissioned security tokens on Solana
- **Key:** Transfer hooks, fractional ownership, compliance rules
- High throughput, low cost
- **Source:** quillaudits.com

### 3. Centrifuge
- **Language:** Rust/Substrate
- **Purpose:** RWA infrastructure + DeFi
- **Key:** RWA Launchpad, pre-built institutional contracts, pools
- **Source:** centrifuge.io

## Agent Frameworks (Rust-native)

| Framework | Type | Best For |
|-----------|------|----------|
| **Holochain** | Agent-centric DLT | Community apps, governance, data sovereignty (NOT tokens) |
| **AutoAgents** | AI agents | Tool-using, high throughput production |
| **RIG** | Single agent | Clean API, multi-LLM |
| **Swarms-RS** | Multi-agent | Orchestration, state management |
| **Moltis** | Personal agent server | Sandboxed, secure, self-hosted |

## Comparison Table

| Purpose | Best Tool | Language |
|---------|----------|----------|
| Permissioned tokens | Polymesh | Rust/Substrate |
| AI agents | AutoAgents/Swarms-RS | Rust-native |
| Community apps (non-token) | Holochain | Rust/DNA |
| Integration | Chainlink oracles | Any |
| Knowledge commons | Integral OAD | Any |
| Governance | Integral CDS | Any |

## Recommendation for RegenTribes

**For ITC (Integral Time Credits):**
1. Build on Polymesh (protocol-level compliance, identity built in, Rust/Substrate)
2. Alternative: Solana RWA Token Program (SPL Token-2022 transfer hooks)

**For non-token community apps:**
- Holochain DNA for CDS governance, member identity, knowledge commons, FRS feedback

**Skip:**
- T-REX (archived, obsolete)
- Fetch.ai (Python-centric, not Rust-native)
- ERC-3643 on EVM (Solidity, less secure than Polymesh protocol-level)

## Sources
- github.com/ERC-3643/ERC-3643 (active canonical)
- github.com/TokenySolutions/T-REX (archived Oct 2025)
- polymesh.network/whitepaper
- quillaudits.com/research/rwa-development/non-evm-standards/solana-rwa-token-program
- centrifuge.io
- holochain.org
- dev.to benchmarking 2026
