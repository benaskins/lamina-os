# Infrastructure Setup Guide

This guide covers infrastructure setup for deploying Lamina Core agents with Docker, service mesh, and observability.

## Overview

Lamina Core provides a containerized infrastructure stack with:

- **Docker Compose**: Service orchestration
- **mTLS Service Mesh**: Secure inter-service communication  
- **Observability Stack**: Logging, metrics, and monitoring
- **Configuration Management**: Environment-based configuration
- **Breath-Aware Infrastructure**: Conscious deployment patterns

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ with uv
- Git

### Basic Setup

1. **Clone and setup:**
```bash
git clone https://github.com/benaskins/lamina-os
cd lamina-os
uv sync
```

2. **Start infrastructure:**
```bash
# Start basic services
uv run docker-compose up -d

# Verify services are running
uv run docker-compose ps
```

3. **Test agent coordination:**
```bash
# Run coordination demo
uv run python examples/working_coordination_demo.py
```

## Infrastructure Components

### Core Services

- Multi-agent routing and coordination
- Breath-aware processing with presence pauses
- Intent classification and intelligent routing

**Backend Providers:**
- Ollama for local AI models
- HuggingFace for cloud models  
- Mock backend for testing

**Memory System:**
- ChromaDB for vector storage
- Semantic memory with evolution tracking
- Context-aware retrieval

### Observability Stack

**Logging (Loki):**
- Centralized log aggregation
- Structured logging for all services
- Query and analysis interface

**Metrics (Grafana):**
- Service health monitoring
- Agent performance dashboards
- Community usage analytics

**Tracing (Vector):**
- Request flow tracking
- Service dependency mapping
- Performance bottleneck identification

## Docker Configuration

### Service Definitions

The infrastructure uses Docker Compose with environment-specific configurations:

```yaml
# docker-compose.yml (simplified)
version: '3.8'

services:
  lamina-coordinator:
    build: .
    ports:
      - "8000:8000"
    environment:
      - BREATH_MODULATION=true
      - CONSCIOUS_PAUSE=0.5
    depends_on:
      - chromadb
      - ollama
      
  chromadb:
    image: chromadb/chroma:latest
    ports:
      - "8001:8000"
    volumes:
      - chromadb_data:/chroma/chroma
      
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
```

### Environment Configuration

**Development (.env.dev):**
```bash
# Core settings
ENVIRONMENT=development
LOG_LEVEL=DEBUG
BREATH_MODULATION=true
CONSCIOUS_PAUSE=1.0

# Backend configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# Memory configuration  
CHROMADB_URL=http://localhost:8001
MEMORY_COLLECTION=lamina_dev
```

**Production (.env.prod):**
```bash
# Core settings
ENVIRONMENT=production
LOG_LEVEL=INFO
BREATH_MODULATION=true
CONSCIOUS_PAUSE=0.5

# Security
SSL_CERT_PATH=/certs/lamina.crt
SSL_KEY_PATH=/certs/lamina.key
MTLS_ENABLED=true

# Scaling
COORDINATOR_REPLICAS=3
BACKEND_TIMEOUT=30
```

## Service Mesh and Security

### mTLS Configuration

For production deployments, enable mutual TLS:

1. **Generate certificates:**
```bash
# Create certificate authority
./scripts/generate-ca.sh

# Generate service certificates
./scripts/generate-service-certs.sh coordinator
./scripts/generate-service-certs.sh chromadb
./scripts/generate-service-certs.sh ollama
```

2. **Configure mTLS:**
```yaml
# docker-compose.mtls.yml
services:
  lamina-coordinator:
    environment:
      - MTLS_ENABLED=true
      - SSL_CERT_PATH=/certs/coordinator.crt
      - SSL_KEY_PATH=/certs/coordinator.key
      - CA_CERT_PATH=/certs/ca.crt
    volumes:
      - ./certs:/certs:ro
```

3. **Deploy with mTLS:**
```bash
docker-compose -f docker-compose.yml -f docker-compose.mtls.yml up -d
```

### Network Security

**Service Isolation:**
- Internal network for service communication
- External access only through designated ports
- Network policies for service-to-service communication

**Secrets Management:**
- Environment-based secret injection
- Encrypted certificate storage
- Rotation policies for credentials

## Deployment Patterns

### Development Deployment

Single-node development with hot reloading:

```bash
# Start with development overrides
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Enable hot reloading
docker-compose exec lamina-coordinator python -m lamina.api.server --reload
```

### Production Deployment

Multi-node production with high availability:

```yaml
# docker-compose.prod.yml
services:
  lamina-coordinator:
    deploy:
      replicas: 3
      restart_policy:
        condition: on-failure
        max_attempts: 3
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'
```

### Cloud Deployment

**AWS ECS:**
```bash
# Build and push images
docker build -t lamina-coordinator .
docker tag lamina-coordinator:latest 123456789012.dkr.ecr.us-west-2.amazonaws.com/lamina-coordinator:latest
docker push 123456789012.dkr.ecr.us-west-2.amazonaws.com/lamina-coordinator:latest

# Deploy with ECS task definition
aws ecs create-service --cluster lamina --task-definition lamina-coordinator --desired-count 3
```

**Kubernetes:**
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: lamina-coordinator
spec:
  replicas: 3
  selector:
    matchLabels:
      app: lamina-coordinator
  template:
    metadata:
      labels:
        app: lamina-coordinator
    spec:
      containers:
      - name: coordinator
        image: lamina-coordinator:latest
        ports:
        - containerPort: 8000
        env:
        - name: BREATH_MODULATION
          value: "true"
        - name: CONSCIOUS_PAUSE
          value: "0.5"
```

## Monitoring and Observability

### Health Checks

**Service Health:**
```python
# Health check endpoints
GET /health          # Basic health status
GET /health/ready    # Readiness probe
GET /health/live     # Liveness probe
GET /metrics         # Prometheus metrics
```

**Agent Health:**
```python
# Agent-specific monitoring
GET /agents/status           # All agent status
GET /agents/{name}/health    # Individual agent health
GET /coordination/stats      # Routing statistics
```

### Dashboards

**Agent Performance Dashboard:**
- Request routing distribution
- Response time by agent type
- Breath-aware processing metrics
- Error rates and patterns

**Infrastructure Dashboard:**
- Service uptime and availability
- Resource utilization (CPU, memory)
- Network traffic and latency
- Database performance metrics

### Alerting

**Critical Alerts:**
- Service downtime
- High error rates (>5%)
- Memory usage >90%
- Disk space <10%

**Breath-Aware Alerts:**
- Excessive processing speed (breathing too fast)
- Processing timeouts (breathing disrupted)
- Coordination failures
- Agent routing imbalances

## Configuration Management

### Hierarchical Configuration

1. **Defaults**: Built-in sensible defaults
2. **Environment Files**: `.env`, `.env.local`
3. **Environment Variables**: Runtime overrides
4. **Command Line**: Explicit parameter passing

### Configuration Schema

```python
# lamina/config.py
@dataclass
class LaminaConfig:
    # Core settings
    environment: str = "development"
    log_level: str = "INFO"
    
    # Breath-first settings
    breath_modulation: bool = True
    presence_pause: float = 0.5
    
    # Backend configuration
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama2"
    
    # Infrastructure
    bind_host: str = "0.0.0.0"
    bind_port: int = 8000
    worker_count: int = 1
```

### Environment-Specific Configs

- Verbose logging
- Longer presence pauses for introspection
- Hot reloading enabled
- Mock backends available

**Staging:**
- Production-like configuration
- Real backends with test data
- Performance monitoring
- Security testing

**Production:**
- Optimized performance settings
- Full security enabled
- Comprehensive monitoring
- Backup and recovery

## Scaling and Performance

### Horizontal Scaling

**Coordinator Scaling:**
```yaml
services:
  lamina-coordinator:
    deploy:
      replicas: 5
    environment:
      - LOAD_BALANCER=round_robin
      - SESSION_AFFINITY=false
```

**Backend Scaling:**
```yaml
services:
  ollama:
    deploy:
      replicas: 3
    environment:
      - MODEL_PARALLEL=true
      - GPU_COUNT=1
```

### Performance Tuning

- Adjust presence pause for load conditions
- Dynamic breathing based on system health
- Graceful degradation under high load

**Resource Optimization:**
- Memory pooling for agent contexts
- Connection pooling for backends
- Caching for repeated queries

### Load Testing

```bash
# Test agent coordination under load
uv run python tests/load_test.py --agents=3 --requests=1000 --concurrent=10

# Breath-aware load testing
uv run python tests/breath_load_test.py --breathing=true --pause=0.5
```

## Backup and Recovery

### Data Backup

**Vector Database:**
```bash
# Backup ChromaDB data
docker exec chromadb python -c "
import chromadb
client = chromadb.Client()
client.backup('/backup/chromadb-$(date +%Y%m%d).tar.gz')
"
```

**Configuration Backup:**
```bash
# Backup all configuration
tar -czf lamina-config-$(date +%Y%m%d).tar.gz \
  docker-compose.yml \
  .env* \
  certs/ \
  configs/
```

### Disaster Recovery

**Service Recovery:**
1. Restore configuration from backup
2. Restart services with Docker Compose
3. Verify agent coordination functionality
4. Restore vector database from backup
5. Validate system health and monitoring

**Data Recovery:**
```bash
# Restore ChromaDB
docker exec chromadb python -c "
import chromadb
client = chromadb.Client()
client.restore('/backup/chromadb-20231201.tar.gz')
"
```

## Troubleshooting

### Common Issues

**Service Won't Start:**
```bash
# Check container logs
docker-compose logs lamina-coordinator

# Verify configuration
uv run python -c "from lamina.config import load_config; print(load_config())"

# Test connectivity
curl http://localhost:8000/health
```

**Agent Routing Issues:**
```bash
# Check coordinator status
curl http://localhost:8000/agents/status

# Test specific routing
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test routing"}'
```

- Check presence pause settings
- Monitor resource usage
- Verify backend connectivity
- Review routing statistics

### Debug Mode

Enable comprehensive debugging:

```bash
# Start with debug configuration
docker-compose -f docker-compose.yml -f docker-compose.debug.yml up

# Enable trace logging
export LOG_LEVEL=TRACE
export BREATH_DEBUGGING=true
```

This infrastructure setup provides a solid foundation for deploying attuned, breath-aware AI systems that scale gracefully while maintaining their contemplative nature.
