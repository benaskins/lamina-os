#!/bin/bash
# Production Kubernetes Cluster Teardown Script - POSIX Compliant
# This script completely removes the k3s cluster and Colima environment
# WITH VERIFICATION at each step
#
# Usage: ./teardown.sh [--env ENVIRONMENT] [--resources-only]
# Example: ./teardown.sh --env production
# Example: ./teardown.sh --env production --resources-only

# Parse command line arguments
ENV="production"  # Default environment
RESOURCES_ONLY=false
while [ $# -gt 0 ]; do
    case $1 in
        --env)
            ENV="$2"
            shift 2
            ;;
        --resources-only)
            RESOURCES_ONLY=true
            shift 1
            ;;
        *)
            printf "Error: Unknown argument: %s\n" "$1" >&2
            printf "Usage: %s [--env ENVIRONMENT] [--resources-only]\n" "$0" >&2
            exit 1
            ;;
    esac
done

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INFRA_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"
LIB_DIR="$INFRA_DIR/lib"

# Set environment-specific resource names
CLUSTER_NAME="lamina-$ENV"
COLIMA_PROFILE="$ENV"
NAMESPACE_PREFIX="$ENV"

# Simple, reliable logging - no complex libraries

# Track teardown status
TEARDOWN_FAILED=false
TEARDOWN_START=$(date +%s)

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
}

lamina_warn() {
    printf "%s[%s] ⚠ WARNING: %s%s\n" "$YELLOW" "$(date +'%Y-%m-%d %H:%M:%S')" "$1" "$NC"
}

lamina_error() {
    printf "%s[%s] ✗ ERROR: %s%s\n" "$RED" "$(date +'%Y-%m-%d %H:%M:%S')" "$1" "$NC"
    TEARDOWN_FAILED=true
}

lamina_info() {
    printf "%s[%s] ℹ %s%s\n" "$BLUE" "$(date +'%Y-%m-%d %H:%M:%S')" "$1" "$NC"
}

lamina_progress() {
    printf "%s[%s] ▶ %s%s\n" "$PURPLE" "$(date +'%Y-%m-%d %H:%M:%S')" "$1" "$NC"
}

section() {
    echo
    printf "%s━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━%s\n" "$CYAN" "$NC"
    printf "%s▌ %s%s\n" "$CYAN" "$1" "$NC"
    printf "%s━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━%s\n" "$CYAN" "$NC"
}

# Verify a resource is removed
verify_removed() {
    resource_type=$1
    check_command=$2
    resource_name=$3
    
    lamina_progress "Verifying $resource_type '$resource_name' is removed..."
    
    if eval "$check_command" >/dev/null 2>&1; then
        lamina_error "$resource_type '$resource_name' still exists after removal attempt"
        return 1
    else
        lamina_log "$resource_type '$resource_name' successfully removed"
        return 0
    fi
}

# Confirm teardown
confirm_teardown() {
    section "TEARDOWN CONFIRMATION"
    
    if [ "$RESOURCES_ONLY" = "true" ]; then
        lamina_warn "This will remove all deployed applications but preserve the cluster!"
        echo "This includes:"
        echo "  • All Helm releases and applications"
        echo "  • All deployed namespaces and resources"
        echo "  • All application data (not persistent volumes)"
        echo
        echo "This preserves:"
        echo "  • k3s cluster and Colima VM"
        echo "  • Cluster configuration"
        echo "  • Persistent volumes (if any)"
        echo "  • Network configuration"
    else
        lamina_warn "This will completely destroy the production cluster and all data!"
        echo "This includes:"
        echo "  • k3d production cluster"
        echo "  • All deployed applications and data"
        echo "  • Colima production profile"
        echo "  • All persistent volumes"
        echo "  • All logs not yet ingested"
    fi
    echo
    
    # Show what will be removed
    lamina_info "Current state:"
    if command -v k3d >/dev/null 2>&1 && k3d cluster list | grep -q production; then
        echo "  • k3s cluster: production (ACTIVE)"
    fi
    if command -v colima >/dev/null 2>&1 && colima list 2>/dev/null | grep -q colima-production; then
        echo "  • Colima profile: colima-production"
    fi
    if kubectl cluster-info >/dev/null 2>&1; then
        resource_count=$(kubectl get all --all-namespaces --no-headers 2>/dev/null | wc -l | tr -d ' ')
        echo "  • Kubernetes resources: $resource_count objects"
    fi
    
    echo
    # Auto-confirm teardown for automation
    if [ "$RESOURCES_ONLY" = "true" ]; then
        lamina_log "Auto-confirming resources-only cleanup for automation..."
    else
        lamina_log "Auto-confirming full teardown for automation..."
    fi
    
}

# Remove Helm releases with verification
remove_helm_releases() {
    section "REMOVING HELM RELEASES"
    
    # Get current kubectl context to ensure we're working with the right cluster
    current_context=$(kubectl config current-context 2>/dev/null || echo "none")
    
    case "$current_context" in
        *production*) ;;
        *)
            lamina_warn "Not connected to production cluster context, skipping Helm cleanup"
            return
            ;;
    esac
    
    # Get all helm releases
    lamina_progress "Discovering Helm releases..."
    if command -v helm >/dev/null 2>&1; then
        release_count=$(helm list --all-namespaces 2>/dev/null | grep -v NAME | wc -l | tr -d ' ')
        lamina_info "Found $release_count Helm releases to remove"
    else
        lamina_warn "Helm not found, skipping Helm cleanup"
        return
    fi
    
    # Remove in reverse order of dependencies - POSIX compatible array simulation
    remove_release() {
        release_name=$1
        namespace=$2
        
        if helm list -n "$namespace" 2>/dev/null | grep -q "^$release_name"; then
            lamina_progress "Removing $release_name from namespace $namespace..."
            
            if helm uninstall "$release_name" -n "$namespace" >/dev/null 2>&1; then
                # Verify removal
                if ! helm list -n "$namespace" 2>/dev/null | grep -q "^$release_name"; then
                    lamina_log "Successfully removed $release_name"
                else
                    lamina_error "Failed to remove $release_name - still exists"
                fi
            else
                lamina_error "Failed to uninstall $release_name"
            fi
        else
            lamina_info "$release_name not found in namespace $namespace, skipping"
        fi
    }
    
    # Remove releases in dependency order
    remove_release "observability" "observability"
    remove_release "monitoring" "monitoring"
    remove_release "istio-config" "istio-system"
    remove_release "istio-gateway" "istio-gateway"
    remove_release "istiod" "istio-system"
    remove_release "istio-base" "istio-system"
    remove_release "metallb-config" "metallb-system"
    remove_release "metallb" "metallb-system"
    
    # Final verification
    remaining=$(helm list --all-namespaces 2>/dev/null | grep -v NAME | wc -l | tr -d ' ')
    if [ "$remaining" -gt 0 ]; then
        lamina_warn "$remaining Helm releases still remain"
    else
        lamina_log "All Helm releases successfully removed"
    fi
    
    # Clean up released persistent volumes to prevent future binding issues
    lamina_progress "Cleaning up released persistent volumes..."
    if kubectl get pv >/dev/null 2>&1; then
        released_pvs=$(kubectl get pv -o jsonpath='{.items[?(@.status.phase=="Released")].metadata.name}' 2>/dev/null || echo "")
        if [ -n "$released_pvs" ]; then
            echo "$released_pvs" | xargs kubectl delete pv 2>/dev/null || true
            lamina_log "Cleaned up released persistent volumes"
        else
            lamina_log "No released persistent volumes found"
        fi
    fi
    
    # Clean up namespaces that might have been left behind
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
                lamina_warn "Namespace $namespace still exists after 60s wait"
            else
                lamina_log "Namespace $namespace fully deleted"
            fi
        fi
    done
    lamina_log "Application namespaces cleaned up"
}

# Remove k3d cluster with verification
remove_k3d_cluster() {
    section "REMOVING K3D CLUSTER"
    
    # Check if production cluster exists
    if ! k3d cluster list | grep -q "production"; then
        lamina_info "k3d production cluster not found, skipping"
        return
    fi
    
    lamina_progress "Deleting k3d production cluster..."
    
    if k3d cluster delete production >/dev/null 2>&1; then
        verify_removed "k3d cluster" "k3d cluster list | grep -q production" "production"
    else
        lamina_error "Failed to delete k3d cluster"
        TEARDOWN_FAILED=true
    fi
    
    # Remove registry if it exists
    if docker ps -a | grep -q "production-registry"; then
        lamina_progress "Removing k3d registry..."
        docker stop production-registry >/dev/null 2>&1 || true
        docker rm production-registry >/dev/null 2>&1 || true
        
        verify_removed "Docker container" "docker ps -a | grep -q production-registry" "production-registry"
    fi
}

# Stop and remove Colima profile with verification
remove_colima_profile() {
    section "REMOVING COLIMA PROFILE ($ENV)"
    
    # Check if profile exists
    if ! colima list 2>/dev/null | grep -q "$COLIMA_PROFILE"; then
        lamina_info "Colima $ENV profile not found, skipping"
        return
    fi
    
    # Stop if running
    if colima list 2>/dev/null | grep -q "^$COLIMA_PROFILE.*Running"; then
        lamina_progress "Stopping Colima $ENV profile..."
        if colima stop -p "$COLIMA_PROFILE"; then
            lamina_log "Colima $ENV profile stopped"
        else
            lamina_error "Failed to stop Colima $ENV profile"
        fi
    fi
    
    # Delete the profile
    lamina_progress "Deleting Colima $ENV profile..."
    if colima delete -p "$COLIMA_PROFILE" --force >/dev/null 2>&1; then
        verify_removed "Colima profile" "colima list 2>/dev/null | grep -q $COLIMA_PROFILE" "$COLIMA_PROFILE"
    else
        lamina_error "Failed to delete Colima $ENV profile"
        TEARDOWN_FAILED=true
    fi
}

# Clean up Docker resources with verification
cleanup_docker_resources() {
    section "CLEANING UP DOCKER RESOURCES"
    
    # Count resources before cleanup
    containers_before=$(docker ps -a --filter "name=k3d-production" --format "{{.Names}}" 2>/dev/null | wc -l | tr -d ' ')
    networks_before=$(docker network ls --filter "name=k3d-production" --format "{{.Name}}" 2>/dev/null | wc -l | tr -d ' ')
    volumes_before=$(docker volume ls --filter "name=k3d-production" --format "{{.Name}}" 2>/dev/null | wc -l | tr -d ' ')
    
    lamina_info "Resources to clean: $containers_before containers, $networks_before networks, $volumes_before volumes"
    
    # Remove k3d-related containers
    if [ "$containers_before" -gt 0 ]; then
        lamina_progress "Removing k3d containers..."
        docker ps -a --filter "name=k3d-production" --format "{{.Names}}" | xargs -r docker rm -f >/dev/null 2>&1 || true
        
        containers_after=$(docker ps -a --filter "name=k3d-production" --format "{{.Names}}" 2>/dev/null | wc -l | tr -d ' ')
        if [ "$containers_after" -eq 0 ]; then
            lamina_log "All k3d containers removed"
        else
            lamina_error "$containers_after k3d containers still remain"
        fi
    fi
    
    # Remove k3d-related networks
    if [ "$networks_before" -gt 0 ]; then
        lamina_progress "Removing k3d networks..."
        docker network ls --filter "name=k3d-production" --format "{{.Name}}" | xargs -r docker network rm >/dev/null 2>&1 || true
        
        networks_after=$(docker network ls --filter "name=k3d-production" --format "{{.Name}}" 2>/dev/null | wc -l | tr -d ' ')
        if [ "$networks_after" -eq 0 ]; then
            lamina_log "All k3d networks removed"
        else
            lamina_error "$networks_after k3d networks still remain"
        fi
    fi
    
    # Remove k3d-related volumes
    if [ "$volumes_before" -gt 0 ]; then
        lamina_progress "Removing k3d volumes..."
        docker volume ls --filter "name=k3d-production" --format "{{.Name}}" | xargs -r docker volume rm >/dev/null 2>&1 || true
        
        volumes_after=$(docker volume ls --filter "name=k3d-production" --format "{{.Name}}" 2>/dev/null | wc -l | tr -d ' ')
        if [ "$volumes_after" -eq 0 ]; then
            lamina_log "All k3d volumes removed"
        else
            lamina_error "$volumes_after k3d volumes still remain"
        fi
    fi
}

# Reset kubectl context with verification
reset_kubectl_context() {
    section "RESETTING KUBECTL CONTEXT"
    
    # Get all k3d-related contexts
    contexts_to_remove=$(kubectl config get-contexts -o name 2>/dev/null | grep "k3d-production" || true)
    
    if [ -z "$contexts_to_remove" ]; then
        lamina_info "No k3d-production contexts found"
        return
    fi
    
    lamina_progress "Removing kubectl contexts..."
    echo "$contexts_to_remove" | while read -r context; do
        kubectl config delete-context "$context" >/dev/null 2>&1 || true
        lamina_log "Removed context: $context"
    done
    
    # Remove k3d clusters from kubeconfig
    lamina_progress "Removing cluster configurations..."
    clusters_to_remove=$(kubectl config get-clusters 2>/dev/null | grep "k3d-production" || true)
    if [ -n "$clusters_to_remove" ]; then
        echo "$clusters_to_remove" | xargs -r kubectl config delete-cluster
    fi
    
    # Remove k3d users from kubeconfig
    lamina_progress "Removing user configurations..."
    users_to_remove=$(kubectl config get-users 2>/dev/null | grep "k3d-production" || true)
    if [ -n "$users_to_remove" ]; then
        echo "$users_to_remove" | xargs -r kubectl config delete-user
    fi
    
    # Verify cleanup
    if kubectl config get-contexts 2>/dev/null | grep -q "k3d-production"; then
        lamina_error "Some k3d contexts still remain"
    else
        lamina_log "All k3d contexts successfully removed"
    fi
}

# Verify complete teardown
verify_teardown_complete() {
    section "VERIFYING TEARDOWN COMPLETION"
    
    verification_passed=true
    
    if [ "$RESOURCES_ONLY" = "true" ]; then
        # Resources-only mode: only check that Helm releases are gone
        lamina_progress "Checking for remaining Helm releases..."
        remaining=$(helm list --all-namespaces 2>/dev/null | grep -v NAME | wc -l | tr -d ' ')
        if [ "$remaining" -gt 0 ]; then
            lamina_error "$remaining Helm releases still remain"
            verification_passed=false
        else
            lamina_log "All Helm releases successfully removed ✓"
        fi
        
        # Verify cluster is still accessible
        lamina_progress "Verifying cluster is still accessible..."
        if kubectl cluster-info >/dev/null 2>&1; then
            lamina_log "Cluster still accessible ✓"
        else
            lamina_error "Cluster is no longer accessible"
            verification_passed=false
        fi
    else
        # Full teardown mode: check everything is gone
        # Check k3d clusters
        lamina_progress "Checking for k3d clusters..."
        if k3d cluster list | grep -q "production"; then
            lamina_error "k3d production cluster still exists"
            verification_passed=false
        else
            lamina_log "No k3d production cluster found ✓"
        fi
        
        # Check Colima profiles
        lamina_progress "Checking for Colima profiles..."
        if colima list 2>/dev/null | grep -q "colima-production"; then
            lamina_error "Colima production profile still exists"
            verification_passed=false
        else
            lamina_log "No Colima production profile found ✓"
        fi
        
        # Check Docker resources
        lamina_progress "Checking for Docker resources..."
        docker_resources=$(docker ps -a --filter "name=k3d-production" --format "{{.Names}}" 2>/dev/null | wc -l | tr -d ' ')
        if [ "$docker_resources" -gt 0 ]; then
            lamina_error "$docker_resources Docker containers still exist"
            verification_passed=false
        else
            lamina_log "No k3d Docker containers found ✓"
        fi
        
        # Check kubectl contexts
        lamina_progress "Checking for kubectl contexts..."
        if kubectl config get-contexts 2>/dev/null | grep -q "k3d-production"; then
            lamina_error "kubectl contexts still exist for k3d-production"
            verification_passed=false
        else
            lamina_log "No k3d kubectl contexts found ✓"
        fi
    fi
    
    [ "$verification_passed" = "true" ]
}

# Display completion message
display_completion_message() {
    status=$1
    duration=$2
    
    if [ "$status" = "success" ]; then
        echo
        printf "%s╔══════════════════════════════════════════════════════════╗%s\n" "$GREEN" "$NC"
        if [ "$RESOURCES_ONLY" = "true" ]; then
            printf "%s║         RESOURCES CLEANUP COMPLETED! 🧹                  ║%s\n" "$GREEN" "$NC"
            printf "%s╠══════════════════════════════════════════════════════════╣%s\n" "$GREEN" "$NC"
            printf "%s║%s ✅ All applications successfully removed\n" "$GREEN" "$NC"
            printf "%s║%s ✅ Cluster infrastructure preserved\n" "$GREEN" "$NC"
        else
            printf "%s║           TEARDOWN COMPLETED SUCCESSFULLY! 🧹            ║%s\n" "$GREEN" "$NC"
            printf "%s╠══════════════════════════════════════════════════════════╣%s\n" "$GREEN" "$NC"
            printf "%s║%s ✅ All components successfully removed\n" "$GREEN" "$NC"
        fi
        printf "%s║%s Duration: %dm %ds\n" "$GREEN" "$NC" $((duration/60)) $((duration%60))
        printf "%s╚══════════════════════════════════════════════════════════╝%s\n" "$GREEN" "$NC"
    else
        echo
        printf "%s╔══════════════════════════════════════════════════════════╗%s\n" "$RED" "$NC"
        if [ "$RESOURCES_ONLY" = "true" ]; then
            printf "%s║        RESOURCES CLEANUP COMPLETED WITH ERRORS! ⚠️       ║%s\n" "$RED" "$NC"
        else
            printf "%s║           TEARDOWN COMPLETED WITH ERRORS! ⚠️             ║%s\n" "$RED" "$NC"
        fi
        printf "%s╠══════════════════════════════════════════════════════════╣%s\n" "$RED" "$NC"
        printf "%s║%s Some components may still exist\n" "$RED" "$NC"
        printf "%s║%s Duration: %dm %ds\n" "$RED" "$NC" $((duration/60)) $((duration%60))
        printf "%s╚══════════════════════════════════════════════════════════╝%s\n" "$RED" "$NC"
    fi
    
    echo
    if [ "$RESOURCES_ONLY" = "true" ]; then
        echo "Cluster infrastructure preserved and ready for redeployment."
        echo "Run './setup.sh --env $ENV' to redeploy applications."
    else
        echo "The system is ready for a fresh setup."
        echo "Run './setup.sh --env production' to recreate the cluster."
    fi
}

# Main execution
main() {
    clear
    printf "%s━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━%s\n" "$PURPLE" "$NC"
    if [ "$RESOURCES_ONLY" = "true" ]; then
        printf "%s     %s RESOURCES CLEANUP       %s\n" "$PURPLE" "$(echo "$ENV" | tr '[:lower:]' '[:upper:]')" "$NC"
    else
        printf "%s     %s CLUSTER TEARDOWN       %s\n" "$PURPLE" "$(echo "$ENV" | tr '[:lower:]' '[:upper:]')" "$NC"
    fi
    printf "%s━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━%s\n" "$PURPLE" "$NC"
    
    confirm_teardown
    
    # Execute teardown steps based on mode
    if [ "$RESOURCES_ONLY" = "true" ]; then
        # Resources-only mode: just remove applications
        remove_helm_releases
        lamina_log "Resources-only cleanup completed - cluster preserved"
    else
        # Full teardown mode: remove everything
        remove_helm_releases
        remove_k3d_cluster
        remove_colima_profile
        cleanup_docker_resources
        reset_kubectl_context
    fi
    
    # Verify and report
    teardown_end=$(date +%s)
    duration=$((teardown_end - TEARDOWN_START))
    
    if verify_teardown_complete; then
        status="success"
    else
        status="partial"
        TEARDOWN_FAILED=true
    fi
    
    # Simple completion log (no complex event system)
    echo "Teardown completed: $status in ${duration}s" > "/tmp/teardown-$(date +%Y%m%d-%H%M%S).log"
    
    display_completion_message "$status" "$duration"
    
    # Exit with appropriate code
    [ "$TEARDOWN_FAILED" = "false" ] && exit 0 || exit 1
}

# Run main
main "$@"