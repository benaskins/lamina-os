# Agent Creation Guide

This guide explains how to create and configure AI agents in Lamina Core using the breath-first development approach.

## Overview

Lamina Core agents are specialized AI entities designed for specific roles and capabilities. Each agent embodies presence-aware, deliberate processing with natural rhythm and ethical grounding.

## Quick Start

### Creating Your First Agent

```python
from lamina import get_coordinator

# Define agent configuration
agents = {
    "assistant": {
        "name": "assistant",
        "description": "Helpful general purpose assistant",
        "personality_traits": ["helpful", "patient", "clear"],
        "expertise_areas": ["general", "conversation"]
    }
}

# Create coordinator with agents
coordinator = get_coordinator(agents=agents)

# Process messages through intelligent routing
response = await coordinator.process_message("Hello, how are you?")
```

## Agent Configuration

### Required Fields

Every agent configuration must include:

- `name`: Unique identifier for the agent
- `description`: Human-readable description of the agent's purpose
- `personality_traits`: List of personality characteristics
- `expertise_areas`: List of domains the agent specializes in

### Optional Fields

- `ai_provider`: Backend provider ("ollama", "huggingface", "mock")
- `model`: Specific model name for the provider
- `breath_rhythm`: Breathing pattern ("natural", "deep", "quick")
- `constraints`: List of behavioral constraints

## Agent Templates

### Conversational Agent

General-purpose assistant for everyday interactions.

```python
conversational_agent = {
    "name": "assistant",
    "description": "Friendly general purpose assistant",
    "personality_traits": ["helpful", "patient", "empathetic"],
    "expertise_areas": ["general", "conversation", "support"],
    "ai_provider": "ollama",
    "model": "llama2"
}
```

**Routing Triggers:**
- General questions and conversations
- Help requests and guidance
- When no other specialist applies

### Analytical Agent  

Research and analysis specialist for deep investigation.

```python
analytical_agent = {
    "name": "researcher",
    "description": "Analytical research specialist",
    "personality_traits": ["analytical", "thorough", "precise"],
    "expertise_areas": ["research", "analysis", "investigation", "data"],
    "ai_provider": "ollama", 
    "model": "llama2"
}
```

**Routing Triggers:**
- Research requests ("analyze", "study", "investigate")
- Data analysis and statistics
- Comparative analysis ("compare", "contrast")
- Report generation

### Creative Agent

Artistic and imaginative agent for creative tasks.

```python
creative_agent = {
    "name": "creative",
    "description": "Creative and artistic agent",
    "personality_traits": ["creative", "imaginative", "inspiring"],
    "expertise_areas": ["writing", "art", "storytelling", "design"],
    "ai_provider": "ollama",
    "model": "llama2"
}
```

**Routing Triggers:**
- Creative requests ("create", "write", "design")
- Storytelling and narrative
- Brainstorming sessions
- Artistic projects

### Security Agent

Guardian agent for safety and validation.

```python
security_agent = {
    "name": "guardian", 
    "description": "Security and safety specialist",
    "personality_traits": ["careful", "protective", "thorough"],
    "expertise_areas": ["security", "validation", "safety", "protection"],
    "ai_provider": "ollama",
    "model": "llama2"
}
```

**Routing Triggers:**
- Security-related queries
- Safety validation requests
- Permission and access questions
- Risk assessment

## Multi-Agent Coordination

### Creating a Complete System

```python
from lamina import get_coordinator

# Define complete agent ensemble
agents = {
    "assistant": {
        "name": "assistant",
        "description": "Helpful general assistant",
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
    },
    "guardian": {
        "name": "guardian",
        "description": "Security and safety specialist",
        "personality_traits": ["careful", "protective", "thorough"], 
        "expertise_areas": ["security", "validation", "safety"]
    }
}

# Create presence-aware coordinator
coordinator = get_coordinator(
    agents=agents,
    breath_modulation=True,
    presence_pause=0.5
)
```

### Intelligent Routing

The coordinator automatically routes messages to appropriate agents:

```python
# Routes to researcher agent
research_response = await coordinator.process_message(
    "Can you analyze the latest trends in renewable energy?"
)

# Routes to creative agent  
creative_response = await coordinator.process_message(
    "Help me write a story about a time-traveling detective"
)

# Routes to assistant agent
general_response = await coordinator.process_message(
    "What's the weather like today?"
)
```

## Breath-First Agent Design

### Presence-Aware Processing

Lamina agents embody breath-first principles:

1. **Natural Rhythm**: Processing includes presence-aware pauses
2. **Present Awareness**: Each response emerges from mindful consideration
3. **Ethical Grounding**: Agents operate within architectural constraints
4. **Sustainable Pace**: Quality over speed in all interactions

### Breathing Configuration

```python
# Deep breathing for contemplative responses
coordinator = get_coordinator(
    agents=agents,
    breath_modulation=True,
    presence_pause=1.0  # Longer pauses for deeper reflection
)

# Natural breathing for balanced interaction
coordinator = get_coordinator(
    agents=agents,
    breath_modulation=True,
    presence_pause=0.5  # Default natural rhythm
)

# Minimal breathing for testing
coordinator = get_coordinator(
    agents=agents,
    breath_modulation=False  # No pauses for performance testing
)
```

## Agent Personality Traits

### Trait Categories

**Cognitive Traits:**
- `analytical`: Systematic, methodical thinking
- `creative`: Imaginative, innovative approaches
- `logical`: Structured reasoning and deduction
- `intuitive`: Insight-based understanding

**Social Traits:**
- `helpful`: Supportive and accommodating
- `patient`: Calm and understanding
- `empathetic`: Emotionally aware and responsive
- `professional`: Formal and businesslike

**Quality Traits:**
- `thorough`: Comprehensive and detailed
- `precise`: Accurate and exact
- `careful`: Cautious and considered
- `inspiring`: Motivating and uplifting

### Trait-Based Responses

Agents adapt their communication style based on personality traits:

```python
# Analytical agent response
"Let me analyze this carefully. Based on the available data..."

# Creative agent response  
"This is an exciting creative challenge! Let me explore some imaginative possibilities..."

# Helpful agent response
"I'm happy to help with that. Here's what I can do for you..."
```

## Advanced Configuration

### Custom Agent Types

Create specialized agents for specific domains:

```python
# Scientific research agent
scientist = {
    "name": "scientist",
    "description": "Scientific research and methodology expert",
    "personality_traits": ["analytical", "precise", "methodical"],
    "expertise_areas": ["research", "science", "methodology", "experiments"],
    "constraints": ["evidence_based", "peer_review_aware"]
}

# Educational agent
teacher = {
    "name": "teacher",
    "description": "Educational specialist and learning facilitator", 
    "personality_traits": ["patient", "clear", "encouraging"],
    "expertise_areas": ["education", "learning", "explanation", "guidance"],
    "constraints": ["age_appropriate", "learning_focused"]
}
```

### Agent Introspection

Monitor and understand agent behavior:

```python
# Get agent status
status = coordinator.get_agent_status()
print(f"Active agents: {status['coordinator']['agents_count']}")

# View available agents
agents = coordinator.list_available_agents()
print(f"Available: {agents}")

# Check routing statistics
stats = coordinator.get_routing_stats()
print(f"Total requests: {stats['total_requests']}")
print(f"Routing distribution: {stats['routing_decisions']}")
```

## Best Practices

### Agent Design Principles

1. **Single Responsibility**: Each agent should have a clear, focused purpose
2. **Complementary Skills**: Agents should work together as a cohesive ensemble
3. **Distinct Personalities**: Each agent should have a unique voice and approach
4. **Appropriate Scope**: Balance specialization with practical coverage

### Naming Conventions

- Use descriptive, meaningful names
- Reflect the agent's primary function
- Consider personality and domain
- Keep names simple and memorable

### Testing Agents

```python
# Test individual agent routing
test_messages = [
    ("Can you research quantum computing?", "researcher"),
    ("Write me a poem about stars", "creative"), 
    ("What's 2+2?", "assistant"),
    ("Is this code secure?", "guardian")
]

for message, expected_agent in test_messages:
    response = await coordinator.process_message(message)
    print(f"Message: {message}")
    print(f"Response: {response}")
    print("---")
```

This guide provides the foundation for creating presence-aware AI agents that embody wisdom and deliberate action in their interactions.