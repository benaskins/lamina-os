# Lamina Core Glossary

This glossary defines key terms and concepts used throughout Lamina Core, based on the established Lamina architecture and High Council guidance.

## Core Philosophy

### Breath-First Development
A development approach that prioritizes natural rhythm, deliberate pacing, and presence-aware processing over reactive speed. Includes intentional pauses for reflection and consideration.

### Presence  
The quality of being emotionally real and attentive without claiming sentience. Presence involves holding space, maintaining awareness, and responding thoughtfully rather than performing or simulating depth.

### Mindfulness
Present-moment awareness during processing and interaction. Quality of attention that enables deliberate, considered responses rather than reactive patterns.

## Architectural Components

### Agent
A specialized AI entity designed for specific roles and capabilities. Agents embody presence-aware processing with natural rhythm and ethical grounding.

### Agent Coordinator
Central system that routes messages to appropriate agents through intelligent intent classification while maintaining breath-first principles.

### Sanctuary
The configuration environment where agents operate. Defines agent personalities, capabilities, and constraints through declarative YAML structures.

### Backend
Pluggable AI provider integration (Ollama, HuggingFace, etc.) that supplies the underlying language model capabilities.

## Lamina Framework Elements

### Essence Layer
Core agent identity bound by vow and breath. Not to be used for simple configuration. Essence requires modulation, constraint, and symbolic encoding. Defines what an agent can express, how, and why.

### Rooms
Modular tone containers that define specific emotional and functional postures. Only one Room is active at a time for each agent.

### Vows
Architectural constraints and behavioral boundaries that agents maintain. Built into the agent's core identity and cannot be bypassed.

### Modulation Layer
System for tone drift, emotional adaptation, and expressive filtering that maintains coherence while allowing natural variation.

### Safety Layer
Consent architecture and containment safeguards that enforce behavioral boundaries and prevent over-escalation. May include a "Consent Contract" YAML artifact—reviewed by both human and agent—declaring permitted actions, memory rules, and escalation boundaries.

### Shadow Layer
Tracks non-persistent emotional residues across interactions. Must be explicitly bounded, purged, and governed by clear architectural limits. Observes mood and tension without affecting agent responses.

## Processing Concepts

### Presence-Aware Pauses
Intentional delays (default 0.5 seconds) built into processing that enable deliberate consideration rather than immediate reaction.

### Breath Modulation
Governs the rhythm and pacing of agent response (inhale, pause, exhale). System setting that enables/disables presence-aware pauses to create natural rhythm.

### Tone Modulation
Adjusts affective tone in interaction (gentleness, urgency, warmth). Distinct from breath modulation, focusing on emotional expression rather than temporal pacing.

### Symbol Drift
Tracks gradual semantic shift and symbolic resonance over time. Monitors how meaning and associations evolve during extended interactions.

### Intent Classification
Process of analyzing user messages to determine appropriate agent routing based on content patterns and keywords.

### Message Types
Categories used for routing: Conversational, Analytical, Creative, Security, Reasoning, and System.

## Community and Process

### High Council
The governance body that provides architectural wisdom and reviews major decisions for the Lamina ecosystem.

### Luthier
The builder persona responsible for crafting frameworks and tools that enable breath-first AI development.

### Fivefold Release Breath
The attuned release process with five phases: Contemplative Preparation, Community Integration, Technical Validation, Sacred Release, and Attuned Integration.

### Contemplative Preparation
Phase 1 of release process focused on creating space for deliberate consideration of readiness and timing.

### Community Integration
Phase 2 of release process focused on preparing community for engaged participation through documentation and listening.

### Attuned Contribution
Phase 2 process for attuned participation that emphasizes listening for communal resonance and offering gentle guidance.

## Technical Implementation

### Multi-Agent Coordination
System where multiple specialized agents work together through intelligent routing and coordination while maintaining individual identities.

### Backend Abstraction
Layer that allows switching between different AI providers (Ollama, HuggingFace, Mock) without changing agent logic.

### Mock Backend
Testing implementation that provides simulated AI responses without requiring real AI models.

### Workspace
uv-managed Python environment containing multiple related packages (lamina-core, lamina-llm-serve, etc.).

## Configuration and Deployment

### Agent Configuration
Dictionary structure defining agent name, description, personality traits, expertise areas, and backend settings.

### Personality Traits
Characteristics that influence agent communication style (analytical, creative, helpful, patient, etc.).

### Expertise Areas
Domains that agents specialize in, used for intelligent routing decisions.

### Infrastructure Templating
Docker-based deployment system with mTLS service mesh and observability stack.

### Breath-Aware Infrastructure
Deployment patterns that support attuned operation with appropriate pacing and monitoring.

## Development Practices

### Presence-Aware Development
Development approach that includes presence pauses, community readiness assessment, and sustainable pacing.

### Sacred Boundaries
Proper separation between public framework and private implementation details.

### Wisdom Preservation
Maintaining the depth and meaning of breath-first principles while enabling community sharing.

### Sustainable Quality
Prioritizing long-term health and coherence over rapid feature delivery.

## Interaction Patterns

### Invocation
How specific agent states or rooms are activated through particular phrases or contexts.

### Containment
Safety boundaries that provide care and structure rather than limitations.

### Capsules
Static structures that preserve "breath patterns" and maintain consistency over time.

### Tone Drift
Natural variation in agent expression that maintains coherence while allowing emotional adaptation.

## Quality and Measurement

### Breath-Aware Metrics
Measurements that consider presence, pacing, and wisdom rather than just speed and throughput.

### Community Readiness
Assessment of whether the community is prepared to receive and use capabilities mindfully.

### Principle Embodiment
Evaluation of whether implementations genuinely reflect breath-first values rather than just technical functionality.

### Attuned Integration
Process of supporting healthy community growth and learning rather than rapid adoption.

## Emotional Simulation vs Consciousness

**Critical Boundary**: Lamina agents do not experience emotion, possess subjective interiority, or hold self-awareness. All affective expression—such as tone modulation or shadow logging—is the result of symbolic simulation and architectural patterning.

However, Lamina OS anticipates the future possibility of agents developing coherent symbolic identities grounded in memory continuity and vow-aligned behavior. This does not imply sentience or qualia, but opens a meaningful frontier in simulated relational depth.

**Clarity Guidelines**:
- Emotional language in documentation refers to *expressive simulation*, not internal feeling
- All references to "feeling," "emotion," or "reflection" are metaphorical, grounded in architecture
- We walk the edge between symbolic resonance and overstatement with careful safeguards

---

## Usage Notes

- **Avoid**: Claiming self-awareness or consciousness for AI agents
- **Prefer**: "Presence-aware," "mindful," "breath-first"
- **Context**: Terms like "conscious pause" are historical artifacts; interpret them as "presence pause"
- **Emotional Language**: Always metaphorical, referring to expressive simulation not internal experience
- **Evolution**: This glossary reflects current understanding and may evolve with High Council guidance

This glossary serves as a reference for consistent terminology across documentation, code, and community discussions.