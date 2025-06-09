#!/bin/sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Source logging and event libraries
. "$SCRIPT_DIR/lib/logging.sh"
. "$SCRIPT_DIR/lib/event-ingestion.sh"

# Initialize logging
init_logging

# Colors for output (POSIX compatible)
if [ -t 1 ]; then
    GREEN='\033[0;32m'
    NC='\033[0m'
else
    GREEN=''
    NC=''
fi

log() {
    printf "%s[%s] ✓ %s%s\n" "$GREEN" "$(date +'%Y-%m-%d %H:%M:%S')" "$1" "$NC"
    log_info "setup" "$1"
}

log "Setup logging test - this should be visible"
log "Second test message"