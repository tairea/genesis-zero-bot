# APK Signing & Verification Toolkit

**Sign Android APKs with a developer key, verify signatures, and publish verifiable releases.**

---

## Quick Start (5 minutes)

```bash
cd sign-verify-apk

# 1. Generate a keystore (one-time)
keytool -genkey -v -keystore release-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias key0

# 2. Sign your APK
./sign-apk.sh unsigned.apk release-key.jks mykeypass

# 3. Verify the signature
./verify-apk.sh signed.apk

# 4. Generate checksums for release
./hash-release.sh ./releases/
```

---

## Why Sign APKs?

Android **requires** every APK to be signed to install. Unsigned APKs cannot be installed on any Android device.

Signing serves multiple trust purposes:

1. **Integrity** — Verifies the APK hasn't been tampered with after signing
2. **Authorship** — Proves the APK came from you (your private key)
3. **Update path** — Android requires new APKs to use the same key for auto-updates
4. **Trust chain** — Users can verify your identity via the signing certificate

### Key Loss = Game Over

**Critical:** If you lose your keystore or password, you **cannot** update existing users. They'll need to uninstall and reinstall. There is no recovery.

**Backup your keystore in multiple secure locations.** Treat it like the keys to your house.

---

## Generating a Keystore

### Using keytool (JDK)

```bash
keytool -genkey -v \
    -keystore release-key.jks \
    -keyalg RSA \
    -keysize 2048 \
    -validity 10000 \
    -alias key0
```

Flags:
- `-keystore release-key.jks` — output file (use `.jks` for Java KeyStore format)
- `-keyalg RSA` — RSA is most compatible
- `-keysize 2048` — 2048-bit RSA is the minimum recommended; 4096 is safer but slower
- `-validity 10000` — days the key is valid (10000 ≈ 27 years)
- `-alias key0` — identifier for the key within the keystore

**When asked for password:** Use a strong, unique password. Store it in a password manager.

**When asked for DN (Distinguished Name):** Use your real info:
```
CN=Your Name, O=YourOrg, C=US
```

### Using openssl (alternative)

```bash
# Generate private key
openssl genrsa -out private-key.pem 2048

# Create PKCS#12 bundle
openssl pkcs12 -export \
    -in certificate.pem \
    -inkey private-key.pem \
    -out release-key.p12 \
    -name key0
```

Then convert to JKS if needed:
```bash
keytool -importkeystore \
    -srckeystore release-key.p12 \
    -srcstoretype PKCS12 \
    -destkeystore release-key.jks
```

---

## Signing APKs

### Using apksigner (Android SDK)

**apksigner** is part of the Android SDK Build Tools. Install via:

```bash
# macOS
brew install android-sdk

# Linux
# Download from https://developer.android.com/studio/releases/build-tools

# Verify installation
apksigner version
```

### Sign with apksigner

```bash
# Basic signing
apksigner sign \
    --ks release-key.jks \
    --ks-key-alias key0 \
    --ks-pass pass:yourpassword \
    --out signed.apk \
    unsigned.apk

# V2 + V3 signing (recommended for broad compatibility)
apksigner sign \
    --ks release-key.jks \
    --v2-signing-enabled true \
    --v3-signing-enabled true \
    --out signed.apk \
    unsigned.apk
```

### Using our script

```bash
./sign-apk.sh unsigned.apk release-key.jks mykeypass [output.apk]
```

Example:
```bash
./sign-apk.sh ./app-unsigned.apk ./keystore/release-key.jks "s3cr3tP@ss"
```

The script:
- Detects if you're using JKS or PKCS#12 keystore
- Enables V1, V2, and V3 signing schemes
- Names output as `app-signed.apk` if not specified

---

## Verifying APK Signatures

### Verify with apksigner

```bash
# Basic verification
apksigner verify --verbose signed.apk

# Show certificate info
apksigner verify --print-certs signed.apk
```

Output example:
```
Signer #1 certificate:
    SHA-256: 3a:bc:12:4d:...:ef
    SHA-1: 12:34:56:78:...:ab
    Issuer: CN=Your Name, O=YourOrg, C=US
    Subject: CN=Your Name, O=YourOrg, C=US
    Serial number: 0x12345678
    Validity: Sun Jan 01 00:00:00 UTC 2024 -> Sat Jan 01 00:00:00 UTC 2054
```

### Using our script

```bash
./verify-apk.sh signed.apk
```

Output includes:
- Signature verification result
- Certificate details (DN, fingerprint, validity)
- Signing scheme used (v1/v2/v3)

### Manual Certificate Fingerprint Check

After first signing, record your fingerprint:

```bash
keytool -exportcert -alias key0 -keystore release-key.jks | \
    keytool -printcert | grep SHA256
```

Share this fingerprint on your website/GitHub. Users can:
1. Download your APK
2. Extract its signing certificate
3. Compare fingerprints

---

## Generating SHA256 Checksums

### Manual

```bash
sha256sum your-app.apk > your-app.apk.sha256
cat your-app.apk.sha256
```

### Using our script

```bash
./hash-release.sh ./releases/
```

This generates for each file:
- `FILENAME.sha256` — SHA256 checksum
- `CHECKSUMS.txt` — all checksums in one file
- `RELEASE_NOTES.txt` — template for PGP-signed notes

---

## PGP-Signed Release Notes

Create a release note and sign it:

```bash
# Create release notes
cat > RELEASES/v1.2.0-notes.txt << 'EOF'
# Release v1.2.0 - Bug Fixes

## What's New
- Fixed crash when opening settings on Android 14
- Improved offline mode reliability
- Security: Updated underlying libraries

## Downloads
- app-v1.2.0.apk (SHA256: see CHECKSUMS.txt)
- Source code: https://github.com/yourorg/app/releases/tag/v1.2.0

## Verification
This release is signed with key: 0xXXXXXXXXXXXX
Fingerprint: SHA256:XX:XX:XX:...
EOF

# Sign the release notes
gpg --armor --detach-sign RELEASES/v1.2.0-notes.txt
```

Users can verify:
```bash
# Download the APK, checksums, and signed notes
gpg --verify RELEASE_NOTES.txt.asc RELEASE_NOTES.txt
sha256sum -c CHECKSUMS.txt
```

---

## VirusTotal Integration (Optional)

Upload to VirusTotal programmatically (free API, rate-limited):

```bash
# Get your API key from https://www.virustotal.com/gui/
VT_API_KEY="your-api-key-here"

# Scan file
curl -X POST \
    -F "file=@your-app.apk" \
    -F "apikey=$VT_API_KEY" \
    https://www.virustotal.com/api/v3/files
```

**Note:** VirusTotal shares uploads with security researchers. Don't use for 0-day exploits or highly sensitive apps.

---

## Split APKs and App Bundles

### Universal vs Split APKs

**Universal APK:** Contains all architectures (arm64-v8a, armeabi-v7a, x86, x86_64). Larger file, simplest distribution.

**Split APKs (ABI splits):** Separate APK per architecture. Users download only what they need.

```bash
# Sign universal APK
apksigner sign --ks key.jks app-universal.apk

# For split APKs, sign each:
apksigner sign --ks key.jks app-arm64-v8a.apk
apksigner sign --ks key.jks app-armeabi-v7a.apk
```

### Android App Bundle (.aab)

Google Play requires `.aab` format. Sign with:
```bash
# Using bundletool
java -jar bundletool.jar build-bundle \
    --modules=base.aab \
    --output=app.aab

# Sign for Play Store upload
apksigner sign --ks key.jks app.aab
```

---

## Security Best Practices

### Protect Your Keystore

1. **Never commit keystore to git**
2. **Store keystore on encrypted storage**
3. **Use different keystores for different apps**
4. **Rotate keys every 2-3 years** (requires migration planning)

### Production Keystore

For production releases, use a **hardware security module (HSM)** or:
- **AWS KMS**
- **Google Cloud KMS**
- **HashiCorp Vault**
- **Smart card / YubiKey**

### Distribute Your Public Key

Users need your **public key** to verify signatures without trusting a CA.

Options:
1. **Upload to GitHub** — trust through GitHub's security
2. **Keybase.io** — link your key to your identity
3. **Your website** — serve the public key over HTTPS
4. **Key server** — publish to `keys.openpgp.org` or `keyserver.ubuntu.com`

Export your public key:
```bash
keytool -exportcert -alias key0 -keystore release-key.jks -file my-app-public-key.cer
# Or GPG export:
gpg --armor --export key0 > public-key.asc
```

---

## Troubleshooting

### " Keystore was tampered with, or password was incorrect"

Password doesn't match keystore. Check for:
- Typo in password
- Using `--ks-pass` vs `--pass` flag
- Wrong keystore file

### " APK signature scheme version not enabled for this signer"

Enable the signing scheme explicitly:
```bash
apksigner sign \
    --ks key.jks \
    --v1-signing-enabled true \
    --v2-signing-enabled true \
    --v3-signing-enabled true \
    --out signed.apk \
    unsigned.apk
```

### "INSTALL_PARSE_FAILED_NO_CERTIFICATES"

The APK isn't signed. Sign it with apksigner or jarsigner.

### "INSTALL_FAILED_UPDATE_INCOMPATIBLE"

The app is already installed with a different key. Uninstall the old version first (or use the same key).

---

## CHECKSUMS.txt Format

```
# CHECKSUMS.txt - Generated by regen-app-stack
# Generated: 2024-01-15T12:00:00Z

# SHA256 checksums
app-v1.2.0.apk         abc123def456...  app-v1.2.0.apk
app-v1.2.0.apk.sig     789xyz012345...  app-v1.2.0.apk.sig (PGP signature)
release-notes.txt      def789abc012...  release-notes.txt
release-notes.txt.asc  345abc789xyz...  release-notes.txt.asc (PGP signature)

# Verification:
# sha256sum -c CHECKSUMS.txt
# gpg --verify release-notes.txt.asc release-notes.txt
```

---

## Related Tools

- **SemVer** — Version numbering: https://semver.org/
- **Android APK Analyzer** — Inspect APK contents
- **apktool** — Decompile and analyze APKs
- **Frida** — Security testing framework
