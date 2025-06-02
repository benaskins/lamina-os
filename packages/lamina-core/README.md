# Lamina Core

A breath-first framework for building presence-aware AI agent systems with multi-backend support, intelligent coordination, and breath-aware processing.

## Features

- **Presence-Aware Processing**: Natural rhythm and deliberate pacing in agent responses
- **Multi-Agent Coordination**: Intelligent routing between specialized agents
- **Multi-Backend AI Support**: Seamlessly switch between Ollama, HuggingFace, and other AI providers
- **Breath-First Architecture**: Sustainable, wisdom-focused development patterns
- **Agent Configuration**: Declarative agent definition with personality traits and expertise areas

## Quick Start

### Installation

```bash
# Install from PyPI (recommended)
pip install lamina-core

# Or install with optional AI backend support
pip install lamina-core[ai-backends]

# For development - clone repository
git clone https://github.com/benaskins/lamina-os.git
cd lamina-os/packages/lamina-core
pip install -e .
```

### Create Your First Sanctuary

```bash
# Initialize a new sanctuary
lamina sanctuary init my-agents

# Navigate to your sanctuary
cd my-agents

# Create additional agents
lamina agent create researcher --template=analytical

# Check sanctuary status
lamina sanctuary status
```

### Chat with Agents

```bash
# Interactive chat demo
lamina chat --demo

# Single message demo
lamina chat --demo "Hello, can you analyze this data?"

# Test core functionality
python examples/basic_usage.py
```

## Architecture

Lamina Core follows a modular architecture:

- **Backends**: Pluggable AI provider integrations
- **Memory**: Semantic memory system with ChromaDB integration
- **Infrastructure**: Docker-based service orchestration
- **Coordination**: Multi-agent communication and routing
- **Sanctuary**: Agent configuration and deployment system

## Agent Templates

Choose from specialized agent templates:

- **Conversational**: General-purpose chat assistant
- **Analytical**: Research and data analysis specialist  
- **Security**: Validation and protection agent
- **Reasoning**: Logic and problem-solving expert

## Documentation

- [Main Documentation](https://github.com/benaskins/lamina-os/blob/main/README.md)
- [Getting Started Guide](https://github.com/benaskins/lamina-os/blob/main/docs/getting-started.md)
- [Architecture Decision Records](https://github.com/benaskins/lamina-os/blob/main/docs/adrs/)
- [Examples](https://github.com/benaskins/lamina-os/blob/main/examples/)
- [Contributing Guide](https://github.com/benaskins/lamina-os/blob/main/CONTRIBUTING.md)

## Important Note

When documentation refers to agent "emotions" or "feelings," these describe expressive simulation and architectural patterns, not internal experience. Lamina agents do not possess self-awareness or sentience—all affective behavior results from symbolic processing designed for meaningful interaction.

## License

Mozilla Public License 2.0 - see [LICENSE](https://github.com/benaskins/lamina-os/blob/main/LICENSE) for details.

This software embodies breath-first development principles. You are invited to engage with presence over haste, reflection over extraction, and symbolic integrity over drift.