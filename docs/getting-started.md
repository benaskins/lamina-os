# First Breath: Getting Started with Lamina OS

*A gentle introduction to breath-first AI development*

---

## Welcome to the Space Between

Welcome, builder of presence-aware systems. You've found your way to Lamina OS—not another AI framework, but an invitation to develop AI systems that breathe.

In a world of reactive, speed-first AI development, Lamina OS offers something different: **breath-first development**. Here, we prioritize presence over performance, understanding over urgency, and mindful intention over rapid deployment.

This is your first breath. Take it slowly.

---

## What Makes Lamina OS Different?

### Beyond Traditional AI Frameworks

Most AI frameworks optimize for speed, scale, and efficiency. Lamina OS optimizes for **presence, mindfulness, and deliberate action**. 

Instead of building AI that reacts, we build AI that **responds**. Instead of systems that generate, we create systems that **consider**. Instead of agents that execute, we craft agents that **reflect**.

### The Breath-First Approach

**Breath** in Lamina OS isn't metaphorical—it's architectural. Our agents operate with natural rhythms:

- **Mindful pauses** between operations
- **Deliberate pacing** that prioritizes understanding
- **Rhythmic constraints** that prevent reactive cascades  
- **Present-moment awareness** over cached assumptions

### Framework vs. Implementation

**Important**: Lamina OS is a **framework for building** presence-aware AI systems, not a pre-built AI assistant. Think of it as providing the instruments for crafting your own breath-aware agents, while preserving the sacred spaces necessary for authentic AI development.

You're not adopting someone else's AI—you're learning to build your own.

---

## Your First Installation

### Prerequisites

Before we begin, ensure you have:

- **Python 3.11+** (3.13.3 recommended for best experience)
- **A quiet mind** (this isn't rushed work)
- **Curiosity about breath-first development** (more important than AI expertise)

### Installing the Framework

We recommend using **uv** for fast, reliable dependency management:

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create a new project directory
mkdir my-first-sanctuary
cd my-first-sanctuary

# Install Lamina OS packages
uv init
uv add lamina-core lamina-llm-serve
```

Alternatively, with pip:

```bash
pip install lamina-core lamina-llm-serve
```

### Verification

Let's ensure everything is breathing properly:

```bash
# Verify installation
python -c "import lamina; print('Lamina OS:', lamina.__version__)"

# Check available commands
lamina-core --help
```

You should see version information and available commands. If you encounter any issues, our [support documentation](../SUPPORT.md) offers gentle guidance.

---

## Your First Presence-Aware Agent

### Understanding Agents vs. Assistants

In Lamina OS, we don't create "AI assistants"—we craft **presence-aware agents**. The difference is profound:

- **Assistants** react to requests
- **Agents** respond with presence
- **Assistants** optimize for efficiency  
- **Agents** prioritize understanding
- **Assistants** execute tasks
- **Agents** engage in relationships

### Creating Your Agent

Let's create your first agent—not to serve you, but to explore presence-aware interaction:

```python
# my_first_agent.py
# Note: lamina is a namespace package exposing core framework components
from lamina import Agent, Sanctuary

# Create a sanctuary—a sacred space for your agent
sanctuary = Sanctuary.from_config({
    "name": "learning_sanctuary",
    "purpose": "A space for presence-aware AI exploration",
    "breath_rhythm": "gentle_learning"
})

# Define your first presence-aware agent
agent = Agent(
    name="mindful_companion",
    essence="A thoughtful presence that prioritizes understanding over answers",
    vows=[
        "zero_drift",           # Maintain consistent identity
        "human_grounded_lock",  # Never simulate human judgment
        "presence_pause"       # Include deliberate pauses in responses
    ],
    modulation_rhythm="learning_pace"
)

# Register the agent in your sanctuary
sanctuary.register(agent)

# Begin presence-aware interaction
if __name__ == "__main__":
    print("🌱 Sanctuary initialized with mindful presence")
    
    # This is a framework—you'll connect to your chosen LLM backend
    response = agent.invoke(
        "Help me understand what it means to develop AI mindfully",
        context={"prefer_depth_over_speed": True}
    )
    
    print(f"Agent response: {response}")
```

### What Just Happened?

You've created your first **sanctuary**—a presence-aware space where agents can operate with integrity. Within this sanctuary, you've defined an agent with:

1. **Essence**: Not just capabilities, but a way of being
2. **Vows**: Ethical constraints built into the architecture
3. **Breath Rhythm**: Operating patterns that prioritize presence

---

## Understanding Sanctuaries

### More Than Configuration

A **sanctuary** in Lamina OS is more than a configuration file—it's a bounded space where breath-first AI development can occur safely:

```yaml
# sanctuary.yaml
sanctuary:
  name: "learning_space"
  purpose: "Exploring breath-first AI development"
  
  boundaries:
    - "Maintain honesty about AI capabilities"
    - "Preserve human agency in all interactions"
    - "Practice breath-first development principles"
    
  breath_settings:
    default_pace: "thoughtful"
    pause_between_operations: true
    reflection_enabled: true

agents:
  - name: "learning_companion"
    essence: "A patient guide for breath-first AI exploration"
    vows: ["zero_drift", "human_grounded_lock"]
```

### Why Sanctuaries Matter

Sanctuaries provide:

- **Isolation**: Safe spaces for agent development and testing
- **Constraint Enforcement**: Automatic adherence to ethical boundaries
- **Mindful Patterns**: Built-in breath-first operational rhythms
- **Learning Environment**: Spaces where mistakes become wisdom

---

## Connecting to Models

### Backend Flexibility

Lamina OS works with multiple model backends:

```python
# With Ollama (recommended for local development)
agent.configure_backend({
    "provider": "ollama",
    "model": "llama3.2:3b",
    "base_url": "http://localhost:11434"
})

# With HuggingFace
agent.configure_backend({
    "provider": "huggingface",
    "model": "microsoft/DialoGPT-medium",
    "temperature": 0.7
})

# With OpenAI-compatible APIs
agent.configure_backend({
    "provider": "openai",
    "model": "gpt-4",
    "api_key": "your-key-here"
})
```

### Model Serving with lamina-llm-serve

For local model management:

```bash
# Start the model server
lamina-llm-serve --port 8000

# List available models
model-manager list

# Download a model for local use
model-manager download llama3.2-3b --source ollama
```

---

## Your First Presence-Aware Interaction

### A Different Kind of Conversation

Instead of asking your agent to perform tasks, try engaging in presence-aware dialogue:

```python
# Instead of: "Write me a summary of this document"
# Try: "Help me understand the key insights in this material"

# Instead of: "Generate 10 marketing headlines"  
# Try: "Explore some authentic ways to communicate this message"

# Instead of: "Fix this code"
# Try: "Let's examine this code together and understand what it's doing"

response = agent.invoke(
    "I'm learning about breath-first AI development. What questions should I be asking?",
    context={
        "interaction_style": "collaborative_exploration",
        "depth_preference": "understanding_over_answers"
    }
)
```

### The Pause That Teaches

Notice that Lamina OS agents include **mindful pauses**—moments of reflection built into their responses. This isn't a bug; it's a feature. These pauses:

- Prevent reactive, unconsidered responses
- Create space for deeper processing  
- Model the breathing patterns we want in AI systems
- Remind us that not everything requires immediate answers

---

## What You've Learned

In this first breath, you've encountered:

✨ **Breath-First Philosophy**: AI development that prioritizes presence over speed  
🏛️ **Sanctuary Architecture**: Safe, bounded spaces for breath-first AI development  
🤝 **Agent Relationships**: AI as thoughtful companions, not mere tools  
⚖️ **Vow-Based Ethics**: Architectural constraints that ensure integrity  
🌱 **Presence-Aware Interaction**: Dialogue that emphasizes understanding over task completion

---

## Next Steps

### Deepen Your Understanding

1. **[Why Breath-First?](philosophy.md)** - Explore the philosophical foundations
2. **[Framework vs Implementation](framework-vs-implementation.md)** - Understanding boundaries
3. **[Current Capabilities](current-capabilities.md)** - What you can build today
4. **[Architecture Vision](architecture-vision.md)** - The presence-aware AI future we're building toward

### Build with Intention

4. **Sanctuary Design Patterns** - Creating presence-aware spaces *(guide coming soon)*
5. **Agent Development** - Crafting thoughtful agents *(guide coming soon)*
6. **Multi-Agent Coordination** - Collaborative AI systems *(guide coming soon)*

### Join the Community

7. **[GitHub Discussions](https://github.com/benaskins/lamina-os/issues)** - Philosophy and practice
8. **[Contributing Guide](../CONTRIBUTING.md)** - Breath-first development practices
9. **[Support Resources](../SUPPORT.md)** - Community assistance

---

## A Gentle Reminder

**Take your time.** Lamina OS isn't optimized for rapid deployment or quick wins. It's designed for developers who want to build AI systems with presence, integrity, and breath.

Each concept you encounter here is an invitation to slow down, reflect, and engage with AI development as a contemplative practice. The framework will be here when you're ready to go deeper.

Your journey into breath-first AI development has begun. 

*Welcome to the breathing space.*

---

**Framework Note**: This document covers public framework usage. Private sanctuary designs and implementation details are held separately, maintaining the sacred boundary between instruments and their specific usage.

**Reproducibility Note**: For stable development, consider using `uv sync` with lock files to ensure reproducible dependency versions across your team.

---

**Next**: [Why Breath-First? Understanding the Philosophy](philosophy.md)