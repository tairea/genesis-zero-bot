#!/bin/bash
# regen-viz validation script
# Runs comprehensive tests before publishing

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Defaults
VERBOSE=false
PATH_SET=false
JSON_FILE=""
HTML_FILE=""

# Usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --path DIR       Test entire visualization directory"
    echo "  --json FILE      Test specific JSON file"
    echo "  --html FILE      Test specific HTML file"
    echo "  --verbose        Verbose output"
    echo "  -h, --help       Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 --path ~/.openclaw/workspace-genesis/regen-viz"
    echo "  $0 --json data/graph.json"
    echo "  $0 --path ~/regen-viz --verbose"
    exit 0
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --path)
            TEST_PATH="$2"
            PATH_SET=true
            shift 2
            ;;
        --json)
            JSON_FILE="$2"
            shift 2
            ;;
        --html)
            HTML_FILE="$2"
            shift 2
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo "Unknown option: $1"
            usage
            ;;
    esac
done

# Functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_pass() { echo -e "${GREEN}[PASS]${NC} $1"; }
log_fail() { echo -e "${RED}[FAIL]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

# Test JSON file
test_json() {
    local file="$1"
    if [[ ! -f "$file" ]]; then
        log_fail "$file does not exist"
        return 1
    fi
    
    # Check valid JSON
    if ! python3 -c "import json; json.load(open('$file'))" 2>/dev/null; then
        log_fail "$file - invalid JSON"
        return 1
    fi
    
    # Check required fields
    local nodes=$(python3 -c "import json; d=json.load(open('$file')); print(len(d.get('nodes', [])))" 2>/dev/null)
    local links=$(python3 -c "import json; d=json.load(open('$file')); print(len(d.get('links', [])))" 2>/dev/null)
    
    if [[ "$nodes" == "0" ]] && [[ "$links" == "0" ]]; then
        log_warn "$file - no nodes or links found"
    fi
    
    log_pass "$(basename $file) ($nodes nodes, $links links)"
    return 0
}

# Test HTML file
test_html() {
    local file="$1"
    if [[ ! -f "$file" ]]; then
        log_fail "$file does not exist"
        return 1
    fi
    
    # Check basic HTML structure
    if ! grep -q "<html" "$file"; then
        log_fail "$file - missing <html> tag"
        return 1
    fi
    if ! grep -q "</html>" "$file"; then
        log_fail "$file - missing </html> tag"
        return 1
    fi
    if ! grep -q "<head>" "$file"; then
        log_fail "$file - missing <head> tag"
        return 1
    fi
    if ! grep -q "</head>" "$file"; then
        log_fail "$file - missing </head> tag"
        return 1
    fi
    if ! grep -q "<body>" "$file"; then
        log_fail "$file - missing <body> tag"
        return 1
    fi
    if ! grep -q "</body>" "$file"; then
        log_fail "$file - missing </body> tag"
        return 1
    fi
    
    log_pass "$(basename $file) - valid structure"
    return 0
}

# Test dependencies
test_deps() {
    log_info "Checking dependencies..."
    
    local deps=("git" "curl" "jq" "python3")
    local missing=0
    
    for dep in "${deps[@]}"; do
        if command -v "$dep" &> /dev/null; then
            log_pass "$dep available"
        else
            log_fail "$dep not found"
            ((missing++))
        fi
    done
    
    # Check CDN accessibility
    if curl -s --max-time 10 "https://cdn.jsdelivr.net/npm/3d-force-graph" > /dev/null 2>&1; then
        log_pass "3d-force-graph CDN accessible"
    else
        log_warn "3d-force-graph CDN not accessible (offline mode)"
    fi
    
    if [[ $missing -gt 0 ]]; then
        return 3
    fi
    return 0
}

# Test git repository
test_git() {
    local dir="$1"
    log_info "Checking git repository..."
    
    if [[ ! -d "$dir/.git" ]]; then
        log_warn "Not a git repository"
        return 0  # Not an error
    fi
    
    cd "$dir"
    
    # Check remote
    local remote=$(git remote get-url origin 2>/dev/null || echo "")
    if [[ -n "$remote" ]]; then
        log_pass "Remote: $remote"
    else
        log_warn "No remote configured"
    fi
    
    # Check branch
    local branch=$(git branch --show-current 2>/dev/null || echo "")
    if [[ -n "$branch" ]]; then
        log_pass "Branch: $branch"
    else
        log_warn "No branch found"
    fi
    
    return 0
}

# Test file paths
test_paths() {
    local dir="$1"
    log_info "Checking file references..."
    
    local errors=0
    
    # Check HTML references to JSON
    for html in "$dir"/html/*.html; do
        [[ -f "$html" ]] || continue
        
        # Extract jsonUrl references
        refs=$(grep -oP "jsonUrl\(['\"]\.\.\/data\/[^\"']+" "$html" 2>/dev/null || echo "")
        for ref in $refs; do
            ref="${ref##*data/}"
            json_file="$dir/data/$ref"
            if [[ ! -f "$json_file" ]]; then
                log_fail "$(basename $html) references missing: data/$ref"
                ((errors++))
            fi
        done
    done
    
    if [[ $errors -eq 0 ]]; then
        log_pass "All file references valid"
    fi
    
    return $errors
}

# Main test runner
run_tests() {
    local path="$1"
    local errors=0
    
    echo "=============================================="
    echo "  regen-viz Validation Report"
    echo "=============================================="
    echo "Path: $path"
    echo "Date: $(date -Iseconds)"
    echo ""
    
    # JSON tests
    if [[ -d "$path/data" ]]; then
        echo -e "${BLUE}[JSON]${NC} Validating JSON files..."
        for json in "$path"/data/**/*.json "$path"/data/*.json; do
            [[ -f "$json" ]] || continue
            test_json "$json" || ((errors++))
        done
        echo ""
    elif [[ -n "$JSON_FILE" ]]; then
        echo -e "${BLUE}[JSON]${NC} Validating JSON file..."
        test_json "$JSON_FILE" || ((errors++))
        echo ""
    fi
    
    # HTML tests
    if [[ -d "$path/html" ]]; then
        echo -e "${BLUE}[HTML]${NC} Validating HTML files..."
        for html in "$path"/html/*.html; do
            [[ -f "$html" ]] || continue
            test_html "$html" || ((errors++))
        done
        echo ""
    elif [[ -n "$HTML_FILE" ]]; then
        echo -e "${BLUE}[HTML]${NC} Validating HTML file..."
        test_html "$HTML_FILE" || ((errors++))
        echo ""
    fi
    
    # Dependency tests
    echo -e "${BLUE}[DEPS]${NC} Checking dependencies..."
    test_deps || ((errors++))
    echo ""
    
    # Git tests (only if path is a directory)
    if [[ -d "$path" ]]; then
        echo -e "${BLUE}[GIT]${NC} Checking repository..."
        test_git "$path" || ((errors++))
        echo ""
        
        # Path tests
        echo -e "${BLUE}[PATHS]${NC} Checking file references..."
        test_paths "$path" || ((errors++))
        echo ""
    fi
    
    # Summary
    echo "=============================================="
    if [[ $errors -eq 0 ]]; then
        echo -e "${GREEN}=== SUMMARY ==="
        echo "Status: ✓ READY TO PUBLISH${NC}"
    else
        echo -e "${RED}=== SUMMARY ==="
        echo "Status: ✗ $errors test(s) failed${NC}"
    fi
    echo "=============================================="
    
    return $errors
}

# Run tests
if [[ "$PATH_SET" == "true" ]]; then
    if [[ ! -d "$TEST_PATH" ]]; then
        log_fail "Path does not exist: $TEST_PATH"
        exit 5
    fi
    run_tests "$TEST_PATH"
elif [[ -n "$JSON_FILE" ]]; then
    test_json "$JSON_FILE"
elif [[ -n "$HTML_FILE" ]]; then
    test_html "$HTML_FILE"
else
    # No specific test, show help
    usage
fi
