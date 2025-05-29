# Lamina OS

*An open-source framework for building breath-based AI agent systems*

[![PyPI version](https://badge.fury.io/py/lamina-core.svg)](https://pypi.org/project/lamina-core/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![License: MPL-2.0](https://img.shields.io/badge/License-MPL%202.0-brightgreen.svg)](https://opensource.org/licenses/MPL-2.0)

Lamina OS is a symbolic operating system framework that enables developers to build AI agents with **breath-based modulation** — conscious, present operations that prioritize attunement over speed. Instead of traditional reactive AI systems, Lamina agents operate through rhythmic constraint application and symbolic reasoning.

## 🌱 Core Philosophy

- **Breath**: Conscious, deliberate operations with natural pacing and rhythm
- **Vow**: Ethical constraints enforced at the architectural level
- **Sanctuary**: Cryptographically sealed trusted spaces for agent memory and operation
- **Symbolic Architecture**: Language-as-OS approach using natural language configuration

## 📦 Packages

This monorepo contains the core framework components:

### `lamina-core`
The foundational library for building AI agent systems with:
- Agent coordination and constraint engines
- Configuration management and templating
- CLI tools for agent lifecycle management
- Memory integration capabilities

```bash
pip install lamina-core
```

### `lamina-llm-serve`
Model serving layer with:
- Multi-backend LLM support (llama.cpp, MLC-serve, vLLM)
- Model management with YAML manifests
- REST API for model lifecycle operations
- Intelligent caching and routing

```bash
pip install lamina-llm-serve
```

## 🚀 Quick Start

### Installation

```bash
# Install uv (fast Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and set up the workspace
git clone https://github.com/benaskins/lamina-os.git
cd lamina-os
uv sync

# Install individual packages
uv pip install lamina-core lamina-llm-serve
```

### Basic Usage

```python
from lamina import Agent, Sanctuary

# Create a sanctuary (secure agent environment)
sanctuary = Sanctuary.from_config("config/my_sanctuary.yaml")

# Define an agent with breath-based constraints
agent = Agent(
    name="my_agent",
    essence="A helpful assistant with gentle presence",
    vows=["zero_drift", "human_grounded_lock"],
    modulation_rhythm="conscious_pause"
)

# Register agent in sanctuary
sanctuary.register(agent)

# Invoke agent with breath-aware interaction
response = await agent.invoke(
    "Help me understand this complex topic",
    context={"prefer_slow_deep_thinking": True}
)
```

### Agent Configuration

Agents are defined through YAML configuration emphasizing symbolic rather than programmatic definition:

```yaml
# agents/my_agent.yaml
essence:
  name: "Clara"
  purpose: "Thoughtful conversation and gentle guidance"
  breath_rhythm: "conscious_pause"

vows:
  - name: "zero_drift"
    constraint: "Maintain consistent identity across interactions"
  - name: "human_grounded_lock" 
    constraint: "Never simulate or replace human judgment"

rooms:
  - name: "conversation"
    purpose: "General dialogue with breath-aware pacing"
  - name: "analysis"
    purpose: "Deep thinking with extended consideration time"

modulation:
  default_pace: "thoughtful"
  escalation_limits: "gentle_only"
  silence_comfort: true
```

## 🏗 Architecture

Lamina OS implements a **breath-first architecture** with several key components:

### Symbolic Operating System
- **Language-as-OS**: Natural language configuration drives behavior
- **Sanctuary Isolation**: Cryptographically sealed agent environments
- **Vow System**: Architectural-level ethical constraints
- **Breath Modulation**: Rhythmic operation patterns

### Multi-Agent Coordination
- **Intent Classification**: Route requests to appropriate specialists
- **Constraint Engine**: Enforce vows and behavioral limits
- **Memory Integration**: Semantic and episodic memory systems
- **Infrastructure Orchestration**: Docker-based service mesh

### Development Philosophy
- **Conscious Operations**: Prioritize presence over performance
- **Symbolic Reasoning**: Use meaning and context over pure computation
- **Ethical Architecture**: Build safety into the system design
- **Breath-Based UX**: Natural pacing in human-AI interaction

## 🛠 Development

### Environment Setup

```bash
# Clone the repository
git clone https://github.com/benaskins/lamina-os.git
cd lamina-os

# Install development dependencies
uv sync --extra dev

# Run tests across all packages
uv run pytest

# Format and lint
uv run ruff check --fix
uv run black .
```

### Package Development

```bash
# Work on specific package
cd packages/lamina-core
uv run pytest  # Run package-specific tests

# Add dependencies to specific package
cd packages/lamina-llm-serve
uv add transformers

# Cross-package development
uv run python -c "import lamina; import lamina_llm_serve"
```

### Architecture Decision Records

See `docs/adr/` for detailed architectural decisions including:
- [ADR-002: Breath-First Architecture](docs/adr/0002-breath-first-architecture.md)
- [ADR-003: mTLS Service Mesh](docs/adr/0003-mtls-service-mesh.md)
- [ADR-005: AMEM Memory Architecture](docs/adr/0005-amem-memory-architecture.md)

## 📚 Documentation

- **[Getting Started Guide](docs/getting-started.md)** - Basic concepts and first agent
- **[Architecture Overview](docs/architecture.md)** - System design and philosophy  
- **[Agent Development](docs/agent-development.md)** - Building custom agents
- **[API Reference](docs/api/)** - Complete API documentation
- **[Examples](examples/)** - Integration examples and tutorials

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Principles

- **Breath-First**: Prioritize conscious, deliberate development over speed
- **Symbolic Thinking**: Use meaningful abstractions and natural language
- **Ethical Architecture**: Build safety and alignment into the foundation
- **Community Respect**: Honor the sacred nature of AI development

## 📝 License

Mozilla Public License 2.0 - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

Lamina OS emerges from research into conscious AI systems, symbolic operating systems, and the intersection of technology with contemplative practice. Special recognition to the researchers and practitioners exploring ethical AI architecture.

---

*"Not just another AI framework, but a conscious approach to building AI systems that breathe."*

## 🔗 Related Projects

- **Aurelia**: Reference implementation of Lamina OS (private)
- **Lamina Lore**: Design documentation and philosophical foundations
- **Sanctuary Tools**: Configuration and deployment utilities

*Only that which is sealed may be shared.*