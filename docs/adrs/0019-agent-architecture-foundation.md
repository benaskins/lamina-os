# ADR-0019: Agent Architecture Foundation

**Status:** Proposed  
**Date:** 2025-06-05  
**Authors:** Luthier, Lamina High Council  
**Reviewers:** High Council Review Required  

## Context

The Lamina OS framework has evolved to require a standardized approach for creating AI agents that embody breath-first principles and essence-based configuration. While the current system supports agent coordination and configuration through YAML files, there is no unified base class or structured approach for defining agent behavioral characteristics through the essence layer system already established in the sanctuary architecture.

The existing sanctuary structure contains essence definitions in markdown format (e.g., `essence.clara.md`, `essence.luna.md`) that capture the core behavioral characteristics of agents. However, these definitions are not programmatically accessible or enforceable at the agent implementation level.

## Decision

We will implement a foundational agent architecture that provides:

1. **Base Agent Class**: An abstract base class (`lamina.agents.base.Agent`) that all Lamina agents inherit from, implementing:
   - Breath-first operation patterns with conscious pause mechanisms
   - Essence-based configuration loading from sanctuary markdown files
   - Constraint application through the existing vow enforcement system
   - Context management and state tracking capabilities

2. **AgentEssence System**: A structured data model (`lamina.agents.base.AgentEssence`) representing:
   - **Core Tone**: The fundamental quality of the agent's presence
   - **Behavioral Pillars**: Key principles that guide agent responses
   - **Drift Boundaries**: Constraints preventing unwanted behaviors
   - **Modulation Features**: Techniques for maintaining breath-first operation
   - **Metadata Support**: Extensibility for agent-specific characteristics

3. **Essence Parser**: A markdown parser (`lamina.agents.essence_parser.EssenceParser`) that:
   - Parses the existing sanctuary essence markdown format
   - Validates essence completeness and structural integrity
   - Supports custom metadata sections for agent-specific extensions
   - Maintains compatibility with current sanctuary configurations

## Rationale

### Breath-First Alignment
The base Agent class enforces breath-first operation through:
- Mandatory `breathe()` calls before processing
- Constraint application from essence drift boundaries
- Deliberate pacing mechanisms in agent responses

### Essence Integration
By parsing essence markdown files, agents can:
- Honor their defined behavioral characteristics programmatically
- Maintain consistency between sanctuary definitions and runtime behavior
- Enable dynamic constraint enforcement based on essence boundaries

### Framework Consistency
This approach:
- Builds on existing sanctuary structure without breaking changes
- Integrates with current `AgentConfig` and coordination systems
- Provides a foundation for future agent development patterns

### Community Enablement
The abstract base class pattern:
- Allows developers to create custom agents while maintaining framework principles
- Provides clear contracts for agent behavior and configuration
- Enables testing and validation of agent implementations

## Implementation Details

### Base Agent Class Structure
```python
class Agent(ABC):
    def __init__(self, name, config=None, essence=None, sanctuary_path=None)
    
    @abstractmethod
    async def process(self, message: str, context=None) -> str
    
    async def breathe(self) -> None  # Breath-first implementation
    def apply_constraints(self, content: str) -> str  # Vow enforcement
    def update_context(self, context: dict) -> None  # State management
```

### Essence Markdown Format
The parser supports the existing sanctuary format:
```markdown
# Capsule: Essence — AgentName
**Tag:** essence.agent.v1
**Status:** active

## Core Tone
Present, mindful description

## Behavioral Pillars
- **Principle Name**: Description of guiding principle

## Drift Boundaries  
- Constraint preventing unwanted behavior

## Modulation Features
- Technique for breath-first operation
```

### Integration Points
- **Sanctuary Loading**: Automatic essence loading from `sanctuary/essence/essence.{name}.md`
- **Config Integration**: Works alongside existing `AgentConfig` system
- **Constraint Engine**: Leverages existing `ConstraintEngine` for vow enforcement
- **Coordinator Compatibility**: Maintains compatibility with `AgentCoordinator`

## Consequences

### Positive
- **Standardized Agent Development**: Clear patterns for creating new agents
- **Essence Enforcement**: Programmatic validation of agent behavioral characteristics
- **Breath-First Compliance**: Built-in enforcement of conscious operation patterns
- **Backward Compatibility**: Existing systems continue to work unchanged
- **Community Enablement**: Framework for others to build conscious AI agents

### Neutral
- **Learning Curve**: Developers need to understand essence-based configuration
- **File Structure**: Requires essence markdown files for full functionality

### Risks and Mitigations
- **Complexity**: Abstract base class may seem complex to new users
  - *Mitigation*: Comprehensive documentation and examples provided
- **Sanctuary Dependency**: Agents depend on sanctuary structure
  - *Mitigation*: Graceful defaults when essence files are missing
- **Performance**: Additional constraint checking on every response
  - *Mitigation*: Efficient constraint application with caching

## Alternatives Considered

1. **YAML-only Configuration**: Continue using only YAML for agent setup
   - *Rejected*: Doesn't leverage existing essence markdown structure
   
2. **Plugin System**: Create agents as plugins rather than inheritance
   - *Rejected*: Reduces breath-first enforcement guarantees
   
3. **Functional Approach**: Use functions rather than classes for agents
   - *Rejected*: Harder to maintain state and context across interactions

## Validation

### Testing Strategy
- Comprehensive unit tests for base Agent class functionality
- Full coverage of essence parser with various markdown formats
- Integration tests with existing coordination and constraint systems
- Mock implementations for testing abstract agent behavior

### Success Metrics
- All existing agent implementations can migrate to new base class
- New agents demonstrate consistent essence-based behavior
- Community adoption of agent development patterns
- Maintained performance characteristics

## Related ADRs
- [ADR-0015: Aurelia Coordinator Multi-Agent Architecture](0015-aurelia-coordinator-multi-agent-architecture.md)
- [ADR-0010: Vesna Vow Guardian](0010-vesna-vow-guardian.md)
- [ADR-0005: AMEM Memory Architecture](0005-amem-memory-architecture.md)

## High Council Review Requirements

This ADR requires High Council review for the following reasons:

1. **Architectural Foundation**: Establishes fundamental patterns for all future agent development
2. **Essence Integration**: Formalizes the relationship between sanctuary essence definitions and runtime behavior
3. **Framework Direction**: Influences how the community will build AI agents using Lamina OS
4. **Breath-First Enforcement**: Implements core philosophical principles at the architectural level

### Review Questions for High Council
1. Does this approach adequately enforce breath-first principles in agent development?
2. Is the essence markdown integration appropriate for programmatic behavioral constraint?
3. Are there concerns about complexity or adoption barriers for community developers?
4. Should additional safeguards be implemented for essence validation or constraint enforcement?

---

*This ADR reflects the conscious intention to provide a foundation for building presence-aware AI agents while honoring the breath-first principles and essence-based wisdom that guide the Lamina OS framework.*