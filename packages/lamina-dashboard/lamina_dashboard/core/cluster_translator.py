#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""
Cluster State Translator

Converts raw Kubernetes cluster data into Lamina OS abstractions
(sanctuaries, agents, breathing patterns, memory systems).
"""

from typing import Dict, List, Any
from datetime import datetime
import re

class ClusterTranslator:
    """Translates Kubernetes resources to Lamina abstractions."""
    
    def __init__(self, k8s_client, prometheus_client=None):
        self.k8s_client = k8s_client
        self.prometheus_client = prometheus_client
        
        # Define Lamina component mappings
        self.lamina_mappings = {
            'ingress': ['istio-gateway', 'metallb'],
            'agents': ['lamina-core', 'agent-', 'clara', 'luna', 'vesna', 'ansel'],
            'models': ['lamina-llm-serve', 'ollama', 'model-'],
            'memory': ['memory-', 'amem-', 'chroma', 'vector-db'],
            'telemetry': ['monitoring', 'observability', 'prometheus', 'grafana', 'jaeger', 'kiali', 'loki', 'vector']
        }
    
    def translate_cluster_state(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Translate raw cluster data to Lamina abstractions."""
        
        pods = raw_data.get('pods', [])
        services = raw_data.get('services', [])
        helm_releases = raw_data.get('helm_releases', [])
        
        lamina_data = {
            'sanctuaries': self._identify_sanctuaries(pods, services),
            'agents': self._identify_agents(pods, services),
            'models': self._identify_models(pods, services, helm_releases),
            'memory_systems': self._identify_memory_systems(pods, services),
            'telemetry': self._identify_telemetry(pods, services, helm_releases),
            'ingress': self._identify_ingress(pods, services),
            'cluster_health': self._assess_cluster_health(raw_data)
        }
        
        # Add network traffic data if Prometheus is available
        if self.prometheus_client:
            try:
                traffic_data = self._get_network_traffic()
                lamina_data.update(traffic_data)
            except Exception as e:
                print(f"Failed to get traffic data: {e}")
                lamina_data['network_traffic'] = {'flows': [], 'metrics': {}}
        
        return lamina_data
    
    def _identify_sanctuaries(self, pods: List[Dict], services: List[Dict]) -> Dict[str, Any]:
        """Identify sanctuary boundaries from namespaces and service groupings."""
        sanctuaries = {}
        
        # Group by namespace as sanctuary boundaries
        namespace_groups = {}
        for pod in pods:
            namespace = pod.get('metadata', {}).get('namespace', 'unknown')
            if namespace not in namespace_groups:
                namespace_groups[namespace] = {
                    'pods': [],
                    'services': [],
                    'agents': []
                }
            namespace_groups[namespace]['pods'].append(pod)
        
        for service in services:
            namespace = service.get('metadata', {}).get('namespace', 'unknown')
            if namespace in namespace_groups:
                namespace_groups[namespace]['services'].append(service)
        
        # Convert to sanctuary representation
        for namespace, data in namespace_groups.items():
            if namespace in ['kube-system', 'kube-public', 'kube-node-lease']:
                continue  # Skip system namespaces
                
            sanctuary_type = self._classify_sanctuary(namespace, data)
            
            sanctuaries[namespace] = {
                'name': namespace,
                'type': sanctuary_type,
                'pod_count': len(data['pods']),
                'service_count': len(data['services']),
                'health': self._calculate_sanctuary_health(data['pods']),
                'agents': self._extract_agents_from_pods(data['pods']),
                'breathing_state': self._assess_breathing_pattern(data['pods'])
            }
        
        return sanctuaries
    
    def _identify_agents(self, pods: List[Dict], services: List[Dict]) -> Dict[str, Any]:
        """Identify individual agents from pods and services."""
        agents = {}
        
        for pod in pods:
            pod_name = pod.get('metadata', {}).get('name', '')
            namespace = pod.get('metadata', {}).get('namespace', '')
            
            # Check if this pod represents an agent
            if self._is_agent_pod(pod_name, namespace):
                agent_name = self._extract_agent_name(pod_name)
                
                agents[agent_name] = {
                    'name': agent_name,
                    'pod_name': pod_name,
                    'namespace': namespace,
                    'status': self._get_pod_status(pod),
                    'essence': self._infer_agent_essence(agent_name),
                    'ready': self._is_pod_ready(pod),
                    'restart_count': self._get_restart_count(pod),
                    'age': self._calculate_pod_age(pod),
                    'breathing': self._assess_agent_breathing(pod)
                }
        
        return agents
    
    def _identify_models(self, pods: List[Dict], services: List[Dict], helm_releases: List[Dict]) -> Dict[str, Any]:
        """Identify model serving instances."""
        models = {}
        
        # Look for lamina-llm-serve and similar model serving pods
        for pod in pods:
            pod_name = pod.get('metadata', {}).get('name', '')
            namespace = pod.get('metadata', {}).get('namespace', '')
            
            if any(keyword in pod_name.lower() for keyword in self.lamina_mappings['models']):
                model_name = self._extract_model_name(pod_name)
                
                models[model_name] = {
                    'name': model_name,
                    'pod_name': pod_name,
                    'namespace': namespace,
                    'status': self._get_pod_status(pod),
                    'ready': self._is_pod_ready(pod),
                    'type': self._infer_model_type(pod_name),
                    'serving_port': self._get_service_port(services, namespace, model_name)
                }
        
        return models
    
    def _identify_memory_systems(self, pods: List[Dict], services: List[Dict]) -> Dict[str, Any]:
        """Identify memory and storage systems (A-MEM, vector databases)."""
        memory_systems = {}
        
        for pod in pods:
            pod_name = pod.get('metadata', {}).get('name', '')
            namespace = pod.get('metadata', {}).get('namespace', '')
            
            if any(keyword in pod_name.lower() for keyword in self.lamina_mappings['memory']):
                memory_name = self._extract_memory_name(pod_name)
                
                memory_systems[memory_name] = {
                    'name': memory_name,
                    'pod_name': pod_name,
                    'namespace': namespace,
                    'status': self._get_pod_status(pod),
                    'type': self._infer_memory_type(pod_name),
                    'ready': self._is_pod_ready(pod)
                }
        
        return memory_systems
    
    def _identify_telemetry(self, pods: List[Dict], services: List[Dict], helm_releases: List[Dict]) -> Dict[str, Any]:
        """Identify telemetry and observability components."""
        telemetry = {}
        
        for pod in pods:
            pod_name = pod.get('metadata', {}).get('name', '')
            namespace = pod.get('metadata', {}).get('namespace', '')
            
            if any(keyword in pod_name.lower() for keyword in self.lamina_mappings['telemetry']):
                component_name = self._extract_telemetry_name(pod_name)
                
                telemetry[component_name] = {
                    'name': component_name,
                    'pod_name': pod_name,
                    'namespace': namespace,
                    'status': self._get_pod_status(pod),
                    'type': self._infer_telemetry_type(pod_name),
                    'ready': self._is_pod_ready(pod),
                    'url': self._get_telemetry_url(component_name)
                }
        
        return telemetry
    
    def _identify_ingress(self, pods: List[Dict], services: List[Dict]) -> Dict[str, Any]:
        """Identify ingress and gateway components."""
        ingress = {}
        
        for pod in pods:
            pod_name = pod.get('metadata', {}).get('name', '')
            namespace = pod.get('metadata', {}).get('namespace', '')
            
            if any(keyword in pod_name.lower() for keyword in self.lamina_mappings['ingress']):
                ingress_name = self._extract_ingress_name(pod_name)
                
                ingress[ingress_name] = {
                    'name': ingress_name,
                    'pod_name': pod_name,
                    'namespace': namespace,
                    'status': self._get_pod_status(pod),
                    'ready': self._is_pod_ready(pod),
                    'type': self._infer_ingress_type(pod_name)
                }
        
        return ingress
    
    def _classify_sanctuary(self, namespace: str, data: Dict) -> str:
        """Classify the type of sanctuary based on namespace and contents."""
        if 'monitoring' in namespace:
            return 'observability'
        elif 'istio' in namespace:
            return 'infrastructure'
        elif 'lamina' in namespace:
            return 'agent_sanctuary'
        elif 'metallb' in namespace:
            return 'networking'
        else:
            return 'application'
    
    def _is_agent_pod(self, pod_name: str, namespace: str) -> bool:
        """Determine if a pod represents an agent."""
        agent_indicators = ['agent', 'clara', 'luna', 'vesna', 'ansel', 'luthier']
        return any(indicator in pod_name.lower() for indicator in agent_indicators)
    
    def _extract_agent_name(self, pod_name: str) -> str:
        """Extract agent name from pod name."""
        # Handle deployment-generated names like "clara-agent-abc123-xyz"
        for agent in ['clara', 'luna', 'vesna', 'ansel', 'luthier']:
            if agent in pod_name.lower():
                return agent.title()
        return pod_name.split('-')[0].title()
    
    def _infer_agent_essence(self, agent_name: str) -> str:
        """Infer agent essence/role from name."""
        essence_map = {
            'Clara': 'research',
            'Luna': 'creative', 
            'Vesna': 'guardian',
            'Ansel': 'documentation',
            'Luthier': 'builder'
        }
        return essence_map.get(agent_name, 'general')
    
    def _get_pod_status(self, pod: Dict) -> str:
        """Get pod status."""
        return pod.get('status', {}).get('phase', 'Unknown')
    
    def _is_pod_ready(self, pod: Dict) -> bool:
        """Check if pod is ready."""
        conditions = pod.get('status', {}).get('conditions', [])
        for condition in conditions:
            if condition.get('type') == 'Ready':
                return condition.get('status') == 'True'
        return False
    
    def _get_restart_count(self, pod: Dict) -> int:
        """Get pod restart count."""
        statuses = pod.get('status', {}).get('containerStatuses', [])
        return sum(status.get('restartCount', 0) for status in statuses)
    
    def _calculate_pod_age(self, pod: Dict) -> str:
        """Calculate pod age."""
        created = pod.get('metadata', {}).get('creationTimestamp')
        if not created:
            return 'unknown'
        
        # Simple age calculation (would need proper datetime parsing in real implementation)
        return 'recent'
    
    def _assess_breathing_pattern(self, pods: List[Dict]) -> str:
        """Assess breathing pattern of sanctuary."""
        ready_count = sum(1 for pod in pods if self._is_pod_ready(pod))
        total_count = len(pods)
        
        if total_count == 0:
            return 'silent'
        elif ready_count == total_count:
            return 'steady'
        elif ready_count > total_count * 0.5:
            return 'shallow'
        else:
            return 'distressed'
    
    def _assess_agent_breathing(self, pod: Dict) -> str:
        """Assess individual agent breathing pattern."""
        if self._is_pod_ready(pod):
            restart_count = self._get_restart_count(pod)
            if restart_count == 0:
                return 'deep'
            elif restart_count < 3:
                return 'steady'
            else:
                return 'irregular'
        else:
            return 'held'
    
    def _calculate_sanctuary_health(self, pods: List[Dict]) -> float:
        """Calculate overall sanctuary health score."""
        if not pods:
            return 0.0
        
        ready_pods = sum(1 for pod in pods if self._is_pod_ready(pod))
        return ready_pods / len(pods)
    
    def _extract_agents_from_pods(self, pods: List[Dict]) -> List[str]:
        """Extract agent names from pods in sanctuary."""
        agents = []
        for pod in pods:
            pod_name = pod.get('metadata', {}).get('name', '')
            if self._is_agent_pod(pod_name, ''):
                agents.append(self._extract_agent_name(pod_name))
        return agents
    
    def _assess_cluster_health(self, raw_data: Dict) -> Dict[str, Any]:
        """Assess overall cluster health."""
        pods = raw_data.get('pods', [])
        ready_pods = sum(1 for pod in pods if self._is_pod_ready(pod))
        total_pods = len(pods)
        
        return {
            'overall_health': ready_pods / total_pods if total_pods > 0 else 0,
            'total_pods': total_pods,
            'ready_pods': ready_pods,
            'failing_pods': total_pods - ready_pods,
            'breathing_state': 'steady' if ready_pods == total_pods else 'irregular'
        }
    
    # Utility methods for other component types
    def _extract_model_name(self, pod_name: str) -> str:
        if 'llm-serve' in pod_name:
            return 'LLM Service'
        return pod_name.split('-')[0].title()
    
    def _infer_model_type(self, pod_name: str) -> str:
        if 'llm' in pod_name.lower():
            return 'language_model'
        return 'unknown'
    
    def _extract_memory_name(self, pod_name: str) -> str:
        if 'chroma' in pod_name:
            return 'Vector Store'
        return pod_name.split('-')[0].title()
    
    def _infer_memory_type(self, pod_name: str) -> str:
        if 'chroma' in pod_name or 'vector' in pod_name:
            return 'vector_database'
        return 'memory_store'
    
    def _extract_telemetry_name(self, pod_name: str) -> str:
        for component in ['prometheus', 'grafana', 'jaeger', 'kiali', 'loki']:
            if component in pod_name:
                return component.title()
        return pod_name.split('-')[0].title()
    
    def _infer_telemetry_type(self, pod_name: str) -> str:
        type_map = {
            'prometheus': 'metrics',
            'grafana': 'dashboard',
            'jaeger': 'tracing',
            'kiali': 'service_mesh',
            'loki': 'logging'
        }
        for key, value in type_map.items():
            if key in pod_name:
                return value
        return 'monitoring'
    
    def _get_telemetry_url(self, component_name: str) -> str:
        """Get telemetry component URL."""
        import os
        
        # Detect if running inside cluster vs externally
        if os.path.exists('/var/run/secrets/kubernetes.io/serviceaccount'):
            # Running inside cluster - provide external URLs for frontend access
            url_map = {
                'Grafana': 'http://grafana.lamina.local',
                'Prometheus': 'http://prometheus.lamina.local',
                'Jaeger': 'http://jaeger.lamina.local',
                'Kiali': 'http://kiali.lamina.local'
            }
        else:
            # Running externally - same external URLs
            url_map = {
                'Grafana': 'http://grafana.lamina.local',
                'Prometheus': 'http://prometheus.lamina.local',
                'Jaeger': 'http://jaeger.lamina.local',
                'Kiali': 'http://kiali.lamina.local'
            }
        return url_map.get(component_name, '')
    
    def _extract_ingress_name(self, pod_name: str) -> str:
        if 'gateway' in pod_name:
            return 'Istio Gateway'
        elif 'metallb' in pod_name:
            return 'MetalLB'
        return pod_name.split('-')[0].title()
    
    def _infer_ingress_type(self, pod_name: str) -> str:
        if 'istio' in pod_name:
            return 'service_mesh_gateway'
        elif 'metallb' in pod_name:
            return 'load_balancer'
        return 'ingress'
    
    def _get_service_port(self, services: List[Dict], namespace: str, service_name: str) -> int:
        """Get service port for a given service."""
        for service in services:
            if (service.get('metadata', {}).get('namespace') == namespace and 
                service_name.lower() in service.get('metadata', {}).get('name', '').lower()):
                ports = service.get('spec', {}).get('ports', [])
                if ports:
                    return ports[0].get('port', 0)
        return 0
    
    def _get_network_traffic(self) -> Dict[str, Any]:
        """Get network traffic data from Prometheus."""
        if not self.prometheus_client:
            return {'network_traffic': {'flows': [], 'metrics': {}}}
        
        # Get service traffic flows
        traffic_flows = self.prometheus_client.get_service_traffic()
        
        # Get service health metrics
        health_metrics = self.prometheus_client.get_service_health()
        
        # Get agent interactions
        agent_interactions = self.prometheus_client.get_agent_interactions()
        
        # Get model usage
        model_usage = self.prometheus_client.get_model_usage()
        
        # Get cluster overview
        cluster_overview = self.prometheus_client.get_cluster_overview()
        
        # Process traffic flows into sanctuary/agent abstractions
        sanctuary_flows = self._process_traffic_flows(traffic_flows.get('flows', []))
        
        return {
            'network_traffic': {
                'flows': sanctuary_flows,
                'agent_interactions': agent_interactions,
                'model_usage': model_usage,
                'metrics': {
                    'health': health_metrics,
                    'overview': cluster_overview
                }
            }
        }
    
    def _process_traffic_flows(self, raw_flows: List[Dict]) -> List[Dict]:
        """Process raw traffic flows into sanctuary/agent abstractions."""
        processed_flows = []
        
        for flow in raw_flows:
            # Determine if this is an agent-to-agent flow
            source = self._map_service_to_lamina_component(flow.get('source', ''))
            destination = self._map_service_to_lamina_component(flow.get('destination', ''))
            
            if source and destination:
                processed_flows.append({
                    'source': source,
                    'destination': destination,
                    'rate': flow.get('rate', 0),
                    'type': self._classify_flow_type(source, destination),
                    'timestamp': flow.get('timestamp'),
                    'namespace': flow.get('namespace', '')
                })
        
        return processed_flows
    
    def _map_service_to_lamina_component(self, service_name: str) -> str:
        """Map service name to Lamina component type."""
        service_lower = service_name.lower()
        
        # Agent mappings
        agent_map = {
            'clara': 'Clara',
            'luna': 'Luna', 
            'vesna': 'Vesna',
            'ansel': 'Ansel',
            'luthier': 'Luthier'
        }
        
        for agent, name in agent_map.items():
            if agent in service_lower:
                return name
        
        # Service type mappings
        if 'llm' in service_lower or 'model' in service_lower:
            return 'Model Service'
        elif 'memory' in service_lower or 'chroma' in service_lower:
            return 'Memory System'
        elif 'gateway' in service_lower or 'ingress' in service_lower:
            return 'Gateway'
        elif any(tel in service_lower for tel in ['prometheus', 'grafana', 'jaeger']):
            return 'Telemetry'
        elif 'lamina' in service_lower:
            return 'Lamina Core'
        
        return service_name.title()
    
    def _classify_flow_type(self, source: str, destination: str) -> str:
        """Classify the type of traffic flow."""
        agents = ['Clara', 'Luna', 'Vesna', 'Ansel', 'Luthier']
        
        if source in agents and destination in agents:
            return 'agent_to_agent'
        elif source in agents and 'Model' in destination:
            return 'agent_to_model'
        elif source in agents and 'Memory' in destination:
            return 'agent_to_memory'
        elif 'Gateway' in source:
            return 'external_to_sanctuary'
        elif 'Telemetry' in destination:
            return 'monitoring'
        else:
            return 'service_to_service'