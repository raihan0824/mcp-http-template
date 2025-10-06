#!/bin/bash

# MCP Server Kubernetes Deployment Script
set -euo pipefail

# Configuration
NAMESPACE="mcp-server"
DEPLOYMENT_TYPE="${1:-helm}"  # helm or k8s
ENVIRONMENT="${2:-dev}"       # dev, staging, prod

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed or not in PATH"
        exit 1
    fi
    
    # Check Helm if needed
    if [[ "$DEPLOYMENT_TYPE" == "helm" ]] && ! command -v helm &> /dev/null; then
        log_error "helm is not installed or not in PATH"
        exit 1
    fi
    
    # Check cluster connectivity
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Deploy with Helm
deploy_helm() {
    log_info "Deploying with Helm..."
    
    local values_file="deployment/helm/mcp-server/values-${ENVIRONMENT}.yaml"
    local helm_args=""
    
    # Use environment-specific values if available
    if [[ -f "$values_file" ]]; then
        helm_args="-f $values_file"
        log_info "Using values file: $values_file"
    else
        log_warning "No environment-specific values file found, using defaults"
    fi
    
    # Install or upgrade
    if helm list -n "$NAMESPACE" | grep -q "mcp-server"; then
        log_info "Upgrading existing Helm release..."
        helm upgrade mcp-server deployment/helm/mcp-server \
            --namespace "$NAMESPACE" \
            $helm_args \
            --wait \
            --timeout 300s
    else
        log_info "Installing new Helm release..."
        helm install mcp-server deployment/helm/mcp-server \
            --namespace "$NAMESPACE" \
            --create-namespace \
            $helm_args \
            --wait \
            --timeout 300s
    fi
    
    log_success "Helm deployment completed"
}

# Deploy with raw Kubernetes manifests
deploy_k8s() {
    log_info "Deploying with Kubernetes manifests..."
    
    # Apply manifests in order
    local manifests=(
        "namespace.yaml"
        "configmap.yaml"
        "deployment.yaml"
        "service.yaml"
    )
    
    # Optional manifests
    local optional_manifests=(
        "ingress.yaml"
        "hpa.yaml"
        "networkpolicy.yaml"
    )
    
    # Apply core manifests
    for manifest in "${manifests[@]}"; do
        log_info "Applying $manifest..."
        kubectl apply -f "deployment/k8s/$manifest"
    done
    
    # Apply optional manifests if they exist and are configured
    for manifest in "${optional_manifests[@]}"; do
        if [[ -f "deployment/k8s/$manifest" ]]; then
            log_info "Applying optional $manifest..."
            kubectl apply -f "deployment/k8s/$manifest" || log_warning "Failed to apply $manifest (this may be expected)"
        fi
    done
    
    # Wait for deployment to be ready
    log_info "Waiting for deployment to be ready..."
    kubectl rollout status deployment/mcp-server -n "$NAMESPACE" --timeout=300s
    
    log_success "Kubernetes deployment completed"
}

# Verify deployment
verify_deployment() {
    log_info "Verifying deployment..."
    
    # Check pods
    local ready_pods=$(kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/name=mcp-server --no-headers | grep Running | wc -l)
    local total_pods=$(kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/name=mcp-server --no-headers | wc -l)
    
    if [[ "$ready_pods" -eq "$total_pods" ]] && [[ "$total_pods" -gt 0 ]]; then
        log_success "All pods are running ($ready_pods/$total_pods)"
    else
        log_error "Not all pods are running ($ready_pods/$total_pods)"
        kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/name=mcp-server
        return 1
    fi
    
    # Check service
    if kubectl get service mcp-server -n "$NAMESPACE" &> /dev/null; then
        log_success "Service is available"
    else
        log_error "Service is not available"
        return 1
    fi
    
    # Test health endpoint
    log_info "Testing health endpoint..."
    if kubectl run test-pod --rm -i --restart=Never --image=curlimages/curl:latest -- \
        curl -f -H "Accept: application/json, text/event-stream" \
        "http://mcp-server.${NAMESPACE}.svc.cluster.local:3000/mcp/" &> /dev/null; then
        log_success "Health endpoint is responding"
    else
        log_warning "Health endpoint test failed (this may be expected in some environments)"
    fi
}

# Show deployment info
show_info() {
    log_info "Deployment Information:"
    echo "========================"
    
    # Pods
    echo -e "${BLUE}Pods:${NC}"
    kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/name=mcp-server
    echo
    
    # Service
    echo -e "${BLUE}Service:${NC}"
    kubectl get service -n "$NAMESPACE"
    echo
    
    # Ingress (if exists)
    if kubectl get ingress -n "$NAMESPACE" &> /dev/null; then
        echo -e "${BLUE}Ingress:${NC}"
        kubectl get ingress -n "$NAMESPACE"
        echo
    fi
    
    # HPA (if exists)
    if kubectl get hpa -n "$NAMESPACE" &> /dev/null; then
        echo -e "${BLUE}HPA:${NC}"
        kubectl get hpa -n "$NAMESPACE"
        echo
    fi
    
    # Port forward command
    echo -e "${BLUE}To access locally:${NC}"
    echo "kubectl port-forward svc/mcp-server 3000:3000 -n $NAMESPACE"
    echo
}

# Main execution
main() {
    log_info "Starting MCP Server deployment..."
    log_info "Deployment type: $DEPLOYMENT_TYPE"
    log_info "Environment: $ENVIRONMENT"
    log_info "Namespace: $NAMESPACE"
    echo
    
    check_prerequisites
    
    case "$DEPLOYMENT_TYPE" in
        "helm")
            deploy_helm
            ;;
        "k8s")
            deploy_k8s
            ;;
        *)
            log_error "Invalid deployment type: $DEPLOYMENT_TYPE (use 'helm' or 'k8s')"
            exit 1
            ;;
    esac
    
    verify_deployment
    show_info
    
    log_success "MCP Server deployment completed successfully!"
}

# Help function
show_help() {
    echo "Usage: $0 [DEPLOYMENT_TYPE] [ENVIRONMENT]"
    echo
    echo "DEPLOYMENT_TYPE:"
    echo "  helm    - Deploy using Helm chart (default)"
    echo "  k8s     - Deploy using raw Kubernetes manifests"
    echo
    echo "ENVIRONMENT:"
    echo "  dev     - Development environment (default)"
    echo "  staging - Staging environment"
    echo "  prod    - Production environment"
    echo
    echo "Examples:"
    echo "  $0                    # Deploy with Helm in dev environment"
    echo "  $0 helm prod          # Deploy with Helm in prod environment"
    echo "  $0 k8s staging        # Deploy with K8s manifests in staging"
    echo
}

# Handle help flag
if [[ "${1:-}" == "-h" ]] || [[ "${1:-}" == "--help" ]]; then
    show_help
    exit 0
fi

# Run main function
main "$@"
