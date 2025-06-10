#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""
Kubernetes Integration for Sanctuary Dashboard

Provides interface to query Kubernetes cluster state using kubectl
and the Kubernetes Python client.
"""

import json
import subprocess
from typing import Dict, List, Any
from datetime import datetime

class KubernetesClient:
    """Client for interacting with Kubernetes cluster."""
    
    def __init__(self):
        self.kubectl_available = self._check_kubectl()
        
    def _check_kubectl(self) -> bool:
        """Check if kubectl is available and configured."""
        try:
            result = subprocess.run(['kubectl', 'version', '--client'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def _run_kubectl(self, args: List[str]) -> Dict[str, Any]:
        """Run kubectl command and return parsed JSON result."""
        if not self.kubectl_available:
            return {}
            
        try:
            cmd = ['kubectl'] + args
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return json.loads(result.stdout) if result.stdout.strip() else {}
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            print(f"kubectl command failed: {' '.join(args)}: {e}")
            return {}
    
    def get_cluster_snapshot(self) -> Dict[str, Any]:
        """Get comprehensive cluster state snapshot."""
        snapshot = {
            'timestamp': datetime.now().isoformat(),
            'pods': self.get_all_pods(),
            'services': self.get_all_services(),
            'deployments': self.get_all_deployments(),
            'virtualservices': self.get_virtual_services(),
            'helm_releases': self.get_helm_releases(),
            'namespaces': self.get_namespaces()
        }
        return snapshot
    
    def get_all_pods(self) -> List[Dict[str, Any]]:
        """Get all pods across all namespaces."""
        result = self._run_kubectl([
            'get', 'pods', '--all-namespaces', 
            '-o', 'json'
        ])
        return result.get('items', [])
    
    def get_all_services(self) -> List[Dict[str, Any]]:
        """Get all services across all namespaces."""
        result = self._run_kubectl([
            'get', 'services', '--all-namespaces',
            '-o', 'json'
        ])
        return result.get('items', [])
    
    def get_all_deployments(self) -> List[Dict[str, Any]]:
        """Get all deployments across all namespaces."""
        result = self._run_kubectl([
            'get', 'deployments', '--all-namespaces',
            '-o', 'json'
        ])
        return result.get('items', [])
    
    def get_virtual_services(self) -> List[Dict[str, Any]]:
        """Get Istio VirtualServices."""
        result = self._run_kubectl([
            'get', 'virtualservices', '--all-namespaces',
            '-o', 'json'
        ])
        return result.get('items', [])
    
    def get_helm_releases(self) -> List[Dict[str, Any]]:
        """Get Helm releases."""
        try:
            result = subprocess.run([
                'helm', 'list', '--all-namespaces', '-o', 'json'
            ], capture_output=True, text=True, check=True)
            return json.loads(result.stdout) if result.stdout.strip() else []
        except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError):
            return []
    
    def get_namespaces(self) -> List[Dict[str, Any]]:
        """Get all namespaces."""
        result = self._run_kubectl([
            'get', 'namespaces', '-o', 'json'
        ])
        return result.get('items', [])
    
    def get_pod_logs(self, namespace: str, pod_name: str, lines: int = 100) -> str:
        """Get logs from a specific pod."""
        try:
            result = subprocess.run([
                'kubectl', 'logs', '-n', namespace, pod_name, 
                '--tail', str(lines)
            ], capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError:
            return ""
    
    def get_service_endpoints(self, namespace: str, service_name: str) -> Dict[str, Any]:
        """Get endpoints for a specific service."""
        result = self._run_kubectl([
            'get', 'endpoints', '-n', namespace, service_name,
            '-o', 'json'
        ])
        return result
    
    def check_connectivity(self) -> bool:
        """Check if we can connect to the cluster."""
        try:
            result = subprocess.run([
                'kubectl', 'cluster-info'
            ], capture_output=True, text=True, check=True)
            return "running at" in result.stdout
        except subprocess.CalledProcessError:
            return False