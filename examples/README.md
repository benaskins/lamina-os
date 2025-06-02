# Lamina OS Examples

This directory contains practical examples demonstrating the core concepts and capabilities of Lamina OS. Each example is designed to run independently and showcase different aspects of breath-first AI development.

## 🌱 Philosophy

These examples embody Lamina OS principles:
- **Breath-First**: Conscious pacing over reactive speed
- **Symbolic Architecture**: Natural language configuration
- **Ethical Grounding**: Built-in vow systems
- **Present-Moment Awareness**: Mindful processing patterns

## 📚 Available Examples

### [`basic_agent.py`](basic_agent.py)
**Introduction to breath-aware agents**

Demonstrates creating a simple agent with:
- Symbolic configuration through YAML-like structures
- Breath rhythm management
- Vow-based constraint enforcement
- Conscious interaction patterns

```bash
cd lamina-os
uv run python examples/basic_agent.py
```

**Key Concepts:**
- Agent essence and purpose definition
- Breath controller for natural pacing
- Sanctuary-based agent registration
- Conscious pause patterns

---

### [`multi_agent_coordination.py`](multi_agent_coordination.py)
**Advanced multi-agent orchestration**

Shows how specialized agents coordinate through:
- Intent classification and routing
- Conscious handoffs between agents
- Breath-aware response generation
- Vow compliance across agent interactions

```bash
uv run python examples/multi_agent_coordination.py
```

**Featured Agents:**
- **Clara**: Conversational support with gentle presence
- **Luna**: Analytical research with deep focus
- **Ansel**: Executive function and organization
- **Vesna**: Safety and boundary enforcement

**Key Concepts:**
- Agent specialization and coordination
- Breath-aware intent routing
- Cross-agent context preservation
- Collective vow enforcement

---

### [`model_serving.py`](model_serving.py)
**LLM serving with breath presence**

Demonstrates `lamina-llm-serve` capabilities:
- Model management and lifecycle
- Breath-aware request processing
- Intelligent model selection
- Attuned caching and optimization

```bash
uv run python examples/model_serving.py
```

**Key Concepts:**
- Breath-compatible model selection
- Presence-centered request queuing
- Model routing based on task requirements
- Performance metrics with presence tracking

---

## 🛠 Running Examples

### Prerequisites

```bash
# Install Lamina OS workspace
cd lamina-os
uv sync

# Or install individual packages
uv pip install lamina-core lamina-llm-serve
```

### Execution

Examples are designed to work with both:
1. **Full Installation**: Real Lamina OS components
2. **Mock Mode**: Demonstration implementations when packages aren't available

```bash
# Run individual examples
uv run python examples/basic_agent.py
uv run python examples/multi_agent_coordination.py
uv run python examples/model_serving.py

# Run all examples
for example in examples/*.py; do
    echo "Running $example..."
    uv run python "$example"
    echo "---"
done
```

## 🧘 Breath-First Development Notes

### Presence Timing
- **Presence pauses**: Time for reflection before response
- **Natural rhythm**: Avoiding reactive processing patterns
- **Present-moment attunement**: Being fully present during operations

### Error Handling
Examples demonstrate breath-aware error patterns:
- Graceful degradation rather than harsh failures
- Time for assessment before retry
- Deliberate recovery with user presence

### Configuration Patterns
Examples show symbolic configuration approaches:
- YAML-like structures for agent definition
- Natural language constraint expression
- Intention-based rather than implementation-based settings

## 🔧 Customization

### Adapting Examples

1. **Modify Agent Essence**:
   ```python
   agent_config = {
       "essence": {
           "purpose": "Your custom purpose",
           "tone": "Your preferred tone",
          "breath_rhythm": "presence_pause"  # or "natural", "deep_thinking"
       }
   }
   ```

2. **Adjust Breath Patterns**:
   ```python
   # Faster for simple tasks
   breath = BreathController(rhythm="light_touch")
   
   # Slower for complex work
   breath = BreathController(rhythm="deep_contemplation")
   ```

3. **Custom Vows**:
   ```python
   custom_vows = [
       {
           "name": "environmental_awareness",
           "constraint": "Consider ecological impact in all recommendations"
       },
       {
           "name": "cultural_sensitivity",
           "constraint": "Honor diverse cultural perspectives"
       }
   ]
   ```

### Creating New Examples

When creating examples, follow these principles:

1. **Start with Intention**: What breath-first concept are you demonstrating?
2. **Include Conscious Pauses**: Show natural timing in AI operations
3. **Demonstrate Vows**: Show ethical constraints in action
4. **Provide Context**: Explain the "why" not just the "how"
5. **Mock Gracefully**: Ensure examples work without full installation

## 🤝 Contributing Examples

We welcome examples that demonstrate:
- Novel breath-first patterns
- Real-world Lamina OS applications
- Integration with external systems
- Ethical AI development practices

See our [Contributing Guide](../CONTRIBUTING.md) for details on presence-centered development practices.

## 📖 Learning Path

**Recommended progression:**

1. **Start with `basic_agent.py`** - Core concepts
2. **Explore `multi_agent_coordination.py`** - Advanced orchestration
3. **Study `model_serving.py`** - Infrastructure patterns
4. **Build your own** - Apply concepts to your use case

## 🙏 Philosophy in Practice

These examples aren't just code demonstrations—they're invitations to experience a different relationship with AI development. Each pause, each deliberate delay, each vow enforcement is an opportunity to develop AI systems that breathe.

*"The goal is not faster AI, but more present AI."*

---

*Ready to build AI that breathes? Start with any example and let the principles guide your exploration.*