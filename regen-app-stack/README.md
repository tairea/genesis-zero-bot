# Regen App Stack

**Trust-minimized, platform-independent app distribution — without the incumbents.**

This is a toolkit for developers who refuse to surrender their users to App Store gatekeepers, proprietary distribution lock-in, or opaque update mechanisms. Every component here serves one purpose: **let developers ship software directly to users, verifiably and sustainably.**

---

## Philosophy

Big tech platforms control what gets installed, when it updates, and who can access it. They can revoke your app overnight. They take 30% of revenue. They surveil your users. They can and will de-platform you for political speech, competitors, or no reason at all.

The alternative isn't anarchy — it's **trust-minimized distribution**:

- **Cryptographic verification** at every step (APK signatures, SHA256 checksums, PGP/GPG signatures, Sigstore transparency logs)
- **User-controlled installation** (APK sideloading, PWA installation, not managed by a store)
- **Federation and interoperability** (Matrix homeservers users own, not corporate chat silos)
- **Multiple verification paths** (PGP web of trust, keybase proofs, in-person verification, Sigstore's transparency log)
- **Open standards** wherever possible (WASM, PWA manifest, Matrix protocol, OpenPGP)

This stack doesn't eliminate trust — it makes it **explicit, verifiable, and recoverable**.

---

## Components

### 1. [Rust + Trunk PWA Starter](./pwa-starter/) — `⭐ Recommended`
Platform-independent web apps that install like native apps, work offline, and run anywhere with a browser. Compiled from Rust to WASM via Leptos + Trunk. Zero App Store dependency.

**Quick start:**
```bash
cd pwa-starter
docker build -t regen-pwa-builder .   # Build WASM without installing Rust
# Or locally:
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
rustup target add wasm32-unknown-unknown
cargo install trunk
trunk serve
```

### 2. [APK Signing & Verification Toolkit](./sign-verify-apk/)
Sign Android APKs with a developer key, verify signatures, generate SHA256 checksums, and publish releases with verifiable integrity. Includes templates for PGP-signed release notes.

**Quick start:**
```bash
cd sign-verify-apk
chmod +x *.sh
./sign-apk.sh unsigned.apk release-key.jks mykeypass    # Sign
./verify-apk.sh signed.apk                               # Verify
./hash-release.sh ./releases/                            # Generate checksums
```

### 3. [Obtainium Config Generator](./obtainium-config-generator.html)
A single HTML file that converts a GitHub repository URL into an Obtainium-compatible app configuration. Obtainium is an open-source, permissions-minimal APK manager for Android that works with direct APK URLs and GitHub releases.

**Quick start:** Open `obtainium-config-generator.html` in any browser. Paste a GitHub repo URL. Copy the generated config.

### 4. [Matrix Homeserver Setup](./matrix-homeserver/)
Self-host a Matrix homeserver (Synapse) with Docker. Own your communication infrastructure. Bridge to Telegram. Full security checklist included.

**Quick start:**
```bash
cd matrix-homeserver
# Edit docker-compose.yml with your domain
docker compose up -d
# Run the registration container to create your admin user
docker compose run --rm register
```

### 5. [PGP Key Setup Guide](./pgp-key-setup/)
Generate your GPG keypair, publish to keyservers, sign releases, write verifiable release notes, and establish trust through multiple paths (web of trust, keybase.io, in-person verification).

**Quick start:**
```bash
cd pgp-key-setup
gpg --full-generate-key          # Generate key
gpg --keyserver keyserver.ubuntu.com --send-keys YOUR_KEY_ID
./sign-release.sh myapp.tar.gz mykey.key  # Sign a release
```

### 6. [Sigstore Integration](./sigstore-guide/)
Keyless artifact signing using GitHub OIDC. Every release automatically signed. Signatures recorded in a public transparency log (Rekor) that anyone can query. No key management overhead.

**Quick start:**
```bash
# Sign an artifact (uses GitHub OIDC, no keys needed)
cosign sign --yes ghcr.io/yourorg/yourapp:v1.2.3

# Verify
cosign verify ghcr.io/yourorg/yourapp:v1.2.3
```

---

## Why Each Piece Matters

| Problem | Solution | Trust Model |
|---------|----------|-------------|
| App Store gatekeeping | PWA + APK sideloading | User controls installation |
| Tampered APKs | APK signing + SHA256 checksums | User verifies signature |
| Stolen/modified releases | PGP signing | Web of trust + key verification |
| Centralized app catalogs | Obtainium | Direct from developer GitHub |
| Corporate chat silos | Matrix federation | Users own their homeserver |
| No audit trail for releases | Sigstore transparency log | Public, verifiable signing |
| Closed app updates | Matrix + Obtainium + direct links | User decides when to update |

---

## License

AGPL-3.0 — See [LICENSE](./LICENSE)

---

## Contributing

This stack is designed to be forkable and extensible. If you improve any component, share it back. The goal is a larger ecosystem of independently-distributed, trust-minimized software.
