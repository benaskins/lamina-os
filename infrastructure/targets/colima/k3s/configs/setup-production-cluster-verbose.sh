#!/bin/bash
set -euo pipefail

# Production Kubernetes Cluster Setup Script - Verbose Version
# This script sets up a complete production-grade k3s cluster on macOS
# with service mesh, observability, and monitoring - WITH FULL VISIBILITY

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFRA_DIR="$(dirname "$SCRIPT_DIR")"
CHARTS_DIR="$INFRA_DIR/charts"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Progress indicators
SPINNER='⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✓ $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠ WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ✗ ERROR: $1${NC}"
    exit 1
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] ℹ $1${NC}"
}

progress() {
    echo -e "${PURPLE}[$(date +'%Y-%m-%d %H:%M:%S')] ▶ $1${NC}"
}

section() {
    echo
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}▌ $1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Show what's running
show_status() {
    local context=$1
    echo
    echo -e "${CYAN}┌─ Current Status ─────────────────────────────────────────┐${NC}"
    
    # Colima status
    if command -v colima &> /dev/null; then
        local colima_status=$(colima list 2>/dev/null | grep -E "colima-production|PROFILE" || echo "No Colima profiles found")
        echo -e "${CYAN}│${NC} Colima: $colima_status"
    fi
    
    # k3d clusters
    if command -v k3d &> /dev/null; then
        local k3d_count=$(k3d cluster list 2>/dev/null | grep -c production || echo "0")
        echo -e "${CYAN}│${NC} k3d Clusters: $k3d_count production cluster(s)"
    fi
    
    # Kubernetes context
    if command -v kubectl &> /dev/null; then
        local kube_context=$(kubectl config current-context 2>/dev/null || echo "No context set")
        echo -e "${CYAN}│${NC} Kubectl Context: $kube_context"
        
        # Node status if cluster is up
        if kubectl get nodes &>/dev/null; then
            local node_count=$(kubectl get nodes --no-headers 2>/dev/null | wc -l | tr -d ' ')
            local ready_nodes=$(kubectl get nodes --no-headers 2>/dev/null | grep -c " Ready " || echo "0")
            echo -e "${CYAN}│${NC} Nodes: $ready_nodes/$node_count Ready"
        fi
    fi
    
    echo -e "${CYAN}└──────────────────────────────────────────────────────────┘${NC}"
    echo
}

# Check prerequisites with detailed output
check_prerequisites() {
    section "CHECKING PREREQUISITES"
    
    local tools=("colima" "kubectl" "helm" "k3d" "docker")
    local missing=()
    
    for tool in "${tools[@]}"; do
        progress "Checking for $tool..."
        if command -v $tool &> /dev/null; then
            local version=$($tool version 2>/dev/null | head -n1 || $tool --version 2>/dev/null | head -n1 || echo "version unknown")
            log "$tool found: $version"
        else
            error "$tool is not installed"
            missing+=($tool)
        fi
    done
    
    if [ ${#missing[@]} -gt 0 ]; then
        error "Missing tools: ${missing[*]}. Please install with: brew install ${missing[*]}"
    fi
    
    log "All prerequisites satisfied!"
    show_status "prerequisites"
}

# Setup Colima with visibility
setup_colima() {
    section "SETTING UP COLIMA PRODUCTION ENVIRONMENT"
    
    progress "Checking existing Colima profiles..."
    colima list 2>/dev/null || true
    
    # Check if colima-production profile exists and is running
    if colima list 2>/dev/null | grep -q "^colima-production.*Running"; then
        log "Colima production profile already running"
        info "Resources: $(colima list 2>/dev/null | grep colima-production)"
        return
    fi
    
    # Check if profile exists but stopped
    if colima list 2>/dev/null | grep -q "^colima-production.*Stopped"; then
        progress "Starting existing Colima production profile..."
        colima start -p colima-production
        log "Colima production profile started"
        return
    fi
    
    # Create new production profile
    progress "Creating new Colima production profile..."
    info "Configuration:"
    info "  • CPUs: 8"
    info "  • Memory: 16GB"
    info "  • Disk: 100GB"
    info "  • DNS: Google (8.8.8.8, 8.8.4.4)"
    info "  • Runtime: Kubernetes enabled"
    
    colima start -p colima-production \
        --cpu 8 \
        --memory 16 \
        --disk 100 \
        --dns 8.8.8.8 \
        --dns 8.8.4.4 \
        --kubernetes
    
    log "Colima production environment ready"
    show_status "colima"
}

# Create k3d cluster with visibility
setup_k3d_cluster() {
    section "SETTING UP K3D CLUSTER"
    
    progress "Checking existing k3d clusters..."
    k3d cluster list
    
    # Check if cluster already exists
    if k3d cluster list | grep -q "production"; then
        log "k3d production cluster already exists"
        k3d kubeconfig merge production --kubeconfig-switch-context
        show_status "k3d"
        return
    fi
    
    # Create k3d cluster with proper configuration
    progress "Creating k3d production cluster..."
    info "Configuration:"
    info "  • Server nodes: 1"
    info "  • Agent nodes: 2"
    info "  • Load balancer ports: 80, 443"
    info "  • Registry: production-registry:5000"
    info "  • Disabled: traefik, metrics-server"
    
    k3d cluster create production \
        --agents 2 \
        --port "80:80@loadbalancer" \
        --port "443:443@loadbalancer" \
        --k3s-arg "--disable=traefik@server:*" \
        --k3s-arg "--disable=metrics-server@server:*" \
        --registry-create production-registry:0.0.0.0:5000 \
        --wait
    
    # Switch kubectl context
    k3d kubeconfig merge production --kubeconfig-switch-context
    
    log "k3d cluster created successfully"
    
    # Show cluster info
    info "Cluster endpoints:"
    kubectl cluster-info
    
    show_status "k3d cluster"
}

# Wait for cluster with detailed progress
wait_for_cluster() {
    section "WAITING FOR CLUSTER TO BE READY"
    
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        progress "Checking cluster status... ($attempt/$max_attempts)"
        
        # Show node status
        kubectl get nodes 2>/dev/null || true
        
        if kubectl get nodes | grep -q "Ready"; then
            log "All nodes are ready!"
            
            # Show pod status in kube-system
            info "System pods status:"
            kubectl get pods -n kube-system
            
            return
        fi
        
        attempt=$((attempt + 1))
        sleep 10
    done
    
    error "Cluster failed to become ready within timeout"
}

# Install MetalLB with progress tracking
install_metallb() {
    section "INSTALLING METALLB LOAD BALANCER"
    
    progress "Checking if MetalLB is already installed..."
    helm list -n metallb-system
    
    # Check if already installed
    if helm list -n metallb-system | grep -q metallb; then
        log "MetalLB already installed"
        kubectl get pods -n metallb-system
        return
    fi
    
    # Add MetalLB Helm repository
    progress "Adding MetalLB Helm repository..."
    helm repo add metallb https://metallb.github.io/metallb
    helm repo update
    
    # Install MetalLB
    progress "Installing MetalLB..."
    helm install metallb metallb/metallb \
        --namespace metallb-system \
        --create-namespace \
        --wait
    
    # Show MetalLB pods
    info "MetalLB pods:"
    kubectl get pods -n metallb-system -w --timeout=60s &
    local watch_pid=$!
    
    # Wait for MetalLB to be ready
    kubectl wait --namespace metallb-system \
        --for=condition=ready pod \
        --selector=app.kubernetes.io/name=metallb \
        --timeout=300s
    
    kill $watch_pid 2>/dev/null || true
    
    # Install MetalLB configuration
    progress "Configuring MetalLB IP address pool..."
    info "IP Range: 192.168.5.240-192.168.5.250"
    
    helm install metallb-config "$CHARTS_DIR/metallb" \
        --namespace metallb-system \
        --wait
    
    log "MetalLB installed and configured"
    
    # Show configuration
    info "MetalLB configuration:"
    kubectl get ipaddresspools -n metallb-system
    kubectl get l2advertisements -n metallb-system
}

# Install Istio with detailed progress
install_istio() {
    section "INSTALLING ISTIO SERVICE MESH"
    
    progress "Checking if Istio is already installed..."
    helm list -n istio-system
    
    # Check if Istio is already installed
    if helm list -n istio-system | grep -q istio-base; then
        log "Istio already installed"
        kubectl get pods -n istio-system
        return
    fi
    
    # Add Istio Helm repository
    progress "Adding Istio Helm repository..."
    helm repo add istio https://istio-release.storage.googleapis.com/charts
    helm repo update
    
    # Install Istio base (CRDs)
    progress "Installing Istio base components (CRDs)..."
    helm install istio-base istio/base \
        --namespace istio-system \
        --create-namespace \
        --wait
    
    info "Istio CRDs installed:"
    kubectl get crds | grep istio | wc -l
    
    # Install Istio control plane (istiod)
    progress "Installing Istio control plane (istiod)..."
    helm install istiod istio/istiod \
        --namespace istio-system \
        --wait
    
    # Show istiod status
    kubectl get pods -n istio-system -l app=istiod
    
    # Install Istio Gateway
    progress "Installing Istio ingress gateway..."
    helm install istio-gateway istio/gateway \
        --namespace istio-gateway \
        --create-namespace \
        --wait
    
    # Show gateway status
    kubectl get pods -n istio-gateway
    
    # Install Istio configuration
    progress "Applying Istio configuration (mTLS, telemetry)..."
    helm install istio-config "$CHARTS_DIR/istio-config" \
        --namespace istio-system \
        --wait
    
    log "Istio service mesh installed"
    
    # Show Istio status
    info "Istio components:"
    kubectl get pods --all-namespaces -l istio
}

# Install monitoring with visibility
install_monitoring() {
    section "INSTALLING MONITORING STACK"
    
    progress "Installing Prometheus, Grafana, Loki, and Vector..."
    
    # Check if monitoring is already installed
    if helm list -n default | grep -q monitoring; then
        log "Monitoring stack already installed"
        kubectl get pods -n monitoring
        return
    fi
    
    # Show what will be installed
    info "Components to install:"
    info "  • Prometheus - Metrics collection"
    info "  • Grafana - Dashboards and visualization"
    info "  • Loki - Log aggregation"
    info "  • Vector - Log collection and routing"
    info "  • Kube-state-metrics - Kubernetes metrics"
    
    # Install monitoring stack
    helm install monitoring "$CHARTS_DIR/monitoring" \
        --namespace default \
        --wait
    
    log "Monitoring stack installed"
    
    # Show monitoring pods
    kubectl get pods -n monitoring
}

# Install observability with detailed output
install_observability() {
    section "INSTALLING OBSERVABILITY STACK"
    
    progress "Installing Jaeger and Kiali..."
    
    # Check if observability is already installed
    if helm list -n observability | grep -q observability; then
        log "Observability stack already installed"
        kubectl get pods -n observability
        return
    fi
    
    # Show what will be installed
    info "Components to install:"
    info "  • Jaeger - Distributed tracing"
    info "  • Kiali - Service mesh observability"
    
    # Install observability stack
    helm install observability "$CHARTS_DIR/observability" \
        --namespace observability \
        --create-namespace \
        --wait
    
    log "Observability stack installed"
    
    # Show observability pods
    kubectl get pods -n observability
}

# Wait for services with detailed progress
wait_for_services() {
    section "WAITING FOR ALL SERVICES TO BE READY"
    
    progress "Checking LoadBalancer service allocations..."
    
    # Show all services
    info "LoadBalancer services:"
    kubectl get services --all-namespaces -o wide | grep LoadBalancer
    
    # Wait for MetalLB to assign external IPs
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        local pending=$(kubectl get services --all-namespaces -o json | jq -r '.items[] | select(.spec.type=="LoadBalancer") | select(.status.loadBalancer.ingress==null) | .metadata.name' | wc -l | tr -d ' ')
        
        if [ "$pending" -eq 0 ]; then
            log "All LoadBalancer services have external IPs!"
            break
        fi
        
        progress "Waiting for $pending LoadBalancer IPs... ($attempt/$max_attempts)"
        kubectl get services --all-namespaces | grep LoadBalancer | grep -E "<pending>|<none>" || true
        
        attempt=$((attempt + 1))
        sleep 10
    done
    
    # Show final service status
    info "All services with external IPs:"
    kubectl get services --all-namespaces -o wide | grep LoadBalancer | grep -v "<"
    
    # Wait for all pods
    progress "Waiting for all pods to be ready..."
    kubectl wait --for=condition=ready pod --all --all-namespaces --timeout=600s || true
    
    # Show pod summary
    info "Pod status summary:"
    kubectl get pods --all-namespaces | grep -v "Running\|Completed" || echo "All pods are running!"
}

# Display comprehensive access information
display_access_info() {
    section "🎉 PRODUCTION CLUSTER SETUP COMPLETE!"
    
    # Get LoadBalancer IPs with error handling
    local grafana_ip=$(kubectl get service grafana -n monitoring -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")
    local prometheus_ip=$(kubectl get service prometheus -n monitoring -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")
    local jaeger_ip=$(kubectl get service jaeger-query -n observability -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")
    local kiali_ip=$(kubectl get service kiali -n observability -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")
    
    echo
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║             SERVICE ACCESS INFORMATION                   ║${NC}"
    echo -e "${GREEN}╠══════════════════════════════════════════════════════════╣${NC}"
    echo -e "${GREEN}║${NC} 📊 Grafana (Dashboards):    http://$grafana_ip:3000"
    echo -e "${GREEN}║${NC} 📈 Prometheus (Metrics):    http://$prometheus_ip:9090"  
    echo -e "${GREEN}║${NC} 🔍 Jaeger (Tracing):       http://$jaeger_ip:16686"
    echo -e "${GREEN}║${NC} 🕸️  Kiali (Service Mesh):   http://$kiali_ip:20001"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
    
    echo
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                 CLUSTER INFORMATION                      ║${NC}"
    echo -e "${BLUE}╠══════════════════════════════════════════════════════════╣${NC}"
    echo -e "${BLUE}║${NC} • Cluster: k3d production (in colima-production)"
    echo -e "${BLUE}║${NC} • Nodes: $(kubectl get nodes --no-headers | wc -l | tr -d ' ') (1 server, 2 agents)"
    echo -e "${BLUE}║${NC} • Service Mesh: Istio with mTLS enabled"
    echo -e "${BLUE}║${NC} • Load Balancer: MetalLB (192.168.5.240-250)"
    echo -e "${BLUE}║${NC} • DNS: Google DNS (8.8.8.8, 8.8.4.4)"
    echo -e "${BLUE}║${NC} • Registry: production-registry:5000"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
    
    echo
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                    USEFUL COMMANDS                       ║${NC}"
    echo -e "${CYAN}╠══════════════════════════════════════════════════════════╣${NC}"
    echo -e "${CYAN}║${NC} View all pods:        kubectl get pods -A"
    echo -e "${CYAN}║${NC} View services:        kubectl get svc -A"
    echo -e "${CYAN}║${NC} View logs:            kubectl logs -n <namespace> <pod>"
    echo -e "${CYAN}║${NC} Exec into pod:        kubectl exec -it -n <ns> <pod> sh"
    echo -e "${CYAN}║${NC} View Istio config:    kubectl get virtualservices -A"
    echo -e "${CYAN}║${NC} View cluster events:  kubectl get events -A --sort-by='.lastTimestamp'"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════╝${NC}"
}

# Show real-time cluster status
show_realtime_status() {
    section "REAL-TIME CLUSTER STATUS"
    
    info "Press Ctrl+C to stop watching..."
    
    # Watch pods in all namespaces
    kubectl get pods --all-namespaces -w
}

# Main execution with better flow
main() {
    clear
    echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${PURPLE}     PRODUCTION KUBERNETES CLUSTER SETUP - VERBOSE MODE       ${NC}"
    echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo
    
    # Add timing
    local start_time=$(date +%s)
    
    check_prerequisites
    setup_colima
    setup_k3d_cluster
    wait_for_cluster
    install_metallb
    install_istio
    install_monitoring
    install_observability
    wait_for_services
    
    # Calculate total time
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    local minutes=$((duration / 60))
    local seconds=$((duration % 60))
    
    display_access_info
    
    echo
    log "Total setup time: ${minutes}m ${seconds}s"
    echo
    
    # Ask if user wants to see real-time status
    read -p "Would you like to watch real-time cluster status? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        show_realtime_status
    fi
}

# Run main function
main "$@"