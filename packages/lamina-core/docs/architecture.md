# Architecture Overview

## Core Concepts

Lamina Core implements a **Agent Coordinator Pattern** that provides intelligent request routing through a unified interface while maintaining clean separation of concerns.

## Agent Coordinator Pattern

### Single Entry Point
- All user interactions go through one coordinator
- Hides multi-agent complexity from users
- Provides consistent interface regardless of backend agents

### Intelligent Routing
- Analyzes user messages to determine intent
- Routes to appropriate specialized agents
- Supports secondary agent consultation

### Constraint Enforcement
- Applies safety and policy constraints
- Validates responses before returning to users
- Maintains system compliance and ethical guidelines

## System Architecture

```
┌─────────────────┐
│     User        │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Agent           │
│ Coordinator     │
├─────────────────┤
│ • Intent        │
│   Classification│
│ • Routing       │
│ • Constraints   │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Specialized     │
│ Agents          │
├─────────────────┤
│ • Conversational│
│ • Analytical    │
│ • Security      │
│ • Reasoning     │
└─────────────────┘
```

## Core Components

### 1. Coordination Layer
- **AgentCoordinator**: Main orchestration logic
- **IntentClassifier**: Message analysis and intent detection
- **ConstraintEngine**: Policy and safety enforcement

### 2. Backend Layer
- **AI Backends**: Pluggable AI provider integrations
- **Memory System**: Intelligent semantic memory
- **Infrastructure**: Docker orchestration and deployment

### 3. CLI Layer
- **Sanctuary Management**: Project scaffolding and setup
- **Agent Management**: Agent creation and configuration
- **Infrastructure**: Deployment and operations

## Agent Types

### Conversational Agent
- General purpose chat and assistance
- Friendly, helpful personality
- Broad knowledge base

### Analytical Agent  
- Research and data analysis
- Pattern recognition and insights
- Objective, thorough approach

### Security Agent
- Validation and threat detection
- Policy enforcement
- Risk assessment

### Reasoning Agent
- Logic and problem solving
- Mathematical computations
- Systematic approach

## Intent Classification

The system analyzes messages using:

1. **Pattern Matching**: Regular expressions for specific intents
2. **Keyword Analysis**: Domain-specific vocabulary detection
3. **Context Evaluation**: Previous conversation context
4. **Confidence Scoring**: Reliability metrics for routing decisions

## Constraint System

### Safety Constraints
- Harmful instruction detection
- Personal attack prevention
- Dangerous content filtering

### Privacy Constraints
- Personal information redaction
- Data protection compliance
- Access control enforcement

### Security Constraints
- Credential exposure prevention
- System exploitation protection
- Vulnerability scanning

### Ethical Constraints
- Bias and discrimination prevention
- Deception detection
- Respectful interaction enforcement

## Memory Architecture

### Semantic Memory
- Vector-based storage using ChromaDB
- Contextual embedding and retrieval
- Memory evolution and consolidation

### Memory Types
- **Short-term**: Current conversation context
- **Long-term**: Persistent knowledge and preferences
- **Episodic**: Specific interaction history

## Infrastructure

### Containerization
- Docker-based deployment
- Service isolation and scaling
- Resource management

### Security
- mTLS communication
- Certificate-based authentication
- Network isolation

### Observability
- Grafana dashboards
- Loki log aggregation
- Vector metrics collection

## Extensibility

### Custom Agents
- Template-based scaffolding
- Configuration-driven setup
- Provider-agnostic design

### Custom Backends
- Abstract base class implementation
- Pluggable architecture
- Runtime provider switching

### Custom Constraints
- Rule-based constraint definitions
- Severity classification
- Action specification (block, modify, redact)

## Performance Considerations

### Routing Efficiency
- Fast intent classification
- Minimal coordinator overhead
- Efficient agent selection

### Memory Management
- Lazy loading of components
- Resource-aware scheduling
- Garbage collection optimization

### Scalability
- Horizontal agent scaling
- Load balancing support
- Distributed deployment ready