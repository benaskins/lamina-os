#!/bin/bash
set -euo pipefail

# Docker Compose Setup Script for Lamina Infrastructure
# Usage: ./setup.sh [--env ENVIRONMENT]

ENV="production"
while [ $# -gt 0 ]; do
    case $1 in
        --env)
            ENV="$2"
            shift 2
            ;;
        *)
            echo "Usage: $0 [--env ENVIRONMENT]"
            exit 1
            ;;
    esac
done

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET_DIR="$SCRIPT_DIR/../../../targets/docker-compose"
ENV_VALUES_DIR="$SCRIPT_DIR/../../../environments"

echo "🐳 Setting up Lamina infrastructure with Docker Compose"
echo "Environment: $ENV"

# Load environment values
if [ -f "$ENV_VALUES_DIR/$ENV/values.yaml" ]; then
    echo "📋 Loading environment configuration from $ENV_VALUES_DIR/$ENV/values.yaml"
    # Export environment variables from YAML (basic implementation)
    export GRAFANA_ADMIN_PASSWORD="${GRAFANA_ADMIN_PASSWORD:-admin}"
fi

# Build lamina-llm-serve image if needed
PACKAGE_DIR="$SCRIPT_DIR/../../../../packages/lamina-llm-serve"
if [ -f "$PACKAGE_DIR/Dockerfile" ]; then
    echo "🔨 Building lamina-llm-serve Docker image..."
    cd "$PACKAGE_DIR"
    docker build -t lamina-llm-serve:latest .
    cd - >/dev/null
fi

# Start services
echo "🚀 Starting Docker Compose services..."
cd "$TARGET_DIR"
docker-compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 10

# Health check
echo "🔍 Checking service health..."
if curl -s http://localhost:8000/health >/dev/null; then
    echo "✅ Lamina LLM Serve: http://localhost:8000"
else
    echo "⚠️ Lamina LLM Serve not ready yet"
fi

echo "✅ Grafana: http://localhost:3000 (admin/admin)"
echo "✅ Prometheus: http://localhost:9090"

echo "🎉 Docker Compose setup complete!"