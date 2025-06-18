# Infrastructure Distribution: Hybrid Approach Implementation Plan

## Overview
This document details the implementation plan for distributing Lamina OS infrastructure components using a hybrid approach that combines multiple distribution channels appropriate to each component type.

## Current State Analysis

### Infrastructure Components Inventory

#### Kubernetes/Helm Components
- **Location**: `infrastructure/targets/colima/k3s/charts/`
  - `colima-service-mesh/` - Istio service mesh configuration
  - `lamina-llm-serve/` - LLM serving Helm chart
  - `metallb/` - LoadBalancer for local Kubernetes
  - `monitoring/` - Prometheus, Grafana, Loki stack
  - `observability/` - Jaeger and Kiali
  - `service-mesh/` - Base Istio configuration

#### Docker Components
- **Build Environment**: `build-env/` - CI/CD containers
- **Service Images**: Various Dockerfiles across packages
- **Compose Templates**: `packages/lamina-core/lamina/infrastructure/`

#### Deployment Scripts
- **Kubernetes Setup**: `infrastructure/targets/colima/k3s/configs/`
- **General Scripts**: `scripts/` - Build, security, release automation

#### Terraform Modules
- **Infrastructure as Code**: `terraform/` - Cloud resource definitions

## Implementation Phases

### Phase 1: Create `lamina-infra` Package (Week 1)

#### Package Structure
```
packages/lamina-infra/
├── pyproject.toml
├── README.md
├── CLAUDE.md
├── lamina_infra/
│   ├── __init__.py
│   ├── cli.py              # Main CLI interface using Typer
│   ├── commands/
│   │   ├── download.py     # Component download commands
│   │   ├── deploy.py       # Deployment orchestration
│   │   ├── validate.py     # Infrastructure validation
│   │   └── config.py       # Configuration management
│   ├── core/
│   │   ├── downloader.py   # Asset download logic
│   │   ├── registry.py     # Component registry client
│   │   ├── compatibility.py # Version compatibility checking
│   │   └── paths.py        # Path management
│   ├── models/
│   │   ├── component.py    # Component data models
│   │   ├── manifest.py     # Manifest parsing
│   │   └── config.py       # Configuration models
│   └── data/
│       ├── compatibility.yaml # Version compatibility matrix
│       └── registry.yaml      # Default component registry
└── tests/
    ├── test_cli.py
    ├── test_downloader.py
    └── test_compatibility.py
```

#### Core Features
1. **Component Management**
   ```bash
   lamina-infra list                          # List available components
   lamina-infra show kubernetes               # Show component details
   lamina-infra download kubernetes --version 0.3.0
   lamina-infra download --all --version 0.3.0
   ```

2. **Version Compatibility**
   ```bash
   lamina-infra check-compatibility          # Verify all components
   lamina-infra upgrade --dry-run            # Show available upgrades
   ```

3. **Deployment Orchestration**
   ```bash
   lamina-infra deploy monitoring --env production
   lamina-infra status                       # Show deployment status
   lamina-infra validate --env production    # Validate configuration
   ```

4. **Configuration Management**
   ```bash
   lamina-infra config set helm.repository https://benaskins.github.io/lamina-os
   lamina-infra config get-all
   lamina-infra env list                     # List environments
   lamina-infra env create staging          # Create new environment
   ```

### Phase 2: Infrastructure Bundling System (Week 1)

#### Bundle Structure
```
release-bundles/
├── manifest.yaml                   # Global manifest with checksums
├── kubernetes/
│   ├── bundle.yaml                # Component manifest
│   ├── helm-charts/
│   │   ├── lamina-llm-serve-0.3.0.tgz
│   │   ├── monitoring-0.3.0.tgz
│   │   └── ...
│   ├── manifests/
│   │   ├── istio-gateway-config.yaml
│   │   └── istio-hostname-routing.yaml
│   └── scripts/
│       ├── setup.sh
│       └── teardown.sh
├── docker/
│   ├── bundle.yaml
│   ├── compose/
│   │   ├── docker-compose.yml
│   │   └── docker-compose-unified.yml
│   └── configs/
│       └── nginx.conf
└── terraform/
    ├── bundle.yaml
    └── modules/
        └── lamina-deployment/
```

#### Build Script: `scripts/build-infrastructure-release.py`
```python
#!/usr/bin/env python3
"""Build infrastructure release bundles for distribution."""

import hashlib
import json
import shutil
import tarfile
from pathlib import Path
from typing import Dict, List

class InfrastructureBuilder:
    def __init__(self, version: str):
        self.version = version
        self.root = Path(__file__).parent.parent
        self.output_dir = self.root / "dist" / "infrastructure"
        
    def build_kubernetes_bundle(self) -> Dict:
        """Build Kubernetes/Helm charts bundle."""
        # Package Helm charts
        # Copy manifests and scripts
        # Create bundle archive
        # Return manifest entry
        
    def build_docker_bundle(self) -> Dict:
        """Build Docker components bundle."""
        # Collect Docker Compose files
        # Copy Dockerfiles
        # Create bundle archive
        # Return manifest entry
        
    def build_terraform_bundle(self) -> Dict:
        """Build Terraform modules bundle."""
        # Package Terraform modules
        # Include examples
        # Create bundle archive
        # Return manifest entry
        
    def generate_manifest(self, bundles: List[Dict]) -> None:
        """Generate global manifest with checksums."""
        # Create manifest.yaml with all components
        # Include version compatibility info
        # Add checksums for verification
```

### Phase 3: Distribution Channel Setup (Week 2)

#### 1. GitHub Container Registry
**Workflow**: `.github/workflows/publish-containers.yml`
```yaml
name: Publish Container Images

on:
  release:
    types: [published]
  workflow_dispatch:
    inputs:
      version:
        description: 'Version tag'
        required: true

jobs:
  publish-images:
    strategy:
      matrix:
        image:
          - lamina-llm-serve
          - lamina-build-env
          - lamina-chromadb
    steps:
      - name: Build and push
        # Build from Dockerfile
        # Tag with version
        # Push to ghcr.io
```

#### 2. Helm Chart Repository
**Setup GitHub Pages Repository**:
1. Create `helm-charts` branch
2. Generate index.yaml
3. Package charts with versions
4. Update index on each release

**Workflow**: `.github/workflows/publish-helm-charts.yml`
```yaml
name: Publish Helm Charts

on:
  release:
    types: [published]

jobs:
  publish-charts:
    steps:
      - name: Package Helm charts
      - name: Generate index
      - name: Publish to GitHub Pages
```

#### 3. GitHub Release Assets
**Workflow**: `.github/workflows/release-infrastructure.yml`
```yaml
name: Release Infrastructure Bundles

on:
  release:
    types: [created]

jobs:
  build-bundles:
    steps:
      - name: Build infrastructure bundles
        run: python scripts/build-infrastructure-release.py --version ${{ github.event.release.tag_name }}
      
      - name: Upload bundles to release
        # Upload each bundle as release asset
        # Include checksums and manifest
```

### Phase 4: Release Process Updates (Week 2)

#### Update `scripts/release.py`
Add infrastructure steps:
1. Build Python packages (existing)
2. Build infrastructure bundles (new)
3. Generate compatibility matrix (new)
4. Create unified manifest (new)
5. Prepare distribution commands (new)

#### Release Checklist Template
```markdown
## Lamina OS v{version} Release Checklist

### Pre-release
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Version bumped in all packages
- [ ] Infrastructure compatibility verified

### Python Packages
- [ ] lamina-core built and tested
- [ ] lamina-llm-serve built and tested
- [ ] lamina-infra built and tested

### Infrastructure Bundles
- [ ] Kubernetes bundle created
- [ ] Docker bundle created
- [ ] Terraform bundle created
- [ ] Manifests generated with checksums

### Distribution
- [ ] GitHub Release created
- [ ] Python packages published to PyPI
- [ ] Infrastructure bundles attached to release
- [ ] Container images published to GHCR
- [ ] Helm charts published to repository

### Post-release
- [ ] Documentation site updated
- [ ] Compatibility matrix updated
- [ ] Release announcement sent
```

### Phase 5: Documentation (Week 2)

#### 1. Infrastructure Deployment Guide
**File**: `docs/infrastructure-deployment-guide.md`
- Installation instructions for each platform
- Environment-specific deployment examples
- Troubleshooting guide
- Best practices

#### 2. Component Reference
**Directory**: `docs/infrastructure/components/`
- Detailed documentation for each component
- Configuration options
- Integration points
- Version compatibility

#### 3. Migration Guide
**File**: `docs/infrastructure-migration-guide.md`
- Migrating from repository-based deployment
- Version upgrade procedures
- Rollback strategies

## Timeline and Milestones

### Week 1
- Day 1-2: Create `lamina-infra` package structure and core CLI
- Day 3-4: Implement download and compatibility features
- Day 5: Build infrastructure bundling system

### Week 2
- Day 1-2: Set up GitHub Container Registry and workflows
- Day 3: Configure Helm chart repository
- Day 4: Update release process and scripts
- Day 5: Documentation and testing

### Success Criteria
1. `lamina-infra` package successfully downloads all components
2. All infrastructure bundles build without errors
3. Container images publish to GHCR
4. Helm charts accessible via repository
5. End-to-end deployment works with new distribution

## Risk Mitigation

### Technical Risks
1. **Large Bundle Sizes**: Implement compression and selective downloads
2. **Version Conflicts**: Strict compatibility checking and clear error messages
3. **Network Issues**: Implement retry logic and resume capabilities

### Process Risks
1. **Complex Release**: Automate all steps, comprehensive checklist
2. **Breaking Changes**: Careful version management, migration guides
3. **User Confusion**: Clear documentation, helpful CLI messages

## Future Enhancements

### Phase 6 (Future)
1. **Terraform Registry**: Publish modules to official registry
2. **Package Managers**: Homebrew formula, APT/YUM packages
3. **Cloud Marketplaces**: AWS/Azure/GCP marketplace listings
4. **Air-gapped Support**: Offline installation bundles

### Phase 7 (Future)
1. **GUI Installer**: Desktop application for infrastructure setup
2. **Cloud Shell**: Browser-based deployment interface
3. **Operators**: Kubernetes operators for automated management

---

This plan provides a structured approach to implementing infrastructure distribution for Lamina OS, ensuring professional deployment capabilities while maintaining the project's philosophical integrity.