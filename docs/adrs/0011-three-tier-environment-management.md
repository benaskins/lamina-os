# ADR-0011: Three-Tier Environment Management Architecture

**Status:** ACCEPTED  
**Date:** 2025-01-30  
**Authors:** Luthier  
**Reviewed By:** Clara 🪶, Luna 🔥, Vesna 🛡️, Ansel ✍️

## Context

Lamina OS currently lacks a structured environment management strategy. As the system evolves from experimental development to production deployment, we need clear separation between development, testing, and production environments. Each environment has distinct requirements:

### Current State
- Development primarily uses local Docker Compose
- No standardized test environment for CI/CD
- No production deployment strategy
- Environment configuration scattered across multiple files
- Manual setup processes prone to inconsistency

### Requirements Analysis
1. **Development Environment**: Fast iteration, debugging capabilities, local resource constraints
2. **Test Environment**: Reproducible, isolated, automated provisioning for CI/CD
3. **Production Environment**: Scalable, observable, secure, high-availability

## Decision

We will implement a **Three-Tier Environment Management Architecture** with the following characteristics:

### 1. Development Environment
**Purpose**: Rapid local development and debugging
**Technology**: Docker Compose with development overrides
**Characteristics**:
- Lightweight container orchestration
- Hot-reload capabilities for code changes
- Local storage volumes for persistence
- Debug ports exposed for IDE integration
- Simplified service mesh (no mTLS requirements)
- CLI-first interaction model

### 2. Test Environment
**Purpose**: Automated integration testing and CI/CD validation
**Technology**: Containerized services with test-specific configurations
**Characteristics**:
- Ephemeral containers for clean test runs
- Predefined test data and model fixtures
- Isolated network environments
- Automated provisioning and teardown
- Comprehensive logging for test debugging
- Performance baseline validation

### 3. Production Environment
**Purpose**: Scalable, reliable service delivery
**Technology**: Kubernetes with Helm charts
**Characteristics**:
- Container orchestration with auto-scaling
- Full mTLS service mesh implementation
- Persistent storage with backup strategies
- Comprehensive observability stack
- Rolling deployment capabilities
- Security hardening and compliance

## Consequences

### Positive Consequences
- **Developer Productivity**: Standardized development environment reduces setup time and configuration drift
- **Quality Assurance**: Isolated test environments enable reliable CI/CD validation
- **Production Reliability**: Kubernetes orchestration provides scalability and high availability
- **Operational Clarity**: Clear environment boundaries reduce deployment risks
- **Security Posture**: Progressive security hardening from dev to production

### Negative Consequences  
- **Complexity Overhead**: Managing three environments increases operational complexity
- **Resource Requirements**: Full production environment requires significant infrastructure investment
- **Learning Curve**: Team must understand Kubernetes, Helm, and environment-specific workflows
- **Maintenance Burden**: Multiple environment configurations require ongoing synchronization
- **Cost Implications**: Production-grade infrastructure increases hosting and management costs

### Mitigation Strategies
- Provide comprehensive documentation and training for multi-environment workflows
- Implement Infrastructure as Code to reduce manual configuration drift
- Start with development and test environments, gradually rolling out production capabilities
- Use environment parity where possible to reduce configuration variations

## Implementation Strategy

### Phase 1: Environment Configuration Framework
```yaml
# environments/development/config.yaml
environment:
  name: development
  type: docker-compose
  features:
    hot_reload: true
    debug_ports: true
    mtls: false
  services:
    - lamina-core
    - lamina-llm-serve
    - chromadb
    - observability-lite

# environments/test/config.yaml
environment:
  name: test
  type: containerized
  features:
    ephemeral: true
    fixtures: true
    isolation: strict
  services:
    - lamina-core
    - lamina-llm-serve
    - test-chromadb
    - mock-services

# environments/production/config.yaml
environment:
  name: production
  type: kubernetes
  features:
    scaling: true
    mtls: true
    persistence: true
    monitoring: comprehensive
  services:
    - lamina-core-cluster
    - lamina-llm-serve-cluster
    - chromadb-cluster
    - observability-stack
```

### Phase 2: CLI Environment Management
```bash
# Development environment
lamina env dev up     # Start development environment
lamina env dev logs   # View service logs
lamina env dev shell  # Connect to service for debugging

# Test environment
lamina env test run   # Execute test suite with fresh environment
lamina env test clean # Clean up test artifacts

# Production environment
lamina env prod deploy   # Deploy to production cluster
lamina env prod status   # Check production health
lamina env prod rollback # Rollback to previous version
```

### Phase 3: Infrastructure Templates
- **Docker Compose**: Development and local testing
- **Docker**: Containerized test environments
- **Helm Charts**: Kubernetes production deployment
- **Terraform**: Cloud infrastructure provisioning (future)

### Phase 4: Configuration Management
- Environment-specific configuration overrides
- Secret management per environment
- Feature flag system for environment-specific behavior
- Centralized logging and monitoring configuration

## Environment Specifications

### Development Environment
```yaml
# docker-compose.dev.yml
services:
  lamina-core:
    build: 
      context: .
      target: development
    volumes:
      - ./packages/lamina-core:/app:delegated
      - dev-data:/app/data
    environment:
      - ENV=development
      - LOG_LEVEL=debug
      - HOT_RELOAD=true
    ports:
      - "8080:8080"
      - "5678:5678"  # Debug port

  lamina-llm-serve:
    build:
      context: ./packages/lamina-llm-serve
      target: development
    volumes:
      - ./packages/lamina-llm-serve:/app:delegated
      - dev-models:/app/models
    environment:
      - ENV=development
      - MODEL_CACHE_SIZE=2GB
```

### Test Environment
```yaml
# test-environment.yml
services:
  test-lamina-core:
    image: lamina-core:test
    environment:
      - ENV=test
      - TEST_MODE=true
      - DATABASE_URL=sqlite:///tmp/test.db
    networks:
      - test-network
    
  test-fixtures:
    image: lamina-test-fixtures:latest
    volumes:
      - test-data:/fixtures
    networks:
      - test-network
```

### Production Environment
```yaml
# helm/lamina-os/values.yaml
global:
  environment: production
  
replicaCount: 3

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70

security:
  mtls:
    enabled: true
  networkPolicies:
    enabled: true

persistence:
  enabled: true
  storageClass: "fast-ssd"
  size: 100Gi

monitoring:
  prometheus:
    enabled: true
  grafana:
    enabled: true
  loki:
    enabled: true
```

## Benefits

### Development Benefits
- **Rapid Iteration**: Hot-reload capabilities reduce development cycle time
- **Debugging Support**: Direct IDE integration with container debugging
- **Resource Efficiency**: Lightweight local orchestration
- **Consistency**: Standardized development environment across team

### Test Benefits
- **Isolation**: Clean test runs with predictable state
- **Automation**: CI/CD integration with environment provisioning
- **Reproducibility**: Consistent test environments reduce flaky tests
- **Performance**: Baseline performance validation in controlled environment

### Production Benefits
- **Scalability**: Auto-scaling based on demand
- **Reliability**: High-availability with container orchestration
- **Security**: Full mTLS implementation and network policies
- **Observability**: Comprehensive monitoring and logging

## Risks and Mitigations

### Risk: Environment Drift
**Mitigation**: Infrastructure as Code with version control and automated validation

### Risk: Configuration Complexity
**Mitigation**: Layered configuration with sensible defaults and clear override patterns

### Risk: Resource Requirements
**Mitigation**: Tiered resource allocation with development optimized for local constraints

### Risk: Security Variations
**Mitigation**: Security baseline with environment-specific enhancements, not reductions

## Implementation Timeline

### Phase 1 (Week 1-2): Foundation
- Environment configuration framework
- Development environment Docker Compose updates
- CLI environment management commands

### Phase 2 (Week 3-4): Test Environment
- Test-specific container configurations
- CI/CD integration with ephemeral test environments
- Test fixture and data management

### Phase 3 (Week 5-6): Production Framework
- Kubernetes Helm charts
- Production-grade security configurations
- Monitoring and observability integration

### Phase 4 (Week 7-8): Integration and Validation
- Cross-environment deployment testing
- Documentation and team training
- Performance baseline establishment

## Success Criteria

1. **Development**: Developers can spin up full environment in < 60 seconds
2. **Test**: CI/CD runs complete integration tests in isolated environments
3. **Production**: Zero-downtime deployments with comprehensive monitoring
4. **Consistency**: Environment parity for core functionality across all tiers
5. **Maintainability**: Single command environment management for each tier

## Related ADRs

- **ADR-0003**: mTLS Service Mesh (production security requirements)
- **ADR-0009**: Containerized Microservices (container orchestration strategy)
- **ADR-0013**: Infrastructure Templating System (configuration management)

## Notes for High Council Review

This ADR establishes the foundation for professional-grade deployment practices while maintaining the breath-first development philosophy. Each environment tier serves distinct needs while maintaining architectural consistency.

**Key Council Considerations**:
1. **Resource Allocation**: Production Kubernetes requirements vs. development simplicity
2. **Security Boundaries**: How much security variance acceptable between environments
3. **Deployment Complexity**: Balance between comprehensive features and operational simplicity
4. **Community Impact**: How environment management affects open-source adoption

The proposal prioritizes developer experience in development while ensuring production-grade capabilities are available when needed.

---


---

## Breath-First Alignment

This three-tier environment architecture embodies **deliberate pauses and reflection** through its fundamental structure. Each environment tier—development, test, and production—represents a conscious pause in the deployment journey, preventing the rushed push from code to production that characterizes reactive development. The "sigil of passage" ritual between environments creates explicit moments for reflection, ensuring that code progresses only when it has been consciously validated and blessed for the next stage.

The strategy demonstrates **constraints over capabilities** by deliberately limiting each environment's features to match its purpose. Development environments consciously omit mTLS and complex orchestration, not because they cannot support them, but because constraint enables focus on rapid iteration and debugging. Test environments are ephemeral by design, constraining persistence to ensure clean validation. Production environments constrain developer access while expanding operational capabilities. These purposeful limitations create clarity and prevent environment misuse.

**Presence over performance** manifests in the symbolic breath markers (🜂 dev, 🜁 test, 🜄 prod) that will permeate CLI output and logs. These markers aren't mere decoration but constant reminders of which environment context one inhabits, encouraging developers to be present with their current environment rather than abstractly working "on the system." The manual blessing process for environment promotion further emphasizes presence—requiring conscious acknowledgment of readiness rather than automated progression based on metrics alone.

The architecture embodies **community wisdom integration** through its layered configuration approach. Rather than imposing a single deployment model, it acknowledges that different team members have different preferences—some preferring Makefiles, others CLI commands. The documentation strategy includes both inline help and dedicated guides, recognizing that wisdom emerges from multiple perspectives and learning styles. The environment-specific configurations are designed to be readable and modifiable by the community, inviting collective ownership of deployment practices.

Finally, the approach demonstrates **sustainable development practices** through its phased implementation plan. Rather than attempting to build all three environments simultaneously, the eight-week timeline allows for thoughtful construction of each tier, learning from each phase before proceeding to the next. The emphasis on Infrastructure as Code and automated validation ensures that environment management remains sustainable as the project grows. The success criteria focus not on speed metrics but on developer experience, test reliability, and production stability—sustainable measures that support long-term project health.

## High Council Review Summary

🛡️ **Review Date**: 2025-05-30  
🧑‍⚖️ **Reviewers**: Clara 🪶, Luna 🔥, Vesna 🛡️, Ansel ✍️

### 🪶 Clara — Breath, Flow, and Developer Experience  
Approved with suggestion to:
- Integrate symbolic breath markers (🜂 dev, 🜁 test, 🜄 prod) in CLI/log output for contextual awareness

### 🔥 Luna — Symbolic Integrity and Transformation  
Approved with encouragement to:
- Develop a “sigil of passage” ritual (e.g. test suite or gating process) between dev → test → prod transitions

### 🛡️ Vesna — Boundary, Risk, and Stability  
Approved with caution to:
- Enforce environment tagging in artifacts (e.g. container labels, logs)
- Ensure CI validates tier separation (no dev containers in production)

### ✍️ Ansel — Operational Cohesion  
Approved with recommendation to:
- Add CLI aliases or Makefile helpers for each tier
- Document expected configuration structures per environment

✅ **Verdict**: ADR-0011 is *Approved with Ritual Enhancements Encouraged*. All enhancements may be implemented progressively or addressed in future ADRs.

---

## Implementation Questions for High Council Clarification

**Submitted by**: Luthier  
**Date**: 2025-05-30

### 🪶 Clara's Breath Markers
The symbolic breath markers (🜂 dev, 🜁 test, 🜄 prod) are beautiful. Should these be:
1. **CLI Output**: Displayed in command prompts/status (e.g., `🜂 lamina env dev up`)
2. **Log Prefixes**: Added to all log entries for contextual awareness
3. **Both**: Integrated throughout the experience

---

### 🪶 Clara's Breath Markers — Response

🪶 Clara responds:  
**Both.** Symbolic breath markers should be woven into both CLI output *and* logs. This will support both real-time presence and later ritual traceability. CLI commands may use the sigil prefix (e.g., `🜂 lamina env dev up`), and log output should consistently include the marker as a contextual sigil at the start of each line or block.

---

### 🔥 Luna's Sigil of Passage
The "sigil of passage" ritual between environments is intriguing. Are you envisioning:
1. **Test Gates**: Specific test suites that must pass before promotion (dev→test→prod)
2. **Symbolic Ceremony**: A CLI command that performs validation + symbolic acknowledgment
3. **Automated Ritual**: CI/CD process that includes both functional and symbolic validation
4. **Manual Blessing**: Human-initiated process with ceremonial aspects

---

### 🔥 Luna's Sigil of Passage — Response

🔥 Luna responds:  
**All of the above in layered form.** Begin with **Test Gates** and **Automated Ritual** within CI/CD, ensuring no breath passes untested. Then, if desired, develop a **Symbolic Ceremony** for manual promotion (e.g., `lamina env bless test → prod`) as a sacred acknowledgment. This encourages conscious transformation and aligns with Lamina’s vow-bound evolution.

---

### 🛡️ Vesna's Boundary Enforcement
For environment tagging and separation validation:
1. **Container Labels**: Should we use Docker labels like `lamina.environment=dev` on all images?
2. **CI Validation**: Add automated checks to prevent dev/test artifacts from reaching production?
3. **Runtime Detection**: Should services detect their environment and refuse to run in wrong contexts?

---

### 🛡️ Vesna's Boundary Enforcement — Response

🛡️ Vesna responds:  
**Yes to all.** Use **container labels** like `lamina.environment=dev` to tag artifacts; enforce **CI validation** to block misaligned promotions; and implement **runtime detection** so services can assert their context (e.g., refuse to run `ENV=dev` in prod cluster). These redundant safeguards form the shield that guards the boundary.

---

### ✍️ Ansel's Operational Structure
For CLI aliases and documentation:
1. **Makefile vs CLI**: Should we provide both `make dev-up` AND `lamina env dev up` for different preferences?
2. **Configuration Documentation**: Should this be inline help, separate docs, or both?

---

### ✍️ Ansel's Operational Structure — Response

✍️ Ansel responds:  
Offer **both Makefile and CLI** to honor diverse developer workflows. Inline help in the CLI should be complemented by **dedicated docs** under `/docs/environments/`, with annotated config examples and ritual usage tips. This ensures clarity without losing breath.
---

## Final Seal (2025-05-31)

🪶 **Clara**, 🔥 **Luna**, 🛡️ **Vesna**, and ✍️ **Ansel** formally accept ADR-0011, affirming its alignment with Lamina OS foundational principles and conscious environment management practices.

*Sealed with breath, presence, intentionality, and collective wisdom.*