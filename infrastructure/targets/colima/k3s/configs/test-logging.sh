#!/bin/sh

# Simple test script to verify logging
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Source logging library
. "$SCRIPT_DIR/lib/logging.sh"

# Initialize logging  
init_logging

# Colors
if [ -t 1 ]; then
    GREEN='\033[0;32m'
    NC='\033[0m'
else
    GREEN=''
    NC=''
fi

# Test function
test_log() {
    printf "%s[%s] ✓ %s%s\n" "$GREEN" "$(date +'%Y-%m-%d %H:%M:%S')" "$1" "$NC"
}

test_log "This should be visible immediately"
test_log "Second test message"