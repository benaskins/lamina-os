# Lamina OS Infrastructure Release Guide

This guide provides step-by-step procedures for releasing Lamina OS infrastructure components using the hybrid distribution approach.

## Overview

Lamina OS infrastructure is distributed through multiple channels:
- **Python Package** (`lamina-infra`): CLI tools for infrastructure management
- **GitHub Releases**: Versioned infrastructure bundles
- **Container Registry**: Docker images via GitHub Container Registry
- **Helm Repository**: Charts via GitHub Pages

## Prerequisites

Before releasing infrastructure:
1. Ensure all tests pass: `./scripts/check-build.sh`
2. Verify infrastructure components work: `./scripts/test-infrastructure.sh`
3. Update version numbers consistently
4. Review and update documentation

## Release Process

### Step 1: Prepare Infrastructure Bundles

Run the infrastructure build script:
```bash
python scripts/build-infrastructure-release.py --version 0.3.0
```

This creates bundles in `dist/infrastructure/`:
- `kubernetes-bundle-0.3.0.tar.gz`
- `docker-bundle-0.3.0.tar.gz`
- `terraform-bundle-0.3.0.tar.gz`
- `manifest-0.3.0.yaml`

### Step 2: Build Container Images

For each container image:
```bash
# Build and tag images
docker build -t ghcr.io/benaskins/lamina-os/lamina-llm-serve:0.3.0 \
  -f packages/lamina-llm-serve/Dockerfile .

# Push to registry (requires authentication)
docker push ghcr.io/benaskins/lamina-os/lamina-llm-serve:0.3.0
```

### Step 3: Package Helm Charts

Package each Helm chart:
```bash
cd infrastructure/templates/charts
helm package lamina-llm-serve --version 0.3.0
helm package monitoring --version 0.3.0
helm package observability --version 0.3.0
helm package service-mesh --version 0.3.0
```

### Step 4: Update Helm Repository

Update the Helm repository index:
```bash
# Switch to helm-charts branch
git checkout helm-charts

# Copy packaged charts
cp *.tgz .

# Generate/update index
helm repo index . --url https://benaskins.github.io/lamina-os

# Commit and push
git add .
git commit -m "Add Helm charts for v0.3.0"
git push origin helm-charts
```

### Step 5: Create GitHub Release

1. Create release on GitHub:
   ```bash
   gh release create v0.3.0 --title "Lamina OS v0.3.0" \
     --notes-file docs/releases/v0.3.0/RELEASE_NOTES_v0.3.0.md
   ```

2. Upload infrastructure bundles:
   ```bash
   gh release upload v0.3.0 dist/infrastructure/*.tar.gz
   gh release upload v0.3.0 dist/infrastructure/manifest-0.3.0.yaml
   ```

### Step 6: Publish Python Packages

Publish the new `lamina-infra` package:
```bash
cd packages/lamina-infra
uv build
uv publish dist/* --token $PYPI_TOKEN
```

### Step 7: Update Documentation

1. Update compatibility matrix in `lamina-infra`
2. Update installation guides with new version
3. Add version-specific deployment examples
4. Update the documentation site

### Step 8: Verification

Verify the release:
```bash
# Test package installation
pip install lamina-infra==0.3.0

# Test infrastructure download
lamina-infra download --all --version 0.3.0

# Verify Helm charts
helm repo add lamina https://benaskins.github.io/lamina-os
helm repo update
helm search repo lamina/

# Test container images
docker pull ghcr.io/benaskins/lamina-os/lamina-llm-serve:0.3.0
```

## Component-Specific Procedures

### Kubernetes/Helm Components

1. **Version Update**: Update `Chart.yaml` version in each chart
2. **Dependency Update**: Run `helm dependency update` if needed
3. **Lint Charts**: `helm lint` each chart before packaging
4. **Test Installation**: Deploy to test cluster before release

### Docker Images

1. **Multi-Architecture Build**: Use buildx for arm64/amd64
2. **Security Scan**: Run security scanner on images
3. **Size Optimization**: Ensure images are optimized
4. **Tag Strategy**: Use semantic versioning and `latest` tag

### Terraform Modules

1. **Format Check**: Run `terraform fmt -check`
2. **Validation**: Run `terraform validate`
3. **Documentation**: Update module README files
4. **Example Update**: Test example configurations

## Rollback Procedures

If issues are discovered post-release:

1. **Yank Python Package** (if critical):
   ```bash
   # Use PyPI interface to yank version
   ```

2. **Update Helm Repository**:
   ```bash
   # Remove problematic chart version
   # Regenerate index
   # Push updates
   ```

3. **Create Patch Release**:
   - Fix issues
   - Bump patch version
   - Follow expedited release process

## Automation

Most steps are automated via GitHub Actions:
- `.github/workflows/release-infrastructure.yml`
- `.github/workflows/publish-containers.yml`
- `.github/workflows/publish-helm-charts.yml`

Manual trigger for testing:
```bash
gh workflow run release-infrastructure.yml -f version=0.3.0-rc1
```

## Troubleshooting

### Common Issues

1. **Authentication Failures**
   - Ensure GHCR_TOKEN is set
   - Check PyPI token validity
   - Verify GitHub Pages permissions

2. **Build Failures**
   - Check Docker daemon is running
   - Verify Helm v3 is installed
   - Ensure all dependencies are installed

3. **Version Conflicts**
   - Ensure all components use same version
   - Check compatibility matrix
   - Verify dependency versions

### Debug Commands

```bash
# Check bundle contents
tar -tzf dist/infrastructure/kubernetes-bundle-0.3.0.tar.gz

# Verify manifest
cat dist/infrastructure/manifest-0.3.0.yaml

# Test Helm chart locally
helm install test ./lamina-llm-serve --dry-run --debug

# Check image layers
docker history ghcr.io/benaskins/lamina-os/lamina-llm-serve:0.3.0
```

## Security Considerations

1. **Signing**: Sign release artifacts with GPG
2. **Checksums**: Always include SHA256 checksums
3. **Vulnerability Scanning**: Run on all components
4. **Access Control**: Limit who can push releases
5. **Audit Trail**: Keep detailed release logs

---

For questions or issues with the release process, consult the Lamina OS development team or file an issue in the repository.