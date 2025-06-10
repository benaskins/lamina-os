#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""
Sanctuary Cluster Visualization Dashboard

A web-based dashboard that visualizes Kubernetes cluster state through
Lamina OS abstractions (sanctuaries, agents, breathing patterns).
"""

# CRITICAL: Import eventlet first and patch before any other modules
import eventlet
eventlet.monkey_patch()

import asyncio
import json
from datetime import datetime
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import threading
import time

from .core.cluster_translator import ClusterTranslator
from .integrations.kubernetes import KubernetesClient
from .integrations.prometheus import PrometheusClient
from .config import DashboardConfig

import os

# Get the directory where this app.py file is located
current_dir = os.path.dirname(os.path.abspath(__file__))
# Templates and static are in the parent directory
parent_dir = os.path.dirname(current_dir)

app = Flask(__name__, 
           template_folder=os.path.join(parent_dir, 'templates'),
           static_folder=os.path.join(parent_dir, 'static'))
app.config['SECRET_KEY'] = 'lamina-sanctuary-dashboard'
socketio = SocketIO(app, cors_allowed_origins="*")

# Load configuration and initialize components
config = DashboardConfig()
monitoring_config = config.get_monitoring_config()

k8s_client = KubernetesClient()
prometheus_client = PrometheusClient()
translator = ClusterTranslator(k8s_client, prometheus_client)

# Global state for real-time updates - use thread-safe approach
cluster_state = {
    'last_updated': None,
    'sanctuaries': {},
    'agents': {},
    'models': {},
    'memory_systems': {},
    'telemetry': {}
}

# No background monitoring in web app - keep it simple and stable
# WebSocket will only send data when API endpoints are called

@app.route('/')
def dashboard():
    """Main dashboard page."""
    # Add cache-busting timestamp
    timestamp = str(int(time.time()))
    return render_template('dashboard.html', cache_bust=timestamp)

@app.route('/api/cluster/state')
def get_cluster_state():
    """Get current cluster state in Lamina abstractions."""
    try:
        # Force fresh data fetch to avoid stale global state in multiprocess environment
        print(f"🔄 Fetching fresh cluster data for API request")
        raw_data = k8s_client.get_cluster_snapshot()
        k8s_translator = ClusterTranslator(k8s_client, None)
        fresh_data = k8s_translator.translate_cluster_state(raw_data)
        fresh_data['last_updated'] = datetime.now().isoformat()
        print(f"✅ Fresh data: {fresh_data.get('cluster_health', {}).get('total_pods')} pods, {fresh_data.get('cluster_health', {}).get('overall_health')} health")
        return jsonify(fresh_data)
    except Exception as e:
        print(f"❌ Error fetching fresh cluster state: {e}")
        # Fallback to global state if fresh fetch fails
        return jsonify(cluster_state)

def get_fresh_cluster_data():
    """Helper function to get fresh cluster data."""
    try:
        raw_data = k8s_client.get_cluster_snapshot()
        k8s_translator = ClusterTranslator(k8s_client, None)
        return k8s_translator.translate_cluster_state(raw_data)
    except Exception as e:
        print(f"Error fetching fresh data: {e}")
        return cluster_state

@app.route('/api/sanctuaries')
def get_sanctuaries():
    """Get all sanctuary information."""
    fresh_data = get_fresh_cluster_data()
    return jsonify(fresh_data.get('sanctuaries', {}))

@app.route('/api/agents')
def get_agents():
    """Get all agent status and information."""
    fresh_data = get_fresh_cluster_data()
    return jsonify(fresh_data.get('agents', {}))

@app.route('/api/models')
def get_models():
    """Get model serving status."""
    fresh_data = get_fresh_cluster_data()
    return jsonify(fresh_data.get('models', {}))

@app.route('/api/memory')
def get_memory_systems():
    """Get memory system status."""
    fresh_data = get_fresh_cluster_data()
    return jsonify(fresh_data.get('memory_systems', {}))

@app.route('/api/telemetry')
def get_telemetry():
    """Get telemetry and observability status."""
    fresh_data = get_fresh_cluster_data()
    return jsonify(fresh_data.get('telemetry', {}))

@app.route('/api/traffic')
def get_network_traffic():
    """Get network traffic flows and metrics."""
    fresh_data = get_fresh_cluster_data()
    return jsonify(fresh_data.get('network_traffic', {'flows': [], 'metrics': {}}))

@app.route('/api/pod-states')
def get_pod_states():
    """Get detailed pod state information including problematic pods."""
    fresh_data = get_fresh_cluster_data()
    cluster_health = fresh_data.get('cluster_health', {})
    return jsonify({
        'pod_states': cluster_health.get('pod_states', {}),
        'problematic_pods': cluster_health.get('problematic_pods', []),
        'summary': {
            'total_pods': cluster_health.get('total_pods', 0),
            'ready_pods': cluster_health.get('ready_pods', 0),
            'failing_pods': cluster_health.get('failing_pods', 0),
            'overall_health': cluster_health.get('overall_health', 0)
        }
    })

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    print('Client connected')
    # Send fresh data on connect
    fresh_data = get_fresh_cluster_data()
    emit('cluster_update', fresh_data)

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    print('Client disconnected')

@socketio.on('request_update')
def handle_update_request():
    """Handle manual update request from client."""
    # Always send fresh data on request
    fresh_data = get_fresh_cluster_data()
    emit('cluster_update', fresh_data)

# Simplified startup - no background threads
print("🌬️ Sanctuary Dashboard initialized")
print("📊 Using on-demand cluster state fetching")
print("🔗 WebSocket support enabled")

if __name__ == '__main__':
    print("🌬️ Starting Sanctuary Dashboard")
    print("🔗 Access at: http://localhost:5001")
    print("📊 Monitoring Lamina OS cluster state...")
    
    # Start Flask app with SocketIO (development mode)
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)