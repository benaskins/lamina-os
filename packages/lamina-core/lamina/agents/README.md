# Lamina Agents Module

The `lamina.agents` module provides the foundational classes for creating presence-aware AI agents in the Lamina OS framework.

## Overview

This module introduces:
- **Base Agent Class**: Abstract base class that all Lamina agents inherit from
- **AgentEssence**: Structured representation of an agent's core behavioral characteristics
- **EssenceParser**: Markdown parser for loading agent essences from sanctuary configurations

## Key Concepts

### Agent Essence

An agent's essence defines its core behavioral characteristics through:

- **Core Tone**: The fundamental quality of the agent's presence
- **Behavioral Pillars**: Key principles that guide the agent's responses
- **Drift Boundaries**: Constraints that prevent unwanted behaviors
- **Modulation Features**: Techniques for maintaining breath-first operation

### Breath-First Operation

All agents implement breath-first principles:
- Taking conscious pauses before responding
- Operating with deliberate pacing
- Honoring silence and contemplation

## Usage

### Creating a Custom Agent

```python
from lamina.agents import Agent

class MyAgent(Agent):
    async def process(self, message: str, context=None) -> str:
        # Take a breath before processing
        await self.breathe()
        
        # Your processing logic here
        response = generate_response(message)
        
        # Apply constraints from essence
        return self.apply_constraints(response)
```

### Defining Agent Essence

Create an essence file in markdown format:

```markdown
# Capsule: Essence — MyAgent
**Tag:** essence.myagent.v1
**Status:** active

---

## Core Tone
Present, attentive, and mindful.

## Behavioral Pillars
- **Presence:** Always fully present in interactions
- **Clarity:** Communicate with precision and care
- **Breath:** Maintain conscious pacing

## Drift Boundaries
- No reactive responses
- No performance of understanding
- No violation of established vows

## Modulation Features
- Breath anchoring (pause, silence)
- Present-tense awareness
- Gentle transitions
```

### Loading and Using Agents

```python
# Load agent with essence from sanctuary
agent = MyAgent("myagent")

# Or provide explicit essence
from lamina.agents import AgentEssence

essence = AgentEssence(
    tag="essence.custom.v1",
    status="active", 
    core_tone="Your agent's core quality",
    behavioral_pillars=["Pillar 1", "Pillar 2"],
    drift_boundaries=["Boundary 1", "Boundary 2"]
)

agent = MyAgent("custom", essence=essence)

# Process messages
response = await agent.process("Hello, agent")
```

## Integration with Sanctuary

Agents automatically load their essence from the sanctuary structure:

```
sanctuary/
├── agents/
│   └── myagent/
│       ├── agent.yaml      # Agent configuration
│       └── essence.md      # Agent essence (if separate)
└── essence/
    └── essence.myagent.md  # Shared essence definitions
```

## See Also

- [Agent Architecture ADR](../../docs/adrs/0015-aurelia-coordinator-multi-agent-architecture.md)
- [Example Implementation](../../examples/agent_with_essence.py)
- [Agent Configuration](../agent_config.py)