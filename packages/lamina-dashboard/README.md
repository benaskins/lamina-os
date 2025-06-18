# Lamina Dashboard

A web-based dashboard that visualizes Kubernetes cluster state through Lamina OS abstractions (sanctuaries, agents, breathing patterns, memory systems).

## Features

- **Real-time Cluster Monitoring**: Live updates of cluster state every 5 seconds
- **Lamina Abstractions**: Translates Kubernetes resources into sanctuary/agent concepts
- **Interactive Visualization**: Click agents and telemetry components for details
- **Breathing Patterns**: Visual representation of system health through breathing metaphors
- **Component Grouping**: Organizes cluster resources by function (Ingress, Agents, Models, Memory, Telemetry)
- **Hostname-based Routing**: Clean URLs for all observability tools (grafana.lamina.local, prometheus.lamina.local, etc.)

## Installation

### Development (Local)

```bash
cd packages/lamina-dashboard
uv sync
uv run lamina-dashboard
```

### Production (Container)

```bash
# Build container
docker build -t lamina-dashboard:latest .

# Run container
docker run -p 5001:5001 lamina-dashboard:latest
```

### Kubernetes Deployment

```bash
# Deploy via Helm
helm install lamina-dashboard ./chart --namespace lamina-dashboard --create-namespace
```

## Architecture

### Backend Components

- **Flask API Server**: Main web server with WebSocket support
- **Kubernetes Client**: Queries cluster state via kubectl
- **Prometheus Client**: Retrieves metrics via hostname-based routing
- **Cluster Translator**: Converts K8s resources to Lamina abstractions

### Frontend Components

- **Interactive Dashboard**: Main UI with real-time updates
- **WebSocket Client**: Live data binding with 5-second refresh
- **Sanctuary Styling**: Lamina-themed CSS with breathing animations

## Component Mapping

The dashboard translates Kubernetes resources to Lamina concepts:

| Kubernetes Resource | Lamina Abstraction |
|-------------------|------------------|
| Namespaces | Sanctuary boundaries |
| Pods with agent names | Individual agents |
| lamina-llm-serve pods | Model serving instances |
| vector/memory pods | Memory systems |
| monitoring pods | Telemetry components |
| Gateway/LoadBalancer | Ingress systems |

## Configuration

### Agent Detection

The system identifies agents by looking for pods with these name patterns:
- `clara`, `luna`, `vesna`, `ansel`, `luthier`
- Pods containing `agent-` prefix
- Pods in lamina-related namespaces

### Telemetry URLs

The dashboard uses hostname-based routing for clean URLs:
- **Grafana**: `http://grafana.lamina.local`
- **Prometheus**: `http://prometheus.lamina.local`
- **Jaeger**: `http://jaeger.lamina.local`
- **Kiali**: `http://kiali.lamina.local`

## Health Indicators

- **Green**: Component is ready and healthy
- **Red**: Component is not ready or failing
- **Breathing Patterns**:
  - Steady: All components healthy
  - Shallow: Some components degraded
  - Irregular: Intermittent issues
  - Distressed: Multiple failures

## Development

### Testing

```bash
uv run pytest tests/ -v
```

### Linting

```bash
uv run ruff check
uv run ruff format
```

## License

Mozilla Public License 2.0 (MPL-2.0)

---

🌬️ **Lamina OS Sanctuary Visualization** - Bringing breath-first principles to cluster monitoring