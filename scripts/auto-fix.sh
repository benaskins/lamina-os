#!/bin/bash
# Auto-fix linting and formatting issues quickly

set -e

echo "🔧 Auto-fixing linting issues..."
uv run ruff check --fix

echo "🎨 Auto-formatting code..."
uv run ruff format

echo "✅ Auto-fix complete! Run 'git add -A && git commit' to commit changes."