#!/usr/bin/env bash
#
# sign-apk.sh - Sign an Android APK with a developer keystore
#
# Usage:
#   ./sign-apk.sh <input.apk> <keystore.jks> <password> [output.apk]
#
# Requirements:
#   - Android SDK Build Tools (apksigner)
#   - keytool (usually comes with JDK)
#
# The script enables v1, v2, and v3 signing schemes for maximum compatibility.
#

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

usage() {
    echo "Usage: $0 <input.apk> <keystore> <password> [output.apk]"
    echo ""
    echo "Arguments:"
    echo "  input.apk    Path to the unsigned APK to sign"
    echo "  keystore      Path to .jks or .p12 keystore file"
    echo "  password      Keystore password"
    echo "  output.apk    Path for signed APK (default: <input>-signed.apk)"
    echo ""
    echo "Examples:"
    echo "  $0 app-unsigned.apk release-key.jks 'mypassword'"
    echo "  $0 ./build/app.apk ./keys/prod.jks 'secret123' ./release/app-signed.apk"
    exit 1
}

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check arguments
if [[ $# -lt 3 ]]; then
    log_error "Missing required arguments"
    usage
fi

INPUT_APK="$1"
KEYSTORE="$2"
PASSWORD="$3"
OUTPUT_APK="${4:-}"

# Resolve paths
INPUT_APK="$(realpath "$INPUT_APK" 2>/dev/null || echo "$INPUT_APK")"
KEYSTORE="$(realpath "$KEYSTORE" 2>/dev/null || echo "$KEYSTORE")"

# Default output name
if [[ -z "$OUTPUT_APK" ]]; then
    BASENAME="${INPUT_APK%.apk}"
    OUTPUT_APK="${BASENAME}-signed.apk"
fi
OUTPUT_APK="$(realpath "$(dirname "$OUTPUT_APK")"/"$(basename "$OUTPUT_APK")" 2>/dev/null || echo "$OUTPUT_APK")"

# Check input file exists
if [[ ! -f "$INPUT_APK" ]]; then
    log_error "Input APK not found: $INPUT_APK"
    exit 1
fi

# Check keystore exists
if [[ ! -f "$KEYSTORE" ]]; then
    log_error "Keystore not found: $KEYSTORE"
    exit 1
fi

# Check for apksigner
if ! command -v apksigner &> /dev/null; then
    log_error "apksigner not found. Install Android SDK Build Tools."
    log_info "macOS: brew install android-sdk"
    log_info "Or download from: https://developer.android.com/studio/releases/build-tools"
    exit 1
fi

# Detect keystore type
KEYSTORE_TYPE="jks"
case "${KEYSTORE,,}" in
    *.p12|*.pkcs12)
        KEYSTORE_TYPE="pkcs12"
        ;;
esac

log_info "Signing APK"
log_info "  Input:    $INPUT_APK"
log_info "  Output:   $OUTPUT_APK"
log_info "  Keystore: $KEYSTORE ($KEYSTORE_TYPE)"

# Create temp directory for signing
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

# Sign the APK
# Using all signing schemes (v1, v2, v3) for maximum compatibility
log_info "Running apksigner..."

apksigner sign \
    --ks "$KEYSTORE" \
    --ks-type "$KEYSTORE_TYPE" \
    --ks-pass "pass:$PASSWORD" \
    --key-pass "pass:$PASSWORD" \
    --v1-signing-enabled true \
    --v2-signing-enabled true \
    --v3-signing-enabled true \
    --out "$OUTPUT_APK" \
    "$INPUT_APK"

if [[ $? -eq 0 ]]; then
    log_info "APK signed successfully!"
    
    # Show file sizes
    INPUT_SIZE=$(du -h "$INPUT_APK" | cut -f1)
    OUTPUT_SIZE=$(du -h "$OUTPUT_APK" | cut -f1)
    log_info "  Input size:  $INPUT_SIZE"
    log_info "  Output size: $OUTPUT_SIZE"
    
    # Verify the signature
    log_info ""
    log_info "Verifying signature..."
    if apksigner verify --verbose "$OUTPUT_APK" 2>&1 | tee /dev/stderr | grep -q "Verified"; then
        log_info "Signature verified ✓"
    else
        log_warn "Verification returned but may have warnings"
    fi
    
    echo ""
    log_info "Done! Signed APK: $OUTPUT_APK"
else
    log_error "Signing failed!"
    exit 1
fi
