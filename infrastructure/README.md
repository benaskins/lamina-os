# Infrastructure Directory

This directory contains the reorganized infrastructure templates, configurations, and deployment scripts for Lamina OS.

## Directory Structure

```
infrastructure/
├── templates/
│   ├── base/                          # Generic Helm charts
│   │   ├── lamina-llm-serve/          # Core LLM serving service
│   │   ├── monitoring/                # Prometheus, Grafana, Loki, Vector
│   │   ├── observability/             # Jaeger, Kiali for service mesh
│   │   └── service-mesh/              # Base Istio configuration
│   └── targets/
│       ├── colima-k3s/                # Target-specific chart modifications
│       │   ├── colima-service-mesh/   # Colima-specific Istio config
│       │   └── metallb/               # LoadBalancer configuration
│       └── k3d/                       # k3d target modifications
│           ├── k3d-service-mesh/      # k3d-specific Istio config
│           └── metallb/               # LoadBalancer configuration
├── scripts/
│   └── targets/
│       ├── colima-k3s/
│       │   ├── setup.sh               # Deployment script
│       │   └── teardown.sh            # Cleanup script
│       └── k3d/
│           ├── setup.sh               # Deployment script
│           └── teardown.sh            # Cleanup script
├── environments/                      # Environment-specific values
│   ├── development/
│   │   └── values.yaml                # Development configuration
│   └── production/
│       └── values.yaml                # Production configuration
├── istio-gateway-config.yaml          # Global Istio gateway config
└── istio-hostname-routing.yaml        # Hostname-based routing rules
```

## Key Improvements

### 1. Separation of Base and Target-Specific Components
- **Base charts** (`templates/base/`) contain generic Helm charts that work across different deployment targets
- **Target-specific charts** (`templates/targets/`) contain modifications specific to deployment environments (e.g., Colima/K3s)

### 2. Environment-Based Configuration
- **Development values** (`environments/development/values.yaml`) - Optimized for local development with lower resource requirements
- **Production values** (`environments/production/values.yaml`) - Scaled for production with HA, security, and performance optimizations

### 3. Centralized Script Management
- Scripts are organized by target environment in `scripts/targets/`
- Each target has its own setup and teardown scripts
- Scripts automatically extract the appropriate values from environment configurations

## Usage

### Development Environment (k3d)
```bash
cd infrastructure/scripts/targets/k3d
./setup.sh --env development
```

### Production Environment (Colima/K3s)
```bash
cd infrastructure/scripts/targets/colima-k3s
./setup.sh --env production
```

### Teardown
```bash
cd infrastructure/scripts/targets/k3d
./teardown.sh --env [development|production]
```

## Chart Dependencies

The setup script installs components in the following order to handle dependencies:

1. **MetalLB** - LoadBalancer implementation
2. **Istio Base** - Service mesh CRDs
3. **Istio Control Plane** - Service mesh control plane  
4. **Istio Gateway** - Ingress gateway
5. **Istio Configuration** - mTLS, telemetry, routing rules
6. **Monitoring Stack** - Prometheus, Grafana, Loki, Vector
7. **Observability Stack** - Jaeger, Kiali
8. **Lamina LLM Serve** - Core application services

## Environment Configuration

Each environment file (`environments/*/values.yaml`) contains consolidated configuration for all services:

- **Global settings** - Environment name, target configuration
- **Service-specific settings** - Resource allocation, replicas, storage
- **Security settings** - Authentication, TLS, access controls
- **Performance tuning** - Resource limits, scaling parameters

The setup scripts automatically extract the relevant sections for each Helm chart deployment.

## Target Customization

To add a new deployment target:

1. Create `templates/targets/[target-name]/` with target-specific chart modifications
2. Create `scripts/targets/[target-name]/` with deployment scripts
3. Create environment configurations in `environments/`
4. Update scripts to reference the new target structure

This organization provides clear separation between reusable components and deployment-specific customizations while maintaining a single source of truth for environment configurations.