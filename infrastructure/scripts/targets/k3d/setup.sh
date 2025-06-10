#!/bin/bash
set -euo pipefail

ENV="development"
while [ $# -gt 0 ]; do
    case "$1" in
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
INFRA_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"
TARGET_DIR="$INFRA_DIR/targets/k3d"
ENV_FILE="$INFRA_DIR/environments/$ENV/values.yaml"
CLUSTER_NAME="lamina-$ENV"

# Ensure prerequisites
for cmd in k3d kubectl helm; do
    command -v "$cmd" >/dev/null 2>&1 || { echo "Missing $cmd"; exit 1; }
done

# Create cluster if it doesn't exist
if ! k3d cluster list | grep -q "^$CLUSTER_NAME"; then
    echo "🛠 Creating k3d cluster $CLUSTER_NAME"
    k3d cluster create "$CLUSTER_NAME" --wait
else
    echo "✅ k3d cluster $CLUSTER_NAME already exists"
fi

# Wait for nodes
kubectl wait --for=condition=Ready nodes --all --timeout=300s

# Install components
helm upgrade --install metallb "$TARGET_DIR/metallb" -n metallb-system --create-namespace --wait
helm upgrade --install service-mesh "$TARGET_DIR/service-mesh" -n istio-system --create-namespace --wait
helm upgrade --install k3d-service-mesh "$TARGET_DIR/k3d-service-mesh" -n istio-system --wait
helm upgrade --install monitoring "$TARGET_DIR/monitoring" -n monitoring --values "$ENV_FILE" --wait
helm upgrade --install observability "$TARGET_DIR/observability" -n observability --values "$ENV_FILE" --wait
helm upgrade --install lamina-llm-serve "$TARGET_DIR/lamina-llm-serve" -n lamina-llm-serve --values "$ENV_FILE" --wait

echo "🎉 k3d cluster setup complete"
