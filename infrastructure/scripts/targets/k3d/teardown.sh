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

CLUSTER_NAME="lamina-$ENV"

if k3d cluster list | grep -q "^$CLUSTER_NAME"; then
    echo "🗑 Deleting k3d cluster $CLUSTER_NAME"
    k3d cluster delete "$CLUSTER_NAME"
else
    echo "k3d cluster $CLUSTER_NAME not found"
fi

docker network rm "lamina-$ENV-net" >/dev/null 2>&1 || true

echo "✅ k3d teardown complete"
