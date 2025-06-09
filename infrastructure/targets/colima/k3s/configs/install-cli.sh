#!/bin/bash

# 🜄 Lamina Environment CLI Installer
# Sets up unified environment management command

set -euo pipefail

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="/opt/homebrew/bin"

log "Installing Lamina Environment Manager..."

# Copy the script to a location in PATH
sudo cp "$SCRIPT_DIR/lamina-env" "$BIN_DIR/lamina-env"
sudo chmod +x "$BIN_DIR/lamina-env"

# Create convenient alias
if ! grep -q "alias lamina=" ~/.zshrc 2>/dev/null; then
    echo 'alias lamina="lamina-env"' >> ~/.zshrc
    log "Added 'lamina' alias to ~/.zshrc"
fi

success "Lamina Environment Manager installed!"
echo ""
echo "🜄 Quick Start:"
echo "  lamina dev start      # Start development environment"  
echo "  lamina prod start     # Start production environment"
echo "  lamina status         # Check both environments"
echo "  lamina prod ui        # Open production monitoring"
echo ""
echo "🔄 Reload your shell: source ~/.zshrc"
echo "📖 Full help: lamina help"