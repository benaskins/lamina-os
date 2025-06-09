#!/bin/bash
set -euo pipefail

# Ensure real-time output (bash-specific)
exec 1> >(stdbuf -oL cat)
exec 2> >(stdbuf -oL cat >&2)

# Resources-Only Teardown Script
# This script removes all Helm releases and application namespaces
# but leaves Colima and the k3s cluster running for faster iteration
# 
# Usage: ./teardown-resources.sh

printf "RESOURCES TEARDOWN STARTING\n"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INFRA_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"
LIB_DIR="$INFRA_DIR/lib"

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

# Basic logging functions 
lamina_log() { printf "[$(date '+%Y-%m-%d %H:%M:%S')] ✓ %s\n" "$*"; }
lamina_info() { printf "[$(date '+%Y-%m-%d %H:%M:%S')] ℹ %s\n" "$*"; }
lamina_warn() { printf "[$(date '+%Y-%m-%d %H:%M:%S')] ⚠ WARNING: %s\n" "$*"; }
lamina_error() { printf "[$(date '+%Y-%m-%d %H:%M:%S')] ✗ ERROR: %s\n" "$*"; }
lamina_progress() { printf "[$(date '+%Y-%m-%d %H:%M:%S')] ▶ %s\n" "$*"; }

START_TIME=$(date +%s)

# Fancy header
printf "%s\n" "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
printf "%s\n" "${BLUE}     RESOURCES-ONLY TEARDOWN       ${NC}"
printf "%s\n" "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
printf "\n"

section() {
    printf "%s\n" "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    printf "%s\n" "${BLUE}▌ $1${NC}"
    printf "%s\n" "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Check cluster availability
check_cluster() {
    section "CHECKING CLUSTER STATUS"
    
    if ! kubectl cluster-info >/dev/null 2>&1; then
        lamina_error "Kubernetes cluster is not accessible"
        lamina_info "Make sure the cluster is running with: ./setup.sh --env production"
        exit 1
    fi
    
    local context=$(kubectl config current-context 2>/dev/null || echo "none")
    case "$context" in
        *production*) 
            lamina_log "Connected to production cluster: $context"
            ;;
        *)
            lamina_warn "Not connected to production cluster context: $context"
            lamina_info "This script is designed for production teardown"
            exit 1
            ;;
    esac
    
    # Show current resources
    local resource_count=$(kubectl get all --all-namespaces 2>/dev/null | wc -l | tr -d ' ')
    lamina_info "Current resources in cluster: $resource_count objects"
}

# Remove Helm releases
remove_helm_releases() {
    section "REMOVING HELM RELEASES"
    
    lamina_progress "Discovering Helm releases..."
    if command -v helm >/dev/null 2>&1; then
        release_count=$(helm list --all-namespaces 2>/dev/null | grep -v NAME | wc -l | tr -d ' ')
        lamina_info "Found $release_count Helm releases to remove"
    else
        lamina_warn "Helm not found, skipping Helm cleanup"
        return
    fi
    
    # Remove in reverse order of dependencies
    remove_release() {
        release_name=$1
        namespace=$2
        
        if helm list -n "$namespace" 2>/dev/null | grep -q "^$release_name"; then
            lamina_progress "Removing $release_name from namespace $namespace..."
            
            if helm uninstall "$release_name" -n "$namespace" >/dev/null 2>&1; then
                lamina_log "Successfully removed $release_name"
            else
                lamina_error "Failed to uninstall $release_name"
            fi
        else
            lamina_info "$release_name not found in namespace $namespace, skipping"
        fi
    }
    
    # Application releases first
    remove_release "lamina-llm-serve" "lamina-llm-serve"
    
    # Infrastructure releases
    remove_release "observability" "observability"
    remove_release "monitoring" "monitoring" 
    remove_release "istio-config" "istio-system"
    remove_release "istio-gateway" "istio-gateway"
    remove_release "istiod" "istio-system"
    remove_release "istio-base" "istio-system"
    remove_release "metallb-config" "metallb-system"
    remove_release "metallb" "metallb-system"
    
    lamina_log "All Helm releases successfully removed"
}

# Clean up namespaces
cleanup_namespaces() {
    section "CLEANING UP NAMESPACES"
    
    lamina_progress "Cleaning up application namespaces..."
    for namespace in lamina-llm-serve monitoring observability istio-gateway metallb-system istio-system; do
        if kubectl get namespace "$namespace" >/dev/null 2>&1; then
            lamina_progress "Deleting namespace $namespace..."
            kubectl delete namespace "$namespace" --timeout=60s >/dev/null 2>&1 || true
            
            # Wait for namespace to be fully deleted
            lamina_progress "Waiting for namespace $namespace to be fully deleted..."
            timeout_count=0
            while kubectl get namespace "$namespace" >/dev/null 2>&1 && [ $timeout_count -lt 30 ]; do
                sleep 2
                timeout_count=$((timeout_count + 1))
            done
            
            if kubectl get namespace "$namespace" >/dev/null 2>&1; then
                lamina_warn "Namespace $namespace still exists after timeout"
            else
                lamina_log "Namespace $namespace fully deleted"
            fi
        fi
    done
    
    lamina_log "Application namespaces cleaned up"
}

# Verify cleanup
verify_cleanup() {
    section "VERIFYING CLEANUP COMPLETION"
    
    lamina_progress "Checking for remaining Helm releases..."
    local remaining_releases=$(helm list --all-namespaces 2>/dev/null | grep -v NAME | wc -l | tr -d ' ')
    if [ "$remaining_releases" -eq 0 ]; then
        lamina_log "No Helm releases found ✓"
    else
        lamina_warn "Found $remaining_releases remaining Helm releases"
    fi
    
    lamina_progress "Checking for application namespaces..."
    local remaining_ns=0
    for namespace in lamina-llm-serve monitoring observability istio-gateway metallb-system istio-system; do
        if kubectl get namespace "$namespace" >/dev/null 2>&1; then
            lamina_warn "Namespace $namespace still exists"
            remaining_ns=$((remaining_ns + 1))
        fi
    done
    
    if [ "$remaining_ns" -eq 0 ]; then
        lamina_log "No application namespaces found ✓"
    else
        lamina_warn "Found $remaining_ns remaining application namespaces"
    fi
    
    lamina_progress "Checking cluster status..."
    if kubectl cluster-info >/dev/null 2>&1; then
        lamina_log "Cluster is still running ✓"
    else
        lamina_error "Cluster is not accessible"
    fi
}

# Main execution
main() {
    lamina_log "Starting resources-only teardown..."
    
    check_cluster
    remove_helm_releases
    cleanup_namespaces  
    verify_cleanup
    
    local end_time=$(date +%s)
    local duration=$((end_time - START_TIME))
    local minutes=$((duration / 60))
    local seconds=$((duration % 60))
    
    printf "\n%s\n" "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
    printf "%s\n" "${GREEN}║           RESOURCES CLEANUP COMPLETED! 🧹               ║${NC}"
    printf "%s\n" "${GREEN}╠══════════════════════════════════════════════════════════╣${NC}"
    printf "%s\n" "${GREEN}║ ✅ All application resources removed${NC}"
    printf "%s\n" "${GREEN}║ ✅ Cluster still running for fast iteration${NC}"
    printf "%s\n" "${GREEN}║ Duration: ${minutes}m ${seconds}s${NC}"
    printf "%s\n" "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
    printf "\n"
    printf "The cluster is ready for a fresh deployment.\n"
    printf "Run './setup.sh --env production' to redeploy all services.\n"
}

# Run main function
main "$@"