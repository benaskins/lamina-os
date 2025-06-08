#!/bin/bash

# 🜄 Lamina OS Production K3s Installation Script
# Optimized for Apple Silicon Mac hardware
# Creates production-ready single-node cluster

set -euo pipefail

echo "🜄 Installing Lamina OS Production K3s Cluster on Mac..."

# Configuration
K3S_DATA_DIR="/opt/lamina/k3s"
K3S_STORAGE_DIR="/opt/lamina/storage"
K3S_VERSION="${K3S_VERSION:-latest}"
KUBECONFIG_PATH="${HOME}/.kube/config"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    error "This script is designed for macOS only"
fi

# Check for Apple Silicon
if [[ "$(uname -m)" != "arm64" ]]; then
    warning "This script is optimized for Apple Silicon (M1/M2/M3), but will work on Intel Macs"
fi

# Check available memory and CPU
TOTAL_MEMORY_GB=$(( $(sysctl -n hw.memsize) / 1024 / 1024 / 1024 ))
CPU_COUNT=$(sysctl -n hw.ncpu)
CHIP_INFO=$(system_profiler SPHardwareDataType | grep "Chip:" | awk '{print $2, $3}')

log "Hardware Detected: $CHIP_INFO"
log "System Resources: $CPU_COUNT cores, ${TOTAL_MEMORY_GB}GB RAM"

# Optimize settings based on available memory
if [[ $TOTAL_MEMORY_GB -lt 16 ]]; then
    error "Minimum 16GB RAM required for production workloads. You have ${TOTAL_MEMORY_GB}GB"
elif [[ $TOTAL_MEMORY_GB -lt 32 ]]; then
    warning "16-32GB detected. Consider upgrading for heavy AI workloads."
    MEMORY_PROFILE="small"
elif [[ $TOTAL_MEMORY_GB -lt 128 ]]; then
    success "32-128GB detected. Good for moderate AI workloads."
    MEMORY_PROFILE="medium"
elif [[ $TOTAL_MEMORY_GB -lt 256 ]]; then
    success "128-256GB detected. Excellent for heavy AI workloads."
    MEMORY_PROFILE="large"
else
    success "256GB+ detected. Enterprise-class AI compute capability!"
    MEMORY_PROFILE="enterprise"
fi

# CPU optimization based on core count
if [[ $CPU_COUNT -lt 8 ]]; then
    warning "Minimum 8 CPU cores recommended for production. You have $CPU_COUNT"
elif [[ $CPU_COUNT -ge 20 ]]; then
    success "High-performance CPU detected ($CPU_COUNT cores)"
    CPU_PROFILE="high_performance"
else
    success "Good CPU configuration ($CPU_COUNT cores)"
    CPU_PROFILE="standard"
fi

# Create directories with proper permissions
log "Creating Lamina directories..."
sudo mkdir -p "$K3S_DATA_DIR" "$K3S_STORAGE_DIR"
sudo chown -R "$USER:staff" "/opt/lamina"
chmod 755 "/opt/lamina" "$K3S_DATA_DIR" "$K3S_STORAGE_DIR"
success "Created directories: $K3S_DATA_DIR, $K3S_STORAGE_DIR"

# Install k3s with production configuration
log "Installing k3s server optimized for $MEMORY_PROFILE memory profile..."

# Dynamic configuration based on hardware
case $MEMORY_PROFILE in
    "enterprise")
        MAX_PODS=200                          # Realistic pod count
        KUBE_RESERVED_CPU="2000m"             # 2 cores for k3s
        KUBE_RESERVED_MEM="8Gi"               # 8GB for k3s
        SYSTEM_RESERVED_CPU="4000m"           # 4 cores for macOS + Colima
        SYSTEM_RESERVED_MEM="32Gi"            # 32GB for macOS + Colima + buffer
        EVICTION_HARD="16Gi"                  # Conservative eviction
        API_REQUESTS_INFLIGHT=800             # Moderate throughput
        API_MUTATING_REQUESTS=400
        ETCD_QUOTA="10737418240"              # 10GB etcd (realistic)
        ;;
    "large")
        MAX_PODS=500
        KUBE_RESERVED_CPU="2000m"
        KUBE_RESERVED_MEM="8Gi"
        SYSTEM_RESERVED_CPU="1000m"
        SYSTEM_RESERVED_MEM="4Gi"
        EVICTION_HARD="16Gi"
        API_REQUESTS_INFLIGHT=1000
        API_MUTATING_REQUESTS=500
        ETCD_QUOTA="21474836480"  # 20GB
        ;;
    "medium")
        MAX_PODS=250
        KUBE_RESERVED_CPU="1500m"
        KUBE_RESERVED_MEM="4Gi"
        SYSTEM_RESERVED_CPU="1000m"
        SYSTEM_RESERVED_MEM="2Gi"
        EVICTION_HARD="8Gi"
        API_REQUESTS_INFLIGHT=600
        API_MUTATING_REQUESTS=300
        ETCD_QUOTA="10737418240"  # 10GB
        ;;
    *)
        MAX_PODS=150
        KUBE_RESERVED_CPU="1000m"
        KUBE_RESERVED_MEM="2Gi"
        SYSTEM_RESERVED_CPU="500m"
        SYSTEM_RESERVED_MEM="2Gi"
        EVICTION_HARD="4Gi"
        API_REQUESTS_INFLIGHT=400
        API_MUTATING_REQUESTS=200
        ETCD_QUOTA="8589934592"  # 8GB
        ;;
esac

log "Configuration: max-pods=$MAX_PODS, kube-reserved=$KUBE_RESERVED_MEM, eviction-hard=$EVICTION_HARD"

# K3s installation with dynamically optimized settings
curl -sfL https://get.k3s.io | INSTALL_K3S_VERSION="$K3S_VERSION" sh -s - server \
    --data-dir="$K3S_DATA_DIR" \
    --disable=traefik \
    --disable=servicelb \
    --disable=metrics-server \
    --cluster-cidr="10.42.0.0/16" \
    --service-cidr="10.43.0.0/16" \
    --flannel-backend=host-gw \
    --kubelet-arg="--max-pods=$MAX_PODS" \
    --kubelet-arg="--kube-reserved=cpu=$KUBE_RESERVED_CPU,memory=$KUBE_RESERVED_MEM" \
    --kubelet-arg="--system-reserved=cpu=$SYSTEM_RESERVED_CPU,memory=$SYSTEM_RESERVED_MEM" \
    --kubelet-arg="--eviction-hard=memory.available<$EVICTION_HARD" \
    --kubelet-arg="--serialize-image-pulls=false" \
    --kubelet-arg="--cpu-manager-policy=static" \
    --kubelet-arg="--topology-manager-policy=single-numa-node" \
    --kube-apiserver-arg="--max-requests-inflight=$API_REQUESTS_INFLIGHT" \
    --kube-apiserver-arg="--max-mutating-requests-inflight=$API_MUTATING_REQUESTS" \
    --kube-apiserver-arg="--target-ram-mb=8192" \
    --kube-controller-manager-arg="--concurrent-deployment-syncs=50" \
    --kube-controller-manager-arg="--concurrent-service-syncs=25" \
    --etcd-arg="--quota-backend-bytes=$ETCD_QUOTA" \
    --etcd-arg="--auto-compaction-retention=30m" \
    --etcd-arg="--auto-compaction-mode=periodic" \
    --etcd-arg="--max-request-bytes=10485760"

success "k3s server installed successfully"

# Wait for k3s to be ready
log "Waiting for k3s to be ready..."
sleep 10

# Set up kubectl configuration
log "Configuring kubectl..."
mkdir -p "$(dirname "$KUBECONFIG_PATH")"
sudo cp /etc/rancher/k3s/k3s.yaml "$KUBECONFIG_PATH"
sudo chown "$USER:staff" "$KUBECONFIG_PATH"
chmod 600 "$KUBECONFIG_PATH"

# Test cluster connectivity
log "Testing cluster connectivity..."
if kubectl cluster-info &>/dev/null; then
    success "kubectl configured successfully"
else
    error "Failed to configure kubectl"
fi

# Label the node for Lamina workloads
NODE_NAME=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')
kubectl label node "$NODE_NAME" lamina.ai/workload-type=ai-compute --overwrite
kubectl label node "$NODE_NAME" lamina.ai/hardware=apple-silicon --overwrite
kubectl label node "$NODE_NAME" lamina.ai/environment=production --overwrite
success "Labeled node for Lamina workloads"

# Create lamina-production namespace
log "Creating lamina-production namespace..."
kubectl create namespace lamina-production || true
kubectl label namespace lamina-production name=lamina-production --overwrite
kubectl label namespace lamina-production lamina.ai/environment=production --overwrite
success "Created lamina-production namespace"

# Apply the k3s configuration
log "Applying Lamina production configuration..."
kubectl apply -f "$(dirname "$0")/k3s-config.yaml"
success "Applied production configuration"

# Install essential production components
log "Installing production components..."

# Install cert-manager for TLS
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.3/cert-manager.yaml
log "Installed cert-manager"

# Install nginx-ingress
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.9.4/deploy/static/provider/cloud/deploy.yaml
log "Installed nginx-ingress"

# Install MetalLB for LoadBalancer services
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.13.12/config/manifests/metallb-native.yaml
log "Installed MetalLB"

# Wait for core components
log "Waiting for core components to be ready..."
kubectl wait --for=condition=Ready pods --all -n cert-manager --timeout=300s
kubectl wait --for=condition=Ready pods --all -n ingress-nginx --timeout=300s
kubectl wait --for=condition=Ready pods --all -n metallb-system --timeout=300s

success "All core components ready"

# Configure MetalLB IP pool (using Docker Desktop range)
cat <<EOF | kubectl apply -f -
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: lamina-pool
  namespace: metallb-system
spec:
  addresses:
  - 192.168.1.240-192.168.1.250
---
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
  name: lamina-l2
  namespace: metallb-system
spec:
  ipAddressPools:
  - lamina-pool
EOF

success "Configured MetalLB IP pool"

# Display cluster information
echo ""
echo "🜄 Lamina OS Production Cluster Ready!"
echo ""
echo "Cluster Information:"
echo "==================="
kubectl cluster-info
echo ""
echo "Node Information:"
echo "=================="
kubectl get nodes -o wide
echo ""
echo "Namespaces:"
echo "==========="
kubectl get namespaces
echo ""
echo "Storage Classes:"
echo "================"
kubectl get storageclass
echo ""

success "Production k3s cluster installation complete!"
success "Your Mac is now running a production-ready Kubernetes cluster"

echo ""
echo "Next steps:"
echo "1. Deploy monitoring stack: helm install prometheus prometheus-community/kube-prometheus-stack"
echo "2. Deploy Lamina services: kubectl apply -f charts/lamina-production/"
echo "3. Access services via: kubectl port-forward or LoadBalancer IPs"
echo ""
echo "Cluster management:"
echo "- Start: sudo systemctl start k3s (Linux) or manually restart on Mac"
echo "- Stop: sudo systemctl stop k3s"  
echo "- Logs: sudo journalctl -u k3s -f"
echo ""