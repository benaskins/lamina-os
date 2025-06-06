# Infrastructure Proposal: Container-First Development and Production Environment

**Prepared for**: Ben Askins  
**Prepared by**: Luthier  
**Date**: June 6, 2025  
**System**: M3 Ultra Mac Studio (32 cores, 512GB RAM, 80 GPU cores)  
**Architecture Alignment**: ADR-0009, ADR-0011, ADR-0013

## Executive Summary

This proposal outlines a comprehensive infrastructure design that aligns with our established breath-first development principles while ensuring consistency between development, test, and production environments. The design emphasizes Docker-based containerization with simple docker-compose orchestration for rapid iteration, backed by Colima for local development and Kubernetes for production deployment.

## Architectural Alignment with ADRs

### ADR-0009: Containerized Microservices Architecture
- **Adopted**: Docker Compose for service orchestration
- **Template-based infrastructure**: Generated from `.template` files using our infrastructure templating system
- **mTLS service mesh**: nginx-based secure service communication

### ADR-0011: Three-Tier Environment Management
- **Development**: Docker Compose with Colima backend for rapid iteration
- **Test**: Containerized services with ephemeral test containers
- **Production**: Kubernetes with identical container images from development

### ADR-0013: Infrastructure Templating System
- **Template separation**: Generic templates in `lamina/infrastructure/`, agent-specific values in `sanctuary/`
- **Build generation**: Infrastructure files generated to `.build/infrastructure/` with unique build IDs
- **CLI integration**: `make generate-infrastructure` for dynamic infrastructure generation

## Current State Analysis

### Existing Infrastructure Strengths
- **Template-based docker-compose**: Already generating infrastructure from templates
- **mTLS service mesh**: Secure nginx-based inter-service communication
- **Unified container**: Single image supporting both single-agent and multi-agent modes
- **Observability stack**: Integrated Grafana, Loki, Vector monitoring

### Current Pain Points
- **Colima underutilization**: 4 cores, 8GB RAM (98% underutilized on 32-core, 512GB system)
- **Build environment inconsistency**: No containerized build environment for CI/CD parity
- **Manual build verification**: No production-like container verification before commits

### Resource Allocation Strategy

| Component | CPU Cores | Memory | Purpose |
|-----------|-----------|---------|---------|
| **Development (Colima)** | 12 cores | 128GB | Fast iteration, docker-compose, AI dev workloads |
| **Production (K8s)** | 16 cores | 256GB | Production AI infrastructure |
| **macOS Host** | 4 cores | 64GB | IDE, tools, system services |
| **System Reserve** | - | 64GB | OS overhead, burst capacity |
| **Total System** | **32 cores** | **512GB** | **Both environments running simultaneously** |

## Proposed Architecture

### 1. Development Environment (Colima + Docker Compose)

**Enhanced Colima Configuration**:
```bash
# Colima configuration for AI development
colima start --cpu 12 --memory 128 --disk 200
```

**Docker Compose Workflow**:
```bash
# Current workflow enhanced
make generate-infrastructure AGENT_NAME=clara
cd .build/infrastructure
docker-compose up -d              # Start development environment
docker-compose exec unified-agent-server bash  # Debug container
```

**AI Development Capabilities with 256GB**:
- **Large Models**: 70B models for development and testing
- **Multi-Agent Development**: Multiple agents running simultaneously
- **Vector Database Development**: ChromaDB with substantial datasets
- **Model Experimentation**: Loading/testing different models
- **Memory-Intensive Development**: AMEM with complex memory graphs
- **Fast Iteration**: Docker-compose with substantial AI workloads

### 2. Containerized Build Environment

**Existing Build System** (already implemented):
- **Build Environment**: `build-env/Dockerfile` with Python 3.12, uv, ruff
- **Automated Commands**: `build-env/Makefile` with format, check, test targets
- **Convenience Script**: `scripts/check-build.sh` for project root execution

**Standard Build Commands**:
```bash
# Auto-fix formatting and linting (PREFERRED METHOD)
cd build-env && make format

# Verify all checks pass - CI simulation (REQUIRED BEFORE PUSH)
cd build-env && make check

# Convenience script from project root
./scripts/check-build.sh

# Individual operations
cd build-env && make lint      # Just linting checks
cd build-env && make test      # Just run tests
cd build-env && make shell     # Interactive debugging
```

**GitHub Actions Integration**:
```yaml
# .github/workflows/ci.yml (already configured)
- name: Build verification container
  run: cd build-env && make build

- name: Run all checks
  run: cd build-env && make check
```

### 3. Production Environment (Kubernetes)

**Container Consistency**:
- **Same base images**: Development and production use identical container images
- **Configuration separation**: Environment-specific configs via ConfigMaps/Secrets
- **Template reuse**: Same docker-compose templates adapted for Kubernetes manifests

**Production Kubernetes Architecture**:
```yaml
# Production namespace structure
namespaces:
  lamina-production:
    - agent-coordination-pods
    - model-serving-infrastructure  
    - sanctuary-configuration-management
    - mtls-service-mesh
    
  lamina-staging:
    - pre-production-testing
    - integration-verification
    
  lamina-build:
    - containerized-build-jobs
    - ci-cd-pipeline-runners
```

### 4. Integrated Build System

**Current Implementation** (leverages existing build-env/):
```makefile
# Use existing containerized build system
check: ## Run all CI checks locally (REQUIRED before push)
	@echo "🔍 Running containerized build checks..."
	./scripts/check-build.sh

format: ## Auto-fix formatting and linting
	@echo "🎨 Auto-fixing code..."
	cd build-env && make format

lint: ## Run linting checks only
	@echo "🔍 Running linting checks..."
	cd build-env && make lint

test: ## Run tests only
	@echo "🧪 Running tests..."
	cd build-env && make test

build-shell: ## Interactive shell in build environment
	@echo "🐚 Opening build environment shell..."
	cd build-env && make shell
```

## Implementation Phases

### Phase 1: Enhanced Development Environment (Week 1)
1. **Upgrade Colima configuration** to use 16 cores, 256GB RAM
2. **Create containerized build environment** with Dockerfile.build-env
3. **Update Makefile** with containerized build commands
4. **Implement pre-commit container verification** workflow

### Phase 2: Build System Containerization (Week 2)  
1. **Containerize all build processes** using uv-based build container
2. **Update GitHub Actions** to use same container images
3. **Create environment consistency verification** scripts
4. **Test container-based development workflow** end-to-end

### Phase 3: Production Kubernetes Preparation (Week 3)
1. **Convert docker-compose templates** to Kubernetes manifests
2. **Set up staging environment** for production testing
3. **Implement container image promotion** pipeline
4. **Create production deployment scripts**

### Phase 4: Integration & Optimization (Week 4)
1. **End-to-end workflow testing** across all environments
2. **Performance optimization** for containerized builds
3. **Documentation updates** for new workflows
4. **Team training** on container-first development

## Developer Workflow

### Daily Development Cycle
```bash
# 1. Start development environment (Colima + docker-compose)
colima start --cpu 12 --memory 128
make generate-infrastructure AGENT_NAME=clara
cd .build/infrastructure && docker-compose up -d

# 2. Make code changes
vim packages/lamina-core/src/lamina/agents/clara.py

# 3. Auto-fix formatting issues
cd build-env && make format

# 4. Verify all checks pass (REQUIRED before commit)
cd build-env && make check

# 5. Commit and push (only after verification passes)
git commit -m "feat: enhance Clara agent capabilities"
git push origin feature-branch
```

### Build Environment Guarantees
- **Identical containers**: Development, CI, and production use same base images
- **Dependency consistency**: uv lock files ensure exact dependency versions
- **Environment isolation**: All builds run in clean, reproducible containers
- **Pre-commit verification**: No commits allowed without container-based verification

## Resource Efficiency

### Current vs Proposed Utilization

| Resource | Current | Proposed | Improvement |
|----------|---------|----------|-------------|
| CPU Cores | 4 (12.5%) | 24 (75%) | **6x increase** |
| Memory | 8GB (1.6%) | 384GB (75%) | **48x increase** |
| AI Model Capacity | Single 7B model | Multiple 70B+ models | **Massive scale** |
| Vector DB Scale | Small datasets | Millions of embeddings | **Production scale** |
| Agent Concurrency | 1 agent | 4+ agents simultaneously | **Multi-agent ready** |

### AI Development Capabilities Unlocked
- **Large Model Development**: Load 70B+ models (Llama-3, CodeLlama, etc.)
- **Multi-Agent Testing**: All 4 agents (Clara, Luna, Vesna, Phi) simultaneously
- **Training Workflows**: Fine-tuning and training with substantial memory
- **Production-Scale Datasets**: Vector databases with millions of embeddings
- **Memory Graph Exploration**: AMEM with extensive relationship networks
- **Model Comparison**: A/B testing multiple models side-by-side
- **Instant Environment Setup**: Full AI stack in seconds with Docker Compose

## Risk Mitigation

### Technical Risks
- **Colima stability**: Enhanced monitoring and automatic restart scripts
- **Container complexity**: Simplified Makefile commands hide complexity
- **Resource contention**: Careful resource allocation and monitoring

### Development Workflow Risks  
- **Learning curve**: Gradual adoption with extensive documentation
- **Build time regression**: Performance monitoring and optimization
- **Dependency conflicts**: uv lock files and container isolation

## Success Metrics

### Development KPIs
- **Build time**: < 60 seconds for full test suite
- **Environment startup**: < 30 seconds for docker-compose up
- **Container verification**: 100% commits verified before push
- **Environment consistency**: Zero production surprises from environment drift

### Infrastructure KPIs
- **Colima utilization**: 40-60% sustained load
- **Container build cache hits**: > 90% for incremental builds
- **CI/CD reliability**: > 99% successful builds
- **Development velocity**: 50% reduction in environment-related issues

## Implementation Considerations

### ADR Compliance
- **ADR-0009**: Maintains containerized microservices with enhanced orchestration
- **ADR-0011**: Strengthens three-tier environment management with container consistency
- **ADR-0013**: Leverages infrastructure templating for multi-environment deployment

### Breath-First Development Alignment
- **Presence over speed**: Container verification encourages thoughtful commits
- **Deliberate development**: Pre-commit verification prevents rushed deployments
- **Conscious tooling**: Infrastructure templates support mindful agent configuration

## Recommendation

**Proceed with phased implementation** of the container-first infrastructure approach. This design:

1. **Maintains simplicity**: Docker Compose for development, Kubernetes for production
2. **Ensures consistency**: Same containers across all environments
3. **Improves reliability**: Containerized build verification prevents environment drift
4. **Maximizes resources**: Better utilization of exceptional hardware
5. **Supports scaling**: Ready for team expansion and production deployment

The approach aligns perfectly with our established ADRs while providing the rapid iteration capabilities needed for breath-first development.

## Next Steps

1. **Review and approval**: Architectural review with High Council
2. **Phase 1 implementation**: Enhanced Colima and containerized builds
3. **Team training**: Container-first development workflow
4. **Monitoring setup**: Infrastructure and performance monitoring
5. **Documentation**: Complete workflow documentation and runbooks

---

*This proposal embodies the breath-first principle of deliberate, conscious infrastructure that supports both rapid development iteration and production reliability through container-based consistency.*

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Ben Askins <human@getlamina.ai>  
Co-Authored-By: Lamina High Council <council@getlamina.ai>