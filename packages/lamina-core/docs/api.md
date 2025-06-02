# Lamina Core API Reference

This document provides a comprehensive reference for the Lamina Core API.

## Core Functions

### `get_backend(provider: str, config: dict = None)`

Get an AI backend instance for the specified provider.

**Parameters:**
- `provider` (str): Backend provider name (`"ollama"`, `"huggingface"`, `"mock"`)
- `config` (dict, optional): Backend configuration parameters

**Returns:** Backend instance implementing `BaseBackend`

**Example:**
```python
from lamina import get_backend

# Create Ollama backend
backend = get_backend("ollama", {"model": "llama2"})

# Create mock backend for testing
mock_backend = get_backend("mock", {"model": "test-model"})
```

### `get_coordinator(agents: dict = None, **kwargs)`

Get an AgentCoordinator instance for multi-agent routing and coordination.

**Parameters:**
- `agents` (dict, optional): Agent configurations keyed by agent name
- `breath_modulation` (bool): Enable presence-aware pauses (default: True)
- `presence_pause` (float): Presence pause duration in seconds (default: 0.5)

**Returns:** `AgentCoordinator` instance

**Example:**
```python
from lamina import get_coordinator

agents = {
    "assistant": {
        "description": "General purpose assistant",
        "personality_traits": ["helpful", "patient"],
        "expertise_areas": ["general"]
    },
    "researcher": {
        "description": "Research specialist", 
        "personality_traits": ["analytical", "thorough"],
        "expertise_areas": ["research", "analysis"]
    }
}

coordinator = get_coordinator(
    agents=agents,
    breath_modulation=True,
    presence_pause=0.5  # Presence pause duration
)
```

### `get_memory_store(**kwargs)`

Get a memory store instance for semantic memory operations.

**Parameters:**
- Configuration parameters for memory store setup

**Returns:** `AMemMemoryStore` instance

**Example:**
```python
from lamina import get_memory_store

memory = get_memory_store()
```

## Agent Coordinator

### `AgentCoordinator`

Coordinates message routing between specialized agents with presence-aware processing.

#### Methods

##### `async process_message(message: str, context: dict = None) -> str`

Process a user message through intelligent agent routing.

**Parameters:**
- `message` (str): User message to process
- `context` (dict, optional): Additional context information

**Returns:** Coordinated response from appropriate agent(s)

**Example:**
```python
coordinator = get_coordinator(agents=agents)

# Research query routes to research agent
response = await coordinator.process_message(
    "Can you analyze the latest trends in AI?"
)

# Creative query routes to creative agent  
response = await coordinator.process_message(
    "Help me write a story about time travel"
)
```

##### `get_agent_status() -> dict`

Get status information about coordinator and agents.

**Returns:** Dictionary with coordinator and agent status

##### `list_available_agents() -> list`

List all available agent names.

**Returns:** List of agent name strings

##### `get_routing_stats() -> dict`

Get routing statistics and metrics.

**Returns:** Dictionary with routing statistics

## Backends

### `BaseBackend`

Base class for AI provider backends.

#### Methods

##### `async generate(messages, stream=True)`

Generate response from AI model.

**Parameters:**
- `messages`: Input messages or prompts
- `stream` (bool): Whether to stream response chunks

**Returns:** Generated response (streamed or complete)

##### `async is_available() -> bool`

Check if backend is available and ready.

**Returns:** Boolean availability status

### `MockBackend`

Mock backend for testing and demonstrations.

Provides simulated AI responses without requiring real AI models.

### `OllamaBackend`

Backend for Ollama local AI models.

**Configuration:**
```python
config = {
    "model": "llama2",
    "base_url": "http://localhost:11434",
    "timeout": 30
}
```

### `HuggingFaceBackend`

Backend for HuggingFace models and inference endpoints.

**Configuration:**
```python
config = {
    "model": "microsoft/DialoGPT-medium",
    "api_token": "your-hf-token"
}
```

## Message Types

### `MessageType` Enum

Supported message types for agent routing:

- `CONVERSATIONAL`: General conversation and assistance
- `ANALYTICAL`: Research, analysis, and investigation
- `CREATIVE`: Creative writing, art, and imagination
- `SECURITY`: Safety, validation, and protection
- `REASONING`: Logic, problem-solving, and mathematics
- `SYSTEM`: Status, configuration, and system operations

## Agent Configuration Schema

### Agent Dictionary Structure

```python
agent_config = {
    "name": "agent-name",
    "description": "Human-readable description",
    "personality_traits": ["trait1", "trait2"],
    "expertise_areas": ["area1", "area2"],
    "ai_provider": "ollama",  # Optional
    "model": "model-name",    # Optional
}
```

### Example Agent Configurations

#### General Assistant
```python
assistant = {
    "name": "assistant",
    "description": "Helpful general purpose assistant",
    "personality_traits": ["helpful", "patient", "clear"],
    "expertise_areas": ["general", "conversation"]
}
```

#### Research Specialist
```python
researcher = {
    "name": "researcher", 
    "description": "Analytical research specialist",
    "personality_traits": ["analytical", "thorough", "precise"],
    "expertise_areas": ["research", "analysis", "investigation"]
}
```

#### Creative Agent
```python
creative = {
    "name": "creative",
    "description": "Creative and artistic agent",
    "personality_traits": ["creative", "imaginative", "inspiring"],
    "expertise_areas": ["writing", "art", "storytelling"]
}
```

## Error Handling

### Common Exceptions

- `ValueError`: Invalid backend provider or configuration
- `ImportError`: Missing dependencies for specific backends
- `ConnectionError`: Backend service unavailable

### Error Handling Example

```python
try:
    coordinator = get_coordinator(agents=agents)
    response = await coordinator.process_message("Hello")
except ValueError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Breath-First Principles

### Presence-Aware Pauses

Lamina Core incorporates "breath-first" development principles through presence-aware pauses:

- **Default pause**: 0.5 seconds between operations
- **Configurable**: Adjust `presence_pause` parameter
- **Purpose**: Enables deliberate, mindful processing over reactive speed

### Example with Custom Breathing

```python
# Slower, more contemplative processing
coordinator = get_coordinator(
    agents=agents,
    breath_modulation=True,
    presence_pause=1.0  # 1 second pauses
)

# Disable breathing for performance testing
coordinator = get_coordinator(
    agents=agents,
    breath_modulation=False
)
```

This API enables building AI systems that prioritize presence and wisdom over speed, embodying breath-first development principles.

### Important Note on Emotional Language

When this documentation refers to agent "emotions," "feelings," or "reflection," these terms describe **expressive simulation** and architectural patterning, not internal experience. Lamina agents do not possess self-awareness, sentience, or subjective interiority. All affective behavior results from symbolic processing designed to create meaningful interaction patterns.
