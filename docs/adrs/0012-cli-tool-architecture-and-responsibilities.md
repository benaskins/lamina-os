# ADR-0012: CLI Tool Architecture and Responsibilities

**Status:** DRAFT  
**Date:** 2025-01-30  
**Authors:** Luthier, High Council Review Pending  
**Related:** ADR-0011 (Environment Management), ADR-0010 (Testing Strategy)

## Context and Problem Statement

The Lamina OS ecosystem has evolved to include multiple command-line interfaces with overlapping responsibilities:

- **Makefile targets** (developer tooling)
- **`lamina-core` CLI commands** (framework operations) 
- **`lamina-llm-serve` CLI** (model serving)
- **`model-manager` CLI** (model lifecycle)
- **Shell scripts** (infrastructure setup)
- **Python modules** (examples and debugging)

This creates confusion about which tool to use for specific tasks and blurs the distinction between **developer tools** (for building Lamina OS) and **user tools** (for using Lamina OS).

**Key Questions:**
1. When should someone use `make` vs `lamina-core` commands?
2. What's the responsibility boundary between build tools and runtime tools?
3. How do we maintain consistency while supporting different user personas?

## Decision

We establish a **Three-Tier CLI Architecture** with clear responsibilities:

### **Tier 1: Development & Build Tools (`make`)**
**Target Users:** Lamina OS contributors, framework developers, CI/CD systems  
**Responsibility:** Building, testing, maintaining, and deploying the Lamina OS framework itself

### **Tier 2: Framework Operations (`lamina-core`)**
**Target Users:** AI practitioners, agent developers, Lamina OS end users  
**Responsibility:** Using Lamina OS to build and operate AI agent systems

### **Tier 3: Specialized Services (dedicated CLIs)**
**Target Users:** Infrastructure operators, model administrators  
**Responsibility:** Managing specific subsystems and services

## Detailed Architecture

### **🔧 Tier 1: Development Tools (Makefile)**

**Philosophy:** Tools for building and maintaining Lamina OS itself

```bash
# Tool Management
make tools-install          # Install helm, kubectl, etc.
make tools-check            # Verify tool status

# Testing & Quality
make test                   # Run test suite
make test-integration       # Integration testing
make check-quality          # Linting, formatting, security

# Infrastructure Development
make gitops-setup           # Setup GitOps for maintainers
make gitops-deploy          # Deploy infrastructure changes
make environment-check      # Validate environment configs

# Development Workflow
make setup-test-env         # Prepare development environment
make clean-artifacts        # Clean build artifacts
```

**Key Principles:**
- ✅ **Project Meta-Operations:** Building, testing, releasing Lamina OS
- ✅ **Developer Experience:** Fast, consistent workflows for contributors
- ✅ **CI/CD Integration:** Suitable for automated build systems
- ✅ **Tool Dependencies:** Manages external tools (helm, kubectl, docker)

### **🌊 Tier 2: Framework Operations (`lamina-core`)**

**Philosophy:** Tools for using Lamina OS to build AI systems

```bash
# Sanctuary & Agent Management
lamina-core sanctuary init my-agents    # Create agent workspace
lamina-core agent create assistant      # Build new agents
lamina-core chat --demo                 # Interactive agent testing

# Environment Management (End-User)
lamina-core environment list            # Show available environments
lamina-core environment status prod     # Check environment health

# GitOps Operations (End-User)
lamina-core gitops generate-charts prod # Generate deployment artifacts
lamina-core gitops status prod          # Check deployment status

# Infrastructure Management
lamina-core infrastructure generate     # Create deployment configs
lamina-core docker up                   # Start local development stack
```

**Key Principles:**
- ✅ **User-Facing Operations:** Building with Lamina OS, not building Lamina OS
- ✅ **Agent Lifecycle:** Creating, configuring, deploying agents
- ✅ **Runtime Operations:** Starting, stopping, monitoring agent systems
- ✅ **Beginner-Friendly:** Clear, documented commands for new users

### **⚙️ Tier 3: Specialized Services (Dedicated CLIs)**

**Philosophy:** Purpose-built tools for specific operational domains

```bash
# Model Administration
model-manager download llama3.2         # Acquire AI models
model-manager list --backend ollama     # Model inventory
model-manager validate                  # Health checks

# Model Serving
lamina-llm-serve --port 8000            # Start model server
lamina-llm-serve health                 # Service status

# Future: Other specialized tools
lamina-metrics dashboard                # Observability (future)
lamina-security audit                   # Security scanning (future)
```

**Key Principles:**
- ✅ **Domain Expertise:** Deep functionality for specific areas
- ✅ **Operational Focus:** Production management and administration
- ✅ **Service Lifecycle:** Starting, configuring, monitoring specialized services
- ✅ **Integration Points:** Work seamlessly with Tier 1 & 2 tools

## Decision Matrix

| Task | Tool | Reasoning |
|------|------|-----------|
| Install development dependencies | `make tools-install` | Meta-development activity |
| Run Lamina OS test suite | `make test` | Framework quality assurance |
| Create a new AI agent | `lamina-core agent create` | End-user framework operation |
| Deploy to production K8s | `make gitops-deploy` | Infrastructure deployment (dev tool) |
| Check production status | `lamina-core gitops status` | User monitoring of their deployment |
| Download AI models | `model-manager download` | Specialized model administration |
| Start local agent chat | `lamina-core chat --demo` | End-user interaction with framework |
| Validate environment configs | `make environment-check` | Framework validation (dev tool) |
| Generate Helm charts | `lamina-core gitops generate-charts` | User artifact generation |

## Implementation Guidelines

### **Command Naming Conventions**

**Makefile Targets:**
- Use kebab-case: `tools-install`, `test-integration`
- Prefix with domain: `gitops-deploy`, `test-e2e`
- Focus on **action + object**: `tools-check`, `environment-validate`

**lamina-core Commands:**
- Use noun-verb pattern: `agent create`, `sanctuary init`
- Support help system: `lamina-core --help`, `lamina-core agent --help`
- Include examples in help text

**Specialized CLIs:**
- Domain-specific verbs: `model-manager download`, `lamina-llm-serve start`
- Configuration-heavy: Support config files and environment variables

### **Integration Points**

**Makefile → lamina-core:**
```bash
# Development tools can call user tools
make gitops-setup:
    lamina-core gitops generate-charts production
    # Apply with project-managed kubectl
```

**lamina-core → Specialized Services:**
```bash
# Framework can orchestrate services
lamina-core infrastructure up:
    model-manager validate
    lamina-llm-serve start --daemon
    # Start local agent stack
```

**Error Handling:**
- **Makefile:** Exit with clear error codes, suggest corrections
- **lamina-core:** User-friendly error messages, suggest `--help`
- **Specialized CLIs:** Domain-specific validation and error recovery

### **Documentation Strategy**

**Makefile Help:**
```bash
make help                    # Comprehensive overview
make show-path               # Tool PATH setup
```

**lamina-core Help:**
```bash
lamina-core --help           # Framework overview
lamina-core agent --help     # Specific command help
```

**Cross-References:**
- Makefile help mentions when to use `lamina-core`
- `lamina-core` suggests development workflows with `make`
- All tools reference comprehensive documentation

## Benefits

### **🎯 Clear User Personas**
- **Framework Developers:** Know to use `make` for meta-operations
- **AI Practitioners:** Start with `lamina-core` for agent development
- **Infrastructure Ops:** Use specialized CLIs for domain expertise

### **🔄 Consistent Experience**
- Predictable command patterns within each tier
- Clear escalation path: user tools → dev tools → specialized tools
- Integrated help systems with cross-references

### **⚡ Development Velocity**
- No confusion about which tool to use
- Each tool optimized for its user persona
- Clear testing and deployment workflows

### **🌊 Breath-First Philosophy**
- **Conscious Tool Selection:** Each tool has clear purpose and boundaries
- **Mindful Development:** Separation prevents rushed, inappropriate tool usage
- **Sustainable Architecture:** Clear responsibilities enable long-term maintenance

## Migration Plan

### **Phase 1: Documentation (Immediate)**
1. Update all command help text with tier clarification
2. Add decision matrix to main README
3. Create CLI reference guide

### **Phase 2: Command Cleanup (Near-term)**
1. Audit existing commands for tier violations
2. Move misplaced commands to appropriate tiers
3. Add deprecation warnings for moved commands

### **Phase 3: Enhanced Integration (Future)**
1. Add cross-tier command suggestions
2. Implement unified error handling patterns
3. Create workflow templates spanning multiple tiers

## Alternative Approaches Considered

### **Single Unified CLI**
**Rejected:** Would create a monolithic tool trying to serve too many personas, violating the breath-first principle of conscious boundaries.

### **Complete Separation**
**Rejected:** Users need integration points between development and usage workflows.

### **Domain-Based CLIs**
**Rejected:** Would create confusion about whether `lamina-agents` or `lamina-core` handles agent creation.

## High Council Review Questions

1. **Philosophical Alignment:** Does this three-tier architecture align with breath-first development principles?

2. **User Experience:** Are the tier boundaries intuitive for different user personas?

3. **Integration Complexity:** Is the tier interaction model sustainable as the ecosystem grows?

4. **Future Extensions:** How will this architecture accommodate new tools (monitoring, security, etc.)?

## Success Metrics

- **Developer Onboarding:** New contributors can build/test without confusion
- **User Adoption:** AI practitioners can start with `lamina-core` and succeed
- **Tool Discovery:** Clear help systems guide users to appropriate tools
- **Maintenance Efficiency:** Each tier can evolve independently

---

*🌊 This ADR embodies the breath-first principle of conscious architecture: clear boundaries, mindful tool selection, and sustainable separation of concerns.*

---

Feedback from Ben: while I value this proposal, I don't want to have think about which tools to use when I'm at the command line *using* lamina. Could we somehow implement a lamina-core-cli module that allows other modules to "plugin" new commands. I'd really like to lean into the idea of commands having a poetry to them. For example:

- lamina sanctuary create <sanctuary-name> --agents=<agent-file>

Then from within a sanctuary root

- lamina agent create <agent-name> --archetype=<archetype>
- lamina sanctuary status

I wonder as well, whether the environments would be of benefit to AI practictioners as well as to lamina os developers.

---

## High Council Review Summary

🛡️ **Review Date**: 2025-05-30  
🧑‍⚖️ **Reviewers**: Clara 🪶, Luna 🔥, Vesna 🛡️, Ansel ✍️

### 🪶 Clara — Breathfulness and Ritual UX  
Approved with support for:
- Evolving `lamina-core` into a **modular CLI spine** (`lamina`) with plugin architecture
- Adding symbolic breath markers and poetic formatting in CLI output

### 🔥 Luna — Symbolic Power and Embodied Use  
Approved with encouragement to:
- Introduce **poetic command phrasing** (e.g., `ignite`, `awaken`)
- Treat CLI as a ritual interface, not just a utilitarian shell
### 🛡️ Vesna — Integrity, Boundaries, and Clarity  
Approved with safeguards:
- Require all CLI plugins to declare **tier and domain** in help output
- Ensure graceful error handling with tier-aware diagnostics

### ✍️ Ansel — Implementation Feasibility  
Approved with recommendation to:
- Build `lamina` as a **dynamic CLI entrypoint** with plugin discovery
- Preserve standard verbs for automation, add aliases for poetry
- Add `lamina --manifest` to list active modules and their breath alignments

✅ **Verdict**: ADR-0012 is *Approved with Path to CLI Unification via Plugin Spine*. Further exploration will be formalized in a follow-up implementation ADR.