#!/bin/bash
# Convenient build check script that can be run from project root

set -e

echo "🔨 Running containerized build checks..."

# Change to build-env directory
cd "$(dirname "$0")/../build-env"

# Run the checks
make check

echo "✅ All build checks passed!"