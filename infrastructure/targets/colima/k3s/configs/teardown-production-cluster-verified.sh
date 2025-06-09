#!/bin/sh
# Production Kubernetes Cluster Teardown Script - POSIX Compliant
# This script completely removes the production k3s cluster and Colima environment
# WITH VERIFICATION at each step

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

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

log() {
    printf "%s[%s] ✓ %s%s\n" "$GREEN" "$(date +'%Y-%m-%d %H:%M:%S')" "$1" "$NC"
}

warn() {
    printf "%s[%s] ⚠ WARNING: %s%s\n" "$YELLOW" "$(date +'%Y-%m-%d %H:%M:%S')" "$1" "$NC"
}

error() {
    printf "%s[%s] ✗ ERROR: %s%s\n" "$RED" "$(date +'%Y-%m-%d %H:%M:%S')" "$1" "$NC"
    TEARDOWN_FAILED=true
}

info() {
    printf "%s[%s] ℹ %s%s\n" "$BLUE" "$(date +'%Y-%m-%d %H:%M:%S')" "$1" "$NC"
}

progress() {
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
    
    progress "Verifying $resource_type '$resource_name' is removed..."
    
    if eval "$check_command" >/dev/null 2>&1; then
        error "$resource_type '$resource_name' still exists after removal attempt"
        return 1
    else
        log "$resource_type '$resource_name' successfully removed"
        return 0
    fi
}

# Confirm teardown
confirm_teardown() {
    section "TEARDOWN CONFIRMATION"
    
    warn "This will completely destroy the production cluster and all data!"
    echo "This includes:"
    echo "  • k3d production cluster"
    echo "  • All deployed applications and data"
    echo "  • Colima production profile"
    echo "  • All persistent volumes"
    echo "  • All logs not yet ingested"
    echo
    
    # Show what will be removed
    info "Current state:"
    if command -v k3d >/dev/null 2>&1 && k3d cluster list | grep -q production; then
        echo "  • k3d cluster: production (ACTIVE)"
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
    log "Auto-confirming teardown for automation..."
    
}

# Remove Helm releases with verification
remove_helm_releases() {
    section "REMOVING HELM RELEASES"
    
    # Get current kubectl context to ensure we're working with the right cluster
    current_context=$(kubectl config current-context 2>/dev/null || echo "none")
    
    case "$current_context" in
        *production*) ;;
        *)
            warn "Not connected to production cluster context, skipping Helm cleanup"
            return
            ;;
    esac
    
    # Get all helm releases
    progress "Discovering Helm releases..."
    if command -v helm >/dev/null 2>&1; then
        release_count=$(helm list --all-namespaces 2>/dev/null | grep -v NAME | wc -l | tr -d ' ')
        info "Found $release_count Helm releases to remove"
    else
        warn "Helm not found, skipping Helm cleanup"
        return
    fi
    
    # Remove in reverse order of dependencies - POSIX compatible array simulation
    remove_release() {
        release_name=$1
        namespace=$2
        
        if helm list -n "$namespace" 2>/dev/null | grep -q "^$release_name"; then
            progress "Removing $release_name from namespace $namespace..."
            
            if helm uninstall "$release_name" -n "$namespace" >/dev/null 2>&1; then
                # Verify removal
                if ! helm list -n "$namespace" 2>/dev/null | grep -q "^$release_name"; then
                    log "Successfully removed $release_name"
                else
                    error "Failed to remove $release_name - still exists"
                fi
            else
                error "Failed to uninstall $release_name"
            fi
        else
            info "$release_name not found in namespace $namespace, skipping"
        fi
    }
    
    # Remove releases in dependency order
    remove_release "observability" "observability"
    remove_release "monitoring" "default"
    remove_release "istio-config" "istio-system"
    remove_release "istio-gateway" "istio-gateway"
    remove_release "istiod" "istio-system"
    remove_release "istio-base" "istio-system"
    remove_release "metallb-config" "metallb-system"
    remove_release "metallb" "metallb-system"
    
    # Final verification
    remaining=$(helm list --all-namespaces 2>/dev/null | grep -v NAME | wc -l | tr -d ' ')
    if [ "$remaining" -gt 0 ]; then
        warn "$remaining Helm releases still remain"
    else
        log "All Helm releases successfully removed"
    fi
}

# Remove k3d cluster with verification
remove_k3d_cluster() {
    section "REMOVING K3D CLUSTER"
    
    # Check if production cluster exists
    if ! k3d cluster list | grep -q "production"; then
        info "k3d production cluster not found, skipping"
        return
    fi
    
    progress "Deleting k3d production cluster..."
    
    if k3d cluster delete production >/dev/null 2>&1; then
        verify_removed "k3d cluster" "k3d cluster list | grep -q production" "production"
    else
        error "Failed to delete k3d cluster"
        TEARDOWN_FAILED=true
    fi
    
    # Remove registry if it exists
    if docker ps -a | grep -q "production-registry"; then
        progress "Removing k3d registry..."
        docker stop production-registry >/dev/null 2>&1 || true
        docker rm production-registry >/dev/null 2>&1 || true
        
        verify_removed "Docker container" "docker ps -a | grep -q production-registry" "production-registry"
    fi
}

# Stop and remove Colima profile with verification
remove_colima_profile() {
    section "REMOVING COLIMA PROFILE"
    
    # Check if colima-production profile exists
    if ! colima list 2>/dev/null | grep -q "colima-production"; then
        info "Colima production profile not found, skipping"
        return
    fi
    
    # Stop if running
    if colima list 2>/dev/null | grep -q "^colima-production.*Running"; then
        progress "Stopping Colima production profile..."
        if colima stop -p colima-production; then
            log "Colima production profile stopped"
        else
            error "Failed to stop Colima production profile"
        fi
    fi
    
    # Delete the profile
    progress "Deleting Colima production profile..."
    if colima delete -p colima-production --force >/dev/null 2>&1; then
        verify_removed "Colima profile" "colima list 2>/dev/null | grep -q colima-production" "colima-production"
    else
        error "Failed to delete Colima production profile"
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
    
    info "Resources to clean: $containers_before containers, $networks_before networks, $volumes_before volumes"
    
    # Remove k3d-related containers
    if [ "$containers_before" -gt 0 ]; then
        progress "Removing k3d containers..."
        docker ps -a --filter "name=k3d-production" --format "{{.Names}}" | xargs -r docker rm -f >/dev/null 2>&1 || true
        
        containers_after=$(docker ps -a --filter "name=k3d-production" --format "{{.Names}}" 2>/dev/null | wc -l | tr -d ' ')
        if [ "$containers_after" -eq 0 ]; then
            log "All k3d containers removed"
        else
            error "$containers_after k3d containers still remain"
        fi
    fi
    
    # Remove k3d-related networks
    if [ "$networks_before" -gt 0 ]; then
        progress "Removing k3d networks..."
        docker network ls --filter "name=k3d-production" --format "{{.Name}}" | xargs -r docker network rm >/dev/null 2>&1 || true
        
        networks_after=$(docker network ls --filter "name=k3d-production" --format "{{.Name}}" 2>/dev/null | wc -l | tr -d ' ')
        if [ "$networks_after" -eq 0 ]; then
            log "All k3d networks removed"
        else
            error "$networks_after k3d networks still remain"
        fi
    fi
    
    # Remove k3d-related volumes
    if [ "$volumes_before" -gt 0 ]; then
        progress "Removing k3d volumes..."
        docker volume ls --filter "name=k3d-production" --format "{{.Name}}" | xargs -r docker volume rm >/dev/null 2>&1 || true
        
        volumes_after=$(docker volume ls --filter "name=k3d-production" --format "{{.Name}}" 2>/dev/null | wc -l | tr -d ' ')
        if [ "$volumes_after" -eq 0 ]; then
            log "All k3d volumes removed"
        else
            error "$volumes_after k3d volumes still remain"
        fi
    fi
}

# Reset kubectl context with verification
reset_kubectl_context() {
    section "RESETTING KUBECTL CONTEXT"
    
    # Get all k3d-related contexts
    contexts_to_remove=$(kubectl config get-contexts -o name 2>/dev/null | grep "k3d-production" || true)
    
    if [ -z "$contexts_to_remove" ]; then
        info "No k3d-production contexts found"
        return
    fi
    
    progress "Removing kubectl contexts..."
    echo "$contexts_to_remove" | while read -r context; do
        kubectl config delete-context "$context" >/dev/null 2>&1 || true
        log "Removed context: $context"
    done
    
    # Remove k3d clusters from kubeconfig
    progress "Removing cluster configurations..."
    clusters_to_remove=$(kubectl config get-clusters 2>/dev/null | grep "k3d-production" || true)
    if [ -n "$clusters_to_remove" ]; then
        echo "$clusters_to_remove" | xargs -r kubectl config delete-cluster
    fi
    
    # Remove k3d users from kubeconfig
    progress "Removing user configurations..."
    users_to_remove=$(kubectl config get-users 2>/dev/null | grep "k3d-production" || true)
    if [ -n "$users_to_remove" ]; then
        echo "$users_to_remove" | xargs -r kubectl config delete-user
    fi
    
    # Verify cleanup
    if kubectl config get-contexts 2>/dev/null | grep -q "k3d-production"; then
        error "Some k3d contexts still remain"
    else
        log "All k3d contexts successfully removed"
    fi
}

# Verify complete teardown
verify_teardown_complete() {
    section "VERIFYING TEARDOWN COMPLETION"
    
    verification_passed=true
    
    # Check k3d clusters
    progress "Checking for k3d clusters..."
    if k3d cluster list | grep -q "production"; then
        error "k3d production cluster still exists"
        verification_passed=false
    else
        log "No k3d production cluster found ✓"
    fi
    
    # Check Colima profiles
    progress "Checking for Colima profiles..."
    if colima list 2>/dev/null | grep -q "colima-production"; then
        error "Colima production profile still exists"
        verification_passed=false
    else
        log "No Colima production profile found ✓"
    fi
    
    # Check Docker resources
    progress "Checking for Docker resources..."
    docker_resources=$(docker ps -a --filter "name=k3d-production" --format "{{.Names}}" 2>/dev/null | wc -l | tr -d ' ')
    if [ "$docker_resources" -gt 0 ]; then
        error "$docker_resources Docker containers still exist"
        verification_passed=false
    else
        log "No k3d Docker containers found ✓"
    fi
    
    # Check kubectl contexts
    progress "Checking for kubectl contexts..."
    if kubectl config get-contexts 2>/dev/null | grep -q "k3d-production"; then
        error "kubectl contexts still exist for k3d-production"
        verification_passed=false
    else
        log "No k3d kubectl contexts found ✓"
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
        printf "%s║           TEARDOWN COMPLETED SUCCESSFULLY! 🧹            ║%s\n" "$GREEN" "$NC"
        printf "%s╠══════════════════════════════════════════════════════════╣%s\n" "$GREEN" "$NC"
        printf "%s║%s ✅ All components successfully removed\n" "$GREEN" "$NC"
        printf "%s║%s Duration: %dm %ds\n" "$GREEN" "$NC" $((duration/60)) $((duration%60))
        printf "%s╚══════════════════════════════════════════════════════════╝%s\n" "$GREEN" "$NC"
    else
        echo
        printf "%s╔══════════════════════════════════════════════════════════╗%s\n" "$RED" "$NC"
        printf "%s║           TEARDOWN COMPLETED WITH ERRORS! ⚠️             ║%s\n" "$RED" "$NC"
        printf "%s╠══════════════════════════════════════════════════════════╣%s\n" "$RED" "$NC"
        printf "%s║%s Some components may still exist\n" "$RED" "$NC"
        printf "%s║%s Duration: %dm %ds\n" "$RED" "$NC" $((duration/60)) $((duration%60))
        printf "%s╚══════════════════════════════════════════════════════════╝%s\n" "$RED" "$NC"
    fi
    
    echo
    echo "The system is ready for a fresh setup."
    echo "Run './setup-production-cluster.sh' to recreate the cluster."
}

# Main execution
main() {
    clear
    printf "%s━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━%s\n" "$PURPLE" "$NC"
    printf "%s     PRODUCTION CLUSTER TEARDOWN - POSIX COMPLIANT       %s\n" "$PURPLE" "$NC"
    printf "%s━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━%s\n" "$PURPLE" "$NC"
    
    confirm_teardown
    
    # Execute teardown steps
    remove_helm_releases
    remove_k3d_cluster
    remove_colima_profile
    cleanup_docker_resources
    reset_kubectl_context
    
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