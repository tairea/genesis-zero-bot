#!/usr/bin/env bash
#
# verify-apk.sh - Verify APK signature and print certificate info
#
# Usage:
#   ./verify-apk.sh <apk-file>
#
# Requirements:
#   - apksigner (Android SDK Build Tools)
#   - keytool (JDK)
#

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

usage() {
    echo "Usage: $0 <apk-file>"
    echo ""
    echo "Verify the signature and print certificate details for an APK."
    exit 1
}

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check arguments
if [[ $# -lt 1 ]]; then
    log_error "Missing APK file argument"
    usage
fi

APK_FILE="$1"
APK_FILE="$(realpath "$APK_FILE" 2>/dev/null || echo "$APK_FILE")"

# Check file exists
if [[ ! -f "$APK_FILE" ]]; then
    log_error "APK not found: $APK_FILE"
    exit 1
fi

# Check for apksigner
if ! command -v apksigner &> /dev/null; then
    log_error "apksigner not found. Install Android SDK Build Tools."
    log_info "macOS: brew install android-sdk"
    exit 1
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  APK Signature Verification"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "  File: $(basename "$APK_FILE")"
echo "  Size: $(du -h "$APK_FILE" | cut -f1)"
echo "  MD5:  $(md5sum "$APK_FILE" | cut -d' ' -f1)"
echo ""

# Verify and print details
echo -e "${CYAN}─────────────────────────────────────────────────────────────────${NC}"
echo -e "${CYAN}Signature Verification Result:${NC}"
echo -e "${CYAN}─────────────────────────────────────────────────────────────────${NC}"

if apksigner verify --print-certs "$APK_FILE" 2>&1; then
    VERIFY_RESULT=0
else
    VERIFY_RESULT=$?
fi

echo ""
echo -e "${CYAN}─────────────────────────────────────────────────────────────────${NC}"
echo -e "${CYAN}Detailed Certificate Information:${NC}"
echo -e "${CYAN}─────────────────────────────────────────────────────────────────${NC}"

# Extract and display certificate info
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

# Use apksigner to extract certificate details
apksigner verify --print-certs "$APK_FILE" > "$TEMP_DIR/certs.txt" 2>&1 || true

if grep -q "Signer #1 certificate" "$TEMP_DIR/certs.txt"; then
    # Extract certificate fingerprint for comparison
    CERT_LINE=$(grep "SHA-256" "$TEMP_DIR/certs.txt" | head -1 || echo "")
    if [[ -n "$CERT_LINE" ]]; then
        echo ""
        echo -e "${YELLOW}Certificate SHA-256 (for verification):${NC}"
        # Extract just the fingerprint
        FINGERPRINT=$(echo "$CERT_LINE" | sed 's/.*SHA-256: */SHA-256: /')
        echo "  ${FINGERPRINT}"
        echo ""
        echo "  Share this fingerprint so users can verify authenticity."
    fi
fi

# Check which signing schemes were used
echo ""
echo -e "${CYAN}Signing Schemes Detected:${NC}"
for scheme in v1 v2 v3; do
    if grep -qi "$scheme signing" "$TEMP_DIR/certs.txt"; then
        echo -e "  ✓ ${GREEN}${scheme^^}${NC}"
    fi
done

echo ""
echo "═══════════════════════════════════════════════════════════"

if [[ $VERIFY_RESULT -eq 0 ]]; then
    echo -e "${GREEN}✓ APK signature is VALID${NC}"
    echo ""
    echo "This APK was signed by the developer and has not been"
    echo "modified since signing."
else
    echo -e "${RED}✗ APK signature verification FAILED${NC}"
    echo ""
    echo "The APK may have been tampered with or was not signed."
    exit 1
fi

# Optional: offer to check against VirusTotal
echo ""
echo "─────────────────────────────────────────────────────────────────"
echo "Optional: VirusTotal Check"
echo "─────────────────────────────────────────────────────────────────"
echo "To check this APK against VirusTotal's malware database:"
echo ""
echo "  1. Go to https://www.virustotal.com/gui/"
echo "  2. Upload the APK or paste its hash"
echo ""
echo "Or use the API (rate-limited, requires free account):"
echo ""
echo "  curl -X POST \\"
echo "    -F 'file=@$APK_FILE' \\"
echo "    -F 'apikey=YOUR_VT_API_KEY' \\"
echo "    https://www.virustotal.com/api/v3/files"
echo ""
