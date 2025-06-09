#!/bin/bash
set -euo pipefail

# Production Kubernetes Cluster Teardown Script
# This script completely removes the production k3s cluster and Colima environment

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

# Confirm teardown
confirm_teardown() {
    warn "This will completely destroy the production cluster and all data!"
    echo "This includes:"
    echo "  • k3d production cluster"
    echo "  • All deployed applications and data"
    echo "  • Colima production profile"
    echo "  • All persistent volumes"
    echo
    read -p "Are you sure you want to continue? (type 'yes' to confirm): " confirmation
    
    if [ "$confirmation" != "yes" ]; then
        log "Teardown cancelled"
        exit 0
    fi
}

# Remove Helm releases
remove_helm_releases() {
    log "Removing Helm releases..."
    
    # Get current kubectl context to ensure we're working with the right cluster
    local current_context=$(kubectl config current-context 2>/dev/null || echo "none")
    
    if [[ "$current_context" == *"production"* ]]; then
        # Remove in reverse order of dependencies
        
        # Remove observability stack
        if helm list -n observability | grep -q observability; then
            info "Removing observability stack..."
            helm uninstall observability -n observability || warn "Failed to uninstall observability"
        fi
        
        # Remove monitoring stack
        if helm list -n default | grep -q monitoring; then
            info "Removing monitoring stack..."
            helm uninstall monitoring -n default || warn "Failed to uninstall monitoring"
        fi
        
        # Remove Istio configuration
        if helm list -n istio-system | grep -q istio-config; then
            info "Removing Istio configuration..."
            helm uninstall istio-config -n istio-system || warn "Failed to uninstall istio-config"
        fi
        
        # Remove Istio Gateway
        if helm list -n istio-gateway | grep -q istio-gateway; then
            info "Removing Istio Gateway..."
            helm uninstall istio-gateway -n istio-gateway || warn "Failed to uninstall istio-gateway"
        fi
        
        # Remove Istio control plane
        if helm list -n istio-system | grep -q istiod; then
            info "Removing Istio control plane..."
            helm uninstall istiod -n istio-system || warn "Failed to uninstall istiod"
        fi
        
        # Remove Istio base
        if helm list -n istio-system | grep -q istio-base; then
            info "Removing Istio base..."
            helm uninstall istio-base -n istio-system || warn "Failed to uninstall istio-base"
        fi
        
        # Remove MetalLB configuration
        if helm list -n metallb-system | grep -q metallb-config; then
            info "Removing MetalLB configuration..."
            helm uninstall metallb-config -n metallb-system || warn "Failed to uninstall metallb-config"
        fi
        
        # Remove MetalLB
        if helm list -n metallb-system | grep -q metallb; then
            info "Removing MetalLB..."
            helm uninstall metallb -n metallb-system || warn "Failed to uninstall metallb"
        fi
        
        log "Helm releases removed"
    else
        warn "Not connected to production cluster context, skipping Helm cleanup"
    fi
}

# Remove k3d cluster
remove_k3d_cluster() {
    log "Removing k3d cluster..."
    
    # Check if production cluster exists
    if k3d cluster list | grep -q "production"; then
        info "Deleting k3d production cluster..."
        k3d cluster delete production
        log "k3d cluster removed"
    else
        info "k3d production cluster not found, skipping"
    fi
    
    # Remove registry if it exists
    if docker ps -a | grep -q "production-registry"; then
        info "Removing k3d registry..."
        docker stop production-registry 2>/dev/null || true
        docker rm production-registry 2>/dev/null || true
    fi
}

# Stop and remove Colima profile
remove_colima_profile() {
    log "Removing Colima production profile..."
    
    # Check if colima-production profile exists
    if colima list 2>/dev/null | grep -q "colima-production"; then
        info "Stopping and deleting Colima production profile..."
        
        # Stop if running
        if colima list 2>/dev/null | grep -q "^colima-production.*Running"; then
            colima stop -p colima-production
        fi
        
        # Delete the profile
        colima delete -p colima-production --force
        
        log "Colima production profile removed"
    else
        info "Colima production profile not found, skipping"
    fi
}

# Clean up Docker resources
cleanup_docker_resources() {
    log "Cleaning up Docker resources..."
    
    # Remove k3d-related containers
    info "Removing k3d containers..."
    docker ps -a --filter "name=k3d-production" --format "table {{.Names}}" | grep -v NAMES | xargs -r docker rm -f || true
    
    # Remove k3d-related images (optional - saves space but will need re-download)
    info "Removing k3d images..."
    docker images --filter "reference=rancher/k3s*" --format "table {{.Repository}}:{{.Tag}}" | grep -v REPOSITORY | xargs -r docker rmi -f || true
    
    # Remove k3d-related networks
    info "Removing k3d networks..."
    docker network ls --filter "name=k3d-production" --format "table {{.Name}}" | grep -v NAME | xargs -r docker network rm || true
    
    # Remove k3d-related volumes
    info "Removing k3d volumes..."
    docker volume ls --filter "name=k3d-production" --format "table {{.Name}}" | grep -v NAME | xargs -r docker volume rm || true
    
    log "Docker resources cleaned up"
}

# Reset kubectl context
reset_kubectl_context() {
    log "Resetting kubectl context..."
    
    # Remove k3d contexts from kubeconfig
    local contexts_to_remove=$(kubectl config get-contexts -o name | grep "k3d-production" || true)
    
    if [ -n "$contexts_to_remove" ]; then
        echo "$contexts_to_remove" | xargs -r kubectl config delete-context
    fi
    
    # Remove k3d clusters from kubeconfig
    local clusters_to_remove=$(kubectl config get-clusters | grep "k3d-production" || true)
    
    if [ -n "$clusters_to_remove" ]; then
        echo "$clusters_to_remove" | xargs -r kubectl config delete-cluster
    fi
    
    # Remove k3d users from kubeconfig
    local users_to_remove=$(kubectl config get-users | grep "k3d-production" || true)
    
    if [ -n "$users_to_remove" ]; then
        echo "$users_to_remove" | xargs -r kubectl config delete-user
    fi
    
    log "kubectl context reset"
}

# Display completion message
display_completion_message() {
    log "Teardown completed successfully! 🧹"
    echo
    echo "=== Teardown Summary ==="
    echo "✅ Helm releases removed"
    echo "✅ k3d cluster deleted"
    echo "✅ Colima production profile removed"
    echo "✅ Docker resources cleaned up"
    echo "✅ kubectl context reset"
    echo
    echo "The system is now clean and ready for a fresh setup."
    echo "Run './setup-production-cluster.sh' to recreate the cluster."
}

# Main execution
main() {
    log "Starting production cluster teardown..."
    
    confirm_teardown
    remove_helm_releases
    remove_k3d_cluster
    remove_colima_profile
    cleanup_docker_resources
    reset_kubectl_context
    display_completion_message
    
    log "Teardown completed! 🎉"
}

# Run main function
main "$@"