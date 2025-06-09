#!/bin/sh
set -eu

printf "SETUP SCRIPT STARTING - VISIBILITY TEST\n"

# Production Kubernetes Cluster Setup Script
# This script sets up a complete production-grade k3s cluster on macOS
# with service mesh, observability, and monitoring

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INFRA_DIR="$(dirname "$SCRIPT_DIR")"
CHARTS_DIR="$INFRA_DIR/charts"

# Simple, reliable logging - no complex libraries

# Colors for output (POSIX compatible)
if [ -t 1 ]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    PURPLE='\033[0;35m'
    CYAN='\033[0;36m'
    NC='\033[0m'
else
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    PURPLE=''
    CYAN=''
    NC=''
fi

log() {
    printf "%s[%s] ✓ %s%s\n" "$GREEN" "$(date +'%Y-%m-%d %H:%M:%S')" "$1" "$NC"
}

warn() {
    printf "%s[%s] ⚠ WARNING: %s%s\n" "$YELLOW" "$(date +'%Y-%m-%d %H:%M:%S')" "$1" "$NC"
}

error() {
    printf "%s[%s] ✗ ERROR: %s%s\n" "$RED" "$(date +'%Y-%m-%d %H:%M:%S')" "$1" "$NC"
    exit 1
}

info() {
    printf "%s[%s] ℹ %s%s\n" "$BLUE" "$(date +'%Y-%m-%d %H:%M:%S')" "$1" "$NC"
}

progress() {
    printf "%s[%s] ▶ %s%s\n" "$PURPLE" "$(date +'%Y-%m-%d %H:%M:%S')" "$1" "$NC"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if Docker/Colima is available
    if ! command -v colima &> /dev/null; then
        error "Colima is not installed. Please install with: brew install colima"
    fi
    
    # Check if kubectl is available
    if ! command -v kubectl &> /dev/null; then
        error "kubectl is not installed. Please install with: brew install kubectl"
    fi
    
    # Check if helm is available
    if ! command -v helm &> /dev/null; then
        error "Helm is not installed. Please install with: brew install helm"
    fi
    
    # Check if k3d is available
    if ! command -v k3d &> /dev/null; then
        error "k3d is not installed. Please install with: brew install k3d"
    fi
    
    log "Prerequisites check passed"
}

# Start Colima if not running
setup_colima() {
    log "Setting up Colima production environment..."
    
    # Check if colima-production profile exists and is running
    if colima list 2>/dev/null | grep -q "^colima-production.*Running"; then
        log "Colima production profile already running"
        return
    fi
    
    # Check if profile exists but stopped
    if colima list 2>/dev/null | grep -q "^colima-production.*Stopped"; then
        log "Starting existing Colima production profile..."
        colima start -p colima-production
        return
    fi
    
    # Create new production profile
    log "Creating new Colima production profile..."
    progress "This may take 2-3 minutes - downloading k3s and setting up VM..."
    colima start -p colima-production \
        --cpu 8 \
        --memory 16 \
        --disk 100 \
        --dns 8.8.8.8 \
        --dns 8.8.4.4 \
        --kubernetes 2>&1 | while read -r line; do
        echo "  $line"
    done
    
    log "Colima production environment ready"
}


# Wait for cluster to be ready
wait_for_cluster() {
    log "Waiting for cluster to be ready..."
    
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if kubectl get nodes | grep -q "Ready"; then
            log "Cluster is ready"
            return
        fi
        
        attempt=$((attempt + 1))
        progress "Waiting for cluster... ($attempt/$max_attempts)"
        sleep 10
    done
    
    error "Cluster failed to become ready within timeout"
}

# Install MetalLB for LoadBalancer services
install_metallb() {
    log "Installing MetalLB..."
    
    # Check if already installed
    if helm list -n metallb-system | grep -q metallb; then
        log "MetalLB already installed"
        return
    fi
    
    # Add MetalLB Helm repository
    helm repo add metallb https://metallb.github.io/metallb
    helm repo update
    
    # Install MetalLB
    progress "Installing MetalLB load balancer - 1-2 minutes..."
    helm install metallb metallb/metallb \
        --namespace metallb-system \
        --create-namespace \
        --wait
    
    # Wait for MetalLB to be ready
    kubectl wait --namespace metallb-system \
        --for=condition=ready pod \
        --selector=app.kubernetes.io/name=metallb \
        --timeout=300s
    
    # Install MetalLB configuration
    helm install metallb-config "$CHARTS_DIR/metallb" \
        --namespace metallb-system \
        --wait
    
    log "MetalLB installed and configured"
}

# Install Istio service mesh
install_istio() {
    log "Installing Istio service mesh..."
    
    # Check if Istio is already installed
    if helm list -n istio-system | grep -q istio-base; then
        log "Istio already installed"
        return
    fi
    
    # Add Istio Helm repository
    helm repo add istio https://istio-release.storage.googleapis.com/charts
    helm repo update
    
    # Install Istio base (CRDs)
    helm install istio-base istio/base \
        --namespace istio-system \
        --create-namespace \
        --wait
    
    # Install Istio control plane (istiod)
    helm install istiod istio/istiod \
        --namespace istio-system \
        --wait
    
    # Install Istio Gateway
    helm install istio-gateway istio/gateway \
        --namespace istio-gateway \
        --create-namespace \
        --wait
    
    # Install Istio configuration
    helm install istio-config "$CHARTS_DIR/istio-config" \
        --namespace istio-system \
        --wait
    
    log "Istio service mesh installed"
}

# Install monitoring stack
install_monitoring() {
    log "Installing monitoring stack..."
    
    # Check if monitoring is already installed
    if helm list -n default | grep -q monitoring; then
        log "Monitoring stack already installed"
        return
    fi
    
    # Install monitoring stack (Prometheus, Grafana, Loki, Vector)
    helm install monitoring "$CHARTS_DIR/monitoring" \
        --namespace default \
        --wait
    
    log "Monitoring stack installed"
}

# Install observability stack
install_observability() {
    log "Installing observability stack..."
    
    # Check if observability is already installed
    if helm list -n observability | grep -q observability; then
        log "Observability stack already installed"
        return
    fi
    
    # Install observability stack (Jaeger, Kiali)
    helm install observability "$CHARTS_DIR/observability" \
        --namespace observability \
        --create-namespace \
        --wait
    
    log "Observability stack installed"
}

# Wait for all services to be ready
wait_for_services() {
    log "Waiting for all services to be ready..."
    
    # Wait for MetalLB to assign external IPs
    info "Waiting for LoadBalancer services to get external IPs..."
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        local pending_services=$(kubectl get services --all-namespaces -o jsonpath='{.items[?(@.spec.type=="LoadBalancer")].status.loadBalancer}' | grep -c "null" || echo "0")
        
        if [ "$pending_services" -eq 0 ]; then
            log "All LoadBalancer services have external IPs"
            break
        fi
        
        attempt=$((attempt + 1))
        progress "Waiting for LoadBalancer IPs... ($attempt/$max_attempts)"
        sleep 10
    done
    
    # Wait for all pods to be ready
    progress "Waiting for all pods to be ready..."
    kubectl wait --for=condition=ready pod --all --all-namespaces --timeout=600s
    
    log "All services are ready"
}

# Display access information
display_access_info() {
    log "Production cluster setup complete!"
    echo
    echo "=== Service Access Information ==="
    echo
    
    # Get LoadBalancer IPs
    local grafana_ip=$(kubectl get service grafana -n monitoring -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")
    local prometheus_ip=$(kubectl get service prometheus -n monitoring -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")
    local jaeger_ip=$(kubectl get service jaeger-query -n observability -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")
    local kiali_ip=$(kubectl get service kiali -n observability -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")
    
    echo "📊 Grafana (Dashboards):    http://$grafana_ip:3000"
    echo "📈 Prometheus (Metrics):    http://$prometheus_ip:9090"  
    echo "🔍 Jaeger (Tracing):       http://$jaeger_ip:16686"
    echo "🕸️  Kiali (Service Mesh):   http://$kiali_ip:20001"
    echo
    echo "=== Cluster Information ==="
    echo "• Cluster: k3d production (running in colima-production)"
    echo "• Service Mesh: Istio with mTLS enabled"
    echo "• Load Balancer: MetalLB"
    echo "• DNS: 8.8.8.8, 8.8.4.4"
    echo
    echo "=== Next Steps ==="
    echo "1. Deploy Lamina OS services to the cluster"
    echo "2. Configure application-specific routing in Istio"
    echo "3. Set up application-specific dashboards in Grafana"
    echo
    echo "Use 'kubectl get pods --all-namespaces' to see all running services"
}

# Cleanup and ingest logs on exit
cleanup_and_ingest() {
    local exit_code=$?
    local end_time=$(date +%s)
    local duration=$((end_time - START_TIME))
    
    log_info "setup" "Cleanup and event ingestion starting"
    
    # Determine setup status
    local status="success"
    if [ "$exit_code" -ne 0 ] || [ "${SETUP_FAILED:-false}" = true ]; then
        status="failure"
    fi
    
    # Create setup event
    local event_data=$(create_setup_event "$status" "$duration" "$CURRENT_LOG_FILE")
    
    # Wait a moment for final logs to be written
    sleep 2
    
    # Ingest setup log and event
    if [ "$status" = "success" ]; then
        log "Ingesting setup logs into observability stack..."
        ingest_setup_log "$CURRENT_LOG_FILE" "$event_data"
        
        # Process any queued events
        process_queued_events
    else
        log_error "setup" "Setup failed, queuing logs for later ingestion"
        echo "$event_data" > "$LOG_BUFFER_DIR/failed-setup-$(date +%s).json"
    fi
    
    # Cleanup logging
    cleanup_logging
    
    # Final message
    if [ "$status" = "success" ]; then
        echo -e "${GREEN}✓ Setup logs have been ingested into the observability stack${NC}"
        echo -e "${GREEN}✓ View setup events in Grafana dashboards and Loki${NC}"
    fi
}

# Main execution
main() {
    # Record start time
    START_TIME=$(date +%s)
    SETUP_FAILED=false
    
    log "Starting production Kubernetes cluster setup..."
    
    check_prerequisites
    setup_colima
    wait_for_cluster
    install_metallb
    install_istio
    install_monitoring
    install_observability
    wait_for_services
    display_access_info
    
    log "Setup completed successfully! 🎉"
}

# Run main function
main "$@"