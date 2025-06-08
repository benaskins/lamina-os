# 🜄 Lamina OS Mac Production Infrastructure

Production-grade Kubernetes cluster optimized for Apple Silicon Mac hardware. This setup provides enterprise-level capabilities while leveraging your Mac's unique advantages for AI workloads.

## 🎯 Architecture Overview

### Why Mac Production?

**Hardware Advantages:**
- **Apple Silicon Performance**: Unified memory architecture perfect for LLM inference
- **NVMe SSD Storage**: Ultra-fast model loading and caching
- **Energy Efficiency**: 24/7 operation without massive power consumption
- **Complete Privacy**: All inference happens locally, no data leaves your machine
- **Zero Cloud Costs**: No ongoing expenses for model serving

**Production Features:**
- **Real Kubernetes**: Full upstream k3s, not simplified dev environment
- **High Availability Services**: Clustered ChromaDB, auto-scaling Lamina services
- **Production Monitoring**: Prometheus, Grafana, Jaeger tracing stack
- **Enterprise Security**: RBAC, Network Policies, TLS everywhere
- **GitOps Ready**: ArgoCD integration for automated deployments

## 🚀 Quick Start

### Prerequisites
- **macOS 12.0+** (Monterey or newer)
- **16GB+ RAM** (32GB+ recommended for large models)
- **100GB+ free storage** (for models and data)
- **Admin privileges** (for k3s installation)

### Installation

```bash
# 1. Clone and navigate to infrastructure
cd lamina-os-test-improvements/infrastructure/mac-production

# 2. Run the installation script
./install-k3s.sh

# 3. Verify cluster is ready
kubectl get nodes
kubectl get namespaces
```

The script will:
- ✅ Install k3s with Mac-optimized configuration
- ✅ Set up production storage classes
- ✅ Configure networking and security
- ✅ Install core production components (cert-manager, nginx-ingress, MetalLB)
- ✅ Create lamina-production namespace with resource quotas

## 🏗️ Infrastructure Components

### Core Kubernetes Stack
```yaml
k3s: v1.28+                    # Lightweight Kubernetes
cert-manager: v1.13+           # TLS certificate management  
nginx-ingress: v1.9+           # HTTP/HTTPS load balancing
metallb: v0.13+                # LoadBalancer services
```

### Storage Configuration
```yaml
Storage Class: mac-ssd-fast
├── Provisioner: local-path      # Fast local SSD storage
├── Mount Options: noatime       # Optimized for Mac SSDs
├── Reclaim Policy: Retain       # Don't lose data on accidents
└── Volume Expansion: true       # Grow volumes as needed
```

### Resource Allocation (32GB Mac Example)
```yaml
System Reserved: 8GB             # macOS + k3s control plane
Application Pool: 24GB           # For Lamina services
├── lamina-core: 1-2GB per pod
├── lamina-llm-serve: 4-8GB per pod  
└── chromadb: 2-4GB per pod
```

## 🔧 Configuration Files

### k3s-config.yaml
Complete production configuration including:
- **Performance optimizations** for Apple Silicon
- **Storage classes** optimized for Mac SSDs  
- **Resource quotas** preventing resource exhaustion
- **Network policies** for production security

### install-k3s.sh
Automated installation script that:
- **Validates hardware** requirements
- **Optimizes k3s settings** for Mac performance
- **Installs core components** needed for production
- **Configures networking** and storage

## 🎛️ Production Features

### Auto-Scaling Configuration
```yaml
# Horizontal Pod Autoscaling based on:
CPU Utilization: 70%            # Scale when CPU hits 70%
Memory Utilization: 80%         # Scale when memory hits 80%
Custom Metrics: Model RPS       # Scale based on inference load
```

### Monitoring & Observability
```yaml
Prometheus: ✅ Metrics collection
Grafana: ✅ Dashboards and alerting
Jaeger: ✅ Distributed tracing
Loki: ✅ Log aggregation
```

### Security Hardening
```yaml
RBAC: ✅ Role-based access control
Network Policies: ✅ Traffic segmentation
TLS Everywhere: ✅ End-to-end encryption
Pod Security: ✅ Non-root containers
```

## 📊 Performance Optimizations

### Apple Silicon Specific
```yaml
# Kubelet optimizations
max-pods: 250                   # Higher pod density
serialize-image-pulls: false    # Parallel pulls (fast SSD)
kube-reserved: cpu=1000m,memory=2Gi
system-reserved: cpu=500m,memory=1Gi
```

### Storage Optimizations
```yaml
# etcd optimizations for SSD
quota-backend-bytes: 8GB        # Large etcd database
auto-compaction: 1h             # Frequent compaction
```

### Networking Optimizations
```yaml
flannel-backend: host-gw        # Fastest for single node
cluster-cidr: 10.42.0.0/16      # Optimized IP allocation
```

## 🛠️ Management Commands

### Cluster Operations
```bash
# Check cluster status
kubectl cluster-info
kubectl get nodes -o wide

# Monitor resource usage
kubectl top nodes
kubectl top pods -A

# View logs
sudo journalctl -u k3s -f
kubectl logs -f deployment/lamina-core -n lamina-production
```

### Service Management
```bash
# Restart k3s (if needed)
sudo systemctl restart k3s

# Stop k3s
sudo systemctl stop k3s

# Check k3s status
sudo systemctl status k3s
```

### Storage Management
```bash
# Check persistent volumes
kubectl get pv
kubectl get pvc -A

# Monitor storage usage
df -h /opt/lamina/storage
```

## 🚀 Next Steps

1. **Deploy Monitoring Stack**:
   ```bash
   helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
   helm install monitoring prometheus-community/kube-prometheus-stack -n monitoring --create-namespace
   ```

2. **Deploy Lamina Services**:
   ```bash
   kubectl apply -f ../../charts/lamina-production/
   ```

3. **Set Up GitOps**:
   ```bash
   kubectl apply -f ../../charts/lamina-production/argocd-application.yaml
   ```

## 🔍 Troubleshooting

### Common Issues

**k3s won't start:**
```bash
# Check system requirements
sudo /usr/local/bin/k3s check-config

# Check logs
sudo journalctl -u k3s -f
```

**Pods stuck in Pending:**
```bash
# Check node resources
kubectl describe nodes
kubectl top nodes

# Check pod events
kubectl describe pod <pod-name> -n lamina-production
```

**Storage issues:**
```bash
# Check available space
df -h /opt/lamina/storage

# Check PV status
kubectl get pv
kubectl describe pv <pv-name>
```

### Performance Tuning

**For 16GB Macs:**
- Reduce replica counts in Helm values
- Lower memory requests/limits
- Disable some monitoring components

**For 64GB+ Macs:**
- Increase worker replicas
- Enable more monitoring features
- Run multiple model serving instances

## 🎯 Production Checklist

- [ ] Cluster installed and healthy
- [ ] All core components running
- [ ] Storage classes configured
- [ ] Monitoring stack deployed
- [ ] Network policies applied
- [ ] Lamina services deployed
- [ ] GitOps configured
- [ ] Backup strategy implemented

---

**🌊 Built with breath-first principles for conscious AI development**

*Infrastructure crafted by Luthier for production AI workloads on Apple Silicon*