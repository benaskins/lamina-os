#!/bin/bash
set -euo pipefail

# Ensure real-time output (bash-specific)
exec 1> >(stdbuf -oL cat)
exec 2> >(stdbuf -oL cat >&2)

# Production Kubernetes Cluster Setup Script
# This script sets up a complete production-grade k3s cluster on macOS
# with service mesh, observability, and monitoring
# 
# Usage: ./setup.sh [--env ENVIRONMENT]
# Example: ./setup.sh --env production

# Parse command line arguments
ENV="production"  # Default environment
while [ $# -gt 0 ]; do
    case $1 in
        --env)
            ENV="$2"
            shift 2
            ;;
        *)
            printf "Error: Unknown argument: %s\n" "$1" >&2
            exit 1
            ;;
    esac
done

printf "SETUP SCRIPT STARTING - ENVIRONMENT: %s\n" "$ENV"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET_DIR="$SCRIPT_DIR"
INFRA_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"
BASE_CHARTS_DIR="$INFRA_DIR/targets/colima-k3s"
TARGET_CHARTS_DIR="$INFRA_DIR/targets/colima-k3s"
ENV_VALUES_DIR="$INFRA_DIR/environments"
ENV_DIR="$INFRA_DIR/../environments/$ENV"

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

lamina_log() {
    printf "%s[%s] ✓ %s%s\n" "$GREEN" "$(date +'%Y-%m-%d %H:%M:%S')" "$1" "$NC"
    sync
}

lamina_warn() {
    printf "%s[%s] ⚠ WARNING: %s%s\n" "$YELLOW" "$(date +'%Y-%m-%d %H:%M:%S')" "$1" "$NC"
}

lamina_error() {
    printf "%s[%s] ✗ ERROR: %s%s\n" "$RED" "$(date +'%Y-%m-%d %H:%M:%S')" "$1" "$NC"
    exit 1
}

lamina_info() {
    printf "%s[%s] ℹ %s%s\n" "$BLUE" "$(date +'%Y-%m-%d %H:%M:%S')" "$1" "$NC"
}

lamina_progress() {
    printf "%s[%s] ▶ %s%s\n" "$PURPLE" "$(date +'%Y-%m-%d %H:%M:%S')" "$1" "$NC"
    sync
}

# Load environment-specific configuration if it exists
if [ -f "$ENV_DIR/config.yaml" ]; then
    lamina_log "Loading environment configuration from $ENV_DIR/config.yaml"
    # For now, we'll use basic shell variable parsing
    # Later we can implement proper YAML parsing
fi

# Set environment-specific resource names
CLUSTER_NAME="lamina-$ENV"
COLIMA_PROFILE="$ENV"
NAMESPACE_PREFIX="$ENV"

# Simple, reliable logging - no complex libraries

# Check prerequisites
check_prerequisites() {
    lamina_log "Checking prerequisites..."
    
    # Check if Docker/Colima is available
    if ! command -v colima &> /dev/null; then
        lamina_error "Colima is not installed. Please install with: brew install colima"
    fi
    
    # Check if kubectl is available
    if ! command -v kubectl &> /dev/null; then
        lamina_error "kubectl is not installed. Please install with: brew install kubectl"
    fi
    
    # Check if helm is available
    if ! command -v helm &> /dev/null; then
        lamina_error "Helm is not installed. Please install with: brew install helm"
    fi
    
    # Check if k3d is available
    if ! command -v k3d &> /dev/null; then
        lamina_error "k3d is not installed. Please install with: brew install k3d"
    fi
    
    lamina_log "Prerequisites check passed"
}

# Start Colima if not running
setup_colima() {
    lamina_log "Setting up Colima $ENV environment..."
    
    # Check if profile exists and is running
    if colima list 2>/dev/null | grep -q "^$COLIMA_PROFILE.*Running"; then
        lamina_log "Colima $ENV profile already running"
        return
    fi
    
    # Check if profile exists but stopped
    if colima list 2>/dev/null | grep -q "^$COLIMA_PROFILE.*Stopped"; then
        lamina_log "Starting existing Colima $ENV profile..."
        colima start -p "$COLIMA_PROFILE"
        return
    fi
    
    # Create new profile
    lamina_log "Creating new Colima $ENV profile..."
    lamina_progress "This may take 2-3 minutes - downloading k3s and setting up VM..."
    
    # Environment-specific resource allocation
    if [ "$ENV" = "production" ]; then
        CPU_COUNT=16
        MEMORY_GB=320  # For multiple 70B models
        DISK_GB=500   # More disk for model storage
        lamina_progress "Configuring production resources for 70B models: ${CPU_COUNT} CPUs, ${MEMORY_GB}GB RAM, ${DISK_GB}GB disk"
    else
        CPU_COUNT=8
        MEMORY_GB=16
        DISK_GB=100
        lamina_progress "Configuring development resources: ${CPU_COUNT} CPUs, ${MEMORY_GB}GB RAM, ${DISK_GB}GB disk"
    fi
    
    # Environment-specific data directory (configurable)
    DATA_DIR="${LAMINA_DATA_DIR:-$HOME/lamina-data}"
    mkdir -p "$DATA_DIR"
    
    # Secure mount configuration - ONLY mount data directory
    # Suppress unnecessary guest agent detection warnings
    export LIMA_INSTANCE_ARCH="aarch64"
    colima start -p "$COLIMA_PROFILE" \
        --cpu "$CPU_COUNT" \
        --memory "$MEMORY_GB" \
        --disk "$DISK_GB" \
        --dns 8.8.8.8 \
        --dns 8.8.4.4 \
        --kubernetes \
        --mount "$DATA_DIR:/lamina-data:w" \
        --mount-type 9p \
        --vm-type vz
    
    lamina_log "Colima $ENV environment ready"
}

# Setup persistent data directory structure
setup_data_directories() {
    lamina_log "Setting up persistent data directory structure..."
    
    local data_dir="${LAMINA_DATA_DIR:-$HOME/lamina-data}"
    
    # Create directories for persistent storage
    local directories=(
        "$data_dir/models"
        "$data_dir/prometheus"
        "$data_dir/loki"
        "$data_dir/grafana"
    )
    
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            lamina_log "Created directory: $dir"
        else
            lamina_log "Directory already exists: $dir"
        fi
    done
    
    # Set permissions for data directories
    chmod 755 "$data_dir"
    find "$data_dir" -type d -exec chmod 755 {} \;
    
    lamina_log "Persistent data directories ready"
}

# Wait for cluster to be ready
wait_for_cluster() {
    lamina_log "Waiting for cluster to be ready..."
    
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if kubectl get nodes | grep -q "Ready"; then
            lamina_log "Cluster is ready"
            return
        fi
        
        attempt=$((attempt + 1))
        lamina_progress "Waiting for cluster... ($attempt/$max_attempts)"
        sleep 10
    done
    
    lamina_error "Cluster failed to become ready within timeout"
}

# Install MetalLB for LoadBalancer services
install_metallb() {
    lamina_log "Installing MetalLB..."
    
    # Add MetalLB Helm repository
    helm repo add metallb https://metallb.github.io/metallb
    helm repo update
    
    # Install/upgrade MetalLB (idempotent)
    lamina_progress "Installing MetalLB load balancer - 1-2 minutes..."
    helm upgrade --install metallb metallb/metallb \
        --namespace metallb-system \
        --create-namespace \
        --wait
    
    # Wait for MetalLB to be ready
    kubectl wait --namespace metallb-system \
        --for=condition=ready pod \
        --selector=app.kubernetes.io/name=metallb \
        --timeout=300s
    
    # Install/upgrade MetalLB configuration (idempotent)
    helm upgrade --install metallb-config "$TARGET_CHARTS_DIR/metallb" \
        --namespace metallb-system \
        --wait
    
    lamina_log "MetalLB installed and configured"
}

# Install Istio service mesh
install_istio() {
    lamina_log "Installing Istio service mesh..."
    
    # Add Istio Helm repository
    helm repo add istio https://istio-release.storage.googleapis.com/charts
    helm repo update
    
    # Install/upgrade Istio base (CRDs) - idempotent
    helm upgrade --install istio-base istio/base \
        --namespace istio-system \
        --create-namespace \
        --wait
    
    # Install/upgrade Istio control plane (istiod) - idempotent
    helm upgrade --install istiod istio/istiod \
        --namespace istio-system \
        --wait
    
    # Install/upgrade Istio Gateway - idempotent
    helm upgrade --install istio-gateway istio/gateway \
        --namespace istio-gateway \
        --create-namespace \
        --wait
    
    lamina_log "Istio base components installed"
}

# Install monitoring stack
install_monitoring() {
    lamina_log "Installing monitoring stack..."
    
    # Extract monitoring values from environment config
    local env_values="$ENV_VALUES_DIR/$ENV/values.yaml"
    local temp_values="/tmp/monitoring-values.yaml"
    
    # Check if environment values file exists
    if [ ! -f "$env_values" ]; then
        lamina_warn "Environment values file not found at $env_values, using chart defaults"
        temp_values=""
    else
        # Extract monitoring section for this deployment
        if command -v yq >/dev/null 2>&1; then
            yq eval '.monitoring' "$env_values" > "$temp_values"
        else
            # Fallback - use the entire environment file and let Helm ignore non-matching keys
            cp "$env_values" "$temp_values"
        fi
    fi
    
    # Install/upgrade monitoring stack (Prometheus, Grafana, Loki, Vector) - idempotent
    local values_flag=""
    if [ -n "$temp_values" ] && [ -f "$temp_values" ]; then
        values_flag="--values $temp_values"
    fi
    
    helm upgrade --install monitoring "$BASE_CHARTS_DIR/monitoring" \
        --namespace monitoring \
        --create-namespace \
        $values_flag \
        --wait
    
    lamina_log "Monitoring stack installed"
}

# Install observability stack
install_observability() {
    lamina_log "Installing observability stack..."
    
    # Extract observability values from environment config
    local env_values="$ENV_VALUES_DIR/$ENV/values.yaml"
    local temp_values="/tmp/observability-values.yaml"
    
    # Check if environment values file exists
    if [ ! -f "$env_values" ]; then
        lamina_warn "Environment values file not found at $env_values, using chart defaults"
        temp_values=""
    else
        # Extract observability section for this deployment
        if command -v yq >/dev/null 2>&1; then
            yq eval '.observability' "$env_values" > "$temp_values"
        else
            # Fallback - use the entire environment file and let Helm ignore non-matching keys
            cp "$env_values" "$temp_values"
        fi
    fi
    
    # Install/upgrade observability stack (Jaeger, Kiali) - idempotent
    local values_flag=""
    if [ -n "$temp_values" ] && [ -f "$temp_values" ]; then
        values_flag="--values $temp_values"
    fi
    
    helm upgrade --install observability "$BASE_CHARTS_DIR/observability" \
        --namespace observability \
        --create-namespace \
        $values_flag \
        --wait
    
    lamina_log "Observability stack installed"
}

# Install Lamina Dashboard
install_lamina_dashboard() {
    lamina_log "Installing Lamina Dashboard..."
    
    # Build and load lamina-dashboard Docker image
    local package_dir="$INFRA_DIR/../packages/lamina-dashboard"
    local image_tar_path="$package_dir/lamina-dashboard.tar"
    
    if [ -f "$package_dir/Dockerfile" ]; then
        lamina_log "Building lamina-dashboard Docker image..."
        cd "$package_dir"
        docker buildx build -t lamina-dashboard:latest --load .
        docker save lamina-dashboard:latest -o lamina-dashboard.tar
        cd - >/dev/null
        
        lamina_log "Loading lamina-dashboard Docker image into cluster..."
        docker load < "$image_tar_path"
    elif [ -f "$image_tar_path" ]; then
        lamina_log "Loading existing lamina-dashboard Docker image into cluster..."
        docker load < "$image_tar_path"
    else
        lamina_warn "No Dockerfile or image tar found, assuming image is already available"
    fi
    
    # Install/upgrade dashboard - idempotent
    helm upgrade --install lamina-dashboard "$BASE_CHARTS_DIR/lamina-dashboard" \
        --namespace lamina-dashboard \
        --create-namespace \
        --wait
    
    # Restart deployment to ensure latest image is used
    kubectl rollout restart deployment/lamina-dashboard -n lamina-dashboard
    kubectl rollout status deployment/lamina-dashboard -n lamina-dashboard --timeout=300s
    
    lamina_log "Lamina Dashboard installed"
}

# Install Istio configuration (after observability stack)
install_istio_config() {
    lamina_log "Installing Istio configuration..."
    
    # Update chart dependencies before installation
    lamina_progress "Updating chart dependencies for colima-service-mesh..."
    cd "$TARGET_CHARTS_DIR/colima-service-mesh"
    helm dependency update
    cd - >/dev/null
    
    # Install/upgrade Istio configuration (mTLS, gateways, telemetry) - idempotent
    helm upgrade --install colima-service-mesh "$TARGET_CHARTS_DIR/colima-service-mesh" \
        --namespace istio-system \
        --wait
    
    lamina_log "Istio configuration installed"
}

# Install Lamina LLM Serve
install_lamina_llm_serve() {
    lamina_log "Installing Lamina LLM Serve..."
    
    # Clean up any released persistent volumes that might conflict
    lamina_progress "Cleaning up any released persistent volumes..."
    if kubectl get pv >/dev/null 2>&1; then
        released_pvs=$(kubectl get pv -o jsonpath='{.items[?(@.status.phase=="Released")].metadata.name}' 2>/dev/null || echo "")
        if [ -n "$released_pvs" ]; then
            echo "$released_pvs" | xargs kubectl delete pv 2>/dev/null || true
            lamina_log "Cleaned up released persistent volumes"
        else
            lamina_log "No released persistent volumes found"
        fi
    fi
    
    # Build and load lamina-llm-serve Docker image
    local package_dir="$INFRA_DIR/../packages/lamina-llm-serve"
    local image_tar_path="$package_dir/lamina-llm-serve.tar"
    
    if [ -f "$package_dir/Dockerfile" ]; then
        lamina_log "Building lamina-llm-serve Docker image..."
        cd "$package_dir"
        docker buildx build -t lamina-llm-serve:latest --load .
        docker save lamina-llm-serve:latest -o lamina-llm-serve.tar
        cd - >/dev/null
        
        lamina_log "Loading lamina-llm-serve Docker image into cluster..."
        docker load < "$image_tar_path"
    elif [ -f "$image_tar_path" ]; then
        lamina_log "Loading existing lamina-llm-serve Docker image into cluster..."
        docker load < "$image_tar_path"
    else
        lamina_warn "No Dockerfile or image tar found, assuming image is already available"
    fi
    
    # Extract lamina-llm-serve values from environment config
    local env_values="$ENV_VALUES_DIR/$ENV/values.yaml"
    local temp_values="/tmp/lamina-llm-serve-values.yaml"
    
    # Extract lamina-llm-serve section for this deployment
    if command -v yq >/dev/null 2>&1; then
        yq eval '.lamina-llm-serve' "$env_values" > "$temp_values"
    else
        # Fallback - use the entire environment file and let Helm ignore non-matching keys
        cp "$env_values" "$temp_values"
    fi
    
    # Install/upgrade Lamina LLM Serve chart - idempotent
    helm upgrade --install lamina-llm-serve "$BASE_CHARTS_DIR/lamina-llm-serve" \
        --namespace lamina-llm-serve \
        --create-namespace \
        --values "$temp_values" \
        --wait
    
    # Force rolling restart to pick up rebuilt image
    lamina_log "Forcing rolling restart to pick up rebuilt image..."
    kubectl rollout restart deployment/lamina-llm-serve -n lamina-llm-serve
    kubectl rollout status deployment/lamina-llm-serve -n lamina-llm-serve --timeout=300s
    
    lamina_log "Lamina LLM Serve installed"
}

# Wait for all services to be ready
wait_for_services() {
    lamina_log "Waiting for all services to be ready..."
    
    # Wait for MetalLB to assign external IPs
    lamina_info "Waiting for LoadBalancer services to get external IPs..."
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        # Count LoadBalancer services without external IPs more reliably
        local pending_services
        pending_services=$(kubectl get services --all-namespaces --field-selector spec.type=LoadBalancer -o jsonpath='{.items[*].status.loadBalancer.ingress}' 2>/dev/null | grep -o "null" | wc -l | tr -d ' \t\n\r')
        # Ensure it's a valid number
        pending_services=${pending_services:-0}
        
        if [ "$pending_services" -eq 0 ]; then
            lamina_log "All LoadBalancer services have external IPs"
            break
        fi
        
        attempt=$((attempt + 1))
        lamina_progress "Waiting for LoadBalancer IPs... ($attempt/$max_attempts)"
        sleep 10
    done
    
    # Wait for all pods to be ready
    lamina_progress "Waiting for all pods to be ready..."
    kubectl wait --for=condition=ready pod --all --all-namespaces --timeout=600s
    
    lamina_log "All services are ready"
}

# Configure port forwarding for host access
configure_host_access() {
    lamina_log "Configuring host access to services..."
    
    # Get Istio gateway service name (now using single gateway)
    local gateway_svc="istio-gateway"
    local gateway_ns="istio-gateway"
    
    # Kill any existing port forwards
    lamina_progress "Stopping any existing port forwards..."
    pkill -f "kubectl.*port-forward.*$gateway_svc" || true
    sleep 2
    
    # Set up persistent port forwarding in background
    lamina_progress "Setting up persistent port forwarding (80 -> istio-gateway:80)..."
    
    # Create port forward script that restarts on failure
    cat > /tmp/lamina-port-forward.sh << 'EOF'
#!/bin/bash
while true; do
    echo "[$(date)] Starting kubectl port-forward for istio-gateway..."
    kubectl port-forward -n istio-gateway svc/istio-gateway 80:80 --address=127.0.0.1
    echo "[$(date)] Port forward died, restarting in 5 seconds..."
    sleep 5
done
EOF
    chmod +x /tmp/lamina-port-forward.sh
    
    # Start port forward in background
    nohup /tmp/lamina-port-forward.sh > /tmp/lamina-port-forward.log 2>&1 &
    local port_forward_pid=$!
    
    # Wait a moment for port forward to establish
    sleep 3
    
    # Test connectivity
    lamina_progress "Testing host connectivity..."
    if curl -m 5 -s "http://localhost:80/health" -H "Host: llm.lamina.local" >/dev/null 2>&1; then
        lamina_log "✅ Services accessible at http://llm.lamina.local/"
        lamina_log "✅ Grafana accessible at http://grafana.lamina.local/grafana"
    else
        lamina_warn "Port forward may still be starting up"
    fi
    
    lamina_log "Port forwarding PID: $port_forward_pid (check /tmp/lamina-port-forward.log for status)"
}

# Display access information
display_access_info() {
    lamina_log "Production cluster setup complete!"
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
    echo "🤖 Lamina LLM Serve:       http://llm.lamina.local/health"
    echo
    echo "=== Hostname-based Access (via Istio Gateway) ==="
    echo "🌬️  Lamina Dashboard:       http://dashboard.lamina.local"
    echo "📊 Grafana:                http://grafana.lamina.local"
    echo "📈 Prometheus:             http://prometheus.lamina.local"
    echo "🔍 Jaeger:                 http://jaeger.lamina.local"
    echo "🕸️  Kiali:                  http://kiali.lamina.local"
    echo
    echo "=== Cluster Information ==="
    echo "• Cluster: k3d production (running in colima-production)"
    echo "• Service Mesh: Istio with mTLS enabled"
    echo "• Load Balancer: MetalLB"
    echo "• DNS: 8.8.8.8, 8.8.4.4"
    echo
    echo "=== Host Configuration Required ==="
    echo "Add these entries to your /etc/hosts file:"
    echo "127.0.0.1 llm.lamina.local"
    echo "127.0.0.1 grafana.lamina.local"
    echo
    echo "=== Next Steps ==="
    echo "1. Update /etc/hosts with the above entries"
    echo "2. Test: curl http://llm.lamina.local/health"
    echo "3. Open: http://grafana.lamina.local/grafana in browser"
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
        lamina_log "Ingesting setup logs into observability stack..."
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

# Function to check for stuck Helm operations and clean them
check_and_clean_helm_locks() {
    lamina_log "Checking for stuck Helm operations..."
    
    # List any pending Helm operations
    local pending_releases=$(helm list --all-namespaces --pending 2>/dev/null | grep -v NAME | wc -l)
    
    if [ "$pending_releases" -gt 0 ]; then
        lamina_warn "Found $pending_releases pending Helm operations. Checking if they're stuck..."
        helm list --all-namespaces --pending
        
        # In a production setup, you might want to automatically rollback stuck releases
        # For now, we'll just warn and let the user decide
        lamina_warn "If setup fails due to stuck operations, run: helm rollback <release-name> <revision> -n <namespace>"
    fi
}

# Main execution
main() {
    # Record start time
    START_TIME=$(date +%s)
    SETUP_FAILED=false
    
    # Set up error handling
    set -e
    trap 'SETUP_FAILED=true; lamina_error "Setup failed at step: $BASH_COMMAND"' ERR
    
    lamina_log "Starting production Kubernetes cluster setup..."
    
    check_prerequisites
    setup_colima
    setup_data_directories
    wait_for_cluster
    install_metallb
    install_istio
    check_and_clean_helm_locks
    install_istio_config
    install_monitoring
    install_observability
    install_lamina_dashboard
    install_lamina_llm_serve
    wait_for_services
    configure_host_access
    display_access_info
    
    lamina_log "Setup completed successfully! 🎉"
}

# Run main function
main "$@"