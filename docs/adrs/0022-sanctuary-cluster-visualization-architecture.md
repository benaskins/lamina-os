# ADR-0022: Sanctuary Cluster Visualization Architecture

## Status
Proposed

## Context
Lamina OS operates as a breath-first AI agent framework with sophisticated infrastructure spanning Kubernetes clusters, service meshes, and distributed agent coordination. Currently, monitoring and visualization tools (Prometheus, Grafana, Kiali) provide low-level infrastructure metrics but lack Lamina-semantic understanding.

There is a need for cluster visualization that operates at the **Lamina abstraction level** rather than raw Kubernetes resources. Users need to see:
- **Sanctuaries** and their constituent agents
- **Agent interactions** and breathing patterns 
- **Memory systems** and their relationships
- **Model serving** status and allocation
- **Real-time conversation flow** between agents

The existing infrastructure provides excellent observability foundations (Istio service mesh, Prometheus metrics, Jaeger tracing) but these tools present data in infrastructure terms (pods, services, HTTP requests) rather than Lamina concepts (agents, sanctuaries, breath cycles, vows).

## Decision
We will build a **Sanctuary Cluster Visualization System** that translates Kubernetes cluster state into Lamina-semantic representations.

### Architecture Components

#### 1. Translation Layer
- **Cluster Abstractor**: Service that queries Kubernetes APIs and translates resources into Lamina concepts
- **Mapping Rules**: 
  - Pods → Agents (with essence and vow metadata)
  - Services → Sanctuary boundaries
  - Network policies → Vow enforcement points
  - Traffic flows → Agent interactions and breath patterns
  - Persistent volumes → Memory systems (A-MEM instances)

#### 2. Sanctuary Dashboard API
- **RESTful API** providing Lamina-semantic cluster data
- **Real-time WebSocket** connections for live updates
- **Integration points** with existing observability stack
- **Kubernetes-native deployment** as part of lamina-system namespace

#### 3. Interactive Visualization Frontend
- **Sanctuary Topology View**: Visual representation of agent relationships
- **Breathing Pattern Indicators**: Real-time visualization of agent activity cycles
- **Memory Flow Visualization**: Shows A-MEM interactions and knowledge sharing
- **Vow Compliance Dashboard**: Displays ethical constraint enforcement status
- **Agent Health Monitoring**: Combines infrastructure and Lamina-specific health metrics

#### 4. Data Integration Strategy
- **Prometheus Integration**: Custom metrics for breath cycles, vow violations, memory access patterns
- **Jaeger Integration**: Distributed tracing with Lamina-semantic span annotations
- **Kiali Enhancement**: Overlay sanctuary information on service mesh topology
- **Custom Resource Definitions**: Extend Kubernetes with Sanctuary, Agent, and Vow resources

### Technical Implementation

#### Backend Architecture
```python
sanctuary-dashboard/
├── app.py                    # Flask/FastAPI main application
├── core/
│   ├── cluster_translator.py # K8s → Lamina abstraction layer
│   ├── sanctuary_discovery.py # Automatic sanctuary detection
│   ├── agent_tracker.py      # Agent lifecycle and state management
│   └── breath_monitor.py     # Breathing pattern analysis
├── api/
│   ├── sanctuaries.py       # Sanctuary API endpoints
│   ├── agents.py            # Agent status and interaction APIs
│   ├── memory.py            # A-MEM and knowledge graph APIs
│   └── websocket.py         # Real-time update streams
├── integrations/
│   ├── kubernetes.py        # kubectl and K8s API client
│   ├── prometheus.py        # Metrics collection
│   ├── istio.py            # Service mesh data
│   └── jaeger.py           # Distributed tracing
└── models/
    ├── sanctuary.py         # Sanctuary data models
    ├── agent.py            # Agent representation
    └── interaction.py      # Agent interaction patterns
```

#### Frontend Architecture
```javascript
frontend/
├── src/
│   ├── components/
│   │   ├── SanctuaryMap.vue      # Main topology visualization
│   │   ├── AgentCard.vue         # Individual agent status
│   │   ├── BreathVisualizer.vue  # Breathing pattern display
│   │   ├── MemoryGraph.vue       # A-MEM relationship view
│   │   └── VowMonitor.vue        # Ethical compliance dashboard
│   ├── services/
│   │   ├── api.js               # Backend API client
│   │   ├── websocket.js         # Real-time updates
│   │   └── visualization.js     # D3.js/vis.js rendering
│   └── stores/
│       ├── sanctuary.js         # Sanctuary state management
│       ├── agents.js           # Agent data store
│       └── realtime.js         # Live data coordination
```

## Consequences

### Positive
- **Lamina-Native Monitoring**: Operators can observe clusters in terms of sanctuaries and agents rather than pods and services
- **Breathing Pattern Visibility**: Real-time visualization of AI system health through breath-first principles
- **Ethical Oversight**: Dashboard for monitoring vow compliance and constraint enforcement
- **Developer Experience**: Faster debugging and system understanding through semantic visualization
- **Community Demonstration**: Powerful tool for showing Lamina OS capabilities to potential users

### Negative
- **Additional Complexity**: New service to maintain alongside existing monitoring stack
- **Resource Overhead**: Dashboard service requires CPU/memory allocation in cluster
- **Learning Curve**: Users must understand both Kubernetes and Lamina concepts
- **Data Consistency**: Potential lag between actual cluster state and dashboard representation

### Neutral
- **Complements Existing Tools**: Works alongside Prometheus/Grafana rather than replacing them
- **Extensible Architecture**: Foundation for future Lamina-specific monitoring and debugging tools
- **Kubernetes Integration**: Follows cloud-native patterns and can be deployed via Helm

## Implementation Plan

### Phase 1: Core Translation Layer (Week 1)
1. Build Kubernetes API integration
2. Implement basic pod→agent mapping
3. Create sanctuary discovery algorithms
4. Develop WebSocket real-time updates

### Phase 2: Visualization Frontend (Week 1-2)
1. Create interactive sanctuary topology view
2. Implement agent status cards and health indicators
3. Add real-time data binding and updates
4. Style according to Lamina OS design principles

### Phase 3: Advanced Features (Week 2-3)
1. Memory system visualization (A-MEM integration)
2. Breathing pattern analysis and display
3. Vow compliance monitoring
4. Traffic flow animation and interaction patterns

### Phase 4: Integration and Deployment (Week 3)
1. Prometheus custom metrics integration
2. Helm chart for dashboard deployment
3. Documentation and user guides
4. Testing with real sanctuary configurations

## Alternatives Considered

1. **Extend Existing Tools**: Customize Grafana/Kiali dashboards
   - Rejected: Limited by tool capabilities, poor Lamina semantic integration

2. **CLI-Only Visualization**: Extend lamina CLI with cluster inspection
   - Rejected: Poor user experience, limited real-time capabilities

3. **Integration with External Tools**: Use tools like Lens or k9s
   - Rejected: No ability to add Lamina-specific concepts

4. **Full Kubernetes Dashboard Replacement**: Build comprehensive K8s management UI
   - Rejected: Scope too large, duplicates existing excellent tools

## Success Criteria

1. **Functional Prototype**: Dashboard successfully displays current cluster state in Lamina terms
2. **Real-time Updates**: Live visualization of agent status changes and interactions
3. **Intuitive Navigation**: Users can understand sanctuary topology without Kubernetes knowledge
4. **Performance**: Dashboard loads within 2 seconds, updates within 500ms
5. **Integration**: Seamless deployment alongside existing Lamina OS infrastructure

## References
- [Kubernetes API Documentation](https://kubernetes.io/docs/reference/kubernetes-api/)
- [Istio Observability](https://istio.io/latest/docs/concepts/observability/)
- [Prometheus Integration Patterns](https://prometheus.io/docs/prometheus/latest/configuration/configuration/)
- [ADR-0020: Lamina Deployment Environment Architecture](0020-lamina-deployment-environment-architecture.md)

---

🔨 Crafted by Luthier