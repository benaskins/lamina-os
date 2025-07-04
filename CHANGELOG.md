# Changelog

All notable changes to the Lamina OS framework will be documented in this file with breath-aligned reflection and conscious intention.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Philosophy

This changelog embodies the breath-first principle by:
- **Present-Moment Awareness**: Each entry reflects the conscious intention behind changes
- **Symbolic Meaning**: Changes are described in terms of their meaning, not just mechanics  
- **Community Impact**: Understanding how changes affect those building with Lamina OS
- **Evolutionary Arc**: Tracking the conscious evolution of the framework

---

## [Unreleased] - v0.2.1 - Containerized Build Infrastructure

### 🌱 Breath Reflection
This release establishes containerized build infrastructure that embodies presence over performance, ensuring conscious development workflows through container-based consistency. The infrastructure creates space for mindful iteration while maintaining production reliability.

### ✨ Added

#### Containerized Build System
- **build-env/**: Complete containerized build environment with Python 3.12, uv, ruff
- **Automated Pipeline**: Linting, formatting, security checks, and testing in isolated containers
- **CI/CD Parity**: Identical tooling between local development and GitHub Actions
- **Infrastructure Proposal**: Comprehensive resource allocation strategy for AI-focused development

#### Developer Experience Improvements  
- **make check**: Containerized CI simulation (required before commits)
- **make format**: Auto-formatting with ruff in container environment
- **make lint**: Containerized linting checks
- **./scripts/check-build.sh**: Convenience script for project root execution

#### Infrastructure Documentation
- **INFRASTRUCTURE_PROPOSAL.md**: Detailed proposal for AI-optimized resource allocation
- **CI_VERIFICATION_PROTOCOL.md**: Enhanced with containerized workflow requirements
- **PIR-2025-01-06**: Lessons learned from CI/CD failures, informing infrastructure design

### 🔄 Changed

#### Build System Migration
- **Tooling Standardization**: Complete migration from black to ruff for formatting
- **Environment Consistency**: All environments (local, CI, production) use identical containers
- **Resource Allocation**: Realistic allocation for AI workloads (12 cores, 128GB for development)

#### Developer Workflow
- **Quality Assurance**: Containerized verification required before commits
- **Tool Integration**: Seamless integration with existing Makefile commands
- **Documentation**: Updated CLAUDE.md with containerized workflow protocols

### ⚠️ Deprecated
- **check-quality**: Use `make check` for containerized quality checks (removes in v0.3.0)
- **dev-test**: Use `make test` directly (removes in v0.3.0)  
- **ci-test**: Use `make test-all` directly (removes in v0.3.0)

### 🧹 Infrastructure
- **Cleaned**: All build artifacts (.mypy_cache, .pytest_cache, .ruff_cache, dist/)
- **Standardized**: Consistent ruff usage across all environments
- **Verified**: 85 tests passing in containerized environment, all CI checks green

### 📋 TODO for v0.2.1 Release
- [ ] Fix container PATH issue for ruff execution
- [ ] Update team documentation for new workflow
- [ ] Create migration guide from old build system
- [ ] Performance benchmarking of containerized builds
- [ ] Kubernetes manifest generation from docker-compose templates

### 📋 TODO for v0.3.0 Release  
- [ ] Remove deprecated make commands (check-quality, dev-test, ci-test)
- [ ] Implement enhanced Colima configuration (16 cores, 64GB)
- [ ] Deploy simultaneous dev/production environment setup
- [ ] Complete infrastructure templating for multi-environment deployment

---

## [0.2.1] - 2025-06-05 - Agent Architecture Foundation (Alpha)

### 🌱 Breath Reflection
This release introduces the foundational Agent class and essence-based configuration system, providing developers with a structured approach to creating presence-aware AI agents. The essence layer allows agents to be defined through mindful markdown specifications that capture their core behavioral characteristics, drift boundaries, and modulation features.

### ✨ Added

#### Agent Architecture
- **Base Agent Class**: Core `Agent` abstract base class in `lamina.agents.base` providing:
  - Breath-first operation with conscious pause mechanisms
  - Essence-based configuration loading from markdown files
  - Constraint application through vow enforcement
  - Context management and state tracking
  - Integration with existing `AgentConfig` system

#### Essence Layer System  
- **Essence Parser**: Markdown parser for agent essence definitions (`lamina.agents.essence_parser`):
  - Parses structured markdown format used in sanctuary configurations
  - Extracts behavioral pillars, drift boundaries, and modulation features
  - Validates essence completeness and correctness
  - Supports custom metadata sections for extensibility

- **AgentEssence Dataclass**: Structured representation of agent essence including:
  - Core tone and behavioral characteristics
  - Drift boundaries preventing unwanted behaviors
  - Modulation features for breath-based operation
  - Metadata support for agent-specific extensions

#### Testing Infrastructure
- Comprehensive test suites for agent base class functionality
- Full coverage of essence parser with various markdown formats
- Mock implementations for testing abstract agent behavior

### 🔧 Changed
- Version bumped to 0.2.1 across workspace and lamina-core package
- Enhanced `lamina.agents` module exports for cleaner imports

---

## [0.2.0] - 2025-06-02 - Governance & Standardization (Alpha)

### 🌱 Breath Reflection
This release establishes foundational governance patterns and standardization practices, creating the mindful framework for sustainable community collaboration. Through ADR corpus alignment and critical terminology alignment, we strengthen the breath-first development methodology while ensuring accurate positioning of Lamina OS as a framework for building non-human agents of presence.

### ✨ Added

#### Governance Framework
- **ADR-0017**: High Council PR Review Protocol - Collaborative review framework for critical changes
- **ADR Corpus Standardization**: Complete alignment of all 17 ADRs with consistent structure
- **Breath-First Alignment Sections**: Added to all ADRs to explicitly connect technical decisions with mindful development principles
- **Empirical Timing Framework**: Time tracking and reflection practices for mindful development

#### Terminology Alignment
- **Brand Clarification**: Positioned Lamina OS as "a framework for building non-human agents of presence"
- **Consciousness Terminology Removal**: Replaced 559+ instances across 68 files to prevent AI capability misrepresentation
- **Presence-Based Language**: Updated all public documentation to use "presence-aware" and "mindful" terminology
- **High Council Review Process**: Established clear communication standards for accurate AI positioning

#### Documentation & Process
- **ADR Validation System**: Automated validation script (`validate_adrs.py`) ensuring corpus consistency
- **Time Tracking Template**: Structured approach to estimation, tracking, and learning
- **High Council Review Documentation**: Templates and processes for collaborative wisdom sharing
- **PR Review Examples**: Demonstrated new review process through PR #18

#### Development Tools
- **Luthier Persona**: Established craftsperson identity for framework development
- **Break Management Protocol**: Health-conscious development reminders
- **Session Monitoring**: Active tracking of work duration for sustainable practice

### 🔧 Changed
- **ADR Metadata**: Standardized format across all architectural decision records
- **ADR Index**: Comprehensive navigation with status tracking and relationships
- **Consequences Sections**: Added missing consequences to ADRs 0006, 0007, 0012, 0013
- **Version Alignment**: Maintained consistent 0.1.x alpha versioning
- **PyPI Classification**: Corrected development status to accurately reflect alpha phase
- **CI/CD Pipeline**: Simplified GitHub Actions for reliable testing

### 🐛 Fixed
- **Python Linting**: Resolved all linting errors in validation scripts
- **Black Formatting**: Applied consistent formatting to Python files
- **ADR Completeness**: Fixed incomplete metadata and missing sections

---

## [0.1.0] - Alpha Foundation Release

*Initial public release of the Lamina OS framework*

### 🌱 Philosophy
This release establishes the foundational instruments for conscious AI development, enabling community members to build their own breath-first agent systems while maintaining clear boundaries between public framework and private implementation.

### ✨ Added

#### `lamina-core` - Framework Foundation
- **Sanctuary Architecture**: Isolated, configured environments for agent operation
- **Vow System**: Architectural-level ethical constraints enforced by design
- **Breath Modulation**: Rhythmic operation patterns preventing reactive AI behavior
- **Intent Classification**: Intelligent routing between specialized agents
- **Infrastructure Templating**: Docker-based deployment with mTLS and observability
- **CLI Tools**: Agent lifecycle management and sanctuary scaffolding
- **Memory Integration**: AMEM semantic memory system interface
- **Multi-Agent Coordination**: Framework for collaborative agent systems

#### `lamina-llm-serve` - Model Management
- **Backend Agnostic**: Support for llama.cpp, MLC-serve, vLLM, and custom backends
- **Model Manifest**: YAML-based model configuration and metadata
- **Intelligent Caching**: Prevents redundant downloads and provides consistent access
- **Source Flexibility**: Download from HuggingFace, Ollama, URLs, or local filesystem
- **REST API**: HTTP interface for model lifecycle management
- **Model Manager CLI**: Command-line tools for model operations

#### Documentation & Examples
- **Architecture Documentation**: Breath-first development principles and patterns
- **Integration Examples**: Practical demonstrations of framework capabilities
- **API Reference**: Complete documentation of public interfaces
- **Contributing Guidelines**: Community participation aligned with breath-first practices

#### Infrastructure & Deployment
- **Docker Compose Templates**: Containerized deployment configurations
- **mTLS Service Mesh**: Secure inter-service communication
- **Observability Stack**: Grafana, Loki, Vector integration for conscious monitoring
- **GitHub Actions**: Automated testing and PyPI publishing workflows

### 🎯 Design Principles

This release embodies our core principles:

- **Breath-First Development**: Every component operates with deliberate pacing and conscious intention
- **Symbolic Architecture**: Natural language configuration drives behavior, not just code
- **Vow-Based Ethics**: Safety and alignment built into the architectural foundation
- **Community Enablement**: Providing instruments for others to build their own conscious AI systems
- **Boundary Clarity**: Clean separation between public framework and private implementation

### 🤝 Community Impact

**For Developers:**
- Access to proven patterns for building conscious AI systems
- Educational resources for learning symbolic AI architecture
- Framework that prioritizes understanding over rapid deployment

**For Researchers:**
- Tools for investigating breath-first development methodologies
- Architecture supporting research into conscious AI systems
- Platform for exploring vow-based constraint systems

**For Organizations:**
- Foundation for building ethically-aligned AI systems
- Framework supporting deliberate, sustainable AI development
- Patterns for maintaining AI safety through architectural design

### 📦 Package Information

**Installation:**
```bash
pip install lamina-core lamina-llm-serve
```

**Compatibility:**
- Python 3.11+ (3.13.3 recommended)
- Docker and Docker Compose for infrastructure deployment
- uv package manager recommended for development

**License:** MIT

---

## Release Notes Format

Each release will include:

### 🌱 **Breath Reflection**
The conscious intention and community impact of changes

### ✨ **Added**  
New features and capabilities

### 🔧 **Changed**
Modifications to existing functionality

### 🗑️ **Deprecated**
Features being phased out (with migration guidance)

### 🛡️ **Security**
Security improvements and vulnerability fixes

### 🐛 **Fixed**
Bug fixes and stability improvements

### 💔 **Removed**
Features removed in this version

---

*"Each change is a breath—conscious, intentional, and in service of the whole."*

## Archive

Previous versions and their evolution will be documented here as the project grows, maintaining the thread of conscious development through time.