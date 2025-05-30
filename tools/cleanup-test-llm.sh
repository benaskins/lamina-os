#!/bin/bash
set -e

echo "🧹 Cleaning up test LLM container and resources"

# Stop and remove container
echo "🛑 Stopping test LLM container..."
docker-compose -f tools/docker-compose.test-llm.yml down -v

# Remove downloaded models (optional - comment out to keep models)
echo "🗑️ Removing test LLM models..."
if [ -d "./tools/test-llm-models" ]; then
    rm -rf ./tools/test-llm-models
    echo "✅ Test LLM models removed"
fi

echo "✅ Test LLM cleanup complete!"
echo "💡 Models were removed. Next test run will re-download (~2.3GB)"