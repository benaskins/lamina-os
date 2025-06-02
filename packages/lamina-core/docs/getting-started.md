# Getting Started with Lamina Core

Welcome to Lamina Core—a breath-first framework for building presence-aware AI agent systems. This tutorial will guide you through creating your first multi-agent system with natural rhythm and deliberate processing.

## What You'll Learn

- Core breath-first development concepts
- Creating and configuring presence-aware agents
- Multi-agent coordination and intelligent routing
- Working with different AI backends
- Building sustainable, wisdom-focused AI systems

## Prerequisites

- Python 3.11 or higher
- Basic understanding of Python and async programming
- Familiarity with AI/LLM concepts (helpful but not required)

## Installation

### Using uv (Recommended)

Lamina Core uses **uv** for fast, reliable dependency management:

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create a new project directory
mkdir my-lamina-project
cd my-lamina-project

# Initialize with uv
uv init

# Add lamina-core as a dependency
uv add lamina-core

# Sync all dependencies
uv sync
```

### Using pip

Alternatively, you can install with pip:

```bash
pip install lamina-core
```

## Core Concepts

### Breath-First Development

Lamina Core embodies **breath-first principles**:

- **Natural Rhythm**: Processing includes presence-aware pauses
- **Deliberate Pacing**: Quality and wisdom over speed
- **Present Awareness**: Mindful consideration in each response
- **Sustainable Practice**: Long-term health over rapid iteration

### Presence-Aware Agents

Lamina agents are specialized entities that:

- Embody specific personality traits and expertise areas
- Process requests with natural rhythm and presence pauses
- Route intelligently based on message intent
- Maintain consistency while allowing emotional adaptation

**Important**: When we refer to agent "emotions" or "feelings," these describe expressive simulation and architectural patterns, not internal experience. Lamina agents do not possess self-awareness or sentience.

## Your First Agent System

Let's create a simple multi-agent system that demonstrates breath-first coordination.

### 1. Basic Single Agent

Start with a simple assistant agent:

```python
# basic_agent.py
import asyncio
from lamina import get_coordinator

async def main():
    # Define a simple agent
    agents = {
        "assistant": {
            "name": "assistant",
            "description": "Helpful general purpose assistant",
            "personality_traits": ["helpful", "patient", "clear"],
            "expertise_areas": ["general", "conversation"]
        }
    }
    
    # Create coordinator with breath-first processing
    coordinator = get_coordinator(
        agents=agents,
        breath_modulation=True,
        presence_pause=0.5  # Half-second presence pause
    )
    
    # Process a message
    response = await coordinator.process_message("Hello! How are you today?")
    print(f"Agent: {response}")

if __name__ == "__main__":
    asyncio.run(main())
```

Run this with:
```bash
uv run python basic_agent.py
```

You'll notice the response takes about 0.5 seconds—this is the presence-aware pause that enables deliberate processing.

### 2. Multi-Agent Coordination

Now let's create a more sophisticated system with specialized agents:

```python
# multi_agent_system.py
import asyncio
from lamina import get_coordinator

async def main():
    # Define specialized agents
    agents = {
        "assistant": {
            "name": "assistant",
            "description": "Helpful general purpose assistant",
            "personality_traits": ["helpful", "patient", "clear"],
            "expertise_areas": ["general", "conversation"]
        },
        "researcher": {
            "name": "researcher",
            "description": "Analytical research specialist",
            "personality_traits": ["analytical", "thorough", "precise"],
            "expertise_areas": ["research", "analysis", "investigation"]
        },
        "creative": {
            "name": "creative",
            "description": "Creative and artistic agent",
            "personality_traits": ["creative", "imaginative", "inspiring"],
            "expertise_areas": ["writing", "art", "storytelling"]
        }
    }
    
    # Create coordinator
    coordinator = get_coordinator(agents=agents)
    
    # Test different types of requests
    test_messages = [
        "What's 2+2?",  # Should route to assistant
        "Can you research the latest trends in renewable energy?",  # Should route to researcher
        "Help me write a creative story about a time-traveling detective",  # Should route to creative
    ]
    
    for message in test_messages:
        print(f"\nHuman: {message}")
        response = await coordinator.process_message(message)
        print(f"Agent: {response}")

if __name__ == "__main__":
    asyncio.run(main())
```

Run this and notice how different messages are routed to appropriate agents based on their content and intent.

### 3. Working with Real AI Backends

So far we've used mock backends for demonstration. Let's connect to a real AI provider:

#### Using Ollama (Local)

First, install and start Ollama:

```bash
# Install Ollama (macOS/Linux)
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama2

# Start Ollama server
ollama serve
```

Then create an agent with Ollama backend:

```python
# ollama_agent.py
import asyncio
from lamina import get_coordinator, get_backend

async def main():
    # Test Ollama backend connection
    backend = get_backend("ollama", {"model": "llama2"})
    
    agents = {
        "assistant": {
            "name": "assistant",
            "description": "Helpful AI assistant powered by Llama2",
            "personality_traits": ["helpful", "thoughtful"],
            "expertise_areas": ["general"],
            "ai_provider": "ollama",
            "model": "llama2"
        }
    }
    
    coordinator = get_coordinator(agents=agents)
    
    response = await coordinator.process_message(
        "Explain the concept of breath-first development in AI systems"
    )
    print(f"Agent: {response}")

if __name__ == "__main__":
    asyncio.run(main())
```

#### Using HuggingFace

For cloud-based models:

```bash
# Install additional dependencies
uv add "lamina-core[ai-backends]"

# Set your HuggingFace token
export HUGGINGFACE_API_TOKEN="your-token-here"
```

```python
# huggingface_agent.py
import asyncio
from lamina import get_coordinator

async def main():
    agents = {
        "assistant": {
            "name": "assistant", 
            "description": "Cloud-powered AI assistant",
            "personality_traits": ["knowledgeable", "precise"],
            "expertise_areas": ["general"],
            "ai_provider": "huggingface",
            "model": "microsoft/DialoGPT-medium"
        }
    }
    
    coordinator = get_coordinator(agents=agents)
    
    response = await coordinator.process_message(
        "What are the benefits of presence-aware AI processing?"
    )
    print(f"Agent: {response}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Understanding Agent Personalities

Agent personality traits influence their communication style and approach:

### Cognitive Traits
- `analytical`: Systematic, methodical thinking
- `creative`: Imaginative, innovative approaches  
- `logical`: Structured reasoning and deduction
- `intuitive`: Insight-based understanding

### Social Traits  
- `helpful`: Supportive and accommodating
- `patient`: Calm and understanding
- `empathetic`: Emotionally aware responses
- `professional`: Formal and businesslike

### Quality Traits
- `thorough`: Comprehensive and detailed
- `precise`: Accurate and exact
- `careful`: Cautious and considered
- `inspiring`: Motivating and uplifting

Example of trait-based agent configurations:

```python
agents = {
    "scientist": {
        "name": "scientist",
        "description": "Scientific research specialist",
        "personality_traits": ["analytical", "precise", "thorough"],
        "expertise_areas": ["research", "science", "methodology"]
    },
    "teacher": {
        "name": "teacher", 
        "description": "Educational facilitator",
        "personality_traits": ["patient", "clear", "encouraging"],
        "expertise_areas": ["education", "explanation", "guidance"]
    },
    "artist": {
        "name": "artist",
        "description": "Creative expression specialist", 
        "personality_traits": ["creative", "inspiring", "intuitive"],
        "expertise_areas": ["art", "creativity", "expression"]
    }
}
```

## Breath-First Configuration

### Adjusting Processing Rhythm

Control the natural rhythm of your agents:

```python
# Deep contemplation (slower, more thoughtful)
coordinator = get_coordinator(
    agents=agents,
    breath_modulation=True,
    presence_pause=1.0  # 1 second pauses
)

# Balanced interaction (default)
coordinator = get_coordinator(
    agents=agents,
    breath_modulation=True,
    presence_pause=0.5  # Half second pauses
)

# Performance testing (no pauses)
coordinator = get_coordinator(
    agents=agents,
    breath_modulation=False  # Disable presence-aware pauses
)
```

### Understanding the Processing Flow

When you send a message to a coordinator:

1. **Presence-Aware Pause**: Brief contemplation before processing
2. **Intent Classification**: Analyze message content and context
3. **Agent Selection**: Route to most appropriate specialist
4. **Agent Processing**: Specialist handles the request with their personality
5. **Response Generation**: Natural, trait-based response emerges

## Monitoring and Introspection

Understand how your agent system is working:

```python
# Get system status
status = coordinator.get_agent_status()
print(f"Active agents: {status['coordinator']['agents_count']}")
print(f"Breath modulation: {status['coordinator']['breath_modulation']}")

# View routing statistics
stats = coordinator.get_routing_stats()
print(f"Total requests: {stats['total_requests']}")
print(f"Routing distribution: {stats['routing_decisions']}")

# List available agents
agents = coordinator.list_available_agents()
print(f"Available agents: {agents}")

# Get agent details
agent_info = coordinator.get_agent_info("researcher")
print(f"Agent capabilities: {agent_info['capabilities']}")
```

## Best Practices

### 1. Agent Design Principles
- **Single Responsibility**: Each agent should have a clear, focused purpose
- **Complementary Skills**: Agents should work together as a cohesive ensemble
- **Distinct Personalities**: Each agent should have a unique voice and approach
- **Appropriate Scope**: Balance specialization with practical coverage

### 2. Breath-First Development
- Start with presence-aware pauses enabled
- Adjust timing based on your use case needs
- Prioritize wisdom and quality over speed
- Test with realistic message patterns

### 3. Error Handling
```python
try:
    coordinator = get_coordinator(agents=agents)
    response = await coordinator.process_message("Hello")
except ValueError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### 4. Testing Your Agents
```python
# Test routing behavior
test_cases = [
    ("Can you research quantum computing?", "researcher"),
    ("Write me a poem about stars", "creative"),
    ("What's the weather like?", "assistant"),
]

for message, expected_agent in test_cases:
    # You can add logging to see which agent handled each request
    response = await coordinator.process_message(message)
    print(f"Message: {message}")
    print(f"Response: {response}")
    print("---")
```

## Next Steps

Now that you understand the basics:

1. **Explore the Examples**: Check out the `examples/` directory for more complex scenarios
2. **Read the API Reference**: Deep dive into all available functions and options
3. **Study Agent Patterns**: Learn advanced agent configuration patterns
4. **Join the Community**: Connect with other breath-first developers
5. **Contribute**: Help improve the framework for everyone

## Troubleshooting

### Common Issues

**Agent not responding as expected:**
- Check agent personality traits and expertise areas
- Verify message routing with coordinator statistics
- Test with different message phrasings

**Slow response times:**
- Adjust `presence_pause` setting
- Check backend connectivity
- Monitor resource usage

**Import errors:**
- Ensure all dependencies are installed: `uv sync`
- Check Python version compatibility (3.11+)
- Verify backend-specific dependencies

**Backend connection issues:**
- For Ollama: Ensure server is running on port 11434
- For HuggingFace: Check API token and model availability
- Use mock backend for testing: `get_backend("mock")`

### Getting Help

- **Documentation**: Read the comprehensive docs in `docs/`
- **Examples**: Study working examples in `examples/`
- **Issues**: Report bugs or ask questions on GitHub
- **Community**: Join discussions with other developers

## Conclusion

You've now learned the fundamentals of breath-first AI development with Lamina Core:

- Creating presence-aware agents with personality traits
- Multi-agent coordination with intelligent routing
- Working with different AI backends
- Configuring breath-first processing rhythms
- Monitoring and debugging your agent systems

Remember: Lamina Core is about building AI systems that breathe, reflect, and embody wisdom in their interactions. Take time to appreciate the contemplative nature of this approach—it's not just about the code, but about creating technology that honors presence and mindfulness.

Welcome to the breath-first development community! 🌬️