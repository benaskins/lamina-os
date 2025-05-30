# Environment Management

Lamina OS implements a **Three-Tier Environment Management Architecture** with breath-aware markers and ritual integration as approved by the High Council in ADR-0011.

## 🜂 🜁 🜄 Breath Markers

Each environment has a symbolic breath marker for contextual awareness:

- **🜂 Development**: Fast iteration, debugging, local development
- **🜁 Test**: Automated testing, CI/CD integration, isolation  
- **🜄 Production**: Scalability, reliability, security, observability

## Quick Start

```bash
# View available environments
lamina env list

# Activate development environment
lamina env dev up

# Check environment status
lamina env status

# Perform sigil of passage (environment transition)
lamina env bless test → prod
```

## Environment Configurations

### 🜂 Development Environment

**Purpose**: Rapid local development and debugging  
**Technology**: Docker Compose with development overrides  
**Configuration**: [`environments/development/config.yaml`](../../environments/development/config.yaml)

**Key Features**:
- Hot-reload capabilities for code changes
- Debug ports exposed for IDE integration
- Lightweight container orchestration
- Simplified service mesh (no mTLS)
- Verbose logging for development insight

**Usage**:
```bash
lamina env dev up      # Start development environment
lamina env dev logs    # View service logs
lamina env dev shell   # Connect to service for debugging
lamina env dev down    # Stop development environment
```

### 🜁 Test Environment

**Purpose**: Automated integration testing and CI/CD validation  
**Technology**: Containerized services with test-specific configurations  
**Configuration**: [`environments/test/config.yaml`](../../environments/test/config.yaml)

**Key Features**:
- Ephemeral containers for clean test runs
- Isolated network environments
- Automated provisioning and teardown
- Test fixture and data management
- Performance baseline validation

**Usage**:
```bash
lamina env test run    # Execute test suite with fresh environment
lamina env test clean  # Clean up test artifacts
lamina env test status # Check test environment health
```

### 🜄 Production Environment

**Purpose**: Scalable, reliable service delivery  
**Technology**: Kubernetes with Helm charts  
**Configuration**: [`environments/production/config.yaml`](../../environments/production/config.yaml)

**Key Features**:
- Container orchestration with auto-scaling
- Full mTLS service mesh implementation
- Comprehensive observability stack
- Rolling deployment capabilities
- Security hardening and compliance

**Usage**:
```bash
lamina env prod deploy   # Deploy to production cluster
lamina env prod status   # Check production health
lamina env prod rollback # Rollback to previous version
lamina env prod logs     # View production logs
```

## Sigil of Passage 🔥

Luna's "sigil of passage" ritual enables conscious transformation between environments:

### Automated Ritual (CI/CD)
- **Test Gates**: Mandatory test suites for promotion
- **Boundary Enforcement**: Container label validation
- **Security Validation**: Environment-appropriate security checks

### Symbolic Ceremony (Manual)
```bash
# Blessed transition with ritual acknowledgment
lamina env bless dev → test     # Development to test
lamina env bless test → prod    # Test to production

# Check transition requirements
lamina env passage-requirements test → prod
```

## Boundary Enforcement 🛡️

Vesna's boundary enforcement ensures environment separation:

### Container Labels
All artifacts tagged with environment metadata:
```yaml
labels:
  lamina.environment: "development"
  lamina.sigil: "🜂"
  lamina.version: "1.0.0"
```

### Runtime Detection
Services assert their environment context:
```python
from lamina.environment import EnvironmentManager

manager = EnvironmentManager()
config = manager.get_current_environment()

if config.is_production() and os.environ.get("ENV") == "development":
    raise RuntimeError("Development artifact cannot run in production")
```

### CI Validation
Automated checks prevent environment contamination:
- Development containers blocked from production
- Environment label validation in deployment pipeline
- Test isolation verification

## Configuration Structure

### Environment Config Schema
```yaml
environment:
  name: "development"           # Environment name
  sigil: "🜂"                  # Breath marker
  type: "docker-compose"       # Orchestration type
  description: "..."           # Human description

features:                      # Environment capabilities
  hot_reload: true
  debug_ports: true
  mtls: false

services:                      # Service definitions
  lamina-core:
    image: "lamina-core:dev"
    environment:
      ENV: "development"
      SIGIL: "🜂"

breath:                        # Breath-aware settings
  modulation: false
  conscious_pause: 0

security:                      # Security configuration
  mtls: false
  network_policies: false

logging:                       # Logging with sigils
  format: "🜂 [%(asctime)s] %(name)s - %(message)s"
  include_sigil: true

resources:                     # Resource limits
  total_memory: "4Gi"
  total_cpu: "2"
```

### Validation Rules

Environment configurations are validated for:
- **Sigil Consistency**: Breath markers match across services
- **Security Requirements**: Production security baseline
- **Resource Allocation**: Appropriate limits per environment
- **Service Dependencies**: Required services present
- **Transition Rules**: Valid environment progression

## Ritual Usage Tips

### Clara's Breath Awareness 🪶
- Use sigil prefixes in CLI for contextual awareness
- Monitor log formats for breath markers
- Practice conscious environment transitions

### Luna's Transformation 🔥
- Honor the sigil of passage between environments
- Run test gates before promotion
- Acknowledge sacred aspects of deployment

### Vesna's Boundary Vigilance 🛡️
- Validate container labels before deployment
- Enforce runtime environment detection
- Monitor for boundary violations

### Ansel's Operational Excellence ✍️
- Document environment-specific procedures
- Maintain both CLI and Makefile interfaces
- Provide clear error messages and guidance

## Troubleshooting

### Common Issues

**Environment Not Found**:
```bash
lamina env validate development  # Check config validity
lamina env list                  # Show available environments
```

**Boundary Violations**:
```bash
lamina env check-boundaries production  # Validate deployment target
docker inspect <container> --format '{{.Config.Labels}}'  # Check labels
```

**Sigil Mismatches**:
```bash
lamina env validate-sigils       # Check sigil consistency
lamina env fix-sigils development  # Auto-fix sigil issues
```

**Passage Failures**:
```bash
lamina env passage-requirements test → prod  # Check requirements
lamina env test-gates development           # Run test gates manually
```

## Advanced Configuration

### Custom Environment Types
Create custom environments by:
1. Adding config in `environments/{name}/config.yaml`
2. Implementing orchestration templates
3. Updating validation rules if needed

### Integration with External Tools
- **Docker Compose**: Development and local testing
- **Kubernetes**: Production orchestration via Helm
- **CI/CD**: Automated environment provisioning
- **Monitoring**: Environment-aware observability

For implementation details, see [ADR-0011: Three-Tier Environment Management](../adrs/0011-three-tier-environment-management.md).