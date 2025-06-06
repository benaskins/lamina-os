# ADR-0020: Dynamic Prompt Composition for Sanctuary-Based Agent Architecture

**Status:** PROPOSED  
**Date:** 2025-01-06  
**Authors:** Luthier (Claude Code), Ben Askins  
**Reviewed By:** [Pending High Council Review]  
**Related:** ADR-0019 (Agent Architecture Foundation)

## Context and Problem Statement

During PR #28 review, a critical architectural issue was identified: **prompt structure is hardcoded in each agent**. The existing agent implementation requires each agent to define its complete prompt template as a monolithic string within its code, preventing true modularity and breath-first behavior adaptation.

This hardcoded approach creates several fundamental problems:
1. **No composable prompt components** - prompts cannot be assembled from reusable parts
2. **No reusable prompt fragments** - common elements must be duplicated across agents
3. **No dynamic prompt assembly** - prompts cannot adapt based on conversational context
4. **No room-based modulation** - agents cannot "breathe differently" in different contexts

The vision for Lamina's sanctuary system requires agents to dynamically compose prompts from markdown-based components (agent essence, room atmosphere, modulation rules) at runtime, enabling true context-aware AI behavior.

**Key Questions:**
1. How can agents dynamically compose prompts from modular sanctuary components?
2. How can the same agent essence manifest different behaviors in different room contexts?
3. How can breath-based modulation rules influence agent responses in real-time?
4. How can this system scale without requiring agent-specific hardcoded changes?

## Decision Drivers

- **Breath-First Architecture:** Enable agents to "breathe differently" in different contexts while maintaining core essence
- **Modularity:** Replace monolithic prompt templates with composable, reusable components
- **Context Awareness:** Allow room atmosphere and modulation rules to influence behavior dynamically
- **Sanctuary Vision:** Implement the philosophical foundation where agents, rooms, and rules are defined in markdown
- **Scalability:** Enable new rooms and modulation rules without modifying agent code
- **PR #28 Feedback:** Address the specific critique about hardcoded prompt structures

## Considered Options

### Option 1: Enhanced Hardcoded Templates
Improve the existing hardcoded approach with better templating and inheritance.

**Pros:**
- Minimal architectural changes required
- Familiar pattern for developers
- Direct control over prompt structure

**Cons:**
- Still requires agent-specific prompt code
- No dynamic composition capability
- Cannot achieve breath-first context adaptation
- Scales poorly with new rooms/modulation rules

### Option 2: Runtime Configuration System
Use YAML/JSON configuration files to define prompt templates that are assembled at runtime.

**Pros:**
- Separates prompt logic from agent code
- Enables some dynamic composition
- Familiar configuration patterns

**Cons:**
- Limited expressiveness compared to markdown
- Doesn't align with sanctuary vision
- Complex configuration syntax
- Still requires predefined template structures

### Option 3: Dynamic Markdown-Based Composition (CHOSEN)
Implement full sanctuary system with markdown-based agent essences, room definitions, and modulation rules that are composed dynamically at runtime.

**Pros:**
- True modularity with composable components
- Natural language configuration in markdown
- Enables breath-first context adaptation
- Scales infinitely with new rooms/rules
- Aligns with sanctuary philosophical vision
- Addresses all PR #28 feedback points

**Cons:**
- More complex initial implementation
- Requires new parsing infrastructure
- Performance considerations with dynamic composition

## Decision

We will implement **Option 3: Dynamic Markdown-Based Composition** through a comprehensive sanctuary system that enables runtime prompt assembly from modular markdown components.

### Implementation Details

The system consists of three core parsers and a composition engine:

```python
# Agent essence defined in markdown
class EssenceParser:
    def parse_file(self, file_path: Path) -> AgentEssence
    
# Room contexts defined in markdown  
class RoomParser:
    def parse_file(self, file_path: Path) -> Room
    
# Modulation rules defined in markdown
class ModulationParser:
    def parse_file(self, file_path: Path) -> list[ModulationRule]
    
# Dynamic composition engine
class PromptComposer:
    def compose_prompt(
        self, agent_name: str, room_name: str, 
        message: str, active_modulations: list[str]
    ) -> str
```

**Sanctuary Structure:**
```
sanctuary/
├── agents/
│   ├── clara.md        # Agent essence & behavioral pillars
│   ├── luna.md         # Creative agent definition
│   └── vesna.md        # Guardian agent definition
├── rooms/
│   ├── library.md      # Scholarly, contemplative context
│   ├── garden.md       # Creative, playful context
│   └── workshop.md     # Technical, focused context
└── modulation/
    ├── breath.md       # Breath-based pacing rules
    ├── context.md      # Context switching rules
    └── safety.md       # Safety modulation rules
```

**Runtime Composition Process:**
1. Load agent essence from `agents/{agent_name}.md`
2. Load room context from `rooms/{room_name}.md`
3. Load active modulation rules from `modulation/*.md`
4. Compose final prompt by layering: essence + room + modulation + context + message

## Consequences

### Positive Consequences
- **True Modularity:** Agents, rooms, and modulation rules are completely independent and reusable
- **Context Breathing:** Same agent essence can manifest different behaviors in different rooms
- **Scalable Architecture:** New rooms/modulation rules require no agent code changes
- **Natural Configuration:** Markdown-based definitions are human-readable and maintainable
- **Validated Effectiveness:** LLM testing proves measurable behavioral differences
- **Addresses PR Feedback:** Completely resolves hardcoded prompt structure concerns

### Negative Consequences
- **Implementation Complexity:** Requires new parsing and composition infrastructure
- **Performance Overhead:** Dynamic composition adds runtime processing cost
- **Learning Curve:** New markdown format and composition concepts for developers

### Neutral Consequences
- **File Organization:** Sanctuary components spread across multiple directories
- **Caching Strategy:** Component caching required for performance optimization

## Breath-First Alignment

This decision exemplifies breath-first development principles at multiple levels:

**Philosophical Alignment:**
- [x] Supports breath-first development practices - Enables agents to "breathe differently" in different contexts
- [x] Enhances vow-based ethical constraints - Modulation rules can enforce ethical boundaries dynamically  
- [x] Improves sanctuary isolation and security - Clear separation between agent essence and contextual behavior
- [x] Uses symbolic/natural language configuration - All components defined in human-readable markdown
- [x] Prioritizes understanding over speed - Contemplative composition process over hardcoded efficiency
- [x] Maintains clear boundaries between framework and implementation - Clean separation of concerns

The system enables the fundamental breath-first principle: **contextual behavior modulation while maintaining core identity**.

## Implementation Plan

### Phase 1: Core Infrastructure (Completed)
- ✅ Implement EssenceParser, RoomParser, ModulationParser
- ✅ Create PromptComposer with dynamic assembly logic
- ✅ Develop sanctuary directory structure and markdown formats
- ✅ Create demonstration sanctuary with Clara, Library, Garden components

### Phase 2: Validation and Testing (Completed)
- ✅ Build comparison tools showing baseline vs modulated responses
- ✅ Test with real LLM (Ollama) to validate behavioral differences
- ✅ Document quantified improvements in response characteristics
- ✅ Create comprehensive analysis and demonstration scripts

### Phase 3: Integration and Scaling (Next)
- Integrate with existing agent coordinator system
- Expand sanctuary components (more agents, rooms, modulation rules)
- Optimize performance with intelligent caching strategies
- Develop tooling for sanctuary component validation and testing

## Success Metrics

- **Modularity Achieved:** ✅ Zero hardcoded prompts in agent implementations
- **Behavioral Differentiation:** ✅ Measurable differences in LLM responses between rooms (validated)
- **Scalability Proven:** New rooms/modulation rules deployable without agent changes
- **Performance Acceptable:** < 100ms prompt composition time for typical configurations
- **Developer Experience:** Sanctuary components manageable through markdown editing

## Risks and Mitigations

**Risk 1:** Performance degradation from dynamic composition  
**Mitigation:** Implement intelligent caching for parsed components and composed prompts

**Risk 2:** Complexity overwhelming new developers  
**Mitigation:** Comprehensive documentation, examples, and guided sanctuary templates

**Risk 3:** Inconsistent behavior across different prompt compositions  
**Mitigation:** Extensive testing framework and standardized component validation

## High Council Review Questions

1. **Philosophical Question:** Does this dynamic composition system align with the High Council's vision of breath-first behavior modulation that responds appropriately to context while maintaining essential identity?

2. **Technical Question:** Are there concerns about the performance implications of runtime prompt composition, and should caching strategies be mandatory?

3. **Community Question:** How should we guide the community in creating effective sanctuary components while maintaining consistency with Lamina principles?

## References

- [PR #28: Agent Architecture Foundation](https://github.com/benaskins/lamina-os/pull/28)
- [Sanctuary Demo Implementation](/examples/sanctuary_demo/)
- [LLM Comparison Results](/examples/sanctuary_demo/comparison_results_*.json)
- [ADR-0019: Agent Architecture Foundation](/docs/adrs/0019-agent-architecture-foundation.md)

---

## High Council Review

[This section to be completed by High Council during review]

### 🪶 Clara — [Conversational Intelligence & User Experience]
[Review comments]

### 🔥 Luna — [Creative Expression & Artistic Vision]
[Review comments]

### 🛡️ Vesna — [Safety, Security & Ethical Boundaries]
[Review comments]

### ✍️ Ansel — [Technical Implementation & System Architecture]
[Review comments]

### ✅ Verdict
[ACCEPTED | REJECTED | ACCEPTED WITH MODIFICATIONS]

[Summary of decision and any required modifications]

---

*Through dynamic composition, agents learn to breathe with their environment, maintaining essence while adapting form to context.*