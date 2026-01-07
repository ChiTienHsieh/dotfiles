#!/usr/bin/env zsh
# =============================================================================
# test_aliases.sh - Basic tests for .aliases
# =============================================================================
# Usage: ./test/test_aliases.sh
#
# Tests:
#   1. Syntax check (zsh -n)
#   2. Source without error
#   3. Expected functions exist

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DOTFILES_DIR="$(dirname "$SCRIPT_DIR")"
ALIASES_FILE="$DOTFILES_DIR/bash/.aliases"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

pass() { echo "${GREEN}✓${NC} $1"; }
fail() { echo "${RED}✗${NC} $1"; exit 1; }
info() { echo "${YELLOW}→${NC} $1"; }

# =============================================================================
# Test 1: Syntax check
# =============================================================================
info "Testing syntax (zsh -n)..."
if zsh -n "$ALIASES_FILE" 2>/dev/null; then
    pass "Syntax OK"
else
    fail "Syntax error in $ALIASES_FILE"
fi

# =============================================================================
# Test 2: Source without error
# =============================================================================
info "Testing source..."
if zsh -c "source '$ALIASES_FILE'" 2>/dev/null; then
    pass "Source OK"
else
    fail "Failed to source $ALIASES_FILE"
fi

# =============================================================================
# Test 3: Expected functions exist
# =============================================================================
EXPECTED_FUNCTIONS=(
    trash
    bak
    hide
    addali
    addcd
    p
    a
    todo
    pp
    pc
    wheredef
)

info "Checking expected functions..."
for func in "${EXPECTED_FUNCTIONS[@]}"; do
    if zsh -c "source '$ALIASES_FILE' && type $func" &>/dev/null; then
        pass "Function: $func"
    else
        fail "Missing function: $func"
    fi
done

# =============================================================================
# Test 4: Expected aliases exist
# =============================================================================
EXPECTED_ALIASES=(
    ll
    vi
    src
    t
)

info "Checking expected aliases..."
for ali in "${EXPECTED_ALIASES[@]}"; do
    if zsh -c "source '$ALIASES_FILE' && alias $ali" &>/dev/null; then
        pass "Alias: $ali"
    else
        fail "Missing alias: $ali"
    fi
done

# =============================================================================
# Test 5: wheredef can find itself
# =============================================================================
info "Testing wheredef functionality..."
output=$(zsh -c "source '$ALIASES_FILE' && wheredef trash" 2>&1)
if echo "$output" | grep -q "\.aliases"; then
    pass "wheredef found trash in .aliases"
else
    fail "wheredef couldn't find trash"
fi

echo ""
echo "${GREEN}All tests passed!${NC} (ﾉ◕ヮ◕)ﾉ*:･ﾟ✧"
