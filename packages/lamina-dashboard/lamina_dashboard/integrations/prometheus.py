#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""
Prometheus Integration for Network Traffic Visualization

Queries Istio service mesh metrics to show real-time traffic flows
between sanctuary components.
"""

import requests
import json
from typing import Dict, List, Any
from datetime import datetime, timedelta

class PrometheusClient:
    """Client for querying Prometheus metrics."""
    
    def __init__(self, prometheus_url: str = None):
        # Detect if we're running inside cluster vs externally
        import os
        
        if os.path.exists('/var/run/secrets/kubernetes.io/serviceaccount'):
            # Running inside cluster - use internal service DNS
            self.base_url = prometheus_url or "http://prometheus.monitoring.svc.cluster.local:9090"
            print("🔧 Running inside cluster - using internal service DNS")
        else:
            # Running externally - use external hostname routing
            self.base_url = prometheus_url or "http://prometheus.lamina.local"
            print("🔧 Running externally - using gateway hostname routing")
            
        self.session = requests.Session()
        
        # Set user agent header
        self.session.headers.update({
            'User-Agent': 'Lamina-Sanctuary-Dashboard/1.0'
        })
        
        print(f"Prometheus client configured for: {self.base_url}")
        
        # Test connectivity
        if self.check_connectivity():
            print("✅ Prometheus connectivity verified")
        else:
            print("⚠️ Prometheus not accessible - checking if route exists in VirtualService")
        
    def query(self, query: str, time_range: str = "5m") -> Dict[str, Any]:
        """Execute a Prometheus query."""
        if not self.base_url:
            return {"status": "error", "data": {"result": []}}
            
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/query",
                params={
                    "query": query,
                    "time": datetime.now().isoformat()
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Prometheus query failed: {e}")
            return {"status": "error", "data": {"result": []}}
    
    def query_range(self, query: str, duration: str = "5m", step: str = "30s") -> Dict[str, Any]:
        """Execute a Prometheus range query."""
        if not self.base_url:
            return {"status": "error", "data": {"result": []}}
            
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(minutes=5)
            
            response = self.session.get(
                f"{self.base_url}/api/v1/query_range",
                params={
                    "query": query,
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat(),
                    "step": step
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Prometheus range query failed: {e}")
            return {"status": "error", "data": {"result": []}}
    
    def get_service_traffic(self) -> Dict[str, Any]:
        """Get current traffic between services."""
        # Query for request rates between services
        query = '''
        sum(rate(istio_requests_total[5m])) by (source_app, destination_service_name, destination_service_namespace)
        '''
        
        result = self.query(query)
        traffic_flows = []
        
        if result.get("status") == "success":
            for metric in result.get("data", {}).get("result", []):
                labels = metric.get("metric", {})
                value = metric.get("value", [None, "0"])
                
                if len(value) >= 2 and float(value[1]) > 0:
                    traffic_flows.append({
                        "source": labels.get("source_app", "unknown"),
                        "destination": labels.get("destination_service_name", "unknown"),
                        "namespace": labels.get("destination_service_namespace", "unknown"),
                        "rate": float(value[1]),
                        "timestamp": value[0]
                    })
        
        return {"flows": traffic_flows}
    
    def get_service_health(self) -> Dict[str, Any]:
        """Get service health metrics (success rates, latency)."""
        queries = {
            "success_rate": '''
            sum(rate(istio_requests_total{response_code!~"5.*"}[5m])) by (destination_service_name, destination_service_namespace) /
            sum(rate(istio_requests_total[5m])) by (destination_service_name, destination_service_namespace) * 100
            ''',
            "request_rate": '''
            sum(rate(istio_requests_total[5m])) by (destination_service_name, destination_service_namespace)
            ''',
            "p99_latency": '''
            histogram_quantile(0.99, sum(rate(istio_request_duration_milliseconds_bucket[5m])) by (destination_service_name, destination_service_namespace, le))
            '''
        }
        
        health_data = {}
        
        for metric_name, query in queries.items():
            result = self.query(query)
            health_data[metric_name] = []
            
            if result.get("status") == "success":
                for metric in result.get("data", {}).get("result", []):
                    labels = metric.get("metric", {})
                    value = metric.get("value", [None, "0"])
                    
                    if len(value) >= 2:
                        health_data[metric_name].append({
                            "service": labels.get("destination_service_name", "unknown"),
                            "namespace": labels.get("destination_service_namespace", "unknown"),
                            "value": float(value[1]) if value[1] != "NaN" else 0,
                            "timestamp": value[0]
                        })
        
        return health_data
    
    def get_agent_interactions(self) -> List[Dict[str, Any]]:
        """Get agent-to-agent interactions from HTTP traffic."""
        # Look for requests with agent-related headers or paths
        query = '''
        sum(rate(istio_requests_total{request_protocol="http"}[5m])) by (source_app, destination_service_name, destination_service_namespace)
        '''
        
        result = self.query(query)
        interactions = []
        
        if result.get("status") == "success":
            for metric in result.get("data", {}).get("result", []):
                labels = metric.get("metric", {})
                value = metric.get("value", [None, "0"])
                
                source = labels.get("source_app", "")
                destination = labels.get("destination_service_name", "")
                
                # Filter for potential agent interactions
                agent_keywords = ["agent", "clara", "luna", "vesna", "ansel", "lamina"]
                if (any(keyword in source.lower() for keyword in agent_keywords) or
                    any(keyword in destination.lower() for keyword in agent_keywords)):
                    
                    if len(value) >= 2 and float(value[1]) > 0:
                        interactions.append({
                            "source": source,
                            "destination": destination,
                            "namespace": labels.get("destination_service_namespace", ""),
                            "rate": float(value[1]),
                            "type": "agent_interaction",
                            "timestamp": value[0]
                        })
        
        return interactions
    
    def get_model_usage(self) -> List[Dict[str, Any]]:
        """Get model serving usage metrics."""
        query = '''
        sum(rate(istio_requests_total{destination_service_name=~".*llm.*|.*model.*"}[5m])) by (source_app, destination_service_name)
        '''
        
        result = self.query(query)
        model_usage = []
        
        if result.get("status") == "success":
            for metric in result.get("data", {}).get("result", []):
                labels = metric.get("metric", {})
                value = metric.get("value", [None, "0"])
                
                if len(value) >= 2 and float(value[1]) > 0:
                    model_usage.append({
                        "client": labels.get("source_app", "unknown"),
                        "model_service": labels.get("destination_service_name", "unknown"),
                        "rate": float(value[1]),
                        "timestamp": value[0]
                    })
        
        return model_usage
    
    def check_connectivity(self) -> bool:
        """Check if Prometheus is reachable."""
        if not self.base_url:
            return False
            
        try:
            response = self.session.get(f"{self.base_url}/api/v1/status/config", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def get_cluster_overview(self) -> Dict[str, Any]:
        """Get high-level cluster traffic overview."""
        queries = {
            "total_requests": "sum(rate(istio_requests_total[5m]))",
            "error_rate": """
            sum(rate(istio_requests_total{response_code=~"5.*"}[5m])) / 
            sum(rate(istio_requests_total[5m])) * 100
            """,
            "active_connections": "sum(istio_tcp_connections_opened_total) - sum(istio_tcp_connections_closed_total)"
        }
        
        overview = {}
        for metric_name, query in queries.items():
            result = self.query(query)
            
            if result.get("status") == "success":
                data = result.get("data", {}).get("result", [])
                if data:
                    value = data[0].get("value", [None, "0"])
                    if len(value) >= 2:
                        overview[metric_name] = float(value[1]) if value[1] != "NaN" else 0
                else:
                    overview[metric_name] = 0
            else:
                overview[metric_name] = 0
        
        return overview