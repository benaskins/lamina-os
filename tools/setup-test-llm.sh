#!/bin/bash
set -e

echo "🧪 Setting up lightweight LLM for sigil comprehension testing"

# Start the test LLM container
echo "🐳 Starting Ollama container..."
docker-compose -f tools/docker-compose.test-llm.yml up -d

# Wait for container to be ready
echo "⏳ Waiting for Ollama to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:11435/api/version > /dev/null; then
        echo "✅ Ollama is ready!"
        break
    fi
    echo "Waiting... ($i/30)"
    sleep 2
done

# Pull a lightweight model for testing
echo "📥 Pulling lightweight test model (phi3:mini - ~2.3GB)..."
docker exec lamina-test-llm ollama pull phi3:mini

echo "✅ Test LLM setup complete!"
echo "🔗 API available at: http://localhost:11435"
echo "🧪 Ready for sigil comprehension testing"