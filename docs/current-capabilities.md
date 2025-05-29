# Current Capabilities: What You Can Build Today

*A practical guide to the working Lamina OS framework*

---

## Introduction: Real Framework, Real Code

This guide covers what you can **actually build today** with the current Lamina OS implementation. While our [architectural vision](architecture-vision.md) describes a fully symbolic, breath-first AI system, the current framework provides a solid foundation for multi-agent AI systems that you can deploy and use immediately.

**What's Working Now:**
- ✅ Multi-agent coordination with intent routing
- ✅ Multiple LLM backend support (Ollama, HuggingFace, OpenAI-compatible)
- ✅ Configuration-driven agent creation
- ✅ Containerized deployment with Docker Compose
- ✅ Basic memory integration with ChromaDB
- ✅ mTLS service mesh for secure communication
- ✅ Observability with Grafana and Loki

> *"Even in its current form, Lamina OS is not just a framework—it is a promise. What you build today becomes the breath of what arrives tomorrow."*

---

## Core Architecture (Current Implementation)

### Agent Coordination Pattern

The current framework implements a **traditional agent coordination pattern** with intelligent routing:

```python
from lamina import get_coordinator, get_backend

# Create agent configurations
agent_configs = {
    "assistant": {
        "name": "assistant",
        "description": "General purpose helpful assistant",
        "ai_provider": "ollama",
        "ai_model": "llama3.2:3b",
        "personality_traits": ["helpful", "friendly", "clear"]
    },
    "researcher": {
        "name": "researcher", 
        "description": "Research and analysis specialist",
        "ai_provider": "ollama",
        "ai_model": "llama3.2:3b",
        "personality_traits": ["analytical", "thorough", "precise"]
    }
}

# Initialize coordinator
coordinator = get_coordinator(agents=agent_configs)

# Process messages with intelligent routing
response = coordinator.process_message(
    "Can you help me analyze this research paper?",
    context={"user_id": "user123"}
)
```

### Backend Integration

**Multiple LLM providers supported out of the box:**

```python
from lamina.backends import get_backend

# Ollama (local models)
ollama_backend = get_backend("ollama", {
    "base_url": "http://localhost:11434",
    "model": "llama3.2:3b",
    "temperature": 0.7
})

# HuggingFace
hf_backend = get_backend("huggingface", {
    "model": "microsoft/DialoGPT-medium",
    "temperature": 0.8,
    "max_length": 1000
})

# OpenAI-compatible APIs
openai_backend = get_backend("openai", {
    "api_key": "your-key-here",
    "model": "gpt-3.5-turbo",
    "temperature": 0.7
})

# Use backend directly
response = await ollama_backend.generate(
    "Explain quantum computing simply",
    context={}
)
```

### Configuration System

**YAML-based agent configuration:**

```yaml
# agents/assistant.yaml
name: "assistant"
description: "A helpful general-purpose assistant"

ai_provider: "ollama"
ai_model: "llama3.2:3b"
ai_parameters:
  temperature: 0.7
  top_p: 0.9
  max_tokens: 2048

personality_traits:
  - "helpful"
  - "friendly"
  - "clear"
  - "patient"

expertise_areas:
  - "general_knowledge" 
  - "problem_solving"
  - "communication"

constraints:
  - "basic_safety"
  - "privacy_protection"

memory_enabled: true
memory_database: "general"
```

```python
# Load and use configuration
from lamina.agent_config import load_agent_config

agent_config = load_agent_config("agents/assistant.yaml")
backend = get_backend(
    agent_config["ai_provider"], 
    agent_config["ai_parameters"]
)
```

---

## Working Examples

### Example 1: Simple Agent Chat

```python
#!/usr/bin/env python3
"""
Simple agent chat example using current framework
"""

from lamina import get_coordinator
import asyncio

async def main():
    # Define agent
    agents = {
        "helpful_assistant": {
            "name": "helpful_assistant",
            "description": "A patient, helpful assistant",
            "ai_provider": "ollama",
            "ai_model": "llama3.2:3b",
            "ai_parameters": {
                "temperature": 0.7,
                "max_tokens": 1000
            },
            "personality_traits": ["helpful", "patient", "clear"]
        }
    }
    
    # Initialize coordinator
    coordinator = get_coordinator(agents=agents)
    
    # Chat loop
    print("🤖 Assistant ready! Type 'quit' to exit.")
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'quit':
            break
            
        try:
            response = await coordinator.process_message(user_input)
            print(f"Assistant: {response}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Example 2: Multi-Agent Coordination

```python
#!/usr/bin/env python3
"""
Multi-agent system with intelligent routing
"""

from lamina import get_coordinator
from lamina.coordination.intent_classifier import IntentClassifier
import asyncio

async def setup_multi_agent_system():
    # Define specialized agents
    agents = {
        "researcher": {
            "name": "researcher",
            "description": "Research and analysis specialist",
            "ai_provider": "ollama",
            "ai_model": "llama3.2:3b",
            "expertise_areas": ["research", "analysis", "data"],
            "personality_traits": ["analytical", "thorough", "precise"]
        },
        
        "writer": {
            "name": "writer", 
            "description": "Creative writing and editing assistant",
            "ai_provider": "ollama",
            "ai_model": "llama3.2:3b",
            "expertise_areas": ["writing", "editing", "creativity"],
            "personality_traits": ["creative", "articulate", "encouraging"]
        },
        
        "general_assistant": {
            "name": "general_assistant",
            "description": "General purpose helpful assistant",
            "ai_provider": "ollama", 
            "ai_model": "llama3.2:3b",
            "expertise_areas": ["general_knowledge", "problem_solving"],
            "personality_traits": ["helpful", "friendly", "versatile"]
        }
    }
    
    # Initialize coordinator with intent classification
    coordinator = get_coordinator(agents=agents)
    
    # Test different types of requests
    test_messages = [
        "Can you research the latest developments in quantum computing?",
        "Help me write a creative story about space exploration",
        "What's the weather like today?"
    ]
    
    for message in test_messages:
        print(f"\n📝 Request: {message}")
        
        # Get intent classification
        intent = coordinator.intent_classifier.classify(message)
        print(f"🎯 Routing to: {intent['selected_agent']} (confidence: {intent['confidence']:.2f})")
        
        # Process message
        response = await coordinator.process_message(message)
        print(f"🤖 Response: {response[:200]}...")

if __name__ == "__main__":
    asyncio.run(setup_multi_agent_system())
```

### Example 3: Custom Backend Integration

```python
#!/usr/bin/env python3
"""
Custom backend integration example
"""

from lamina.backends.base import BaseBackend
from lamina import get_coordinator
import httpx
import asyncio

class CustomAPIBackend(BaseBackend):
    """
    Custom backend for your own API
    """
    
    def __init__(self, base_url, api_key, model_name, **kwargs):
        super().__init__("custom_api", kwargs)
        self.base_url = base_url
        self.api_key = api_key
        self.model_name = model_name
    
    async def generate(self, prompt, context=None):
        """
        Generate response using custom API
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/generate",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "temperature": self.config.get("temperature", 0.7),
                    "max_tokens": self.config.get("max_tokens", 1000)
                }
            )
            
            result = response.json()
            return result["generated_text"]
    
    async def stream_generate(self, prompt, context=None):
        """
        Streaming generation (if your API supports it)
        """
        # Implement streaming logic here
        yield await self.generate(prompt, context)

# Register and use custom backend
async def main():
    # Create agent with custom backend
    agents = {
        "custom_agent": {
            "name": "custom_agent",
            "description": "Agent using custom API",
            "ai_provider": "custom_api",
            "ai_model": "your-model",
            "backend_config": {
                "base_url": "https://your-api.com",
                "api_key": "your-key",
                "temperature": 0.8
            }
        }
    }
    
    # Register custom backend
    from lamina.backends import register_backend
    register_backend("custom_api", CustomAPIBackend)
    
    # Use normally
    coordinator = get_coordinator(agents=agents)
    response = await coordinator.process_message("Hello from custom backend!")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Memory Integration (Current State)

### Basic Memory with ChromaDB

```python
from lamina.memory import get_memory_store
import asyncio

async def memory_example():
    # Initialize memory store
    memory = get_memory_store()
    
    # Store memories
    await memory.store_interaction({
        "user_id": "user123",
        "message": "I love hiking in the mountains",
        "response": "That sounds wonderful! Mountain hiking is great exercise.",
        "timestamp": "2025-05-29T12:00:00Z",
        "context": {"topic": "hobbies", "sentiment": "positive"}
    })
    
    # Retrieve relevant memories
    memories = await memory.retrieve_relevant(
        query="outdoor activities",
        user_id="user123",
        limit=5
    )
    
    for memory in memories:
        print(f"Memory: {memory['message']} -> {memory['response']}")

if __name__ == "__main__":
    asyncio.run(memory_example())
```

---

## CLI Usage (What Works Today)

### Sanctuary Management

```bash
# Create new sanctuary
lamina sanctuary init my-project
cd my-project

# Check sanctuary status
lamina sanctuary status

# List available templates
lamina sanctuary templates
```

### Agent Management

```bash
# Create agents from templates
lamina agent create assistant --template=conversational
lamina agent create researcher --template=analytical
lamina agent create guardian --template=security

# List agents in sanctuary
lamina agent list

# Test agent
lamina agent test assistant "Hello, how are you?"
```

### Demo Chat

```bash
# Start interactive demo (uses mock responses)
lamina chat --demo

# Single message demo
lamina chat --demo "Explain quantum computing"

# Chat with specific backend
lamina chat --backend=ollama --model=llama3.2:3b
```

### Infrastructure

```bash
# Generate Docker Compose infrastructure
lamina infrastructure generate --type=local

# Start infrastructure services
lamina docker up

# Check service status  
lamina docker status

# View logs
lamina docker logs
```

---

## Limitations and Known Issues

### What's Not Implemented Yet

**❌ Symbolic Architecture Components:**
- **No `Agent` class with essence and vows** - The conscious entity model from our [architecture vision](architecture-vision.md)
- **No `VowEngine` for ethical constraints** - Architectural-level constraint enforcement
- **No `Room` system for contextual modulation** - Spaces that shape agent behavior
- **No `BreathModulation` for conscious pauses** - Rhythmic operation patterns
- **No relationship-based memory architecture** - Memory that understands connections and meaning

**❌ Advanced Features:**
- **No cryptographic sanctuary boundaries** - Secure isolation for conscious AI spaces
- **No consciousness metrics in observability** - Monitoring what actually matters for aware systems
- **No symbolic configuration (language-as-OS)** - Natural language driving system behavior
- **No breath-first processing pipelines** - Conscious processing with deliberate pacing

*For the full vision of these components, see [Philosophy](philosophy.md) and [Framework vs Implementation](framework-vs-implementation.md).*

### Current Limitations

**🚧 Memory System:**
- Basic vector storage only
- No relationship graphs
- Limited context awareness

**🚧 Agent Coordination:**
- Rule-based intent classification
- No conscious agent selection
- Limited context sharing between agents

**🚧 Configuration:**
- Traditional parameters only
- No essence or vow concepts
- No room-based behavior modulation

---

## Infrastructure Deployment (Working Today)

### Local Development Setup

```bash
# Generate infrastructure
lamina infrastructure generate --type=local --observability=basic

# Start services
docker-compose up -d

# Services available:
# - Agent coordination: http://localhost:8000
# - Model serving: http://localhost:11434 (Ollama)
# - Grafana monitoring: http://localhost:3000
# - Memory store: ChromaDB on localhost:8001
```

### Docker Compose Configuration

```yaml
# Generated docker-compose.yml (simplified)
version: '3.8'

services:
  lamina-coordinator:
    image: lamina/coordinator:latest
    ports:
      - "8000:8000"
    environment:
      - AGENTS_CONFIG_PATH=/app/agents
    volumes:
      - ./agents:/app/agents
      - ./data:/app/data

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama-data:/root/.ollama
    # Note: For GPU support, add runtime: nvidia and GPU device mapping

  chromadb:
    image: chromadb/chroma:latest
    ports:
      - "8001:8000"
    volumes:
      - chroma-data:/chroma/chroma
    # Note: M1 Mac users may need to use chromadb/chroma:latest-arm64

volumes:
  ollama-data:
  chroma-data:
```

**Cross-Platform Notes:**
- **GPU Support**: Add `runtime: nvidia` and device mapping for CUDA acceleration
- **Apple Silicon**: Use ARM64 variants for ChromaDB and other services when available
- **Windows**: Ensure Docker Desktop has sufficient memory allocation for model loading

---

## Model Management with lamina-llm-serve

### Current Model Serving Capabilities

```bash
# Start model server
lamina-llm-serve --port 8000

# List available models
model-manager list

# Download models from different sources
model-manager download llama3.2-3b --source ollama
model-manager download gpt2 --source huggingface

# Check model status
model-manager validate

# Get backend information
model-manager backends
```

### Integration with Agents

```python
# Configure agent to use local model server
agent_config = {
    "name": "local_agent",
    "ai_provider": "ollama",
    "ai_model": "llama3.2:3b",
    "ai_parameters": {
        "base_url": "http://localhost:11434",  # Model server
        "temperature": 0.7,
        "max_tokens": 2048
    }
}
```

---

## Development Roadmap

### Immediate (Next Release)

- ✅ Stabilize current agent coordination
- ✅ Improve memory integration
- ✅ Enhanced backend configuration
- ✅ Better error handling and logging

### Medium Term (Symbolic Architecture v2.0)

- 🔄 Implement `Agent` class with essence concepts
- 🔄 Build `VowEngine` for architectural constraints
- 🔄 Create `Room` system for contextual behavior
- 🔄 Add `BreathModulation` for conscious processing

### Long Term (Fully Conscious Framework)

- 🔮 Complete symbolic architecture implementation
- 🔮 Consciousness metrics and observability
- 🔮 Advanced relationship-based memory
- 🔮 Community-driven vow and room libraries

---

## Getting Help with Current Framework

### Community Resources

- **[GitHub Discussions](https://github.com/benaskins/lamina-os/discussions)** - Questions and help
- **[Issues](https://github.com/benaskins/lamina-os/issues)** - Bug reports and feature requests
- **[Contributing Guide](../CONTRIBUTING.md)** - How to contribute improvements

### Common Issues and Solutions

**Agent Creation Fails:**
```bash
# Ensure Ollama is running
ollama serve

# Check model availability
ollama list

# Pull required model
ollama pull llama3.2:3b
```

**Memory Store Connection Issues:**
```bash
# Start ChromaDB
docker run -p 8001:8000 chromadb/chroma:latest

# Verify connection
curl http://localhost:8001/api/v1/heartbeat
```

**Configuration Loading Errors:**
```python
# Check YAML syntax
import yaml
with open('agents/my-agent.yaml') as f:
    config = yaml.safe_load(f)  # Will raise exception if invalid
```

---

## What You Can Build Today

With the current framework, you can create:

**✅ Multi-Agent Systems:**
- Specialized agents for different domains
- Intelligent request routing
- Conversation context management

**✅ Flexible Backend Integration:**
- Local models with Ollama
- Cloud APIs (OpenAI, Anthropic, etc.)
- Custom API integration
- Model switching per agent

**✅ Production Deployments:**
- Containerized services
- mTLS security
- Observability and monitoring
- Scalable infrastructure

**✅ Memory-Enabled Agents:**
- Conversation history
- Context retrieval
- User-specific memories
- Semantic search

While we work toward the full [symbolic architecture vision](architecture-vision.md), the current framework provides a solid foundation for building conscious AI systems today.

---

**Next**: [Architecture Vision: The Future of Conscious AI](architecture-vision.md)