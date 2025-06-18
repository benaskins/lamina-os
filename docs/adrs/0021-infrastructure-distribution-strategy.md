# ADR-0021: Infrastructure Distribution Strategy

## Status
Proposed

## Context
Lamina OS has grown to include significant infrastructure components beyond the core Python packages:
- Kubernetes manifests and Helm charts
- Docker Compose configurations
- Terraform modules
- Deployment scripts and automation
- Container images and Dockerfiles
- Monitoring and observability configurations

Currently, these infrastructure components exist only in the repository and are not distributed through any package management system. This creates challenges for users who want to deploy Lamina OS infrastructure without cloning the entire repository.

The v0.3.0 release highlighted this gap when we attempted to create a release and realized that infrastructure components have no distribution mechanism.

## Decision
We will implement a hybrid distribution approach that leverages multiple channels appropriate to each component type:

1. **Python Package (`lamina-infra`)**: A new package providing CLI tools for infrastructure management
2. **GitHub Releases**: Versioned bundles of infrastructure components as release assets
3. **Container Registry**: Published Docker images via GitHub Container Registry
4. **Helm Repository**: Helm charts published to GitHub Pages
5. **Terraform Registry**: Terraform modules published for reuse (future)

The `lamina-infra` package will serve as the orchestration layer, providing:
- Infrastructure component discovery and download
- Version compatibility management
- Deployment automation
- Configuration validation

## Consequences

### Positive
- **Native Distribution**: Each component type is distributed through its ecosystem's standard channels
- **Selective Installation**: Users can install only the components they need
- **Version Management**: Clear versioning and compatibility tracking between components
- **Professional Approach**: Follows industry best practices for infrastructure distribution
- **Automation Friendly**: CLI tools enable scripted deployments and CI/CD integration

### Negative
- **Complexity**: Multiple distribution channels to maintain
- **Release Overhead**: More complex release process requiring coordination
- **Learning Curve**: Users must understand multiple tools and registries
- **Maintenance Burden**: Each distribution channel requires ongoing maintenance

### Neutral
- Infrastructure and Python packages can be versioned independently if needed
- Requires new CI/CD workflows for each distribution channel
- Creates a clear separation between application code and infrastructure

## Implementation

### Phase 1: Package Creation
Create `packages/lamina-infra/` with CLI tools for infrastructure management.

### Phase 2: Distribution Channels
1. Set up GitHub Container Registry for Docker images
2. Configure GitHub Pages as Helm chart repository
3. Automate GitHub Release asset creation

### Phase 3: Automation
Update release scripts to handle multi-channel distribution.

### Phase 4: Documentation
Comprehensive guides for infrastructure deployment using the new tools.

## Alternatives Considered

1. **Repository-only**: Keep infrastructure in repo only
   - Rejected: Poor user experience, requires full repo clone

2. **Single Python Package**: Bundle all infrastructure as package data
   - Rejected: Unnatural fit, large package size, poor tooling integration

3. **Separate Repository**: Move infrastructure to dedicated repo
   - Rejected: Splits codebase, complicates development

4. **Platform-specific Packages**: Create OS packages (deb, rpm, brew)
   - Rejected: High maintenance, limited reach

## References
- [Helm Chart Repository Guide](https://helm.sh/docs/topics/chart_repository/)
- [GitHub Container Registry Docs](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Terraform Registry Publishing](https://www.terraform.io/docs/registry/modules/publish.html)

## Appendix
Detailed implementation plan available in `/docs/proposals/infrastructure/hybrid-distribution-plan.md`

---

🔨 Crafted by Luthier